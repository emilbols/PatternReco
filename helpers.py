import math
import numpy as np
import argparse
import cv2
import os
from copy import deepcopy



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
                        print ("\nIncorrect line constructor\n")
                        os._exit(0)
                if np.abs(self.y2-self.y1) < np.abs(self.x2-self.x1):
                        self.vertical = False
                else:
                        self.vertical = True


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
        if line.vertical:
                a =  float(line.x2-line.x1)/float(line.y2-line.y1+0.0001)
                b = line.x1-a*line.y1
        else:
                a =  float(line.y2-line.y1)/float(line.x2-line.x1+0.0001)
                b = line.y1-a*line.x1
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
        x1 = int(x0 + 2448*(-b))
        y1 = int(y0 + 2048*(a))
        x2 = int(x0 - 2448*(-b))
        y2 = int(y0 - 2048*(a))
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

def select_lines(lines,n_edge=0):
        selected_lines_v1 = []
        selected_lines_v2 = []
        max_x = 0
        max_l = 0
        for l in lines:
                dirx,diry = l.direction()
                dot = np.abs(dirx * 1.0 + diry * 0.0)
                if(dot < 0.3):
                        selected_lines_v1.append(l)
        for l in selected_lines_v1:
                if (l.x1+l.x2)/2.0 > max_x:
                        max_l = l
                        max_x = (l.x1+l.x2)/2.0
        for l in selected_lines_v1:
                if np.abs( (l.x1+l.x2)/2.0 - max_x ) < 5:
                        selected_lines_v2.append(l)
                elif (n_edge==1 or n_edge==3) and (np.abs( (l.x1+l.x2)/2.0 - max_x ) > 700 and np.abs( (l.x1+l.x2)/2.0 - max_x ) < 870):
                        selected_lines_v2.append(l)
                elif (n_edge==0 or n_edge==2) and (np.abs( (l.x1+l.x2)/2.0 - max_x ) > 450 and np.abs( (l.x1+l.x2)/2.0 - max_x ) < 550):
                        selected_lines_v2.append(l)
        return selected_lines_v2

def select_corner_lines(lines,n_edge=0):
        selected_lines_v1 = []
        selected_lines_v2 = []
        max_x = 0
        max_l = 0
        for l in lines:
                dirx,diry = l.direction()
                dot = np.abs(dirx * 1.0 + diry * 0.0)
                if(dot < 0.3):
                        selected_lines_v1.append(l)
        for l in selected_lines_v1:
                if (l.x1+l.x2)/2.0 > max_x:
                        max_l = l
                        max_x = (l.x1+l.x2)/2.0
        for l in selected_lines_v1:
                if np.abs( (l.x1+l.x2)/2.0 - max_x ) < 5:
                        selected_lines_v2.append(l)
        return selected_lines_v2


def distance_between_points(x1,y1,x2,y2) :
        distance = np.sqrt( (y2-y1)**2 + (x2-x1)**2 )
        return distance ## absolute distance


def select_line_pairs(lines):
        selected_lines = []
        for l in lines:
                for z in lines:
                        d1 = distance_between_points(l.x1,l.y1,z.x1,z.y1)
                        d2 = distance_between_points(l.x2,l.y2,z.x2,z.y2)
                        d = (d1+d2)/2.0
                        if (d > 600 and d < 1000):
                                selected_lines.append([l,z])
        return selected_lines


def distance_between_line_point(x0,y0,line) :
        ## shortest distance of a point to a line segment (s)
        return dist #(dist x,dist y)


def distance_between_lines(line_1,line_2,npoints = 2,vertical=False):
        scanned_lines = []
        distances = []
        a1,b1 = get_coeff(line_1)
        a2,b2 = get_coeff(line_2)
        if vertical:
                y_step = (2048.0)/float(npoints)
        else:
                y_step = (2448.0)/float(npoints)
        scan_y = 0
        if vertical:
                for i in range(npoints):
                        scan_y = scan_y + y_step
                        scan_x1 = a1*scan_y+b1
                        scan_x2 = a2*scan_y+b2
                        distances.append( (scan_y, np.abs(scan_x1-scan_x2)) )
                        scanned_lines.append( line(int(scan_x1),int(scan_y),int(scan_x2),int(scan_y)) )
        else:
                for i in range(npoints):
                        scan_y = scan_y + y_step
                        scan_x1 = a1*scan_y+b1
                        scan_x2 = a2*scan_y+b2
                        distances.append( (scan_y, np.abs(scan_x1-scan_x2)) )
                        scanned_lines.append( line(int(scan_y),int(scan_x1),int(scan_y),int(scan_x2)) )
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

def average_over_nearby_lines(xy_lines,dot_threshold = 0.5,dist_threshold = 20.0):
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

