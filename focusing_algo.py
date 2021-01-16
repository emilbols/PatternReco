import matplotlib.pyplot as plt
import numpy as np
import ctypes
import time
import cv2
from scipy.optimize import curve_fit
from numpy import asarray as ar,exp
from ctypes import windll, c_double



def gaus(x,amp,x0,sigma):
    return amp*exp(-(x-x0)**2/(2*sigma**2))

def sharpness_calculation(s):
    sharpness=0
    numberOfAverage=1
    for i in range(numberOfAverage):
        if vc.isOpened():
            status,img_s=vc.read()
        else:
            print("error in opening")
        status,img_s=vc.read()
        img=cv2.cvtColor(img_s,cv2.COLOR_BGR2GRAY)
        img=cv2.Canny(img_s,20,120)
        SumOverPixels=img[0:img.shape[0],0:img.shape[1]]
        SumOverPixels=cv2.sumElems(SumOverPixels)
        sharpness=sharpness+SumOverPixels[0]
    sharpness=sharpness/numberOfAverage
    return sharpness

def z_fit(x,y):
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
    print("Position: %3.3f Mean: %3.3f Diff: %3.3f " %(GetPositionEx(zPS, nAxis),popt[1] ,popt[1]-GetPositionEx(zPS, nAxis)))
    plt.plot(x,y,'b',label='data')
    plt.plot(x,gaus(x,*popt),'r',label='fit')
    plt.legend()
    plt.title('Fig. 1 - Fit for sharpness')
    plt.xlabel('Z (um)')
    plt.ylabel('Sharpness')
    #plt.show()
    plt.savefig('z_fit_mean_'+str(popt[1])+'.pdf')
    return correctedPosition

def z_move(zSteps):
    zReadOutStart=GetPositionEx(zPS, nAxis)
    zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(zSteps),1)
    zstate= mydll.PS10_GetMoveState(zPS, nAxis)
    while(zstate > 0):
        zstate = mydll.PS10_GetMoveState(zPS, nAxis)
    zReadOutEnd=GetPositionEx(zPS, nAxis)
    return zReadOutStart #sharpness is calculated for start position

def z_scan(zRange,step):
    #zRange=0.2 # 0.2mm
    #step=0.002   # 2um
    global_range=zRange
    z_move(-zRange/2)
    data=[]
    z=[]
    for s in range(int(zRange/step)):
        sharpness=sharpness_calculation(s)
        data.append(sharpness)
        z.append(moveZ(step))
    z_move(-zRange/2)
    print("Z Scan is finished")
    return z_fit(z,data)
