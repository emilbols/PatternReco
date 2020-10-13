import numpy as np
import cv2
import os
import math
import glob
from copy import deepcopy
import matplotlib.pyplot as plt
import csv
from edge_finder import edge_find, corner_find, line, xy_intersection, check_perpendicular, cv2HoughLines, average_over_nearby_lines, process_image, process_image_more_outputs, distance_between_lines, select_lines, select_line_pairs

dir_name = 'images/measurement_correctSideSensorB/contours/'
input_dir = 'images/measurement_correctSideSensorB/'

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
    #filename = 'side1x0.95y80.0.jpg'
    the_file = os.path.join(input_dir, filename)
    name = filename.split('.j')[0]
    print(name)
    global_cord = float(name.split('y')[1])*1000.0
    output_name = dir_name+name
    
    img = cv2.imread(the_file)
    #img = cv2.imread(the_file,0)
    edges, lines_img, threshold, lines, scanned_lines, distances, all_lines_img,selected_lines_img = process_image_more_outputs(img)
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

