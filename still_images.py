import numpy as np
import cv2
import os
import math
import glob
from copy import deepcopy
import matplotlib.pyplot as plt
from edge_finder import edge_find, corner_find, line, xy_intersection, check_perpendicular, cv2HoughLines, average_over_nearby_lines, process_image, distance_between_lines, select_lines, select_line_pairs

dir_name = 'images/measurement_sensorA/contours/'
input_dir = 'images/measurement_sensorA/'

if not os.path.exists(dir_name):
    os.mkdir(dir_name)

full_files = [i.split('/')[-1] for i in glob.glob(input_dir+"*.jpg")]
for filename in full_files:
    #filename = 'side1x0.95y80.0.jpg'
    the_file = os.path.join(input_dir, filename)
    name = filename.split('.j')[0]
    output_name = dir_name+name
    
    img = cv2.imread(the_file)
    #img = cv2.imread(the_file,0)
    edges, lines_img, threshold, lines, scanned_lines, distances = process_image(img)
    cv2.imwrite(output_name+'_threshold.jpg',threshold)
    cv2.imwrite(output_name+'_edges.jpg',edges)
    cv2.imwrite(output_name+'_lines.jpg',lines_img)

## Fin

