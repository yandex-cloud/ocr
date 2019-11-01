#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding=utf8

import sys
import os

import argparse
import Polygon as plg
import numpy as np

def get_intersection(pD,pG):
    pInt = pD & pG
    if len(pInt) == 0:
        return 0
    return pInt.area()

def get_union(pD,pG):
    areaA = pD.area();
    areaB = pG.area();
    return areaA + areaB - get_intersection(pD, pG);

def get_intersection_over_union(pD,pG):
    try:
        return get_intersection(pD, pG) / get_union(pD, pG);
    except:
        return 0

IOU = 0.3
BLANK_IOU = 0.3

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluation script.')
    parser.add_argument('gt', metavar='G', type=str,
                        help='directory with gt')
    parser.add_argument('res', metavar='R', type=str,
                        help='directory with results')
    args = parser.parse_args()
    global_result_blank = 0
    global_gt_blank = 0
    global_true_positive = 0
    global_gt_num = 0
    global_res_num = 0

    name2file = {}

    for file in os.listdir(args.res):
        if file.endswith('.txt') and file.startswith('res_'):
            number = file[8:-4]
            name2file[number] = file

    #for file in sorted(os.listdir(args.res)):
    for k in sorted(name2file.keys()):
        file = name2file[k]
        if file.endswith('.txt') and file.startswith('res_'):
            result_blank = 0
            gt_blank = 0
            true_positive = 0
            gt_num = 0
            res_num = 0

            res_name = os.path.join(args.res, file)
            gt_name = os.path.join(args.gt, 'gt_' + file[4:])
            if not os.path.exists(res_name):
                print("Results file not exist: " + res_name)
                sys.exit(255)
            if not os.path.exists(gt_name):
                print("Gt file not exist: " + gt_name)
                sys.exit(255)
            gt = []
            with open(gt_name, 'r') as gt_file:
                for line in gt_file:
                    points = map(int, line.split(',')[:8])
                    word = ','.join(line.split(',')[8:])
                    resBoxes=np.zeros([8],dtype='int32')
                    resBoxes[0]=int(points[0])
                    resBoxes[4]=int(points[1])
                    resBoxes[1]=int(points[2])
                    resBoxes[5]=int(points[3])
                    resBoxes[2]=int(points[4])
                    resBoxes[6]=int(points[5])
                    resBoxes[3]=int(points[6])
                    resBoxes[7]=int(points[7])
                    pointMat = resBoxes.reshape([2,4]).T
                    polygon = plg.Polygon(pointMat)
                    gt.append((word.decode('utf-8').lower().strip(), polygon))
                    if gt[-1][0] == u'###':
                        gt_blank += 1
            results = []
            with open(res_name, 'r') as res_file:
                for line in res_file:
                    points = map(int, line.split(',')[:8])
                    word = ','.join(line.split(',')[8:])
                    resBoxes=np.zeros([8],dtype='int32')
                    resBoxes[0]=int(points[0])
                    resBoxes[4]=int(points[1])
                    resBoxes[1]=int(points[2])
                    resBoxes[5]=int(points[3])
                    resBoxes[2]=int(points[4])
                    resBoxes[6]=int(points[5])
                    resBoxes[3]=int(points[6])
                    resBoxes[7]=int(points[7])
                    pointMat = resBoxes.reshape([2,4]).T
                    polygon = plg.Polygon(pointMat)
                    results.append((word.decode('utf-8').lower().strip(), polygon))

            iou_mat = np.empty([len(gt),len(results)],dtype='float32')

            for i in xrange(len(gt)):
                for j in xrange(len(results)):
                    iou_mat[i, j] = get_intersection_over_union(gt[i][1], results[j][1])

            if len(results) > 0:
                for i in xrange(len(gt)):
                    for j in xrange(len(results)):
                        if gt[i][0] == u'###' and get_intersection(gt[i][1], results[j][1]) / results[j][1].area() > BLANK_IOU:
                            result_blank += 1

                    j = np.argmax(iou_mat[i])
                    if iou_mat[i, j] >= IOU:
                        if gt[i][0] == results[j][0]:
                            true_positive += 1
            gt_num += len(gt)
            res_num += len(results)
            global_gt_num += gt_num
            global_res_num += res_num
            global_gt_blank += gt_blank
            global_result_blank += result_blank
            global_true_positive += true_positive

            gt_num -= gt_blank
            res_num -= result_blank
    recall = 1.0 * global_true_positive / (global_gt_num - global_gt_blank) * 100
    precison = 1.0 * global_true_positive / (global_res_num - global_result_blank) * 100
    print ("Total number of images: ", len(name2file.keys()))
    print("Recall: ", recall)
    print("Precision: ", precison)
    print ("F-measure: ", 2 * recall * precison / (recall + precison))

