import numpy as np
import cv2
import os
import math
import glob
from copy import deepcopy
import matplotlib.pyplot as plt
import csv

from helpers import line, xy_intersection, check_perpendicular, average_over_nearby_lines, distance_between_lines, select_lines, select_line_pairs
from edge_finder import edge_find, corner_find, cv2HoughLines, process_more_outputs

dir_name = '/home/denise/Documents/images_patternreco/2021-03-19/rotated/contours/'
input_dir = '/home/denise/Documents/images_patternreco/2021-03-19/rotated/'

def PixelCordToMicronCord(p):
    x = -p[0]*1.14547537228
    y = p[1]*1.14547537228
    converted = (x,y)
    return converted

if not os.path.exists(dir_name):
    os.mkdir(dir_name)

full_files = [i.split('/')[-1] for i in glob.glob(input_dir+"*.jpg")]
csvfile = open('measurementA.csv', 'w+')
writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
for filename in full_files:
#for filename in range(0,1):
    #filename = '0p5_lighting_single_sensor.jpg'
    the_file = os.path.join(input_dir, filename)
    name = filename.split('.j')[0]
    print(name)
    global_cord = float(name.split('y')[1])*1000.0
    #global_cord = 0.0
    output_name = dir_name+name
    
    img = cv2.imread(the_file)
    #img = cv2.imread(the_file,0)

    edges, lines_img, threshold, lines, scanned_lines, distances, all_lines_img,selected_lines_img = process_more_outputs(img,1)
    print(distances)
    if distances != 0:
        for p in distances:
            converted = PixelCordToMicronCord(p)
            y = global_cord+converted[0]
            dist = converted[1]
            writer.writerow([y,dist])
    cv2.imwrite(output_name+'_threshold.jpg',threshold)
    cv2.imwrite(output_name+'_edges.jpg',edges)
    cv2.imwrite(output_name+'_all_lines.jpg',all_lines_img)
    cv2.imwrite(output_name+'_selected_lines.jpg',selected_lines_img)
    cv2.imwrite(output_name+'_lines.jpg',lines_img)

## Fin

