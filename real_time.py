# OpenCV program to perform Edge detection in real time
# import libraries of python OpenCV
# where its functionality resides
import cv2

# np is an alias pointing to numpy library
import numpy as np
from edge_finder import edge_find, rho_theta_to_xy, select_lines,average_over_nearby_lines
# capture frames from a camera
cap = cv2.VideoCapture('videos/letstry.avi')


# loop runs if capturing has been initialized
while(1):

    # reads frames from a camera
    ret, frame = cap.read()   
    # Display an original image
    
    cv2.namedWindow('Original',cv2.WINDOW_NORMAL)
    cv2.imshow('Original',frame) 
    cv2.resizeWindow('Original', 900,500)
    # finds edges in the input image image and
    # marks them in the output map edges
    #edges = cv2.Canny(frame,50,150)
    edges,cnts,lines = edge_find(frame)
    # Display edges in a frame
    line_copy = frame.copy()
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
        
    cv2.namedWindow('Edges',cv2.WINDOW_NORMAL)    
    cv2.imshow('Edges',line_copy)
    cv2.resizeWindow('Edges', 900,500)
   
    key = cv2.waitKey(1) 
    if key == ('c'):
        break

# Close the window
cap.release()

    # De-allocate any associated memory usage
cv2.destroyAllWindows()
