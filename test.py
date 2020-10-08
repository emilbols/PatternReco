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
from edge_finder import edge_find, rho_theta_to_xy, select_lines,average_over_nearby_lines,distance_between_lines, corner_find

class VideoWriterWidget(object):
    def __init__(self, video_file_name, src=0):
        # Create a VideoCapture object
        self.frame = 0
        self.frame_name = 'cam_output'+str(src)
        self.video_file = video_file_name
        self.video_file_name = video_file_name + '.avi'
        self.capture = cv2.VideoCapture(src,cv2.CAP_V4L )
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH,2560)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT,2560)
		self.capture.set(cv2.CAP_PROP_FPS,25)

        # Default resolutions of the frame are obtained (system dependent)
        self.frame_width = int(self.capture.get(3))
        self.frame_height = int(self.capture.get(4))

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
            cv2.imshow(self.frame_name, self.frame)

        # Press Q on keyboard to stop recording
        key = cv2.waitKey(1)
        if key == ord('q'):
            self.capture.release()
            self.output_video.release()
            cv2.destroyAllWindows()
            exit(1)

    def save_frame(self):
        # Save obtained frame into video output file
        self.output_video.write(self.frame)

    def start_recording(self):
        # Create another thread to show/save frames
        def start_recording_thread():
            while True:
                try:
                    self.show_frame()
                    #self.save_frame()
                except AttributeError:
                    pass
        self.recording_thread = Thread(target=start_recording_thread, args=())
        self.recording_thread.daemon = True
        self.recording_thread.start()

video_feed = VideoWriterWidget('Camera_1', 0)

xComPort=5
yComPort=7
zComPort=4
xPS = 1
yPS = 2
zPS = 3
nAxis=1
nPosF=10000
xDistance=0.0
yDistance=0.0
zDistance=0.0
nExport=0
z_value=0.0


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

GetPositionEx=my_dll.PS10_GetPositionEx
GetPositionEx.restype = ctypes.c_double
   

#in case this setup_stage functions works as intented we can remove this.
"""
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
zstage=mydll.PS10_SetTargetMode(zPS, nAxis, 1)
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
zstage=mydll.PS10_SetTargetMode(zPS, nAxis, 0)
print("setting z-axis to relative positioning mode")
time.sleep(2)


#out.write(frame)
#should be read by the stage
                                              

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

time.sleep(5)

ystage=mydll.PS10_MoveEx(yPS, nAxis, c_double(yDistance), 1)
ystate = mydll.PS10_GetMoveState(yPS, nAxis)

while(ystate > 0):
  
    #should be read by the stage
    yreadout=PS10_GetPositionEx(yPS, nAxis)
    print( "Position=%.3f" %(yreadout) )
    # reads frames from a camera
    ystate = mydll.PS10_GetMoveState(yPS, nAxis) 


    
time.sleep(5)

xstage=mydll.PS10_MoveEx(xPS, nAxis, c_double(-xDistance), 1)
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

time.sleep(5)

ystage=mydll.PS10_MoveEx(yPS, nAxis, c_double(-yDistance), 1)
ystate = mydll.PS10_GetMoveState(yPS, nAxis)

while(ystate > 0):
  
    #should be read by the stage
    yreadout=PS10_GetPositionEx(yPS, nAxis)
    print( "Position=%.3f" %(yreadout) )
    # reads frames from a camera
    ystate = mydll.PS10_GetMoveState(yPS, nAxis) 


    
time.sleep(5)

zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(zDistance), 1)
zstate = mydll.PS10_GetMoveState(zPS, nAxis)

while(zstate > 0):
  
    #should be read by the stage
    zreadout=PS10_GetPositionEx(zPS, nAxis)
    print( "Position=%.3f" %(zreadout) )
    # reads frames from a camera
    zstate = mydll.PS10_GetMoveState(zPS, nAxis)




# close interface

closingx=mydll.PS10_Disconnect(xPS)
closingy=mydll.PS10_Disconnect(yPS)
closingz=mydll.PS10_Disconnect(zPS)
