import math

class Line:
    def __init__(self, pt1, pt2, angle = 0, sector = 0, color = None, id = ''):
        self.pt1 = pt1
        self.pt2 = pt2
        self.angle = angle
        self.sector = sector
        self.color = color
        self.count = 0
        
        k = pt2[0] - pt1[0];
        if k == 0:
            self.k = 999999999
        else: 
            self.k = (pt2[1] - pt1[1]) / (pt2[0] - pt1[0])

        self.center = (int((self.pt1[0] + self.pt2[0]) / 2), int((self.pt1[1] + self.pt2[1]) / 2))

        if id != '':
            l = 30

            x0 = self.center[0]
            y0 = self.center[1]

            k1 = math.tan(math.pi / 2 + math.atan(self.k))
            b1 = self.center[1] - k1 * self.center[0]

            a = 1 + k1 * k1
            b = 2 * (k1 * b1 - x0 - y0 * k1)
            c = x0 * x0 + y0 * y0 - 2 * y0 * b1 + b1 * b1 - l * l
        
            ds = math.sqrt(b * b - 4 * a * c)
        
            points = []
            x1 = (-b + ds) / (2 * a)
            y1 = int(k1 * x1 + b1)

            points.append((int(x1), y1));

            x2 = (-b - ds) / (2 * a)
            y2 = int(k1 * x2 + b1)

            points.append((x2, y2));

            self.vertor_pt1 = (x0, y0);

            if self.pt1[0] <= x0:
                index = 0 if points[0][0] <= points[1][0] else 1
                vector = (points[index][0], points[index][1]);
            else:
                index = 0 if points[0][0] > points[1][0] else 1
                vector = (points[index][0], points[index][1]);

            a = -angle * math.pi / 180

            self.vertor_pt2 = (int((vector[0] - x0) * math.cos(a) + (vector[1] - y0) *  math.sin(a) + x0), int((vector[1] - y0) * math.cos(a) - (vector[0] - x0) *  math.sin(a) + y0))

        self.b = pt1[1] - self.k * pt1[0]
        self.id = id
        self.rects = []

    def intersect(self, line):
        if self.k == line.k: return False

        x = (self.b - line.b) / (line.k - self.k)
        y = line.k * x + line.b;

        x = int(x)
        y = int(y)

        minX1 = min(self.pt1[0], self.pt2[0])
        maxX1 = max(self.pt1[0], self.pt2[0])
        minY1 = min(self.pt1[1], self.pt2[1])
        maxY1 = max(self.pt1[1], self.pt2[1])

        minX2 = min(line.pt1[0], line.pt2[0])
        maxX2 = max(line.pt1[0], line.pt2[0])
        minY2 = min(line.pt1[1], line.pt2[1])
        maxY2 = max(line.pt1[1], line.pt2[1])

        return x >= minX1 and x <= maxX1 and x >= minX2 and x <= maxX2 and y >= minY1 and y <= maxY1 and y >= minY2 and y <= maxY2

    def intersectRect(self, rect):
        l_top = Line((rect.pt[0], rect.pt[1]), (rect.pt[0] + rect.size[0], rect.pt[1]))
        l_right = Line((rect.pt[0] + rect.size[0], rect.pt[1]), (rect.pt[0] + rect.size[0], rect.pt[1] + rect.size[1]))
        l_bottom = Line((rect.pt[0], rect.pt[1] + rect.size[1]), (rect.pt[0] + rect.size[0], rect.pt[1] + rect.size[1]))
        l_left = Line((rect.pt[0], rect.pt[1]), (rect.pt[0], rect.pt[1] + rect.size[1]))

        if self.intersect(l_top) or self.intersect(l_bottom) or self.intersect(l_left) or self.intersect(l_right):
            return True
        else:
            return (self.pt1[0] >= l_left.pt1[0] and self.pt1[0] <= l_right.pt1[0] and self.pt1[1] >= l_top.pt1[1] and self.pt1[1] <= l_bottom.pt1[1] and
                    self.pt2[0] >= l_left.pt2[0] and self.pt2[0] <= l_right.pt2[0] and self.pt2[1] >= l_top.pt2[1] and self.pt2[1] <= l_bottom.pt2[1]);

    def in_sector(self, points):
        angles = 0
        a_count = 0

        v1 = (self.vertor_pt2[0] - self.vertor_pt1[0], self.vertor_pt2[1] - self.vertor_pt1[1])
        count = 0;
        i = len(points) - 1
        for point in reversed(points):
            count += 1
            if i == 0 or count == 11:
                break

            pt2 = point
            pt1 = points[i - 1]

            v2 = (pt2[0] - pt1[0], pt2[1] - pt1[1])

            length1 = math.sqrt(v1[0] * v1[0] + v1[1] * v1[1])
            length2 = math.sqrt(v2[0] * v2[0] + v2[1] * v2[1])

            if length1 == 0 or length2 == 0:
                continue

            a = (v1[0] * v2[0] + v1[1] * v2[1]) / (length1 * length2)
            if a > 1:
                a = 1
            
            angles += math.acos(a) * 180 / math.pi
            a_count += 1

            i -= 1

        return angles / a_count <= self.sector / 2


class Rect:
    def __init__(self, id, pt, size):
        self.id = id
        self.pt = pt
        self.size = size
        self.disabled = False
        self.flag = False

    def matches(self, rect, offset):
        width_offset = max(self.size[0], rect.size[0]) * offset / 100
        height_offset = max(self.size[1], rect.size[1]) * offset / 100

        match = self.matchPoint(self.pt, rect.pt, width_offset, height_offset)
        if not match: return False

        match = self.matchPoint((self.pt[0] + self.size[0], self.pt[1]), (rect.pt[0] + rect.size[0], rect.pt[1]), width_offset, height_offset)
        if not match: return False

        match = self.matchPoint((self.pt[0] + self.size[0], self.pt[1] + self.size[1]), (rect.pt[0] + rect.size[0], rect.pt[1] + rect.size[1]), width_offset, height_offset)
        if not match: return False

        match = self.matchPoint((self.pt[0], self.pt[1] + self.size[1]), (rect.pt[0], rect.pt[1] + rect.size[1]), width_offset, height_offset)
        if not match: return False

        return True

    def matchPoint(self, pt1, pt2, width_offset, height_offset):
        return pt2[0] >= pt1[0] - width_offset and pt2[0] <= pt1[0] + width_offset and pt2[1] >= pt1[1] - height_offset and pt2[1] <= pt1[1] + height_offset

    def get_center(self):
        return (int(self.pt[0] + self.size[0] / 2), int(self.pt[1] + self.size[1] / 2))
        #return (int(self.pt[0]), int(self.pt[1]))