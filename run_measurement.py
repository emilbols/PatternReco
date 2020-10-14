# OpenCV program to perform Edge detection in real time
# import libraries of python OpenCV
# where its functionality resides
import cv2
import ctypes
#from ctypes import *
from ctypes import windll, c_double
#from ctypes import windll, c_double, create_string_buffer
import sys, time
import os.path
import numpy as np
from threading import Thread
from edge_finder import edge_find, rho_theta_to_xy, select_lines,average_over_nearby_lines,distance_between_lines, corner_find, process_image
from video_tools import VideoFeedHandler
import csv

def PixelCordToMicronCord(p):
    x = -p[0]*1.14547537228
    y = p[1]*1.14547537228
    converted = (x,y)
    return converted
                


video_feed = VideoFeedHandler('Camera_1', 0, process_image)
test_video_only = False

if test_video_only:
    time.sleep(100)
    quit()

    
csvfile = open('measurement.csv', 'w+')    
writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
xComPort=3
yComPort=5
zComPort=4

xPS = 1
yPS = 2
zPS = 3
nAxis=1
nPosF=2500
xDistance=0.0
yDistance=80.0
zDistance=0.0
nExport=0
z_value=3.834


dll_name = "ps10.dll"
dllabspath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + dll_name
# load library
# give location of dll
mydll = windll.LoadLibrary(dllabspath)

def setup_stage(dll_ref,PS,ComPort,speed,absolute):
    stage=dll_ref.PS10_Connect(PS, 0, ComPort, 9600,0,0,0,0)
    stage=dll_ref.PS10_MotorInit(PS, 1)
    stage=dll_ref.PS10_SetTargetMode(PS, 1, absolute)
    if speed > 0:
        stage=dll_ref.PS10_SetPosF(PS, 1, speed)
    return dll_ref,stage




mydll,xstage = setup_stage(mydll,xPS,xComPort,nPosF,0)
mydll,ystage = setup_stage(mydll,yPS,yComPort,nPosF,0)
mydll,zstage = setup_stage(mydll,zPS,zComPort,nPosF,1)

GetPositionEx=mydll.PS10_GetPositionEx
GetPositionEx.restype = ctypes.c_double
   


"""
#Initiliaze stages
xstage = mydll.PS10_GoRef(xPS, nAxis, 4)
xstate = mydll.PS10_GetMoveState(xPS, nAxis)
while xstate > 0: 
    xstate = mydll.PS10_GetMoveState(xPS, nAxis)

print("x-axis is in position.")
xreadout=GetPositionEx(xPS, nAxis)
print( "Position=%.3f" %(xreadout) )

ystage=mydll.PS10_GoRef(yPS, nAxis, 4)

ystate = mydll.PS10_GetMoveState(yPS, nAxis)
while ystate > 0: 
    ystate = mydll.PS10_GetMoveState(yPS, nAxis)

print("y-axis is in initial position.")
yreadout=PS10_GetPositionEx(yPS, nAxis)
print( "Position=%.3f" %(yreadout) )

zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(z_value), 1)
zstate = mydll.PS10_GetMoveState(zPS, nAxis)
while zstate > 0: 
    zstate = mydll.PS10_GetMoveState(zPS, nAxis)

print("z-axis is in position.")
zreadout=PS10_GetPositionEx(zPS, nAxis)
print( "Position=%.3f" %(zreadout) )
time.sleep(2)

"""
#out.write(frame)
#should be read by the stage
                                              



ystage=mydll.PS10_MoveEx(yPS, nAxis, c_double(yDistance), 1)
ystate = mydll.PS10_GetMoveState(yPS, nAxis)
while(ystate > 0):
    #should be read by the stage
    yreadout=GetPositionEx(yPS, nAxis)
    print( "Position=%.3f" %(yreadout) )
    global_cord = yreadout*1000.0
    # reads frames from a camera
    distances = video_feed.processed_objects
    if distances:
        for p in distances:
            converted = PixelCordToMicronCord(p)
            y = global_cord+converted[0]
            dist = converted[1]
            writer.writerow([y,dist])
    ystate = mydll.PS10_GetMoveState(yPS, nAxis) 


"""
xstage=mydll.PS10_MoveEx(xPS, nAxis, c_double(xDistance), 1)
xstate = mydll.PS10_GetMoveState(xPS, nAxis)

while(xstate > 0):
    xreadout=GetPositionEx(xPS, nAxis)
    print( "Position=%.3f" %(xreadout) )
    # reads frames from a camera  
    #should be read by the stage
    xstate = mydll.PS10_GetMoveState(xPS, nAxis)
 

xreadout=GetPositionEx(xPS, nAxis)
print( "Position=%.3f" %(xreadout) )

while xstate > 0:
    xstate = mydll.PS10_GetMoveState(xPS, nAxis)

time.sleep(5)
    
time.sleep(5)

xstage=mydll.PS10_MoveEx(xPS, nAxis, c_double(-xDistance), 1)
xstate = mydll.PS10_GetMoveState(xPS, nAxis)

while(xstate > 0):
  
    #should be read by the stage
    xreadout=GetPositionEx(xPS, nAxis)
    print( "Position=%.3f" %(xreadout) )
    # reads frames from a camera
    xstate = mydll.PS10_GetMoveState(xPS, nAxis) 



xreadout=GetPositionEx(xPS, nAxis)
print( "Position=%.3f" %(xreadout) )
while xstate > 0:
    xstate = mydll.PS10_GetMoveState(xPS, nAxis)

time.sleep(5)

ystage=mydll.PS10_MoveEx(yPS, nAxis, c_double(-yDistance), 1)
ystate = mydll.PS10_GetMoveState(yPS, nAxis)

while(ystate > 0):
  
    #should be read by the stage
    yreadout=GetPositionEx(yPS, nAxis)
    print( "Position=%.3f" %(yreadout) )
    # reads frames from a camera
    ystate = mydll.PS10_GetMoveState(yPS, nAxis) 


    
time.sleep(5)

zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(zDistance), 1)
zstate = mydll.PS10_GetMoveState(zPS, nAxis)

while(zstate > 0):
  
    #should be read by the stage
    zreadout=GetPositionEx(zPS, nAxis)
    print( "Position=%.3f" %(zreadout) )
    # reads frames from a camera
    zstate = mydll.PS10_GetMoveState(zPS, nAxis)

"""


# close interface
closingx=mydll.PS10_Disconnect(xPS)
closingy=mydll.PS10_Disconnect(yPS)
closingz=mydll.PS10_Disconnect(zPS)
