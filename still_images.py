import numpy as np
import cv2
import os
import math

import matplotlib.pyplot as plt
from edge_finder import edge_find, corner_find, line, xy_intersection, check_perpendicular, cv2HoughLines

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

        ###############################	
	### Edge, contour and Hough Line detection
        ###############################

        img = cv2.imread(the_file,0)
        edges, cnts, lines = edge_find(img)
        cv2.imwrite(output_name+'_edges.jpg',edges) 
        contour_img = img.copy()
        cv2.drawContours(contour_img, [cnts[0]], 0, (255,255,255), 3)
        cv2.imwrite(output_name+'_edges_extract.jpg',contour_img)
        if lines is not None:
            for l in lines:
                cv2.line(img,(l.x1,l.y1),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
        cv2.imwrite(output_name+'_hough.jpg',img)

        ###############################
        ### ADM corner detection WIP
        ###############################

        # Create a multi plot to display intermediate stage images
        fig, plot = plt.subplots(3,3, sharex=True)

	debug = True

	input_img = cv2.imread(the_file,1)
	xy, lines, debugPics = corner_find(input_img, debug)

        org_img_lines = input_img.copy()
        org_img_circles = input_img.copy()

        if lines is not None:
            for l in lines:
                cv2.line(org_img_lines,(l.x1,l.y1),(l.x2,l.y2),(123,234,123),2, cv2.LINE_AA)

	if xy is not None:
		for corner in xy:
			org_img_circles = cv2.circle(org_img_circles, tuple(corner), 25, (0,0,255), 5)
			
        cv2.imwrite(output_name+'_houghLines.jpg',org_img_lines)
        cv2.imwrite(output_name+'_corners.jpg',org_img_circles)


	## Debug Plots
	if debug is True :
		#Fill plots
		if debugPics is not None:
			plot[0,0].imshow(debugPics[0])
			plot[0,1].imshow(debugPics[1])
			plot[0,2].imshow(debugPics[2])
			plot[1,0].imshow(debugPics[3])
			plot[1,1].imshow(debugPics[4])
			plot[1,2].imshow(debugPics[5])
			plot[2,0].imshow(debugPics[6])
			plot[2,1].imshow(debugPics[7])
			plot[2,2].imshow(debugPics[8])
        	# Add titles
	        fig.canvas.set_window_title(output_name)
        	fig.suptitle(output_name)
	        plot[0,0].set_title('Source Image')
        	plot[0,1].set_title('Source Greyscale')
	        plot[0,2].set_title('Blur')
	        plot[1,0].set_title('Canny')
	        plot[1,1].set_title('Floodfill')
	        plot[1,2].set_title('Masking')
	        plot[2,0].set_title('Edges after masking')
	        plot[2,1].set_title('Hough Lines')
	        plot[2,2].set_title('Corners Found')
	        # Edit axes
        	plot[0,0].axis('off')
	        plot[0,1].axis('off')
        	plot[0,2].axis('off')
	        plot[1,0].axis('off')
        	plot[1,1].axis('off')
	        plot[1,2].axis('off')
        	plot[2,0].axis('off')
	        plot[2,1].axis('off')
        	plot[2,2].axis('off')
	        ## Show/Save plot with debug-pictures
		# plt.savefig(output_name+"_fig.png", format="png")
		plt.show()

## Fin

