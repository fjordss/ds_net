import os
# comment out below line to enable tensorflow logging outputs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from absl import app, flags, logging
from dstools import Line, Rect
from object_tracker import load_net, init, iterate
import numpy as np
import cv2
import time
import pathlib

def main(_argv):
    print("test")
    print(pathlib.Path().absolute())

    input()

    lines = [];

    #lines.append(Line((141, 800), (922, 980), (255, 0, 0), '1'))
    #lines.append(Line((1205, 150), (1650, 180), (255, 0, 0), '2'))

    lines.append(Line((664, 605), (1000, 444), -40, 100, (255, 0, 0), '1_1'))
    lines.append(Line((375, 402), (485, 364), -34, 40, (255, 0, 0), '1_2'))
    lines.append(Line((227, 365), (277, 292), 165, 100, (255, 0, 0), '2_1'))
    lines.append(Line((265, 500), (440, 450), 165, 100, (255, 0, 0), '2_2'))
    lines.append(Line((282, 325), (350, 258), -40, 100, (255, 0, 0), '3_1'))
    lines.append(Line((520, 258), (520, 298), 174, 40, (255, 0, 0), '3_2'))
    
    
    
    #try:
    #    vid = cv2.VideoCapture(int('./data/video/test3.mp4'))
    #except:
    #    vid = cv2.VideoCapture('./data/video/test3.mp4')
    
    #while True:
    #    result, frame = vid.read()
    
    #    if not result:
    #        break
   
    #    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #    for line in lines:
    #        cv2.line(frame, line.pt1, line.pt2, line.color, 2)
    #        cv2.line(frame, line.vertor_pt1, line.vertor_pt2, (255, 255, 0), 2)
    #        cv2.putText(frame, str(line.count), (int((line.pt1[0] + line.pt2[0]) / 2), int((line.pt1[1] + line.pt2[1]) / 2)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2);

    #    cv2.imshow("Output Video", cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2BGR))
    #    cv2.waitKey(10000)
    
    #    print("frame");


    vid, model = load_net()

    init(vid)

    while True:
        iter(lines, vid, model)
        i = input()
        if i == 'break':
            break

def iter(lines, vid, model):
    all = []
    pairs = []
    last_points = []
    dict = {}

    frame_num = 0
    while True:
        print("press to continue...")
        #input()

        print('Frame #: ', frame_num)
        frame_num += 1

        result, tracks = iterate(lines, model, vid, frame_num)

        newRects = []
        for track1 in tracks:
            if all.count(track1.id) == 0:
                newRects.append(track1.id)

            if len([i for i in pairs if i[0] == track1.id or i[1] == track1.id]) != 0:
                continue;

            for track2 in tracks:
                if track1.id == track2.id:
                    continue

                if (track1.matches(track2, 25)):
                    pairs.append((track1.id, track2.id))
                    print("new pair added (" + str(track1.id) + ", " + str(track2.id) + ")")

        for newRect in newRects:
            all.append(newRect)

        l_index = 1
        for line in lines:
            print('----------------------');
            print('line ' + str(l_index) + '. (' + str(line.pt1[0]) + ',' + str(line.pt1[1]) + ') - (' + str(line.pt2[0]) + ',' + str(line.pt2[1]) + ')')

            rects = []
            for track in tracks: 
                if line.intersectRect(track):
                    rects.append(track.id)
                    print('track ' + str(track.id) + ' intersected')

            for rect in rects:
                if line.rects.count(rect) == 0:
                    ex_pairs = [i for i in pairs if i[0] == rect or i[1] == rect]
                    if len(ex_pairs) != 0 and (line.rects.count(ex_pairs[0][0]) != 0 or line.rects.count(ex_pairs[0][1]) != 0):
                        index = 1 if ex_pairs[0][0] == rect else 0
                        print('track ' + str(rect) + " intersected line but not added to line because his pair (id: " + str(ex_pairs[0][index]) + ") is already added")
                    else:
                        line.rects.append(rect)
                        print("track " + str(rect) + " added to line " + str(l_index))
                else:
                    print('track ' + str(rect) + ' is already added to line')

            newRects = [];
            for rect in line.rects:
                left_canvas = len([i for i in tracks if i.id == rect]) == 0

                if rects.count(rect) == 0 or left_canvas:
                    if not left_canvas:
                        print("track " + str(rect) + " left line " + str(l_index))
                    else:
                        print("track " + str(rect) + " left canvas");

                    ex_pairs = [i for i in pairs if i[0] == rect or i[1] == rect]
                    if len(ex_pairs) != 0:
                        index = 1 if ex_pairs[0][0] == rect else 0
                        pair = ex_pairs[0][index]

                        ex_tracks = [i for i in tracks if i.id == pair]
                        if len(ex_tracks) != 0 and line.intersectRect(ex_tracks[0]):
                            line.rects.append(ex_tracks[0].id)
                            print('but his pair (id: ' + str(ex_tracks[0].id) + ') is still on line')
                            continue;

                    if left_canvas:
                        continue

                    track = [i for i in tracks if i.id == rect][0]
                    dict[track.id].append(track.get_center())
                    track.flag = True

                    if not line.in_sector(dict[rect]):
                        print('car (id: ' + str(rect) + ') intersected the line, but car is not in sector')
                        continue
                    
                    line.count += 1

                    print('car (id: ' + str(rect) + ') intersected the line, total count = ' + str(line.count))
                else:
                    newRects.append(rect)

            line.rects = newRects

            new_pairs = []
            for pair in pairs:
                if len([i for i in tracks if i.id == pair[0]]) != 0 and len([i for i in tracks if i.id == pair[1]]) != 0:
                    new_pairs.append(pair)

            pairs = new_pairs

            l_index += 1

            print('----------------------');

        for track in tracks:
            if not track.id in dict:
                dict[track.id] = []

            if not track.flag:
                dict[track.id].append(track.get_center())
            else:
                track.flag = False

        if not result:
            break;

if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
