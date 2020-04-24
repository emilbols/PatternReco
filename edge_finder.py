import math
import numpy as np
import argparse
import cv2
import os

class point:
        x = 0
        y = 0
        # Points for Left Right Top and Bottom
corner = point()

def midpoint(ptA, ptB):
        return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

dir_name = 'images/dummy_sensor_2_contours/'
input_dir = 'images/dummy_sensor_2/'
if not os.path.exists(dir_name):
                os.mkdir(dir_name)

def edge_find(img,output_name):

        #runs the edge finding algorithm. The min and max value of Canny are very important to tune!
        edges = cv2.Canny(img,30,100)
        #we have to find good values for iterations for these two functions. They smooth the edges found so we can draw contours better.
        edges = cv2.dilate(edges, None, iterations=1)
        edges = cv2.erode(edges, None, iterations=1)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        edges = cv2.filter2D(edges, -1, kernel)
        
        cv2.imwrite(dir_name+output_name+'_edges.jpg',edges) 
        contour_img = img.copy()
        # finds contours you can from the edge image. Right now it is not working great. You can get the coordinates of these contours here.
        cnts = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL,
	                        cv2.CHAIN_APPROX_SIMPLE)
        #
        cnts = cnts[0]
        chosen_cnts = []
        best_contour = 0
        contour_size = 0
        for c in cnts:
                if c.shape[0] > contour_size:
                        best_contour = c
                        contour_size = c.shape[0]
                        
        cnts = [best_contour]
        colors = ((0, 0, 255), (240, 0, 159), (0, 165, 255), (255, 255, 0),
	          (255, 0, 255))
        refObj = None
        pixelsPerMetric = None
        
        def distance_vector(x):
                dist = np.array([])
                for z in range(x.shape[0]-1):
                        diff_x = x[z+1,0]-x[z,0]
                        diff_y = x[z+1,1]-x[z,1]
                        dist = np.append(dist,np.sqrt(diff_x*diff_x+diff_y*diff_y))
                return dist

        #hull = cv2.convexHull(cnts[0])
        cv2.drawContours(contour_img, [cnts[0]], 0, (255,255,255), 3)
        #cv2.circle(img, ( x[a[-1]],y[a[-1]] ), 10, (0, 0, 255), -1)
        cv2.imwrite(dir_name+output_name+'_edges_extract.jpg',contour_img) 

        # another method, hough lines, might be better
        lines = cv2.HoughLines(edges,1,np.pi/180,200)
        if lines is not None:
                for rho,theta in lines[0]:
                        a = np.cos(theta)
                        b = np.sin(theta)
                        x0 = a*rho
                        y0 = b*rho
                        x1 = int(x0 + 1000*(-b))
                        y1 = int(y0 + 1000*(a))
                        x2 = int(x0 - 1000*(-b))
                        y2 = int(y0 - 1000*(a))
                
                        cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)
        cv2.imwrite(dir_name+output_name+'_hough.jpg',img)
        
        

for filename in os.listdir(input_dir):
        if filename.endswith(".jpg"):
                print filename
                the_file = os.path.join(input_dir, filename)
                name = filename.split('.j')[0]
                img = cv2.imread(the_file,0)
                edge_find(img,name)
