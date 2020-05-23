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

class line:
	def __init__ (self, *args):
		if len(args) == 2 :
			self.rho = args[0]
			self.theta = args[1]

			__x1,__y1,__x2,__y2 = rho_theta_to_xy(self.rho, self.theta)
			self.x1 = __x1
			self.y1 = __y1
			self.x2 = __x2
			self.y2 = __y2

		elif len(args) == 4 :
			self.x1 = args[0]
                        self.y1 = args[1]
                        self.x2 = args[2]
                        self.y2 = args[3]

			__rho, __theta = xy_to_rho_theta(self.x1, self.y1, self.x2, self.x2)
			self.rho = __rho
			self.theta = __theta

		else:
			print "\nIncorrect line constructor\n"
			os._exit(0)

	def polar_coords (self):
		return self.rho, self.theta

	def line_endpoints (self):
		return self.x1, self.y1, self.x2, self.y2

	def midpoint (self):
		return ( (self.x1 + self.x2) * 0.5, (self.y1 + self.y2) * 0.5)

	def direction (self, unit=True):
		length = np.sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2 )
		if unit:
			dirx = (self.x2 - self.x1) / length
			diry = (self.y2 - self.y1) / length
		else:
			dirx = (self.x2 - self.x1)
			diry = (self.y2 - self.y1)
		return dirx,diry

def get_coeff(line):
        # x = a*y+b
        a =  float(line.x2-line.x1)/float(line.y2-line.y1)
        b = line.x1-a*line.y1
        return a,b

def is_point_on_line(line_1, line_2,threshold=20.0):
        point_on_line = False
        steps = 100
        dirx_1,diry_1 = line1.direction(unit=False)
        dirx_2,diry_2 = line2.direction(unit=True)
        step_length = np.sqrt((line_2.x2-line_2.x1)**2 + (line_2.y2-line_2.y1)**2 )/float(steps)
        scan_x = line_2.x1
       	scan_y = line_2.y1
        for n in range(steps):
                scan_x = scan_x-dirx_2*step_length
                scan_y = scan_y-diry_2*step_length         
                dpx = scan_x-line_1.x1
                dpy = scan_y-line_1.y1
                cross = dpx * diry_1 - dpy * dirx_1;
                if (abs(cross) < threshold):
                        point_on_line = True
                        return point_on_line
        return point_on_line


def rphi_to_xy(r,phi):
	x = r * np.cos(phi)
	y = r * np.sin(phi)
	return x,y

def xy_to_rphi(x,y):
	r = np.sqrt( x**2 + y**2 )
	phi = np.arctan2 (y/x)
	if phi < 0 : phi += 2*math.pi
	return r,phi

def rho_theta_to_xy(rho,theta):
        a = np.cos(theta)
        b = np.sin(theta)
	x0 = a*rho
        y0 = b*rho
	x1 = int(x0 + 1000*(-b))
	y1 = int(y0 + 1000*(a))
	x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))
	if y1 > y2:
        	temp_y1 = y1
        	temp_y2 = y2
	        y2 = temp_y1
        	y1 = temp_y2
                temp_x1 = x1
	        temp_x2 = x2
        	x2 = temp_x1
                x1 = temp_x2
	return x1,y1,x2,y2

def xy_to_rho_theta(x1,y1,x2,y2):
	x0 = (x1+x2)/2
	y0 = (y1+y2)/2
	theta = np.arctan2( (y1+y2) , (x1+x2) )
	if theta < 0 : theta += 2*math.pi
	rho =  x0 * np.cos(theta) + y0 * np.sin(theta)
	return rho, theta

def select_lines(lines):
        selected_lines = []
        for l in lines:
                dirx,diry = l.direction()
                dot = np.abs(dirx * 1.0 + diry * 0.0)
                if(dot < 0.3):
                        selected_lines.append(l)
        return selected_lines

def distance_between_points(x1,y1,x2,y2) :
	distance = np.sqrt( (y2-y1)**2 + (x2-x1)**2 )
	return distance ## absolute distance

def distance_between_line_point(x0,y0,line) :
	## shortest distance of a point to a line segment (s)

	return dist #(dist x,dist y)

def distance_between_lines(line_1,line_2,npoints = 20):
        scanned_lines = []
        distances = []
        a1,b1 = get_coeff(line_1)
        a2,b2 = get_coeff(line_2)
        y_step = (1080.0)/float(npoints)
        scan_y = 0
        for i in range(npoints):
                scan_y = scan_y + y_step
                scan_x1 = a1*scan_y+b1
                scan_x2 = a2*scan_y+b2
                distances.append( (scan_y, np.abs(scan_x1-scan_x2)) )
                scanned_lines.append( line(int(scan_x1),int(scan_y),int(scan_x2),int(scan_y)) )
        return scanned_lines,distances

def is_line_close(line_1, line_2,threshold=50.0):
        _, distances = distance_between_lines(line_1,line_2)
        its_close = False
        for point in distances:
                if (point[1] < threshold):
                        its_close = True
        return its_close
        
def check_parallel(line_1, line_2,threshold = 0.5):

        parallel = False
        dirx_1,diry_1 = line_1.direction()
        dirx_2,diry_2 = line_2.direction()     
        dot = np.abs(dirx_1*dirx_2 + diry_1*diry_2)
        if dot > threshold:
                parallel = True
        return parallel

def check_perpendicular(line_1, line_2, threshold = 0.5):

	perpendicular = False
	dirx_1,diry_1 = line_1.direction()
        dirx_2,diry_2 = line_2.direction()
        dot = np.abs(dirx_1*dirx_2 + diry_1*diry_2)
        if dot < threshold:
		perpendicular = True
	return perpendicular

def average_over_nearby_lines(xy_lines,dot_threshold = 0.5,dist_threshold = 50.0):
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
                sum_x1 = line_1.x1
                sum_y1 = line_1.y1
                sum_x2 = line_1.x2
                sum_y2 = line_1.y2
                count = 1.0
                for j in range(i+1,n_lines):
                        line_2 = xy_lines[j]
                        mostly_parallel = check_parallel(line_1,line_2,threshold = dot_threshold)
                        if mostly_parallel:
                                point_on_line = is_line_close(line_1, line_2, threshold = dist_threshold)
                                if point_on_line:
                                        sum_x1 = sum_x1+line_2.x1
                                        sum_y1 = sum_y1+line_2.y1
                                        sum_x2 = sum_x2+line_2.x2
                                        sum_y2 = sum_y2+line_2.y2
                                        count = count+1
                                        line_averaged.append(j)
                                        already_averaged[j] = True
                averaged_lines.append( line(int(sum_x1/count),int(sum_y1/count),int(sum_x2/count),int(sum_y2/count)) )
        return averaged_lines

def xy_intersection(line1, line2):
    rho1, theta1 = line1.polar_coords()
    rho2, theta2 = line2.polar_coords()
    A = np.array([
        [np.cos(theta1), np.sin(theta1)],
        [np.cos(theta2), np.sin(theta2)]
    ])
    b = np.array([[rho1], [rho2]])

    x0, y0 = np.linalg.solve(A, b)
    x0, y0 = int(np.round(x0)), int(np.round(y0))
    return x0, y0

def find_intersections(lines, threshold = 0.1):
        xy = []
        if lines is not None:
            for i in range(0, len(lines)):
                for j in range(i+1, len(lines)):
                    rho1, theta1 = lines[i].polar_coords()
                    rho2, theta2 = lines[j].polar_coords()
                    if ( check_perpendicular(lines[i], lines[j], threshold) is True ) :
                        _xy = xy_intersection(lines[i], lines[j])
                        xy.append( _xy )
        return xy

def rphi_intersection(line1, line2):
    rho1, theta1 = line1.polar_coords()
    rho2, theta2 = line2.polar_coords()
    A = np.array([
        [np.cos(theta1), np.sin(theta1)],
        [np.cos(theta2), np.sin(theta2)]
    ])
    b = np.array([[rho1], [rho2]])

    x0, y0 = np.linalg.solve(A, b)
    x0, y0 = int(np.round(x0)), int(np.round(y0))
    r,phi = xy_to_rphi(x0,y0)
    return [[r,phi]]

def edge_find(img):

        #runs the edge finding algorithm. The min and max value of Canny are very important to tune!

        # preprocessing parameters
        cannyThreshold1 = 30
        cannyThreshold2 = 100
        cannyAperture = 3
        dilateIt = 1
        erodeIt = 1
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])

        # preprocess image with canny edge detection and edge smoothing
        edges = preprocess_image(img, cannyThreshold1, cannyThreshold2, cannyAperture, dilateIt, erodeIt, kernel)

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
	lines = cv2HoughLines(edges, 200)

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
	edges = preprocess_image(blur_greyscale, cannyThreshold1, cannyThreshold2, cannyAperture, dilateIt, erodeIt, kernel)

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

def preprocess_image( input, cannyThreshold1 = 50, cannyThreshold2 = 150, cannyAperture = 3, dilateIt = 1, erodeIt = 1, filterKernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]) ) :

        ## Apply canny edge detection algo to input blurred image
	edges = cv2.Canny(input, cannyThreshold1, cannyThreshold2, cannyAperture)
        ## Smooth edges so that we can find/draw the lines/contours/intersection better
        edges = cv2.dilate(edges, None, dilateIt)
        edges = cv2.erode(edges, None, erodeIt)
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

def cv2HoughLines (edges, threshold, min_line_length = 0, max_line_gap = 0, Probabilistic = False) :
	lines = []
	if Probabilistic is False :
		houghLines = cv2.HoughLines(edges,1,np.pi/180, threshold, None, min_line_length, max_line_gap) ### default hough lines
		if houghLines is not None:
			for i in range(0, len(houghLines)) :
				tempLine = line(houghLines[i][0][0], houghLines[i][0][1])
				lines.append(tempLine)
	else :
		houghLinesP = cv2.HoughLinesP(edges,1,np.pi/180, threshold, None, min_line_length, max_line_gap)
		if houghLinesP is not None:
			for i in range(0, len(houghLinesP)) :    
                                tempLine = line(houghLinesP[i][0][0], houghLinesP[i][0][1], houghLinesP[i][0][2],houghLinesP[i][0][3])
				lines.append(tempLine)

	return lines
