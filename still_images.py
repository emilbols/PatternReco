import numpy as np
import cv2
import os
from edge_finder import edge_find

dir_name = 'images/dummy_sensor_2_contours/'
input_dir = 'images/dummy_sensor_2/'
if not os.path.exists(dir_name):
    os.mkdir(dir_name)

for filename in os.listdir(input_dir):
    if filename.endswith(".jpg"):
        print filename
        the_file = os.path.join(input_dir, filename)
        name = filename.split('.j')[0]
        output_name = dir_name+name
        img = cv2.imread(the_file,0)
        edges, cnts, lines = edge_find(img)
        cv2.imwrite(output_name+'_edges.jpg',edges) 
        contour_img = img.copy()
        cv2.drawContours(contour_img, [cnts[0]], 0, (255,255,255), 3)
        cv2.imwrite(output_name+'_edges_extract.jpg',contour_img)
        if lines is not None:
            for l in lines:
                cv2.line(img,(l.x1,l.y1),(l.x2,l.y2),(0,0,255),2)
        cv2.imwrite(output_name+'_hough.jpg',img)
