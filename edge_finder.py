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

def rho_theta_to_xy(rho,theta):
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
        return x1,y1,x2,y2

def get_direction(line,unit=True):
        length = np.sqrt((line[2]-line[0])**2 + (line[3]-line[1])**2 )
        if unit:
                dirx = (line[2]-line[0]) / length 
                diry = (line[3]-line[1]) / length
        else:
                dirx = (line[2]-line[0]) 
                diry = (line[3]-line[1])
        return dirx,diry


def select_lines(xy_lines):
        selected_lines = []
        for line in xy_lines:
                dirx,diry = get_direction(line)
                dot = dirx * 1.0 + diry * 0.0
                if(dot < 0.5):
                        selected_lines.append(line)
        return selected_lines

def is_point_on_line(line_1, line_2,threshold=20.0):
        point_on_line = False
        steps = 100
        dirx_1,diry_1 = get_direction(line_1,unit=False)
        dirx_2,diry_2 = get_direction(line_2,unit=True)
        step_length = np.sqrt((line_2[2]-line_2[0])**2 + (line_2[3]-line_2[1])**2 )/float(steps)
        scan_x = line_2[0]
        scan_y = line_2[1]
        for n in range(steps):
                scan_x = scan_x-dirx_2*step_length
                scan_y = scan_y-diry_2*step_length         
                dpx = scan_x-line_1[0]
                dpy = scan_y-line_1[1]
                cross = dpx * diry_1 - dpy * dirx_1;
                if (abs(cross) < threshold):
                        point_on_line = True
                        return point_on_line
        return point_on_line

def is_line_close(line_1, line_2,threshold=200.0):
        close_line = False
        steps = 100
        dirx_1,diry_1 = get_direction(line_1,unit=False)
        dirx_2,diry_2 = get_direction(line_2,unit=True)
        step_length = np.sqrt((line_2[2]-line_2[0])**2 + (line_2[3]-line_2[1])**2 )/float(steps)
        scan_x = line_2[0]
        scan_y = line_2[1]
        for n in range(steps):
                scan_x = scan_x-dirx_2*step_length
                scan_y = scan_y-diry_2*step_length         
                dpx1 = scan_x-line_1[0]
                dpy1 = scan_y-line_1[1]

                dpx2 = scan_x-line_1[2]
                dpy2 = scan_y-line_1[3]

                dpx3 = scan_x - ( (line_1[2]+line_1[0])/2.0 )
                dpy3 = scan_y - ( (line_1[3]+line_1[1])/2.0 )
            
                dist1 = np.sqrt(dpx1 * dpx1 + dpy1 * dpy1);
                dist2 = np.sqrt(dpx2 * dpx2 + dpy2 * dpy2);
                dist3 = np.sqrt(dpx3 * dpx3 + dpy3 * dpy3);
             
                if (dist1 < threshold):
                        close_line = True
                        return close_line
                if (dist2 < threshold):
                        close_line = True
                        return close_line
                if (dist3 < threshold):
                        close_line = True
                        return close_line
        return close_line

        
def check_parralel(line_1, line_2,threshold = 0.5):

        parralel = False
        dirx_1,diry_1 = get_direction(line_1)
        dirx_2,diry_2 = get_direction(line_2)        
        dot = dirx_1*dirx_2 + diry_1*diry_2
        if dot > threshold:
                parralel = True
        return parralel
                
def average_over_nearby_lines(xy_lines):
        averaged_lines = []
        already_averaged = []
        n_lines = len(xy_lines)
        for i in range(n_lines):
                already_averaged.append(False)
        for i in range(n_lines):
                if already_averaged[i]:
                        continue
                line_1 = xy_lines[i]
                line_averaged = [i]
                sum_x1 = line_1[0]
                sum_y1 = line_1[1]
                sum_x2 = line_1[2]
                sum_y2 = line_1[3]
                count = 1.0
                for j in range(i+1,n_lines):
                        line_2 = xy_lines[j]
                        mostly_parralel = check_parralel(line_1,line_2)
                        if mostly_parralel:
                                point_on_line = is_line_close(line_1, line_2)
                                if point_on_line:
                                        sum_x1 = sum_x1+line_2[0]
                                        sum_y1 = sum_y1+line_2[1]
                                        sum_x2 = sum_x2+line_2[2]
                                        sum_y2 = sum_y2+line_2[3]
                                        count = count+1
                                        line_averaged.append(j)
                                        already_averaged[j] = True
                averaged_lines.append((int(sum_x1/count),int(sum_y1/count),int(sum_x2/count),int(sum_y2/count)))
        return averaged_lines


def edge_find(img):

        #runs the edge finding algorithm. The min and max value of Canny are very important to tune!
        edges = cv2.Canny(img,30,100)
        #we have to find good values for iterations for these two functions. They smooth the edges found so we can draw contours better.
        edges = cv2.dilate(edges, None, iterations=1)
        edges = cv2.erode(edges, None, iterations=1)
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        edges = cv2.filter2D(edges, -1, kernel)

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

        # another method, hough lines, might be better
        lines = cv2.HoughLines(edges,1,np.pi/180,200)

        return edges, cnts, lines
