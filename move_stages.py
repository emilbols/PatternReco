# OpenCV program to perform Edge detection in real time
# import libraries of python OpenCV
# where its functionality resides
import cv2
import ctypes
#from ctypes import *
from ctypes import windll, c_double
#from ctypes import windll, c_double, create_string_buffer
import sys, time

xComPort=7
yComPort=6
zComPort=4
xPS = 1
yPS = 2
zPS = 3
nAxis=1
nPosF=10000
xDistance=-23.0
##yDistance=94.0
##xDistance=0.0
yDistance=0.0
zDistance=0.0
nExport=0
##7.8
##z_value=3.8

# np is an alias pointing to numpy library
import numpy as np
# capture frames from a camera

import os.path
dll_name = "ps10.dll"
dllabspath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + dll_name
# load library
# give location of dll
mydll = windll.LoadLibrary(dllabspath)


xstage=mydll.PS10_Connect(xPS, 0, xComPort, 9600,0,0,0,0)
xstage=mydll.PS10_MotorInit(xPS, nAxis)
ystage=mydll.PS10_Connect(yPS, 0, yComPort, 9600,0,0,0,0)
ystage=mydll.PS10_MotorInit(yPS, nAxis)
zstage=mydll.PS10_Connect(zPS, 0, zComPort, 9600,0,0,0,0)
zstage=mydll.PS10_MotorInit(zPS, nAxis)
# loop runs if capturing has been initialized
# 0 is relative, i guess 1 would be absolute
xstage=mydll.PS10_SetTargetMode(xPS, nAxis, 0)
ystage=mydll.PS10_SetTargetMode(yPS, nAxis, 0)
zstage=mydll.PS10_SetTargetMode(zPS, nAxis, 0)
# set velocity 
if nPosF > 0:
    xstage=mydll.PS10_SetPosF(xPS, nAxis, nPosF)
    ystage=mydll.PS10_SetPosF(yPS, nAxis, nPosF)
    zstage=mydll.PS10_SetPosF(zPS, nAxis, nPosF)
PS10_GetPositionEx=mydll.PS10_GetPositionEx
PS10_GetPositionEx.restype = ctypes.c_double
xreadout=PS10_GetPositionEx(xPS, nAxis)
yreadout=PS10_GetPositionEx(yPS, nAxis)
zreadout=PS10_GetPositionEx(zPS, nAxis)

measurement = []
global_y_cord = 0
test = True
xstage=mydll.PS10_MoveEx(xPS, nAxis, c_double(xDistance), 1)
xstate = mydll.PS10_GetMoveState(xPS, nAxis)

while(xstate > 0):
  
    #should be read by the stage
    xreadout=PS10_GetPositionEx(xPS, nAxis)
    print( "Position=%.3f" %(xreadout) )
    # reads frames from a camera
    xstate = mydll.PS10_GetMoveState(xPS, nAxis) 


xreadout=PS10_GetPositionEx(xPS, nAxis)
print( "Position=%.3f" %(xreadout) )
while xstate > 0:
    xstate = mydll.PS10_GetMoveState(xPS, nAxis)

time.sleep(1)

ystage=mydll.PS10_MoveEx(yPS, nAxis, c_double(yDistance), 1)
ystate = mydll.PS10_GetMoveState(yPS, nAxis)

while(ystate > 0):
  
    #should be read by the stage
    yreadout=PS10_GetPositionEx(yPS, nAxis)
    print( "Position=%.3f" %(yreadout) )
    # reads frames from a camera
    ystate = mydll.PS10_GetMoveState(yPS, nAxis)

zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(zDistance), 1)
zstate = mydll.PS10_GetMoveState(zPS, nAxis)

while(zstate > 0):
  
    #should be read by the stage
    zreadout=PS10_GetPositionEx(zPS, nAxis)
    print( "Position=%.3f" %(zreadout) )
    # reads frames from a camera
    zstate = mydll.PS10_GetMoveState(zPS, nAxis) 

xreadout=PS10_GetPositionEx(xPS, nAxis)
print( "x=%.3f" %(xreadout) )
yreadout=PS10_GetPositionEx(yPS, nAxis)
print( "y=%.3f" %(yreadout) )
zreadout=PS10_GetPositionEx(zPS, nAxis)
print( "z=%.3f" %(zreadout) )
closingx=mydll.PS10_Disconnect(xPS)
closingy=mydll.PS10_Disconnect(yPS)
closingz=mydll.PS10_Disconnect(zPS)
