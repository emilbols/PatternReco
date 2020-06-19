# OpenCV program to perform Edge detection in real time
# import libraries of python OpenCV
# where its functionality resides
import cv2
import ctypes
#from ctypes import *
from ctypes import windll, c_double
#from ctypes import windll, c_double, create_string_buffer
import sys

nComPort=4
nAxis=1
nPosF=10000
dDistance=0.0
nExport=0

# np is an alias pointing to numpy library
import numpy as np
# capture frames from a camera
#cap = cv2.VideoCapture('videos/edge_scan.mp4')
cap = cv2.VideoCapture(1)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH,2500);
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT,2500);

import os.path
dll_name = "ps10.dll"
dllabspath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + dll_name
# load library
# give location of dll
mydll = windll.LoadLibrary(dllabspath)
if nComPort==0: # find first connected control unit
    result1=mydll.PS10_SimpleConnect(1, b"") # ANSI/Unicode !!
elif nComPort==-1: # find the first connected control unit via tcp/ip socket (localhost, port=1200)
    result1=mydll.PS10_SimpleConnect(1, b"net") # ANSI/Unicode !!
else: # connect control unit with defined COM port
    result1=mydll.PS10_Connect(1, 0, nComPort, 9600,0,0,0,0)
result1=mydll.PS10_MotorInit(1, nAxis)
# loop runs if capturing has been initialized
# 0 is relative, i guess 1 would be absolute
result1=mydll.PS10_SetTargetMode(1, nAxis, 0)
# set velocity 
if nPosF > 0:
    result1=mydll.PS10_SetPosF(1, nAxis, nPosF)
PS10_GetPositionEx=mydll.PS10_GetPositionEx
PS10_GetPositionEx.restype = ctypes.c_double
result2=PS10_GetPositionEx(1, nAxis)
result1=mydll.PS10_GoRef(1, nAxis, 4)
state = mydll.PS10_GetMoveState(1, nAxis)
while state > 0: 
    state = mydll.PS10_GetMoveState(1, nAxis)

print("Axis is in position.")
result2=PS10_GetPositionEx(1, nAxis)
print( "Position=%.3f" %(result2) )


measurement = []
global_y_cord = 0
test = True
result1=mydll.PS10_MoveEx(1, nAxis, c_double(dDistance), 1)
state = mydll.PS10_GetMoveState(1, nAxis) 
while(state > 0):
  
    #should be read by the stage
    global_y_cord = global_y_cord + 5.0
    result2=PS10_GetPositionEx(1, nAxis)
    print( "Position=%.3f" %(result2) )
    # reads frames from a camera
    ret, frame = cap.read()
    test = cap.isOpened()
    if not test:
        break
    if frame is None:
        test = False
        break
    # Display an original image

    cv2.namedWindow('Original',cv2.WINDOW_NORMAL)
    cv2.imshow('Original',frame) 
    cv2.resizeWindow('Original', 1024,800)
    state = mydll.PS10_GetMoveState(1, nAxis) 
    key = cv2.waitKey(1) 
    if key == ('c'):
        break

# Close the window
cap.release()
# De-allocate any associated memory usage
cv2.destroyAllWindows()
result2=PS10_GetPositionEx(1, nAxis)
print( "Position=%.3f" %(result2) )
while state > 0:
    state = mydll.PS10_GetMoveState(1, nAxis)
# close interface
result1=mydll.PS10_Disconnect(1)
