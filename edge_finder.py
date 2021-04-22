import math
import numpy as np
import argparse
import cv2
import os
from copy import deepcopy

from image_processing import canny_image, process_image, floodfill_mask_image
from helpers import distance_between_lines, average_over_nearby_lines, select_lines, select_corner_lines, find_intersections, line,select_inner_lines,select_outer_lines



# for edges measurement
def process_edges(color_image,n_edge):
        thres_image = process_image(color_image,do_threshold=True,thres_val=90)
        #thres_edges, thres_cnts, thres_lines = edge_find(thres_image,0,150,250,dilate=1)
        thres_edges, thres_cnts, thres_lines = edge_find(thres_image,10,30,250,dilate=1)
        scanned_lines = 0
        distances = 0
        #thres_edges = cv2.erode(thres_edges,kernel,1)
        #averaged_thres_lines = average_over_nearby_lines(thres_lines)
        averaged_thres_lines = average_over_nearby_lines(select_lines(thres_lines,n_edge))
        lines_img = deepcopy(color_image)
        if averaged_thres_lines:
           for l in averaged_thres_lines:
                   cv2.line(lines_img,(l.x1,l.y1),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
        if(len(averaged_thres_lines) > 1):
                scanned_lines,distances = distance_between_lines(averaged_thres_lines[0],averaged_thres_lines[1],vertical=True)
                if scanned_lines:
                        for l in scanned_lines:
                                cv2.line(lines_img,(l.x1,l.y1),(l.x2,l.y2),(255,0,0),2,cv2.LINE_AA)
        return thres_edges, lines_img, thres_image, averaged_thres_lines, scanned_lines, distances


# for corner-to-corner measurement
def process_corner(color_image,n_edge):
        thres_image = process_image(color_image,do_threshold=False)
        thres_edges, thres_cnts, thres_lines = edge_find(thres_image,130,200,250,dilate=1)
        scanned_lines = 0
        distances = 0
        #thres_edges = cv2.erode(thres_edges,kernel,1)
        #averaged_thres_lines = average_over_nearby_lines(thres_lines)
        selected_lines = select_corner_lines(thres_lines)
        averaged_thres_lines = average_over_nearby_lines(selected_lines)
        selected_lines_img = deepcopy(color_image)
        all_lines_img = deepcopy(color_image)
        lines_img = deepcopy(color_image)
        if thres_lines:
           for l in thres_lines:
                   cv2.line(all_lines_img,(l.x1,l.y1),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
        if selected_lines:
                for l in selected_lines:
                        cv2.line(selected_lines_img,(l.x1,l.y1),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
        if averaged_thres_lines:
           for l in averaged_thres_lines:
                   cv2.line(lines_img,(l.x1,l.y1),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
        if(len(averaged_thres_lines) > 0):
                scanned_lines = averaged_thres_lines
                distances = []
                for l in averaged_thres_lines:
                         distances.append( ( (l.x1+l.x2)/2, (l.y1+l.y2)/2 ) )
                if scanned_lines:
                        for l in scanned_lines:
                                cv2.line(lines_img,(l.x1,l.y1),(l.x2,l.y2),(255,0,0),2,cv2.LINE_AA)
        return thres_edges, lines_img, all_lines_img, averaged_thres_lines, scanned_lines, distances


#return thres_edges, lines_img, averaged_thres_lines, scanned_lines, distances, all_lines_img, selected_lines_img
def process_more_outputs(color_image,n_edge):
        thres_image = process_image(color_image,do_threshold=True,thres_val=90)
        med_val=np.median(thres_image)
        lower=int(max(0 ,0.7*med_val))
        upper=int(min(255,1.3*med_val))
        #lower = 50
        #upper = 100
        thres_edges, thres_cnts, thres_lines = edge_find(thres_image,lower,upper,250,dilate=1)
        scanned_lines = 0
        distances = 0
        #thres_edges = cv2.erode(thres_edges,kernel,1)
        #averaged_thres_lines = average_over_nearby_lines(thres_lines)
        selected_outer_lines = select_outer_lines(thres_lines,n_edge)
        

        inner_thres_image = process_image(color_image,do_threshold=True,thres_val=130)
        med_val=np.median(inner_thres_image)
        lower=int(max(0 ,0.7*med_val))
        upper=int(min(255,1.3*med_val))
        #lower = 50
        #upper = 100
        inner_thres_edges, inner_thres_cnts, inner_thres_lines = edge_find(inner_thres_image,lower,upper,250,dilate=1)

        selected_inner_lines = select_inner_lines(inner_thres_lines,thres_lines,n_edge)
        
        selected_lines = selected_inner_lines+selected_outer_lines
        averaged_thres_lines = average_over_nearby_lines(selected_lines)
        selected_lines_img = deepcopy(color_image)
        all_lines_img = deepcopy(color_image)
        lines_img = deepcopy(color_image)

        if thres_lines:
           for l in thres_lines:
                   cv2.line(all_lines_img,(l.x1,l.y1),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
        if selected_lines:
                for l in selected_lines:
                        cv2.line(selected_lines_img,(l.x1,l.y1),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
        if averaged_thres_lines:
           for l in averaged_thres_lines:
                   cv2.line(lines_img,(l.x1,l.y1),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
        if(len(averaged_thres_lines) > 1):
                scanned_lines,distances = distance_between_lines(averaged_thres_lines[0],averaged_thres_lines[1],vertical=True)
                if scanned_lines:
                        for l in scanned_lines:
                                cv2.line(lines_img,(l.x1,l.y1),(l.x2,l.y2),(255,0,0),2,cv2.LINE_AA)
        return thres_edges, lines_img, thres_image, averaged_thres_lines, scanned_lines, distances,all_lines_img,selected_lines_img


def edge_find(img,cannyThreshold1 = 10, cannyThreshold2 = 20,hough_lenght=300,dilate=1):

        #runs the edge finding algorithm. The min and max value of Canny are very important to tune!


        # preprocessing parameters
        #cannyThreshold1 = 10
        #cannyThreshold2 = 120
        cannyAperture = 5
        dilateIt = dilate
        erodeIt = 1
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])

        # preprocess image with canny edge detection and edge smoothing
        edges = canny_image(img, cannyThreshold1, cannyThreshold2, cannyAperture, dilateIt, erodeIt, kernel)

        contour_img = img.copy()
        # finds contours you can from the edge image. Right now it is not working great. You can get the coordinates of these contours here.
        cnts = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        
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
        min_line_length = 100
        max_line_gap = 5
        probabilisticHT = True
        lines = cv2HoughLines(edges, hough_lenght,min_line_length, max_line_gap, probabilisticHT)
        return edges, cnts, lines


def corner_find (img, debug = False):
        debugPics = []
        if debug is True : debugPics.append(img)
        ## Ensure input image is greyscale
        grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if debug is True : debugPics.append(grey_img)
        ## Blur the greyscale image
        blur_greyscale = cv2.GaussianBlur(grey_img, (5,5), 0)
        if debug is True : debugPics.append(blur_greyscale)
        # preprocessing parameters
        cannyThreshold1 = 50
        cannyThreshold2 = 150
        cannyAperture = 3
        dilateIt = 1
        erodeIt = 1
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])

        ## Apply canny edge detection algo to input blurred image and smooth edges
        edges = canny_image(blur_greyscale, cannyThreshold1, cannyThreshold2, cannyAperture, dilateIt, erodeIt, kernel)
        if debug is True : debugPics.append(edges)
        ## post-flooodfill and masking canny parameters
        postMaskCannyThreshold1 = 15
        postMaskCannyThreshold2 = 50
        postMaskCannyAperture = 3
        ## floodfill and mask preprocessed image and edge detector said image
        masked_edges = floodfill_mask_image(edges, debugPics, postMaskCannyThreshold1, postMaskCannyThreshold2, postMaskCannyAperture)
        ## Find Hough Lines on the edges after masking
        min_line_length = 0  # Original test value of 50
        max_line_gap = 0     # Original value of 20
        threshold = 100      # Original value of 100
        probabilisticHT = False
        lines = cv2HoughLines(masked_edges, threshold, min_line_length, max_line_gap, probabilisticHT)

        ## Draw lines on original image for debug plot
        if debug is True:
                org_img_lines = img.copy()
                if lines is not None and debug:
                        for i in range(0, len(lines)):
                                rho = lines[i].rho
                                theta = lines[i].theta
                                a = math.cos(theta)
                                b = math.sin(theta)
                                x0 = a * rho
                                y0 = b * rho
                                pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
                                pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
                                cv2.line(org_img_lines, pt1, pt2, (123,234,123), 2, cv2.LINE_AA)
                debugPics.append(org_img_lines)
        ## Find intersection of every line found and if debug over original image
        ## loop over all line pairs to consider if they intersect (if they are not parallel)
        org_img_circles = None
        if debug is True : org_img_circles = img.copy() #copy of input image for debug
        threshold = 0.1
        xy = find_intersections(lines, threshold)
        if debug is True and xy is not None:
                for i in range (0, len(xy)) :
                        xyTuple = tuple(xy[i])
                        org_img_circles = cv2.circle(org_img_circles, xyTuple, 25, 255, 5)
                debugPics.append(org_img_circles)
        return xy, lines, debugPics


def cv2HoughLines (edges, threshold, min_line_length = 0, max_line_gap = 5, Probabilistic = False, rho = 1, angle = np.pi/180) :
        lines = []
        if Probabilistic is False :
                houghLines = cv2.HoughLines(edges,rho,angle, threshold, None, 0, 0) ### default hough lines
                if houghLines is not None:
                        for i in range(0, len(houghLines)) :
                                tempLine = line(houghLines[i][0][0], houghLines[i][0][1])
                                lines.append(tempLine)
        else :
                houghLinesP = cv2.HoughLinesP(edges,rho,angle, threshold, None, min_line_length, max_line_gap)
                if houghLinesP is not None:
                        for i in range(0, len(houghLinesP)):
                                tempLine = line(houghLinesP[i][0][0], houghLinesP[i][0][1], houghLinesP[i][0][2],houghLinesP[i][0][3])
                                lines.append(tempLine)
        return lines
