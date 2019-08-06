from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
import time
import cv2
import numpy as np

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#Setting up PiCam

camera =PiCamera()                            #picam object
rowsp=160                                     #defining rows for the input frame,frame size is reduced for increased frame rate
colsp=128                                     #column for the frames
camera.resolution=(640,480)
camera.framerate=30
rawCapture=PiRGBArray(camera,size=(160,128))  #low resolution for line following to increase frame rate
still=PiRGBArray(camera,size=(640,480))       #high resolution  for shape detection
print "initiating"
time.sleep(0.1)
rawCapture.truncate(0)
still.truncate(0)

font = cv2.FONT_HERSHEY_SIMPLEX                

 
GREEN = 22              #GREEN PIN RGB LED
RED = 21                #RED PIN OF RGB LED
BLUE= 25                #BLUE PIN OF RGB LED
GPIO.setup(RED,GPIO.OUT) 
GPIO.setup(GREEN,GPIO.OUT)
GPIO.setup(BLUE,GPIO.OUT)


# Motor setup

Motor1A = 32
Motor1B = 35
Motor1E = 37
Motor2A = 36
Motor2B = 38
Motor2E = 40

GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)
GPIO.setup(Motor1E,GPIO.OUT)
GPIO.setup(Motor2A,GPIO.OUT)
GPIO.setup(Motor2B,GPIO.OUT)
GPIO.setup(Motor2E,GPIO.OUT)

left = GPIO.PWM(Motor1E, 100)
right = GPIO.PWM(Motor2E, 100)


img0 = cv2.imread('Plantation.png')
cv2.imshow("overlay",img0)




def forward(speed):
    left.start(25)
    right.start(25)
 
    print "forward"
    GPIO.output(Motor1A,GPIO.LOW) #RIGHT MOTOR forward
    GPIO.output(Motor1B,GPIO.HIGH)
    left.ChangeDutyCycle(speed)
    GPIO.output(Motor2A,GPIO.HIGH) #LEFT MOTOR FORWARD
    GPIO.output(Motor2B,GPIO.LOW)
    right.ChangeDutyCycle(speed)


def turn_left(cx):
    l=(cx*100/(rowsp/2))             #calculating the duty cycle from the centroid
    left.start(25)
    right.start(25)
    print "Turning left"
    GPIO.output(Motor1A,GPIO.LOW) #RIGHT MOTOR FULL PWM FORWARD
    GPIO.output(Motor1B,GPIO.HIGH)
    left.ChangeDutyCycle(100)     
    GPIO.output(Motor2A,GPIO.HIGH)  #LEFT MOTOR PROPORTIONAL PWM FORWARD
    GPIO.output(Motor2B,GPIO.LOW)
    right.ChangeDutyCycle(abs(l))



def turn_softleft(cx):
    l=(cx*100/(rowsp/2))                #calculating the duty cycle from the centroid
    left.start(25)
    right.start(0)
    print "Turning soft left"
    GPIO.output(Motor1A,GPIO.LOW)          #RIGHT MOTOR PROPORTIONAL PWM FORWARD
    GPIO.output(Motor1B,GPIO.HIGH)
    left.ChangeDutyCycle(abs(l))
    GPIO.output(Motor2A,GPIO.HIGH)         #LEFT MOTOR STOP
    GPIO.output(Motor2B,GPIO.LOW)
    right.ChangeDutyCycle(0)


def turn_simpleleft(speed):
    
    left.start(25)
    right.start(25)
    print "Turning simple left"  #moving both the motors in opposite direction
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.HIGH)
    left.ChangeDutyCycle(speed)
    GPIO.output(Motor2A,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.HIGH)
    right.ChangeDutyCycle(speed)




    
def turn_softright(cx):
    r=((rowsp-cx)*100/(rowsp/2))          #calculating the duty cycle from the centroid
    left.start(0)
    right.start(25)
    print "turning soft right"
    GPIO.output(Motor1A,GPIO.LOW)      #RIGHT MOTOR STOP
    GPIO.output(Motor1B,GPIO.HIGH)
    left.ChangeDutyCycle(0)
    GPIO.output(Motor2A,GPIO.HIGH)     #LEFT MOTOR PROPORTIONAL PWM FORWARD
    GPIO.output(Motor2B,GPIO.LOW)
    right.ChangeDutyCycle(abs(r))



    
def turn_right(cx):
    r=((rowsp-cx)*100/(rowsp/2))
    left.start(25)
    right.start(25)
 
    print "Turning right"
    GPIO.output(Motor1A,GPIO.LOW)           #RIGHT MOTOR PROPORTIONAL PWM FORWARD
    GPIO.output(Motor1B,GPIO.HIGH)
    left.ChangeDutyCycle(abs(r))
    GPIO.output(Motor2A,GPIO.HIGH)          #LEFT MOTOR FULL PWM FORWARD
    GPIO.output(Motor2B,GPIO.LOW)
    right.ChangeDutyCycle(100)
 


def stop():
    left.stop()                #BOTH MOTORS STOP
    right.stop()
    print "Stopping motor"
    GPIO.output(Motor1E,GPIO.LOW)
    GPIO.output(Motor2E,GPIO.LOW)



def apply_smoothing(image,kernel_size=69):
    return cv2.GaussianBlur(image,(kernel_size,kernel_size),0)        #GAUSIAN BLURRING TO REMOVE GRID LINES 


def filter_region(image, vertices):
    mask = np.zeros_like(image)                                #REGION OF INTREST FOR CONTOUR DETECTION
    if len(mask.shape)==2:
        cv2.fillPoly(mask, vertices, 255)
    else:
        cv2.fillPoly(mask, vertices, (255,)*mask.shape[2])        
    return cv2.bitwise_and(image, mask)



    
def select_region(image,image1):                       #REGION1 FOR FIRST CONTOUR DETECTION
    rows, cols = image.shape[:2]
    bottom_left  = [cols*0.01, rows*1]
    top_left     = [cols*0.01, rows*0.9]
    bottom_right = [cols*0.99, rows*1]
    top_right    = [cols*0.99, rows*0.9] 
    vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
    cv2.polylines(image1,[vertices],True,(0,255,255))
    return filter_region(image, vertices)
def select_region2(image,image1):                     #REGION2 FOR SECOND CONTOUR
    rows,cols = image.shape[:2]
    bottom_left  = [cols*0.01,rows*0.9]
    top_left     = [cols*0.01,rows*0.8]
    bottom_right = [cols*0.99,rows*0.9]
    top_right    = [cols*0.99,rows*0.8]
    vertices = np.array([[bottom_left, top_left, top_right, bottom_right]], dtype=np.int32)
    cv2.polylines(image1,[vertices],True,(0,255,255))
    return filter_region(image,vertices)
def select_region3(image,image1):
    rows,cols =image.shape[:2]                         #REGION 3 FOR THIRD CONTOUR
    bottom_left    = [cols*0.01,rows*0.8]
    top_left       = [cols*0.01,rows*0.7]
    bottom_right   = [cols*0.99,rows*0.8]
    top_right      = [cols*0.99,rows*0.7]
    vertices = np.array([[bottom_left,top_left,top_right,bottom_right]],dtype=np.int32)
    cv2.polylines(image1,[vertices],True,(0,255,255))
    return filter_region(image,vertices)



def select_regionIP1(image,image1):
    rows,cols =image.shape[:2]
    bottom_left    = [cols*0.2,rows*1]           #DECRESING THE AREA OF SIGHT SO THAT IT SEES 0NLY THE WHITE LINE BETWEEN TWO BLACK PATCHES
    top_left       = [cols*0.2,rows*0.9]         
    bottom_right   = [cols*0.8,rows*1]
    top_right      = [cols*0.8,rows*0.9]
    vertices = np.array([[bottom_left,top_left,top_right,bottom_right]],dtype=np.int32)
    cv2.polylines(image1,[vertices],True,(0,255,255))
    return filter_region(image,vertices)
def select_regionIP2(image,image1):
    rows,cols =image.shape[:2]
    bottom_left    = [cols*0.2,rows*0.9]
    top_left       = [cols*0.2,rows*0.8]
    bottom_right   = [cols*0.8,rows*0.9]
    top_right      = [cols*0.8,rows*0.8]
    vertices = np.array([[bottom_left,top_left,top_right,bottom_right]],dtype=np.int32)
    cv2.polylines(image1,[vertices],True,(0,255,255))
    return filter_region(image,vertices)
def select_regionIP3(image,image1):
    rows,cols =image.shape[:2]
    bottom_left    = [cols*0.2,rows*0.8]
    top_left       = [cols*0.2,rows*0.7]
    bottom_right   = [cols*0.8,rows*0.8]
    top_right      = [cols*0.8,rows*0.7]
    vertices = np.array([[bottom_left,top_left,top_right,bottom_right]],dtype=np.int32)
    cv2.polylines(image1,[vertices],True,(0,255,255))
    return filter_region(image,vertices)



  
def get_contour(image):
        ret,contours,heirarchy = cv2.findContours(image,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)          #contour detection 
        return contours


def get_centroid(contours):
        for s in contours:
            M = cv2.moments(s)                     #centroid calculation using moments
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx=50
                cy=64
        return cx,cy


def draw_output(image,contour,cx,cy):
        cv2.drawContours(image,contour,-1,(0,255,0),2)                #drawing detected contour
        cv2.circle(image,(cx,cy),7,(255,255,255),-1)                  #drawing centroid
        cv2.line(image,((rowsp/2),(colsp/2)),((rowsp/2),((colsp/2)+30)),(0,0,255),4)   #frame center



def compute_pwm(cx,image,d1,d2,c):
        if(cx<(rowsp/2)):
            #cv2.putText(image,"LEFT",(((colsp/2)-30),50),font,2,(0,0,255),1)
            #turn_left(cx)
            time.sleep((abs((rowsp/2)-cx))*d1)    #d1=0.0003
            if(cx>((rowsp/2)-10)):
                forward(100)                          #if deviation is unnoticible neglible move forward
                time.sleep(d2/(abs((rowsp/2)-cx)))
            elif(cx<=((rowsp/2)-10)):                 #if devition is too much move left
                turn_softleft(cx)
                time.sleep((abs((rowsp/2)-cx))*d1)
                if(cx<=((rowsp/2)-35)):                  #if devition is very large ex:90 turns.move both the motors in opposite directions
                    time.sleep((abs((rowsp/2)-cx))*d1)
                    time.sleep((abs((rowsp/2)-cx))*d1)
                    time.sleep((abs((rowsp/2)-cx))*d1)
        elif(cx>(rowsp/2)):
            #cv2.putText(image,"RIGHT",((colsp/2)-30,50),font,2,(0,0,255),1)
            #turn_right(cx)
            time.sleep((abs((rowsp/2)-cx))*d1)
            if(cx<((rowsp/2)+10)):
                 forward(100)
                 time.sleep(d2/(abs((rowsp/2)-cx)))
            elif(cx>=((rowsp/2)+10)):
                turn_softright(cx)
                time.sleep((abs((rowsp/2)-cx))*d1)
                if(cx>=((rowsp/2)+35)):
                     time.sleep((abs((rowsp/2)-cx))*d1)
                     time.sleep((abs((rowsp/2)-cx))*d1)
        elif(cx==rowsp/2 and c==1):
            #cv2.putText(image,"CENTRE",(((colsp/2)-30),50),font,2,(0,0,255),1)
            forward(100)
            time.sleep(0.001)


def back_end(image):
    
    inimg1=image
    inimg = cv2.blur(inimg1, (5,5))
    hsv = cv2.cvtColor(inimg, cv2.COLOR_BGR2HSV)

    lowerred = np.array([0, 70, 70], dtype=np.uint8)          #hsv range for red
    upperred = np.array([20, 255, 255], dtype=np.uint8)
    lowerblue = np.array([98, 50, 50], dtype=np.uint8)        #hsv range for blue
    upperblue = np.array([170, 255, 255], dtype=np.uint8)
    lowergreen = np.array([75, 50, 50], dtype=np.uint8)       #hsv range for green
    uppergreen = np.array([90, 255, 170], dtype=np.uint8)



    p=0               #color maping 0 for green ,1 for red and 2 for blue
    d=[]
    
    shape= "no_CM"     #initial values
    contclr= "no_CM"


    while(p<3):

        if(p==0):

            color="green"
            lower=lowergreen
            upper=uppergreen
        elif (p==1):
            color="red"
            lower=lowerred
            upper=upperred
        elif (p==2):
            color="blue"
            lower=lowerblue
            upper=upperblue
        
        threshin = cv2.inRange(hsv, lower, upper)
        #noise removal
        median = cv2.medianBlur(threshin,5)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
        dilated = cv2.dilate(median, kernel)
        blur3 = cv2.bilateralFilter(dilated,9,75,75)
        median3 = cv2.medianBlur(blur3,5)
        incont, contours, hierarchy = cv2.findContours(median3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        if (len(contours)>=1):

            print len(contours)
            cv2.drawContours(inimg1, contours, -1, (0,255,0), 3)
            perimeter = cv2.arcLength(contours[0],True)
            print "p=", perimeter
            if (perimeter>=190):            #classifying shapes based on perimeter
                  shape= "square"
                  #print "square"

            elif(perimeter>=160 and perimeter<190):
                  #print "circle"                   
                  shape="circle"
            elif(perimeter<160 and perimeter >120):
                  #print "triangle"
                  shape="triangle"
            contclr = color
            break
        p=p+1

    
    return shape,contclr,len(contours)


def detect_shape():
    tri=0              #to count the number of votes each shape for accuracy
    cir=0
    squ=0
    gr=0               #to count the number of votes each color gets to obtain accurate results
    bl=0
    re=0
    cont1=0            #to count the number of votes each number gets to obtain accurate results
    cont2=0
    cont3=0
    cont4=0
    #initial values
    shp="no_cm"
    clr="no_cm"
    num_cont=0
    frame_cnt=0
    blink=0
    i=0
   
    for frameo in camera.capture_continuous(still,format='bgr',use_video_port=True,splitter_port=3,resize=(640,480)):
        frame =frameo.array
       
        frame_cnt = frame_cnt+1


        if(frame_cnt>7):
             break                        
        if (frame_cnt>4):                 #skipping frames to let the camera stabilize
             shape,contclr,no_of_contour=back_end(frame)
             if(no_of_contour==0):
                 break
             if(shape=="triangle"):
                 tri=tri+1               #incrementing votes for the shape
             elif(shape=="circle"):
                 cir=cir+1
             elif(shape=="square"):
                 squ=squ+1
             if(contclr=="green"):
                 gr=gr+1                #incrementing votes for color
             elif(contclr=="blue"):
                 bl=bl+1
             elif(contclr=="red"):
                 re+re+1
             if(no_of_contour==1):
                 cont1=(cont1)+1        #incrementing votes for number of contours
             elif(no_of_contour==2):
                 cont2=(cont2)+1
             elif(no_of_contour==3):
                 cont3=(cont3)+1
             elif(no_of_contour==4):
                 cont4=(cont4)+1

            
        still.truncate(0)
    #comparing votes    
    if(tri>cir and tri>squ):
          print "triangle"
          shp="triangle"
    elif(cir>tri and cir>squ):
          print "circle"
          shp="circle"
    else:
          print "square"
          shp="square"
    
    if(gr>bl and gr>re):
          print  "green"
          clr="green"
          blink=GREEN
    elif(bl>gr and bl>re):
          print "blue"
          clr="blue"
          blink=BLUE
    else:
          print "red"
          clr="red"
          blink=RED
    if(cont1>cont2 and cont1>cont3 and cont1>cont4):
          print "1"
          num_cont=1
    elif(cont2>cont1 and cont2>cont3 and cont2>cont4):
          print "2"
          num_cont=2
    elif(cont3>cont1 and cont3>cont2 and cont3>cont4):
          print "3"
          num_cont=3
    elif(cont4>cont1 and cont4>cont3 and cont4>cont2):
          print "4"
          num_cont=4

#blinking the RGB led at the zone indicator after shape detection
    i=0
    for i in range (0,num_cont):

         GPIO.output(blink,GPIO.LOW)
         time.sleep(0.6)
         GPIO.output(blink,GPIO.HIGH)
         time.sleep(0.6)
    camera.stop_preview
    return shp,clr,num_cont
    
    


def make_overlay(image,shp,clr,no_cont,z):
    img1 = image
    #img1 = cv2.imread('Plantation.png')
    F1 = 'poinsettia.png' #TR
    F2 = 'lilac.png' #TB
    F3 = 'marigold.png' #TG
    F4 = 'rosesred.png' #SR
    F5 = 'orchid.png' #SB
    F6 = 'hibiscusyellow.png' #SG
    F7 = 'gerber.png'  #CR
    F8 = 'tulipblue.png' #CB
    F9 = 'lily.png' #CG

    shape =shp
    colour=clr
    zone=z
    white=0
    if(shape=="triangle"):
        if(colour=="red"):
            pz1 = cv2.imread(F1)#TR
            h, w, ch = pz1.shape
            img2 = cv2.resize(pz1,(30, 30), interpolation = cv2.INTER_CUBIC)
        elif(colour=="blue"):
             pz2 = cv2.imread(F2)#TB
             h, w, ch = pz2.shape
             img2 = cv2.resize(pz2,(30, 30), interpolation = cv2.INTER_CUBIC)
        elif(colour=="green"):
             pz3 = cv2.imread(F3)#TG
             h, w, ch = pz3.shape
             img2 = cv2.resize(pz3,(30, 30), interpolation = cv2.INTER_CUBIC)

    elif(shape=="square"):
        if(colour=="red"):
            pz4 = cv2.imread(F4)#SR
            h, w, ch = pz4.shape
            img2 = cv2.resize(pz4,(30, 30), interpolation = cv2.INTER_CUBIC)
            
        elif(colour=="blue"):
             pz5 = cv2.imread(F5)#SB
             h, w, ch = pz5.shape
             img2 = cv2.resize(pz5,(30, 30), interpolation = cv2.INTER_CUBIC)
             white=1
        elif(colour=="green"):
             pz6 = cv2.imread(F6)#SG
             h, w, ch = pz6.shape
             img2 = cv2.resize(pz6,(30, 30), interpolation = cv2.INTER_CUBIC)

    elif(shape=="circle"):
        if(colour=="red"):
            pz7 = cv2.imread(F7)#CR
            h, w, ch = pz7.shape
            img2 = cv2.resize(pz7,(30, 30), interpolation = cv2.INTER_CUBIC)
            white=1
        elif(colour=="blue"):
             pz8 = cv2.imread(F8)#CB
             h, w, ch = pz8.shape
             img2 = cv2.resize(pz8,(30, 30), interpolation = cv2.INTER_CUBIC)
             white=1
        elif(colour=="green"):
             pz9 = cv2.imread(F9)#CG
             h, w, ch = pz9.shape
             img2 = cv2.resize(pz9,(30, 30), interpolation = cv2.INTER_CUBIC)

    rows,cols,channels = img2.shape
    print rows,cols
    ###############____________REGIONS_______________#######################
    val=0
    if(zone=="region1"):
        r=250
        r1=0                
        i=340
        j=0
    elif(zone=="region2"):
        val=1
        r=235
        r1=200
        i=70
        j=120
    elif(zone=="region3"):
        r=180
        r1=152
        i=230
        j=300
        val=1
    elif(zone=="region4"):
        r=185
        r1=0
        i=470
        j=0
    else:
        r=0
        r1=0
        i=0
        j=0
        print "no region"
    # print zone
    ###########______________NUMBER______________#############
    #num=input("num: ")
    num=no_cont
    if (val==0):

        if(num==4):
            a=200
            b=0
        elif (num==3):
            a=150
            b=0
        elif (num==2):
            a=100
            b=0
        elif (num==1):
            a=50
            b=0
        else:
            a=-10
            b=-10
            print "no flower"
    elif (val==1):
        if(num==4):
            a=100
            b=100
        elif (num==3):
            a=100
            b=50
        elif (num==2):
            a=100
            b=0
        elif (num==1):
            a=50
            b=0
        else:
            a=-10
            b=-10
            print "no flower"
    print num
    ######################################################################
    for a in range(0,a,50):
        a=a+i
        print a
        roi1 = img1[r:r+rows, a:a+cols]
        img2gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
        if(white==0):
            ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            img1_bg1 = cv2.bitwise_and(roi1,roi1,mask = mask_inv)
            img2_fg = cv2.bitwise_and(img2,img2,mask = mask)
        elif(white==1):        # inverting the background of the seedlings if it has black background
            ret, mask = cv2.threshold(img2gray, 185, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            img1_bg1 = cv2.bitwise_and(roi1,roi1,mask = mask)
            img2_fg = cv2.bitwise_and(img2,img2,mask = mask_inv)

        dst1 = cv2.add(img1_bg1,img2_fg)
        img1[r:r+rows, a:a+cols ] = dst1

    for b in range(0,b,50):
        b=b+j
        print b
        roi1 = img1[r1:r1+rows, b:b+cols]
        img2gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
        if(white==0):
            ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            img1_bg1 = cv2.bitwise_and(roi1,roi1,mask = mask_inv)
            img2_fg = cv2.bitwise_and(img2,img2,mask = mask)
        elif(white==1):
            ret, mask = cv2.threshold(img2gray, 185, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            img1_bg1 = cv2.bitwise_and(roi1,roi1,mask = mask)
            img2_fg = cv2.bitwise_and(img2,img2,mask = mask_inv)

        dst1 = cv2.add(img1_bg1,img2_fg)
        img1[r1:r1+rows, b:b+cols ] = dst1

    
    return img1


def blink_end(color,number):
        if(color=="red"):
            blink=RED
        elif(color=="green"):
            blink=GREEN
        elif(color=="blue"):
            blink=BLUE
        for i in range (0,number):

           GPIO.output(blink,GPIO.LOW)
           time.sleep(1)
           GPIO.output(blink,GPIO.HIGH)
           time.sleep(1)



def main():
        frame_count = 0       #to skip few frames
        zone_count =0         #to know the zone to overlay the seedling images
        speed=50              #speed of the bot
        skip=12               #how many frames to skip
        count=0               #to knw the start of inverted plane
        count2=0              #to know the end of inverted plane
	for frameo in camera.capture_continuous(rawCapture,format='bgr',use_video_port=True,splitter_port=2,resize=(160,128)):
		frame=frameo.array    #fetching the frame

		
		gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                blur=apply_smoothing(gray)
                
                ret,th1 = cv2.threshold(blur,5,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)#using threshold to get a binary image
                ret1,th2 = cv2.threshold(th1,127,255,cv2.THRESH_BINARY_INV)# invert the pixels of the image 
                frame_count=frame_count+1                                
                
                if(frame_count<10):                                #skipping few frames as soon as the bot has been turned on to allow the camera to heat up and stabilize
                      rawCapture.truncate(0)
                      continue
                if(zone_count==5):                                 #sending the noninverted thresholded frame for futher processing if inverted plane is detected
                      if(count2==1):
                            make=th1
                            count=1
                            skip=1000                              
                            speed=12                               #decrease the speed in the inverted plane 
                            print "inverted plane"
                            smooth1=cv2.erode(make,None,iterations=7)
                            dil=cv2.dilate(smooth1,None,iterations=11)
                            forward(speed)  
		            selected_region=select_regionIP1(dil,frame)
                            selected_region2=select_regionIP2(dil,frame)
                            selected_region3=select_regionIP3(dil,frame)      
                            cont= get_contour(selected_regionIP1)
                            cont2=get_contour(selected_regionIP2)
                            cont3=get_contour(selected_regionIP3)
                      else:
                            make=th2                             
                      
                else:
                     make=th2             #if it is black line detection send inverter thresholded frame for further processing

                     smooth1=cv2.erode(make,None,iterations=7)           #erosion and dilation operation to remove the grid lines as they would interfere in proper line detection
                     dil=cv2.dilate(smooth1,None,iterations=11)
                     
                     forward(speed)                                     #no matter what move the bot forward at lower pwm


                     #the lower part of the input frame is divided into 3 regions 
		     selected_region=select_region(dil,frame)
                     selected_region2=select_region2(dil,frame)
                     selected_region3=select_region3(dil,frame)
                     #contours are detected in each region
                     cont= get_contour(selected_region)
                     cont2=get_contour(selected_region2)
                     cont3=get_contour(selected_region3)

##########################################################################################################################################
#for every frame 3 contours are detected along the black line and its deviation from the centre of the frame is calculated and the pwm are upadted accordingly
##########################################################################################################################################
                     
                if len(cont)==1:                         #contour of region 1
                      Cx,Cy= get_centroid(cont)          #centroid of the contour to find the devition from the centre of the frame
                      area= cv2.contourArea(cont[0])     #area of the contour to indentify whether zone has been encountered
                      draw_output(frame,cont,Cx,Cy)
                      
                      frame_count +=1
                      if(frame_count>10):
                         
                           compute_pwm(Cx,frame,0.0003,0.0018,0)      #update the pwm of the motors proportional to its devition from the centroid
                           if len(cont2)==1:             #contour of region 2
                                Cx2,Cy2=get_centroid(cont2)
                                draw_output(frame,cont2,Cx2,Cy2)
                                compute_pwm(Cx2,frame,0.0002,0.0015,0)
                                area2= cv2.contourArea(cont2[0])
                            
                                if len(cont3)==1:       #contour of region 3
                                     Cx3,Cy3=get_centroid(cont3)
                                     draw_output(frame,cont3,Cx3,Cy3)
                                     area3= cv2.contourArea(cont3[0])
                                     
                                    #identifying whether the zone has been encountered from the area of the detected contour
                                     if(area>1100 and area2>1100 and area3>1000 and frame_count>skip and zone_count<5):
                                                                               
                                         zone_count =zone_count+1
                                        
                                         left.start(0)                     #stopiing at the zone
                                         right.start(0)
                                        
                                         shape,color,number=detect_shape()  # detecting shapes
                                         print shape,color,number          
                                         Region= "region"+str(zone_count)

                                         #overlaying on the plantation image 
                                         if(zone_count==1 and number>0):
                                       
                                             img=img0                  #plantation image
                                             skip=50                  
                                             speed=20
                                             numz1=number    #storing number of CM to blink the Led at the end
                                             colz1=color     #storing color of CM to blink that particular color
                                             image2=make_overlay(img,shape,color,number,Region)   #overlay image
                                             cv2.imshow("overlay",image2)
                                             cv2.waitKey(1)
                                         elif(zone_count==2 and number>0):
                                             img=image2
                                             skip=400
                                             speed=25
                                             numz2=number    #storing number of CM to blink the Led at the end
                                             colz2=color     #storing color of CM to blink that particular color

                                             image3=make_overlay(img,shape,color,number,Region)
                                             cv2.imshow("overlay",image3)
                                             cv2.waitKey(1)

                                         elif(zone_count==3 and number>0):
                                             img=image3
                                             speed=12
                                             skip=20
                                             numz3=number    #storing number of CM to blink the Led at the end
                                             colz3=color     #storing color of CM to blink that particular color

                                             image4=make_overlay(img,shape,color,number,Region)
                                             cv2.imshow("overlay",image4)
                                             cv2.waitKey(1)

                                         elif(zone_count==4 and number>0):
                                             img=image4
                                             speed=50
                                             skip=50
                                             numz4=number    #storing number of CM to blink the Led at the end
                                             colz4=color     #storing color of CM to blink that particular color

                                             image5=make_overlay(img,shape,color,number,Region)
                                             cv2.imshow("overlay",image5)
                                             cv2.waitKey(1)
                                         if(number>0 or (zone_count>4 and number==0)):
                                             forward(40)
                                             time.sleep(0.1)
                                         else:
                                             zone_count=zone_count-1            #if no color markers are detected
                                         left.start(0)
                                         right.start(0)
                                         rawCapture.truncate(0)
                                         still.truncate(0)
                                         frame_count=0
                                         continue

                                         
                                     #if all the centroid of the three contours detected on the line are in the centre of the frame move a bit faster   
                                     if (((Cx<(rowsp/2)+5) and (Cx>(rowsp/2)-5)) and ((Cx2<(rowsp/2)+5) and (Cx2>(rowsp/2)-5)) and ((Cx3<(rowsp/2)+5) and (Cx3>(rowsp/2)-5))):
                                     	compute_pwm(Cx3,frame,0.0001,0.002,1)
                                     else:
                                     	compute_pwm(Cx3,frame,0.0001,0.002,0)


                
                elif (len(cont)>1):                      
                      if(zone_count==5 and count==0):       #if inverted plane is encountered there will be two contours detected
                          left.start(0)
                          right.start(0)
                          time.sleep(0.1)
                          count2=1
                          print "change count2"
                          forward(10)
                          time.sleep(0.8)
                          turn_softright(90)
                          time.sleep(0.1)
                          left.start(0)
                          right.start(0)
                          rawCapture.truncate(0)
                          continue
                      elif(zone_count==5 and count==1 and frame_count>skip):   #when the inverted plane ends again two contours are detected
                                                                               #which indicated shed has been reached

                          left.start(0)
                          right.start(0)
                          print "SHED reached"
                          forward(20)
                          print "zone1",colz1,numz1
                          print "zone2",colz2,numz2
                          print "zone3",colz3,numz3
                          print "zone4",colz4,numz4
                          time.sleep(2)
                          left.start(0)
                          right.start(0)
                          blink_end(colz1,1)
                          blink_end(colz2,1)
                          blink_end(colz3,1)
                          blink_end(colz4,1)
                          while(1):
                                left.start(0)
                                right.start(0)      #stop at the shed permanently
                      elif(zone_count<5):
                          turn_softleft(10)
                          time.sleep((abs((rowsp/2)-50)*2)*0.0008)
                          print("more contour")
                      turn_softleft(10)
                      time.sleep((abs((rowsp/2)-50)*3)*0.0008)
   
                      print len(cont)
                else:                                   #some random case 
                      if(zone_count==5):                #might be due to reflection or shadows
                            forward(20)                 
                            time.sleep(0.1)
                            turn_softleft(20)           #moving the bot slightly left and right insuch case worked for me
                            time.sleep(0.1)
                            left.start(0)
                            right.start(0)
                            rawCapture.truncate(0)
                            continue
                      turn_softright(10)
                       
                      time.sleep((abs((rowsp/2)-50)*2)*0.0009)
                      print("in some random case")
               
                rawCapture.truncate(0)
      
                left.start(0)
                right.start(0)




		key=cv2.waitKey(1) & 0xFF
		if key ==ord("q"):
                        rawCapture.truncate(0)
                        camera.stop_preview()
                        camera.close()
                        GPIO.cleanup()                        
			break

	cv2.destroyAllWindows()


if __name__=="__main__":
	 main()
 

