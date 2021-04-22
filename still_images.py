import numpy as np
import cv2
import os
import math
import glob
from copy import deepcopy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv

from helpers import line, xy_intersection, check_perpendicular, average_over_nearby_lines, distance_between_lines, select_lines, select_line_pairs
from edge_finder import edge_find, corner_find, cv2HoughLines, process_more_outputs

dir_name = 'images/sensor002/contours/'
input_dir = 'images/sensor002/'

def PixelCordToMicronCord(p):
    x = -p[0]*1.14547537228
    y = p[1]*1.14547537228
    converted = (x,y)
    return converted

if not os.path.exists(dir_name):
    os.mkdir(dir_name)

full_files = [i.split('/')[-1] for i in glob.glob(input_dir+"*.jpg")]
csvfile = open('measurement_sensor_SAFETY.csv', 'w+')
writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
for filename in full_files:
#for filename in range(0,1):
    #filename = '0p5_lighting_single_sensor.jpg'
    the_file = os.path.join(input_dir, filename)
    name = filename.split('.j')[0]
    n_edge = int(filename.split('edge')[-1].split('_')[0])
    global_cord = 0.0
    
    #global_cord = 0.0
    output_name = dir_name+name
    
    img = cv2.imread(the_file)
    if (n_edge == 0):
        global_cord = float(name.split('x_')[1].split('_y')[0])*1000.0
        img = cv2.rotate(img,cv2.ROTATE_90_COUNTERCLOCKWISE)
    if (n_edge == 1):
        global_cord = float(name.split('y_')[1].split('_z')[0])*1000.0
        img = cv2.rotate(img,cv2.ROTATE_180)
    if (n_edge == 2):
        global_cord = float(name.split('x_')[1].split('_y')[0])*1000.0
        img = cv2.rotate(img,cv2.ROTATE_90_CLOCKWISE)
    if (n_edge == 3):
        global_cord = float(name.split('y_')[1].split('_z')[0])*1000.0

    #img = cv2.imread(the_file,0)

    edges, lines_img, threshold, lines, scanned_lines, distances, all_lines_img,selected_lines_img = process_more_outputs(img,n_edge)

    if distances != 0:
        for p in distances:
            converted = PixelCordToMicronCord(p)
            y = global_cord+converted[0]
            dist = converted[1]
            writer.writerow([n_edge,y,dist])
    cv2.imwrite(output_name+'_threshold.jpg',threshold)
    cv2.imwrite(output_name+'_edges.jpg',edges)
    cv2.imwrite(output_name+'_all_lines.jpg',all_lines_img)
    cv2.imwrite(output_name+'_selected_lines.jpg',selected_lines_img)
    cv2.imwrite(output_name+'_lines.jpg',lines_img)

## Fin

