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

# time stamp of measurement
time_measure = time.strftime("%d-%m-%Y_%H-%M-%S", time.gmtime())
print("time stamp of measurement: ", time_measure)

# measurement type: "corner" (corner top to corner bottom) or "edges" (all edges of top sensor)
measure_type = "corner"

if measure_type == "corner":
    print("Performing corner to corner measurement")
    video_feed = VideoFeedHandler('Camera_1', 1, process_corner)
elif measure_type == "edges":
    print("Performing measurement of sensor egdes")
    video_feed = VideoFeedHandler('Camera_1', 1, process_edges)
else:
    print("ERROR: missing argument for measurement type:\n 'edges' for measuring all edges of top sensor\n 'corner': measure distance of bottom and top sensor corners")
    exit()



def PixelCordToMicronCord(p):
    x = -p[0]*1.14547537228
    y = p[1]*1.14547537228
    converted = (x,y)
    return converted
                

test_video_only = False

if test_video_only:
    time.sleep(100)
    quit()

    

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

output_dir = 'images_sharpness_check/'

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


nom_height = 5.7
z_diff = 1.7
if measure_type == "corner":
    steps = 3
if measure_type == "edges":
    steps = 3

x_start = 0.0
y_start = 3.5

y_dim = 93.5+y_start
x_dim = 102.0+x_start
#### CORNER:
#starting point: southeast corner top sensor
#   
#  --1----3----5----7-- top
#
#  --2----4----6----8-- bottom
#
#[:-2] -> measure corners at begin and middle of edge (4 measurement points in total)
if measure_type == "corner":
    path = [(x_start, round(y,1),nom_height+fac*z_diff) for y in numpy.linspace(y_start,y_dim,steps) for fac in [1,0]][:-2]
    edges = [ path ]

#### EDGES:
#starting point: southwest corner
#path: SE -> SW (-> NW -> NE)
#[1:2] -> only one sharpness check in the middle of the edge
if measure_type == "edges":
    edge1_positions = [(round(x,1),y_start,nom_height) for x in numpy.linspace(x_start,x_dim,steps)[1:2]]
    edge2_positions = [(x_dim,round(y,1),nom_height) for y in numpy.linspace(y_start,y_dim,steps)[1:2]]    
    #edge3_positions = [(round(x,1),y_dim,nom_height) for x in numpy.linspace(x_dim,x_start,steps)[1:2]]
    #edge4_positions = [(x_start,round(y,1),nom_height) for y in numpy.linspace(y_dim,y_start,steps)[1:2]]

    #edges = [ edge1_positions, edge2_positions, edge3_positions, edge4_positions ]
    edges = [ edge1_positions, edge2_positions ]
    #edges = [ edge1_positions ]
#out.write(frame)
#should be read by the stage
                                              
edge_count = 0
sharpness_all_edges = []
for edge in edges:
    video_feed.n_edge = edge_count
    sharpness_edge = []
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
        #focusing z position
        current_sharpness = sharpness_calculation(video_feed, 0)
        sharpness_edge.append(current_sharpness)
        print("Current sharpness: ", current_sharpness)
        #measure for 10 seconds
        t0 = time.time()
        t1 = time.time()
        while(t1-t0 < 5.0):
            #should be read by the stage
            xreadout=GetPositionEx(xPS, nAxis)
            yreadout=GetPositionEx(yPS, nAxis)
            zreadout=GetPositionEx(zPS, nAxis)
            if measure_type == "corner":
                global_cord = yreadout*1000.0
            if measure_type == "edges":
                if (edge_count==0) or (edge_count==2):
                    global_cord = yreadout*1000.0
                else:
                    global_cord = xreadout*1000.0
            # reads frames from a camera
            cv2.imwrite(output_dir+'edge'+str(edge_count)+'_x_'+str(xreadout)+'_y_'+str(yreadout)+'_z_'+str(zreadout)+'_s_'+str(current_sharpness)+'.jpg',video_feed.frame)
            distances = video_feed.processed_objects
            if distances:
                for p in distances:
                    converted = PixelCordToMicronCord(p)
                    y = global_cord+converted[0]
                    dist = converted[1]
                    with open("csv_measurements/measurement_sharpness_"+str(time_measure)+".csv", 'a+', newline='') as csvfile:
                        writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        writer.writerow([x,y,z,dist])
            t1 = time.time()
        with open("sharpness/sharpness_"+str(time_measure)+".csv", 'a+', newline='') as csvfile_sharp:
            writer_sharp = csv.writer(csvfile_sharp, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer_sharp.writerow([x,y,z,current_sharpness])
    edge_count = edge_count + 1
    sharpness_all_edges.append(sharpness_edge)
    #print("Sharpness of the edge: ", sharpness_edge)
    #print("Maximum sharpness: ", max(sharpness_edge))
    #print("Minimum sharpness: ", min(sharpness_edge))    
print("Sharpness of all edges: ", sharpness_all_edges)
for sharp_edge in sharpness_all_edges:
    counter = 0
    print("Maximum sharpness of edge ",counter,": ", max(sharp_edge))
    counter += 1



# close interface
closingx=mydll.PS10_Disconnect(xPS)
closingy=mydll.PS10_Disconnect(yPS)
closingz=mydll.PS10_Disconnect(zPS)
