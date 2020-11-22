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
import csv

def PixelCordToMicronCord(p):
    x = -p[0]*1.14547537228
    y = p[1]*1.14547537228
    converted = (x,y)
    return converted
                

class VideoFeedHandler(object):
    def __init__(self, video_file_name, src, processing_function):
        # Create a VideoCapture object
        self.frame = 0
        self.processed_frame = 0
        self.processed_objects = 0
        self.frame_name = 'cam_output'+str(src)
        self.processing_function = processing_function
        self.video_file = video_file_name
        self.video_file_name = video_file_name + '.avi'
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,2560);
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,2560);

        # Default resolutions of the frame are obtained (system dependent)
        #self.frame_width = int(self.capture.get(3))
        #print(self.frame_width)
        #self.frame_height = int(self.capture.get(4))
        #print(self.frame_height)
        self.frame_width = 1024
        print(self.frame_width)
        self.frame_height = 1024
        print(self.frame_height) 
        # Set up codec and output video settings
        #self.codec = cv2.VideoWriter_fourcc('M','J','P','G')
        #self.output_video = cv2.VideoWriter(self.video_file_name, self.codec, 30, (self.frame_width, self.frame_height))

        # Start the thread to read frames from the video stream
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

        # Start another thread to show/save frames
        self.start_recording()
        print('initialized {}'.format(self.video_file))

    def update(self):
        # Read the next frame from the stream in a different thread
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()


    def show_frame(self):
        # Display frames in main program
        if self.status:
            cv2.namedWindow(self.frame_name,cv2.WINDOW_NORMAL)
            cv2.imshow(self.frame_name, self.frame)
            cv2.resizeWindow(self.frame_name, self.frame_width,self.frame_height)
            
        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            self.output_video.release()
            cv2.destroyAllWindows()
            exit(1)

    def show_processed_frame(self):
        # Display frames in main program
        if True:
            processed_frame, lines_img, _, _, _, distances = self.processing_function(self.frame)
            cv2.namedWindow("processed_frame",cv2.WINDOW_NORMAL)
            cv2.imshow("processed_frame", lines_img)
            cv2.resizeWindow("processed_frame", self.frame_width,self.frame_height)
            self.processed_objects = distances
            
    def save_frame(self):
        # Save obtained frame into video output file
        self.output_video.write(self.frame)

    def start_recording(self):
        # Create another thread to show/save frames
        def start_recording_thread():
            while True:
                try:
                    self.show_frame()
                    self.show_processed_frame()
                    #self.save_frame()
                except AttributeError:
                    pass
        self.recording_thread = Thread(target=start_recording_thread, args=())
        self.recording_thread.daemon = True
        self.recording_thread.start()

video_feed = VideoFeedHandler('Camera_1', 0, process_image)
test_video_only = False

if test_video_only:
    time.sleep(100)
    quit()

    
csvfile = open('measurementA.csv', 'w+')
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
