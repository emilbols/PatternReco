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
from helpers import rho_theta_to_xy, select_lines,average_over_nearby_lines,distance_between_lines
from edge_finder import edge_find, corner_find, process_edges
from video_tools import VideoFeedHandler
import csv

def PixelCordToMicronCord(p):
    x = -p[0]*1.14547537228
    y = p[1]*1.14547537228
    converted = (x,y)
    return converted
                


video_feed = VideoFeedHandler('Camera_1', 0, process_edges)
test_video_only = False

if test_video_only:
    time.sleep(100)
    quit()

    
csvfile = open('measurement_sensor2019.csv', 'w+')    
writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
xComPort=4
yComPort=6
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

output_dir = 'images_sensor2040/'

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

height1 = 8.32
height2 = 8.32
nom_height = 9.05
steps = 5
y_dim = 92.8 # 94.183
x_dim = 101.2 # 102.7

edge1_positions = [[0,round(y,1),nom_height] for y in np.linspace(0,y_dim,steps)]
edge2_positions = [[round(x,1),y_dim,nom_height+0.3] for x in np.linspace(0,x_dim,steps)]
edge3_positions = [[x_dim,round(y,1),nom_height] for y in np.linspace(y_dim,0,steps)]
edge4_positions = [[round(x,1),0,nom_height] for x in np.linspace(x_dim,0,steps)]

edge1_positions[1][2]=nom_height
edge1_positions[2][2]=nom_height
edge1_positions[3][2]=nom_height+0.1
edge1_positions[4][2]=nom_height+0.3

edge2_positions[1][2]=nom_height+0.1
edge2_positions[2][2]=nom_height-0.05
edge2_positions[3][2]=nom_height-0.05
edge2_positions[4][2]=nom_height-0.05

edge3_positions[1][2]=nom_height-0.25
edge3_positions[2][2]=nom_height-0.35
edge3_positions[3][2]=nom_height-0.4
edge3_positions[4][2]=nom_height-0.45

edge4_positions[1][2]=nom_height-0.4
edge4_positions[2][2]=nom_height-0.35
edge4_positions[3][2]=nom_height-0.25
edge4_positions[4][2]=nom_height


#edges = [ edge1_positions, edge2_positions, edge3_positions, edge4_positions ]

test_pos = [ [ edge4_positions[4][0],edge4_positions[4][1], edge4_positions[4][2] ] ]
edges = [ test_pos ]

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
                                              
edge_count = 3
for edge in edges:
    video_feed.n_edge = edge_count
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
        #measure for 10 seconds
        t0 = time.time()
        t1 = time.time()
        while(t1-t0 < 3.0):
            #should be read by the stage
            xreadout=GetPositionEx(xPS, nAxis)
            yreadout=GetPositionEx(yPS, nAxis)
            zreadout=GetPositionEx(zPS, nAxis)
            if (edge_count==0) or (edge_count==2):
                global_cord = yreadout*1000.0
            else:
                global_cord = xreadout*1000.0
            # reads frames from a camera
            cv2.imwrite(output_dir+'edge'+str(edge_count)+'_x_'+str(xreadout)+'_y_'+str(yreadout)+'.jpg',video_feed.frame)
            distances = video_feed.processed_objects
            if distances:
                for p in distances:
                    converted = PixelCordToMicronCord(p)
                    y = global_cord+converted[0]
                    dist = converted[1]
                    writer.writerow([x,y,z,dist])
            t1 = time.time()
    edge_count = edge_count + 1
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
