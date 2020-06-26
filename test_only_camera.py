# OpenCV program to perform Edge detection in real time
# import libraries of python OpenCV
# where its functionality resides
import cv2

# np is an alias pointing to numpy library
import numpy as np
from edge_finder import edge_find, rho_theta_to_xy, select_lines,average_over_nearby_lines,distance_between_lines, corner_find
# capture frames from a camera
#cap = cv2.VideoCapture('videos/edge_scan.mp4')
cap = cv2.VideoCapture(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,2560);
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,2560);
cap.set(cv2.CAP_PROP_FPS,5);

# loop runs if capturing has been initialized
measurement = []
global_y_cord = 0
test = True
#out = cv2.VideoWriter('dummy_sensor_scan_v3.avi', cv2.VideoWriter_fourcc(*'XVID'), 25,(2448,2048))
while(test):
    ret, frame = cap.read()
    #out.write(frame)
    #should be read by the stage
    cv2.namedWindow('Original',cv2.WINDOW_NORMAL)

    cv2.imshow('Original',frame) 
    cv2.resizeWindow('Original', 1024,800)
    cv2.imwrite('more_tricky_mask.jpg',frame)
    # Display edges in a frame
    #for l in lines:
      #  cv2.line(line_copy,(l.x1,l.x2),(l.x2,l.y2),(0,0,255),2,cv2.LINE_AA)
    key = cv2.waitKey(1) 
    if key == ('c'):
        break

# Close the window
cap.release()
# De-allocate any associated memory usage
cv2.destroyAllWindows()

