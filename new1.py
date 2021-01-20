import matplotlib.pyplot as plt
import pylab as plb
import numpy as np
import winsound
import ctypes
import time
import math
import sys
import cv2
import csv
import os
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import curve_fit
from numpy import asarray as ar,exp
from ctypes import windll, c_double
from datetime import datetime
from threading import Thread

frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second


def video():
    vc=cv2.VideoCapture(0)
    vc.set(3,1280)
    vc.set(4,1024)
    time.sleep(2)
    vc.set(15, -8.0)
    time.sleep(0.1)
    if vc.isOpened():
        status,img=vc.read()
    else:
        print("err in openning")
    status,img=vc.read()
    while status:
        status,img=vc.read()
        cv2.imshow("img",img)
        img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        img=cv2.Canny(img,25,50)
        #cv2.imshow("canny",img)
        cv2.waitKey(1)
#video()
def PixelCordToMicronCord(p):
    x = -p[0]*1.14547537228
    y = p[1]*1.14547537228
    converted = (x,y)
    return converted
	
xComPort=4
yComPort=3
zComPort=7

xPS = 1
yPS = 2
zPS = 3
nAxis=1
nPosF=5000
xDistance=5.0
yDistance=2.0
zDistance=5
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
	
mydll,xstage = setup_stage(mydll,xPS,xComPort,nPosF,0)
mydll,ystage = setup_stage(mydll,yPS,yComPort,nPosF,0)
mydll,zstage = setup_stage(mydll,zPS,zComPort,nPosF,0)
print( "State x= ", (xstage))
print( "State y= ", (ystage))
print( "State z= ", (zstage))
GetPositionEx=mydll.PS10_GetPositionEx
GetPositionEx.restype = ctypes.c_double
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
csvfile = open('data.csv', 'w+')    
writer = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
file1 = open("myfile.txt","w") 
#.........................
global_range=0
def camera():
    position = (50, 50) # org 
    fontScale = 1# fontScale 
    color = (0, 0, 255) # Blue color in BGR 
    thickness = 2# Line thickness of 2 px 
    if vc.isOpened():
        status,img_s=vc.read()
    else:
        print("err in openning")
        status,img_s=vc.read()
    text=" x: " + str('%.3f' % GetPositionEx(xPS, nAxis)) + " um  " + "   y: " + str('%.3f' % GetPositionEx(yPS, nAxis)) + " um  " + "   Z: " + str('%.3f' % GetPositionEx(zPS, nAxis)) + " um "  #+ str('%.2f' %((GetPositionEx(zPS, nAxis)-1.5)/1)*100) + " %"
    cv2.putText(img_s, text, position, 0, fontScale, color,2)#, thickness, cv2.LINE_AA) 
    cv2.imshow("reference",img_s)
    cv2.waitKey(1)
def gaus(x,amp,x0,sigma):
    return amp*exp(-(x-x0)**2/(2*sigma**2))
def moveX(xSteps):
    xReadOutStart=GetPositionEx(xPS, nAxis)
    xstage=mydll.PS10_MoveEx(xPS, nAxis, c_double(xSteps),1)
    xstate= mydll.PS10_GetMoveState(xPS, nAxis)
    while(xstate > 0):
        xstate = mydll.PS10_GetMoveState(xPS, nAxis)
        camera()
    xReadOutEnd=GetPositionEx(xPS, nAxis)
    print( "X motor state = ", xstate ," from %3.3f" %(xReadOutStart) , " to %3.3f"%( xReadOutEnd))			
def moveY(ySteps):
    yReadOutStart=GetPositionEx(yPS, nAxis)
    ystage=mydll.PS10_MoveEx(yPS, nAxis, c_double(ySteps),1)
    ystate= mydll.PS10_GetMoveState(yPS, nAxis)
    while(ystate > 0):
        ystate = mydll.PS10_GetMoveState(yPS, nAxis)
        camera()
    yReadOutEnd=GetPositionEx(yPS, nAxis)
    print( "Y motor state = ", ystate ," from %3.3f" %(yReadOutStart) , " to %3.3f"%( yReadOutEnd))	
def moveZ(zSteps):
    zReadOutStart=GetPositionEx(zPS, nAxis)
    zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(zSteps),1)
    zstate= mydll.PS10_GetMoveState(zPS, nAxis)
    while(zstate > 0):
        zstate = mydll.PS10_GetMoveState(zPS, nAxis)
        camera()
    zReadOutEnd=GetPositionEx(zPS, nAxis)
    return zReadOutStart #sharpness is calculated for start positin
    #print( "Z motor state = ", zstate ," from ", zReadOutStart , " to " , zReadOutEnd)		
def sharpness_calculation(s):
    sharpness=0
    numberOfAverage=1
    for i in range(numberOfAverage):
        if vc.isOpened():
            status,img_s=vc.read()
        else:
            print("err in openning")
        status,img_s=vc.read()
        #if s==330:

        img=cv2.cvtColor(img_s,cv2.COLOR_BGR2GRAY)
        img=cv2.Canny(img_s,20,120)
        #cv2.imshow("canny",img)
        SumOverPixels=img[0:img.shape[0],0:img.shape[1]]
        SumOverPixels=cv2.sumElems(SumOverPixels)
        sharpness=sharpness+SumOverPixels[0]
    sharpness=sharpness/numberOfAverage
    #font = cv2.FONT_HERSHEY_SIMPLEX # font 

    #posZ=" Z Position: " + str('%.3f' % GetPositionEx(zPS, nAxis)) + " um  " #+ str('%.2f' %((GetPositionEx(zPS, nAxis)-1.5)/1)*100) + " %"
    #cv2.putText(img_s, posZ, position, 0, fontScale, color,2)#, thickness, cv2.LINE_AA) 
    #cv2.imshow("reference",img_s)
    #cv2.waitKey(1)
    #camera()
    return sharpness
def fit(x,y):
    x=np.array(x)
    y=np.array(y)
    y=y/max(y)
    n = len(y)
    mean = x[np.argmax(y)]
    sigma = 65/1000.0
    def gaus(y,a,mean,sigma):
        return a*np.exp(-(y-mean)**2/(2*sigma**2))
    plt.plot(x,gaus(x,1,mean,sigma),'g',label='function')
    popt,pcov = curve_fit(gaus,x,y,p0 = [1.,mean, sigma])#<<<<<<
    correctedPosition=popt[1] #<<<<<<<<<<<<<
    #print("Result: ",popt," co: ",pcov)
    #print("Position: %3.3f Mean: %3.3f Diff: %3.3f " %(GetPositionEx(zPS, nAxis),mean ,mean-GetPositionEx(zPS, nAxis)))
    print("Position: %3.3f Mean: %3.3f Diff: %3.3f " %(GetPositionEx(zPS, nAxis),popt[1] ,popt[1]-GetPositionEx(zPS, nAxis)))
    plt.plot(x,y,'b',label='data')
    plt.plot(x,gaus(x,*popt),'r',label='fit')
    plt.legend()
    plt.title('Fig. 1 - Fit for sharpness')
    plt.xlabel('Z (um)')
    plt.ylabel('Sharpness')
    winsound.Beep(frequency, duration)
    plt.show()
    return correctedPosition
def Z_SCAN():
    zRange=1.5 # 1mm
    step=0.002   # 2um
    global_range=zRange
    moveZ(-zRange/2)
    data=[]
    z=[]
    for s in range(int(zRange/step)):
        sharpness=sharpness_calculation(s)
        data.append(sharpness)
        z.append(moveZ(step))
        writer.writerow([s,sharpness])
    moveZ(-zRange/2)
    print("Z Scan is finished")
    return fit(z,data)
def Z_Cal(norm,d):
    x=GetPositionEx(xPS, nAxis)
    y=GetPositionEx(yPS, nAxis)
    return (d-norm[0]*x-norm[1]*y)/norm[2]
def tilt():
    ref_points=[[0,0],[0,105],[140,0]]
    p=[]
    for pxy in ref_points:
        x,y=pxy
        moveX(x)
        moveY(y)
        p.append([GetPositionEx(xPS, nAxis),GetPositionEx(yPS, nAxis),Z_SCAN()])
    b = np.array(p[0])  
    a = np.array(p[1])  
    c = np.array(p[2])
    ab=b-a
    ac=c-a
    norm=np.cross(ab,ac)
    cte=norm[0]*b[0]+norm[1]*b[1]+norm[2]*b[2]
    print("--------------------------")
    print ("Point A: ", a)
    print ("Point B: ", b)
    print ("Point C: ", c)
    print ("Vector AB: ",ab)
    print ("Vector AC: ",ac)
    print("Norm vector: ", norm)		
    print("Plane const: ", cte)
    print("--------------------------")
    angleX=math.acos((norm[0]*1)/(math.sqrt((norm[0])**2+(norm[1])**2+(norm[2])**2)))
    angleY=math.acos((norm[1]*1)/(math.sqrt((norm[0])**2+(norm[1])**2+(norm[2])**2)))
    angleZ=math.acos((norm[2]*1)/(math.sqrt((norm[0])**2+(norm[1])**2+(norm[2])**2)))
    #print("angleX: ", angleX," angley: ", angleY," anglez: ", angleZ)
    
    dx,dy=ref_points[1]
     
    moveY(-dy)
    moveX(-dx)
    print("fit     x: %3.3f y: %3.3f z :%3.3f"%(GetPositionEx(xPS, nAxis),GetPositionEx(yPS, nAxis),Z_SCAN()))
    print("exp(cal) x: %3.3f y: %3.3f z :%3.3f"%(GetPositionEx(xPS, nAxis),GetPositionEx(yPS, nAxis),Z_Cal(norm,cte)))
    print("encoder     x: %3.3f y: %3.3f z :%3.3f"%(GetPositionEx(xPS, nAxis),GetPositionEx(yPS, nAxis),GetPositionEx(zPS, nAxis)))
    dx,dy=ref_points[2]
    moveY(-dy)
    moveX(-dx)
    return norm,cte

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~    
	
	
vc=cv2.VideoCapture(0)
vc.set(3,1280)
vc.set(4,1024)
time.sleep(2)
vc.set(15, -8.0)
time.sleep(0.1)
    ##glass Z (0,0,2.08)#########################
#moveZ(2.08)
#norm,d=tilt()
print("Tilt calculation is finished...")
winsound.Beep(frequency, duration)
    ##Corner of bridge (14.25,73.4,1.125)########
#moveX(14.25)
#moveY(73.4)
#moveZ(-1.015)
	#part A L-shape
#partA=[[0,0],
       #[0.5,-0.5],[0,-8.5],[0,-10.5],   
       #[6,0],[0,10.5],[0,8.5],
       
	   #[2.34,-1.75],
	   #[0,-4],
	   #[4.03,0],[0,4],
       
	   #[3.01,1.7],[0,-7.0],	#1
	   #[8.45,0],[0,7.0],	#2
	   #[8.45,0],[0,-7.0],	#3
	   #[8.45,0],[0,7.0],	#4
	   #[8.45,0],[0,-7.0],	#5
	   #[8.45,0],[0,7.0],	#6
	   #[8.45,0],[0,-7.0],	#7
	   #[8.45,0],[0,7.0],	#8
	   #[8.45,0],[0,-7.0],	#9
	   #[8.45,0],[0,7.0],	#10
	   #[8.45,0],[0,-7.0],	#11
	   #[8.0,0],[0,7.4],	#12
	   
	   #[2.92,-1.7],[0,-4],
	   #[4.03,0],[0,4],
	   
	   #[2.34,1.75],[0,-7.75],[0,-9.75],
       #[6.5,0],[0,9.75],[0,9.75],
	   
       #[-35.22,-3.75],[-18.00,0],[-17.5,0],[-16.5,0]
	   #]
partA=[
       [0.5,-0.5],[0,-7],[0,-7],[0,-1],[0,-1.5],
       [7,0],[0,1.5],[0,1],[0,7],[0,7],[-7.5,.5]
	   ]

partA_points_2D=np.array(partA)
partA_points_2D.shape
n=0
norm=np.cross(np.array([1,1,1])-np.array([2,-2,1]),np.array([3,1,3])-np.array([2,-2,1]))
cte=2*norm[0]-2*norm[1]+norm[2]
for xy_points in partA_points_2D:
    
    n=n+1
    x,y=xy_points
    moveX(x)
    moveY(y)
    z_fit=Z_SCAN()
    z_tilt=Z_Cal(norm,cte)
    print("N: %d X: %3.3f Y: %3.3f Z: %3.3f fromTilt: %3.3f"%(n,GetPositionEx(xPS, nAxis),GetPositionEx(yPS, nAxis),z_fit,z_tilt))
    L = [str(n),"\t",str(x), "\t",str(y),"\t",str('%3.3f' %(GetPositionEx(xPS, nAxis))), "\t",str('%3.3f' %(GetPositionEx(yPS, nAxis))),"\t",str('%3.3f' %(z_fit)),"\t",str('%3.3f' %(z_tilt)),"\n"]
    file1.writelines(L) 

winsound.Beep(2000, duration)
winsound.Beep(2200, duration)
winsound.Beep(2500, duration)
	
	


file1.close()
closingx=mydll.PS10_Disconnect(xPS)
closingy=mydll.PS10_Disconnect(yPS)
closingz=mydll.PS10_Disconnect(zPS)
