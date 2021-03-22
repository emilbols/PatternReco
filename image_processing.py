import numpy as np
import cv2
from copy import deepcopy


def process_image(color_image, do_threshold=True):
        #threshold needed for edges measurement, grayscale image sufficient for corner measurement
        if do_threshold:
                image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
                cutoff, thres_image = cv2.threshold(image, 90, 255, cv2.THRESH_BINARY)
                thres_image = cv2.GaussianBlur(thres_image,(9,9),0)
                kernel = np.ones((5, 5), np.uint8)
                thres_image = cv2.dilate(thres_image, kernel, 1000)
        else:
                thres_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

        return thres_image


def canny_image( input, cannyThreshold1 = 50, cannyThreshold2 = 150, cannyAperture = 3, dilateIt = 2, erodeIt = 2, filterKernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) ) :
        ## Apply canny edge detection algo to input blurred image

        filtered = cv2.bilateralFilter(input, 5, 200, 200)
        filtered = cv2.GaussianBlur(filtered, (3, 3), 0)
        #filtered = input
        v = np.median(filtered)
        sigma = 0.05
        #---- apply optimal Canny edge detection using the computed median----
        #lower_thresh = int(max(0, (1.0 - sigma) * v))
        #upper_thresh = int(min(255, (1.0 + sigma) * v))
        #lower_thresh = 10
        #upper_thresh = 80
        lower_thresh = cannyThreshold1
        upper_thresh = cannyThreshold2
        
        edges = cv2.Canny(filtered, lower_thresh, upper_thresh, 3)
        ## Smooth edges so that we can find/draw the lines/contours/intersection better
        edges = cv2.dilate(edges, filterKernel, dilateIt)
        #edges = cv2.erode(edges, None, erodeIt)
        edges = cv2.filter2D(edges, -1, filterKernel)
        return edges


def floodfill_mask_image(edges, debugPics, postMaskCannyThreshold1 = 15, postMaskCannyThreshold2 = 50, postMaskCannyAperture = 3) :

        ## Now edges have been found, floodfill the image to segment the object from the background
        h, w = edges.shape[:2]
        mask = np.zeros((h+2, w+2), np.uint8)
        cv2.floodFill(edges, mask, (0,0), 123);
        floodfill = edges.copy()
        if debugPics is not None : debugPics.append(floodfill)

        ## Apply masking and show masked image
        bg = np.zeros_like(floodfill)
        bg[floodfill == 123] = 255
        if debugPics is not None : debugPics.append(bg)

        ## Now find the edges after masking using Canny and print them to plot
        bg = cv2.blur(bg, (1,1))
        masked_edges = cv2.Canny(bg, postMaskCannyThreshold1, postMaskCannyThreshold2, postMaskCannyAperture)
        if debugPics is not None : debugPics.append(masked_edges)
        return masked_edges

