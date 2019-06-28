####e-Yantra Robotics Competition 2017####
###########Theme - Planter Bot############
#########Author - Sudarshan ###########
##########File Name - determine_contours_centroid############
#add the imports
import cv2
import os
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import time

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
#save the output video in avi format for a specific resolution with the name PB#1234 where 1234 is your TeamId 
out = cv2.VideoWriter('PB#1234.avi',fourcc, 5, (640,480))
#initialize a PiCam object
cam = PiCamera()
#set the resolution of the video to be captured
cam.resolution = (640,480)
#set the framerate
cam.framerate = 5
#create a RGB Array of PiCam storage type
raw_cap = PiRGBArray(cam,(640,480))
#initialize the frame count
frame_cnt = 0
#to capture video coninuously create a video object
for frame in cam.capture_continuous(raw_cap,format="bgr",use_video_port=True,splitter_port=2,resize=(640,480)):
#add some sleep to warm up PiCam
#time.sleep(1.0)
#print "done warming up"
#capture continuously
#while(True):
    #grab a frame
    #image = frame.next()
    #extract opencv bgr array of color frame
    color_image = frame.array
    # write the frame to avi file
    out.write(color_image) 
    #display color frame
    cv2.imshow("Video",color_image)
    #wait or hold frame for 1 millisecond
    cv2.waitKey(1)
    #clear the data of the previous frame
    raw_cap.truncate(0)
    #raw_cap.seek(0)
    #increment the frame count

    ## determine contours in the image
    
    img = cv.imread('color_image',0)
    ret,thresh = cv.threshold(img,127,255,0)
    im2,contours,hierarchy = cv.findContours(thresh, 1, 2)
    cnt = contours[0]
    M = cv.moments(cnt)
    print( M )

    ##  determine centroid of the contours

    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    
print "Ending...."
out.release()
cv2.destroyAllWindows()
