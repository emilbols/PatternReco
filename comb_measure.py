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
from edge_finder import edge_find, rho_theta_to_xy, select_lines,average_over_nearby_lines,distance_between_lines, corner_find, process_image, process_corner
from video_tools import VideoFeedHandler
from focusing_algo import gaus, sharpness_calculation, z_fit, z_move, z_scan
import csv


if sys.argv[1] == "corner":
    print("Performing corner to corner measurement")
    video_feed = VideoFeedHandler('Camera_1', 0, process_corner)
elif sys.argv[1] == "edges":
    print("Performing measurement of sensor egdes")
    video_feed = VideoFeedHandler('Camera_1', 0, process_image)
else:
    sys.exit("ERROR: missing argument for measurement type:\n 'edges' for measuring all edges of top sensor\n 'corner': measure distance of bottom and top sensor corners")



def PixelCordToMicronCord(p):
    x = -p[0]*1.14547537228
    y = p[1]*1.14547537228
    converted = (x,y)
    return converted
                

test_video_only = False

if test_video_only:
    time.sleep(100)
    quit()

    
csvfile = open('measurement.csv', 'w+')    
writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
xComPort=6
yComPort=3
zComPort=4

xPS = 1
yPS = 2
zPS = 3
nAxis=1
nPosF=2500
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

output_dir = 'images_used/'

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

nom_height = 5.0
z_diff = 1.8
if sys.argv[1] == "corner":
    steps = 4
if sys.argv[1] == "edges":
    steps = 5
y_dim = 94.183
x_dim = 102.7


#### CORNER:
#   
#  --1----3----5----7-- top
#
#  --2----4----6----8-- bottom
#
if sys.argv[1] == "corner":
    path = [(x_dim, round(y,1),nom_height+fac*z_diff) for y in numpy.linspace(0,y_dim,steps) for fac in [1,0]]
    edges = [ path ]

#### EDGES:
if sys.argv[1] == "edges":
    edge1_positions = [(0,round(y,1),nom_height) for y in numpy.linspace(0,y_dim,steps)]
    edge2_positions = [(round(x,1),y_dim,nom_height) for x in numpy.linspace(0,x_dim,steps)]
    edge3_positions = [(x_dim,round(y,1),nom_height) for y in numpy.linspace(y_dim,0,steps)]
    edge4_positions = [(round(x,1),0,nom_height) for x in numpy.linspace(x_dim,0,steps)]

    edges = [ edge1_positions, edge2_positions, edge3_positions, edge4_positions ]


#out.write(frame)
#should be read by the stage
                                              
edge_count = 0
for edge in edges:
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
            print( "Position=( %.3f, %.3f , %.3f )" %(xreadout, yreadout, zreadout) )
            xstate = mydll.PS10_GetMoveState(xPS, nAxis) 
            ystate = mydll.PS10_GetMoveState(yPS, nAxis) 
            zstate = mydll.PS10_GetMoveState(zPS, nAxis)
            #focusing z position
            print("starting z-focusing")
            z_range = 0.2
            z_steps = 0.002
            z_focused = z_scan(z_range, z_steps)
            zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(z_focused), 1)
            zstate = mydll.PS10_GetMoveState(zPS, nAxis)
            zreadout=GetPositionEx(zPS, nAxis)
            print( "new z position after focusing: %.3f )" %(zreadout) )
        #measure for 10 seconds
        t0 = time.time()
        t1 = time.time()
        while(t1-t0 < 10.0):
            #should be read by the stage
            xreadout=GetPositionEx(xPS, nAxis)
            yreadout=GetPositionEx(yPS, nAxis)
            zreadout=GetPositionEx(zPS, nAxis)
            if sys.argv[1] == "corner":
                global_cord = yreadout*1000.0
            if sys.argv[1] == "edges":
                if (edge_count==0) or (edge_count==2):
                    global_cord = yreadout*1000.0
                else:
                    global_cord = xreadout*1000.0
            # reads frames from a camera
            cv2.imwrite(output_dir+'edge'+str(edge_count)+'_x_'+str(xreadout)+'_y_'+str(yreadout)+'_z_'+str(zreadout)+'.jpg',video_feed.frame)
            distances = video_feed.processed_objects
            if distances:
                for p in distances:
                    converted = PixelCordToMicronCord(p)
                    y = global_cord+converted[0]
                    dist = converted[1]
                    writer.writerow([x,y,z,dist])
            t1 = time.time()
    edge_count = edge_count + 1


# close interface
closingx=mydll.PS10_Disconnect(xPS)
closingy=mydll.PS10_Disconnect(yPS)
closingz=mydll.PS10_Disconnect(zPS)
