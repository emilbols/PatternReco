
# OpenCV program to perform Edge detection in real time
# import libraries of python OpenCV
# where its functionality resides
import cv2

# np is an alias pointing to numpy library
import numpy as np
from edge_finder import edge_find, rho_theta_to_xy, select_lines,average_over_nearby_lines,distance_between_lines, corner_find
# capture frames from a camera
cap = cv2.VideoCapture('videos/videos_final_setup/dummy_sensor_scan.avi')
#cap = cv2.VideoCapture(1)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH,2500);
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT,2500);
#start_frame_number = 30
cap.set(cv2.CAP_PROP_FPS, 5)
# loop runs if capturing has been initialized
measurement = []
global_y_cord = 0
test = True
frame_rate = 10
frame_count = 0
vertical=True
while(test):

    #should be read by the stage
    global_y_cord = global_y_cord + 5.0
    frame_count = frame_count+1
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
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cutoff_val = int( (np.median(img)-np.min(img))/2.5 + np.min(img) )
    #print cutoff_val
    cutoff, thres_image = cv2.threshold(img, cutoff_val, 255, cv2.THRESH_BINARY)
    # finds edges,countours, and hough lines in the input image image
    thres_edges, thres_cnts, thres_lines = edge_find(thres_image,220,250,250)
    lower = 70
    upper = 129
    edges, cnts, lines = edge_find(img,lower,upper,300,dilate=1)
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
        if edge_l:
            cv2.line(line_copy,(edge_l.x1,edge_l.y1),(edge_l.x2,edge_l.y2),(0,0,255),2,cv2.LINE_AA)
        min_l = 0
        min_l_y = 9999
        min_l = 0
        max_l_x = 0
      
    if thres_lines and edge_l:
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
        if min_l:
            cv2.line(line_copy,(min_l.x1,min_l.y1),(min_l.x2,min_l.y2),(0,0,255),2,cv2.LINE_AA)
    cv2.namedWindow('Original',cv2.WINDOW_NORMAL)
    cv2.imshow('Original',frame) 
    cv2.resizeWindow('Original', 1024,800)

    #cv2.namedWindow('Edges',cv2.WINDOW_NORMAL)
    #cv2.imshow('Edges',edges) 
    #cv2.resizeWindow('Edges', 1024,800)

    # Display edges in a frame
    
    #for l in lines:
    #  cv2.line(line_copy,(l.x1,l.x2),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
    
    #selected_lines = select_lines(lines)
    #selected_lines = lines
    
    #if selected_lines is not None:
    #    averaged_selected_lines = average_over_nearby_lines(selected_lines)
    #    for l in averaged_selected_lines:
    #        cv2.line(line_copy,(l.x1,l.y1),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
    #    if len(averaged_selected_lines) == 2:
    #        scanned_lines,distances = distance_between_lines(averaged_selected_lines[0],averaged_selected_lines[1])
    #        for l in scanned_lines:
    #            cv2.line(line_copy,(l.x1,l.y1),(l.x2,l.y2),(255,0,0),2,cv2.LINE_AA)
    #        for point in distances:
    #            y_cord = global_y_cord + point[0]
    #            dist_x = point[1]
    #            measurement.append((y_cord,dist_x))
    #if corners is not None:
    #   for corner in corners:
    #        line_copy = cv2.circle(line_copy, tuple(corner), 25, (0,0,255), 5)
    
    cv2.namedWindow('Lines',cv2.WINDOW_NORMAL)
    cv2.imshow('Lines',line_copy)
    cv2.resizeWindow('Lines', 1024,800)
    
    key = cv2.waitKey(1) 
    if key == ('c'):
        break

# Close the window
cap.release()
# De-allocate any associated memory usage
cv2.destroyAllWindows()

