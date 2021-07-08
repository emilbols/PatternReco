import matplotlib.pyplot as plt
import numpy as np
import ctypes
import time
import cv2
import os
from scipy.optimize import curve_fit
from numpy import asarray as ar,exp
from ctypes import windll, c_double

dll_name = "ps10.dll"
dllabspath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + dll_name
mydll = windll.LoadLibrary(dllabspath)
GetPositionEx=mydll.PS10_GetPositionEx
GetPositionEx.restype = ctypes.c_double

xPS = 1
yPS = 2
zPS = 3
nAxis=1


def gaus(x,amp,x0,sigma):
    return amp*exp(-(x-x0)**2/(2*sigma**2))

def sharpness_calculation(video_feed,s):
    sharpness=0
    numberOfAverage=1
    for i in range(numberOfAverage):
        if video_feed.frame is not None:
            img_s=video_feed.frame
        else:
            print("error in opening")
        img=cv2.cvtColor(img_s,cv2.COLOR_BGR2GRAY)
        med_val=np.median(img)
        lower=int(max(0 ,0.7*med_val))
        upper=int(min(255,1.3*med_val))
        out_dir = "test_pics"
        cv2.imwrite(out_dir+"/testbeforeCanny_"+str(s)+".png",img)
        img=cv2.Canny(img_s,lower,upper)
        SumOverPixels=img[0:img.shape[0],0:img.shape[1]]
        SumOverPixels=cv2.sumElems(SumOverPixels)
        sharpness=sharpness+SumOverPixels[0]
        cv2.imwrite(out_dir+"/test"+str(sharpness)+".png",img)
    sharpness=sharpness/numberOfAverage
    return sharpness

def z_fit(x,y):
    x=np.array(x)
    y=np.array(y)    
    print("ymax: ", max(y))
    print("y: ", y)
    y=y/max(y)
    print("y_norm: ", y)
    n = len(y)
    mean = x[np.argmax(y)]
    sigma = 65/1000.0
    def gaus(y,a,mean,sigma):
        return a*np.exp(-(y-mean)**2/(2*sigma**2))
    #plt.plot(x,gaus(x,1,mean,sigma),'g',label='function')
    try:
        popt,pcov = curve_fit(gaus,x,y,p0 = [1.,mean, sigma])#<<<<<<
    except RuntimeError:
        print("Error - curve_fit failed")
        correctedPosition = np.mean(x)
        return correctedPosition
    if popt[1] > 11.95: # no fit results larger 11.95 - range/2 allowed (maximum z height of stage is 12mm)
        correctedPosition=11.95-(np.mean(x)-np.min(x))
    else:
        correctedPosition=popt[1] #<<<<<<<<<<<<<
    print("Position: %3.3f Mean: %3.3f Diff: %3.3f " %(GetPositionEx(zPS, nAxis),popt[1] ,popt[1]-GetPositionEx(zPS, nAxis)))
    plt.plot(x,y,'b',label='data')
    plt.plot(x,gaus(x,*popt),'r',label='fit')
    plt.legend()
    plt.title('Fig. 1 - Fit for sharpness')
    plt.xlabel('Z (um)')
    plt.ylabel('Sharpness')
    #plt.show()
    out_dir = "test_pics"
    plt.savefig(out_dir+'/z_fit_mean_'+str(popt[1])+'.pdf')
    plt.clf()
    return correctedPosition

def z_move(zSteps):
    zReadOutStart=GetPositionEx(zPS, nAxis)
    zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(zSteps), 1)
    zstate= mydll.PS10_GetMoveState(zPS, nAxis)
    while(zstate > 0):
        zstate = mydll.PS10_GetMoveState(zPS, nAxis)
    zReadOutEnd=GetPositionEx(zPS, nAxis)
    print("zreadout start: ", zReadOutStart)
    print("zreadout end: ", zReadOutEnd)
    return zReadOutEnd #sharpness is calculated for start position

def z_scan(zRange,nsteps,video_feed):
    #zRange=0.2 # 0.2mm
    #step=0.002   # 2um
    data=[]
    z=[]
    zstart=GetPositionEx(zPS, nAxis)
    print("zstart: ", zstart)
    steps = np.linspace(-zRange/2.+zstart, zRange/2.+zstart, nsteps)
    print("steps array: ",steps)
    for s in steps:
        print("s: ", s)
        z.append(z_move(s))
        sharpness=sharpness_calculation(video_feed,s)
        data.append(sharpness)
    print("Z Scan is finished")
    print("z array: ", z)
    print("data: ", data)
    return z_fit(z,data)
