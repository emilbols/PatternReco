import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import RPi.GPIO as gpio
import time
from datetime import datetime
import os
import time
import sys


def move(steps,direction):
    gpio.output(23,gpio.LOW)#en
    if direction==-1:
        gpio.output(18,gpio.LOW)#dir
    if direction==1:
        gpio.output(18,gpio.HIGH)#dir
    for i in range(0,steps):
        gpio.output(17,gpio.LOW)
        time.sleep(0.01)
        gpio.output(17,gpio.HIGH)
        time.sleep(0.01)
    gpio.output(23,gpio.HIGH)
    gpio.output(23,gpio.HIGH)#dis


#################### main function for calculation sharpness 
def tp():
    sharpness=0
    for m in range(0,5):                                #average over 5 pictures
        starus,img=vc.read()                            #take a picture
        image=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)      #convert to gray
        image=cv2.Canny(image,min_canny,max_canny)      #Canny filter
        sum1=0
        sum1=image[0:image.shape[0],0:image.shape[1]]   # Maybe I used a mask previously ??? :hmmm
        sum1=cv2.sumElems(sum1)                         #Summation over all pixels of image
        sharpness=sharpness+sum1[0]                     
    sharpness=sharpness/5
    return sharpness
################################################




cv2.namedWindow("preview")
vc=cv2.VideoCapture(0)
time.sleep(0.1)
os.system('clear')

if vc.isOpened():
    status,img=vc.read()
else:
    print("err in openning")
distance=100 #um
st=1 #steps:min 1 um
offset=2
hnp=int(distance/st)
np=hnp*2
while status:
        status,img=vc.read()
        cv2.imshow("reference",img)
        if key==ord("s"):
            start=time.time()
            for b in range(0,20):
                for i in range(0,hnp):#1/2 next for
                    move(st*2,1)
                for i in range(0,np):
                    sharpness=tp()
                    move(st*2,-1)
                    #plot(i,j,sharpness)
                    finalData[j,i]=sharpness
                    #key=cv2.waitKey(1)
                    plt2(sharpness,0)
                    if i==np-1:
                        plt2(sharpness,1)
                for i in range(0,hnp):#1/2 next for
                    move(st*2,1)
                end=time.time()
                print("total time:", (end-start)/60)
                print("### write the output file name: (surface_date.txt) ###")
                file_name=fn + str(b)
                file=open(file_name,'w')
                for i in range(1,np-offset):
                    file.write("%d \t %d \n" % (i,finalData[0,i+offset]))
                file.close()
                print("##############################")
            
            
##################################################
#break
cv2.destroyWindow("preview")
vc.release()