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
import numpy
from threading import Thread
from helpers import rho_theta_to_xy, select_lines,average_over_nearby_lines,distance_between_lines
from edge_finder import edge_find, corner_find, process_edges, process_corner
from video_tools import VideoFeedHandler
from focusing_algo import gaus, sharpness_calculation, z_fit, z_move, z_scan
import csv



video_feed = VideoFeedHandler('Camera_1', 0, process_edges)


xComPort=4
yComPort=7
zComPort=3

xPS = 1
yPS = 2
zPS = 3
nAxis=1
nPosF=10000
xDistance=0.0
yDistance=0.0
zDistance=0.0
nExport=0
z_value=-0.3


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





mydll,xstage = setup_stage(mydll,xPS,xComPort,nPosF,1)
mydll,ystage = setup_stage(mydll,yPS,yComPort,nPosF,1)
mydll,zstage = setup_stage(mydll,zPS,zComPort,nPosF,1)


GetPositionEx=mydll.PS10_GetPositionEx
GetPositionEx.restype = ctypes.c_double


nom_height = 4.440
z_diff = 1.7

x_start = 4.0
y_start = 5.0

y_dim = 93.0+y_start
x_dim = 101.5+x_start

edge_positions = [(x_start,y_start,nom_height),(x_start+x_dim,y_start,nom_height),(x_start+x_dim,y_start+y_dim,nom_height),(x_start,y_start+y_dim,nom_height)]
edges = [ edge_positions ]

#should be read by the stage
                                              
edge_count = 0
for edge in edges:
    video_feed.n_edge = edge_count
    cord_count = 0
    for cord in edge:
        x = cord[0]
        y = cord[1]
        z = cord[2]
        
        xstage=mydll.PS10_MoveEx(xPS, nAxis, c_double(x), 1)
        xstate = mydll.PS10_GetMoveState(xPS, nAxis)
        ystage=mydll.PS10_MoveEx(yPS, nAxis, c_double(y), 1)
        ystate = mydll.PS10_GetMoveState(yPS, nAxis)
        zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(z), 1)
        zstate = mydll.PS10_GetMoveState(zPS, nAxis)
        while(ystate+xstate+zstate > 0):
            xreadout=GetPositionEx(xPS, nAxis)
            yreadout=GetPositionEx(yPS, nAxis)
            zreadout=GetPositionEx(zPS, nAxis)
            #print( "Position=( %.3f, %.3f , %.3f )" %(xreadout, yreadout, zreadout) )
            xstate = mydll.PS10_GetMoveState(xPS, nAxis) 
            ystate = mydll.PS10_GetMoveState(yPS, nAxis) 
            zstate = mydll.PS10_GetMoveState(zPS, nAxis)
        t0 = time.time()
        t1 = time.time()
        while(t1-t0 < 5.0):
            #should be read by the stage
            xreadout=GetPositionEx(xPS, nAxis)
            yreadout=GetPositionEx(yPS, nAxis)
            zreadout=GetPositionEx(zPS, nAxis)
            t1 = time.time()
    edge_count = edge_count + 1


# close interface
closingx=mydll.PS10_Disconnect(xPS)
closingy=mydll.PS10_Disconnect(yPS)
closingz=mydll.PS10_Disconnect(zPS)
