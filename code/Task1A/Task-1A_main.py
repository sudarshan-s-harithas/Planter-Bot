#classes and subclasses to import
import cv2
import numpy as np
import os

filename = 'result1A_2740.csv'
#################################################################################################
# DO NOT EDIT!!!
#################################################################################################
#subroutine to write results to a csv
def writecsv(color,shape,(cx,cy)):
    global filename
    #open csv file in append mode
    filep = open(filename,'a')
    # create string data to write per image
    datastr = "," + color + "-" + shape + "-" + str(cx) + "-" + str(cy)
    #write to csv
    filep.write(datastr)
    filep.close()

def main(path):
#####################################################################################################
    #Write your code here!!!
#####################################################################################################
 def getn(z):
     return int(''.join(ele for ele in z if ele.isdigit()))
    
 def detect(c):
         shape='unidentified'
         peri=cv2.arcLength(c,True)
         approx=cv2.approxPolyDP(c,0.04*peri,True)
         if len(approx)==3:
             shape="triangle"
         elif len(approx)==4:
             (x, y, w, h)=cv2.boundingRect(approx)
             ar=w/float(h)
             if ar>0.95 and ar<1.05:
                 shape="Square"
             else:
                 shape="Rectangle"
         elif len(approx)==5:
             shape="Pentagon"
         elif len(approx)==6:
             shape="Hexagon"
         else:
             shape="Circle"
         return shape
        
 def detectcol(c):
         px=img[cy,cx]
         if px[0]==255:
             color="Blue"
         elif px[2]==255:
             color="Red"
         else:
             color="Green"
         return color
        
 img=cv2.imread(path,1)
 imgrey=cv2.cvtColor(img,cv2.COLOR_BGRA2GRAY)
 ret,thresh=cv2.threshold(imgrey,127,255,0)
 image, contours, hierarchy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
 cnt=contours[0]
 itercontours=iter(contours)
 next(itercontours)
 for c in itercontours:
    M=cv2.moments(c)
    cx=int(M["m10"]/M["m00"])
    cy=int(M["m01"]/M["m00"])
    centroid=(cx,cy)
    shape=detect(c)
    color=detectcol(c)
    if shape=="Rectangle":
        r=cv2.matchShapes(cnt,c,1,0.0)
        if r<0.1:
            shape="Rhombus"
        else:
            shape="Trapezium"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img,shape,(cx-30,cy), font, .6,(0,0,0),1,cv2.LINE_AA)
    cv2.putText(img,color,(cx-30,cy+20), font, .6,(0,0,0),1,cv2.LINE_AA)
    cv2.putText(img,str(centroid),(cx-30,cy+40), font, .6,(0,0,0),1,cv2.LINE_AA)
    writecsv(color,shape,(cx,cy))
    data=str(color)+str(shape)+str(cx)+str(cy)
 count = getn(path)
 cv2.imwrite('test%doutput.png'%count,img)
 return data;
 

#################################################################################################
# DO NOT EDIT!!!
#################################################################################################
#main where the path is set for the directory containing the test images
if __name__ == "__main__":
    mypath='.'
    #getting all files in the directory
    onlyfiles = [os.path.join(mypath, f) for f in os.listdir(mypath) if f.endswith(".png")]
    #iterate over each file in the directory
    for fp in onlyfiles:
        #Open the csv to write in append mode
        filep = open('result1A_2740.csv','a')
        #this csv will later be used to save processed data, thus write the file name of the image 
        filep.write(fp)
        #close the file so that it can be reopened again later
        filep.close()
        #print fp
        #process the image
        data = main(fp)
        #open the csv
        filep = open('result1A_2740.csv','a')
        #make a newline entry so that the next image data is written on a newline
        filep.write('\n')
        #close the file
        filep.close()
