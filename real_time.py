# OpenCV program to perform Edge detection in real time
# import libraries of python OpenCV
# where its functionality resides
import cv2

# np is an alias pointing to numpy library
import numpy as np
from edge_finder import edge_find, rho_theta_to_xy, select_lines,average_over_nearby_lines,distance_between_lines
# capture frames from a camera
cap = cv2.VideoCapture('videos/letstry.avi')


# loop runs if capturing has been initialized
measurement = []
global_y_cord = 0
test = True
while(test):

    #should be read by the stage
    global_y_cord = global_y_cord + 5.0
    
    # reads frames from a camera
    ret, frame = cap.read()
    test = cap.isOpened()
    if not test:
        break
    if frame is None:
        test = False
        break
    # Display an original image
    line_copy = frame.copy()
    # finds edges,countours, and hough lines in the input image image
    edges,cnts,lines = edge_find(frame)
    
    cv2.namedWindow('Original',cv2.WINDOW_NORMAL)
    cv2.imshow('Original',frame) 
    cv2.resizeWindow('Original', 900,500)
    # Display edges in a frame
    xy_lines = []
    if lines is not None:
        for l in lines:
            for rho,theta in l:
                x1,y1,x2,y2 = rho_theta_to_xy(rho,theta)
                xy_lines.append((x1,y1,x2,y2))
    #for l in xy_lines:
      #  cv2.line(line_copy,(l[0],l[1]),(l[2],l[3]),(0,0,255),2)
    selected_lines = select_lines(xy_lines)
    if selected_lines is not None:
        averaged_selected_lines = average_over_nearby_lines(selected_lines)
        for l in averaged_selected_lines:
            cv2.line(line_copy,(l[0],l[1]),(l[2],l[3]),(0,0,255),2)
        if len(averaged_selected_lines) == 2:
            scanned_lines,distances = distance_between_lines(averaged_selected_lines[0],averaged_selected_lines[1])
            for l in scanned_lines:
                cv2.line(line_copy,(l[0],l[1]),(l[2],l[3]),(255,0,0),2)
    cv2.namedWindow('Edges',cv2.WINDOW_NORMAL)    
    cv2.imshow('Edges',line_copy)
    cv2.resizeWindow('Edges', 900,500)
    for point in distances:
        y_cord = global_y_cord + point[0]
        dist_x = point[1]
        measurement.append((y_cord,dist_x))
    key = cv2.waitKey(1) 
    if key == ('c'):
        break

# Close the window
cap.release()
# De-allocate any associated memory usage
cv2.destroyAllWindows()

