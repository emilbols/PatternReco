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

# sharpness threshold for using auto focusing, to be obtained from sharpness check program:
sharp_thres = 500000000

# measurement type: "corner" (corner top to corner bottom) or "edges" (all edges of top sensor)
measure_type = "edges"

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

output_dir = 'dummy_sensor_blackbox_cover_lesslight/'

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


#nom_height = 5.6
nom_height = 7.9
z_diff = 1.7
if measure_type == "corner":
    steps = 3
if measure_type == "edges":
    steps = 5

x_start = 0.0
y_start = 3.0

#y_dim = 93.0+y_start
y_dim = 96.0+y_start
x_dim = 101.5+x_start

#### CORNER:
#starting point: southeast corner top sensor
#   
#  --1----3----5----7-- top
#
#  --2----4----6----8-- bottom
#
if measure_type == "corner":
    #path = [(x_start, round(y,1),nom_height+fac*z_diff) for y in numpy.linspace(y_start,y_dim,steps) for fac in [1,0]]
    #edges = [ path ]
    #edges = [ [(x_start, y_start, nom_height),(x_start, y_start, nom_height+z_diff), (x_start, y_dim, nom_height-0.4), (x_start, y_dim, nom_height+z_diff-0.4)] ]

    edges = [ [(x_start, y_start, nom_height),(x_start, y_start, nom_height+z_diff), (x_start, y_dim, nom_height-0.1), (x_start, y_dim, nom_height+z_diff-0.1)] ]    
#### EDGES:
#starting point: southeast corner
#path: SW -> SE -> NE -> NW
#avoid duplicates with [1:] -> removing first element of edges 2-4
if measure_type == "edges":
    edge1_positions = [(round(x,1),y_start,nom_height) for x in numpy.linspace(x_start,x_dim,steps)]
    edge2_positions = [(x_dim,round(y,1),nom_height) for y in numpy.linspace(y_start,y_dim,steps)[1:]]
    edge3_positions = [(round(x,1),y_dim,nom_height) for x in numpy.linspace(x_dim,x_start,steps)[1:]]
    edge4_positions = [(x_start,round(y,1),nom_height) for y in numpy.linspace(y_dim,y_start,steps)[1:-1]]
    #edges = [ edge1_positions, edge2_positions, edge3_positions, edge4_positions ]
    edges = [ edge4_positions ]
#out.write(frame)
#should be read by the stage
                                              
edge_count = 3
for edge in edges:
    video_feed.n_edge = edge_count
    cord_count = 0
    for cord in edge:
        x = cord[0]
        y = cord[1]
        # first cord of first edge: use z-value of initialized array (cord[2])
        # first cord of all following edges: use focused z-value from previous edge (z_focused)
        # all other cords but the first cord: use focused z-value from previous cord (z_focused)
        if cord_count == 0:
            if edge_count == 3:
                z_focused = cord[2]
                z = cord[2]
            else:
                z = z_focused
        else:
            if measure_type == "corner":
                z = cord[2] #corner issue here!
            else:
                z = z_focused  
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
        z_range = 1.0
        z_steps = 15
        current_sharpness = sharpness_calculation(video_feed, 0)
        if current_sharpness < sharp_thres:
            print("starting z-focusing")
            z_focused = z_scan(z_range, z_steps,video_feed)
        else:
            z_focused = z
        cord_count += 1
        print("z_focused: ", z_focused)
        zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(z_focused), 1)
        zstate = mydll.PS10_GetMoveState(zPS, nAxis)
        while zstate > 0:
            zstate = mydll.PS10_GetMoveState(zPS, nAxis)
            zreadout=GetPositionEx(zPS, nAxis)
            #print( "new z position after focusing: %.3f )" %(zreadout) )
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
            cv2.imwrite(output_dir+'edge'+str(edge_count)+'_x_'+str(xreadout)+'_y_'+str(yreadout)+'_z_'+str(zreadout)+'.jpg',video_feed.frame)
            distances = video_feed.processed_objects
            if distances:
                for p in distances:
                    converted = PixelCordToMicronCord(p)
                    y = global_cord+converted[0]
                    dist = converted[1]
                    with open("csv_measurements/measurement_"+str(measure_type)+"_"+str(time_measure)+".csv", 'a+', newline='') as csvfile:
                        writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        writer.writerow([x,y,z,dist])
            t1 = time.time()
    edge_count = edge_count + 1


# close interface
closingx=mydll.PS10_Disconnect(xPS)
closingy=mydll.PS10_Disconnect(yPS)
closingz=mydll.PS10_Disconnect(zPS)
