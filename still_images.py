import numpy as np
import cv2
import os
import math

import matplotlib.pyplot as plt
from edge_finder import edge_find, corner_find, line, xy_intersection, check_perpendicular, cv2HoughLines

dir_name = 'photos/contours/'
input_dir = 'photos/'

if not os.path.exists(dir_name):
    os.mkdir(dir_name)

vertical = True
threshold_scan = [160]
for upper_value in threshold_scan:
    if True:
        #if filename.endswith("dummy_sensor_edge_second.jpg"):
       
        filename = 'dummy_sensor_edge_orthogonal.jpg'
        #print filename
        the_file = os.path.join(input_dir, filename)
        name = filename.split('.j')[0]
        output_name = dir_name+name

        ###############################	
	### Edge, contour and Hough Line detection
        ###############################

        img = cv2.imread(the_file,0)
        cutoff_val = int( (np.median(img)-np.min(img))/2.5 + np.min(img) )
        print cutoff_val
        cutoff, thres_image = cv2.threshold(img, cutoff_val, 255, cv2.THRESH_BINARY)
                
        #thres_image = cv2.GaussianBlur(thres_image,(9,9),0)
        cv2.imwrite(output_name+'_threshold.jpg',thres_image)       
        thres_edges, thres_cnts, thres_lines = edge_find(thres_image,220,250,250)
        kernel = np.ones((5, 5), np.uint8) 
        #thres_edges = cv2.erode(thres_edges, kernel, 1000)
        
        cv2.imwrite(output_name+'_threshold_edge.jpg',thres_edges)

        v = np.median(img)
        sigma = 0.33
        # apply automatic Canny edge detection using the computed median
        #lower = int(max(0, (1.0 - sigma) * v))
        #upper = int(min(255, (1.0 + sigma) * v))
        #lower = 64
        lower = 70
        upper = 129
        #upper = 150
        edges, cnts, lines = edge_find(img,lower,upper,300,dilate=1)
        cv2.imwrite(output_name+'_edges_'+str(lower)+'_'+str(upper)+'.jpg',edges) 
        #contour_img = img.copy()
        #if not isinstance(cnts[0], int):
        #    cv2.drawContours(contour_img, [cnts[0]], 0, (255,255,255), 3)
        #cv2.imwrite(output_name+'_edges_extract_10_'+str(upper_value)+'.jpg',contour_img)
        edge_l = 0
        edge_l_y = 9999
        max_l_x = 0
        if lines:
            for l in lines:
                if vertical:
                    if (l.x1 > max_l_x):
                        max_l_x = l.x1
                        edge_l = l
                else:
                    if (l.y1 < edge_l_y):
                        edge_l_y = l.y1
                        edge_l = l
            cv2.line(img,(edge_l.x1,edge_l.y1),(edge_l.x2,edge_l.y2),(0,0,255),2,cv2.LINE_AA)
        cv2.imwrite(output_name+'_hough_'+str(lower)+'_'+str(upper)+'.jpg',img)
        print(edge_l.x1)
        print(edge_l.y1)
        min_l = 0
        min_l_y = 9999
        min_l = 0
        max_l_x = 0
      
        if thres_lines:
            for l in thres_lines:
                if vertical:
                    if (np.abs(edge_l.x1-l.x1) > 500) and (np.abs(edge_l.x1-l.x1) < 1200):
                        if (l.x1 > max_l_x):
                            max_l_x = l.x1
                            min_l = l
                else:
                    if np.abs(edge_l.y1-l.y1) > 500 and np.abs(edge_l.y1-l.y1) < 1200:
                        if (l.y1 < min_l_y):
                            min_l_y = l.y1
                            min_l = l
            cv2.line(img,(min_l.x1,min_l.y1),(min_l.x2,min_l.y2),(0,0,255),2,cv2.LINE_AA)
        cv2.imwrite(output_name+'_threshold_lines.jpg',img)
      
        
        ###############################
        ### ADM corner detection WIP
        ###############################

        # Create a multi plot to display intermediate stage images
        """
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
	if debug is True and debugPics is not None :
		#Fill plots
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
		plt.savefig(output_name+"_fig.png", format="png")
		#plt.show()
        """

## Fin

