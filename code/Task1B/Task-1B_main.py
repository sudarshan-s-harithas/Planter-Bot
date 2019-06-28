#classes and subclasses to import
import cv2
import numpy as np
import os

filename='result1B_2740.csv'
##################################################################################################
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

#################################################################################################
# DO NOT EDIT!!!
#################################################################################################
def blend_transparent(face_img, overlay_t_img):
    # Split out the transparency mask from the colour info
    overlay_img = overlay_t_img[:,:,:3] # Grab the BRG planes
    overlay_mask = overlay_t_img[:,:,3:]  # And the alpha plane

    # Again calculate the inverse mask
    background_mask = 255 - overlay_mask

    # Turn the masks into three channel, so we can use them as weights
    overlay_mask = cv2.cvtColor(overlay_mask, cv2.COLOR_GRAY2BGR)
    background_mask = cv2.cvtColor(background_mask, cv2.COLOR_GRAY2BGR)
    # Create a masked out face image, and masked out overlay
    # We convert the images to floating point in range 0.0 - 1.0
    face_part = (face_img * (1 / 255.0)) * (background_mask * (1 / 255.0))
    overlay_part = (overlay_img * (1 / 255.0)) * (overlay_mask * (1 / 255.0))

    # And finally just add them together, and rescale it back to an 8bit integer image    
    return np.uint8(cv2.addWeighted(face_part, 255.0, overlay_part, 255.0, 0.0))


def main(video_file_with_path):
    
#####################################################################################################
    #Write your code here!!!
#####################################################################################################
    i=0
    cap = cv2.VideoCapture(video_file_with_path)
    fourcc=cv2.VideoWriter_fourcc('m','p','4','v')
    out = cv2.VideoWriter('video_output.mp4',fourcc,16,(1280,720))
    image_red = cv2.imread("Overlay_Images\\yellow_flower.png",-1)
    image_blue = cv2.imread("Overlay_Images\\pink_flower.png",-1)
    image_green = cv2.imread("Overlay_Images\\red_flower.png",-1)
           
    
    def detect(c):                                 #function to detect shape
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
                 t=cv2.matchShapes(cnt,c,1,0.0)
                 if t>0.08:
                    shape="Rhombus"
                 else:
                    shape="Trapezium"
         elif len(approx)==5:
             shape="Pentagon"
         elif len(approx)==6:
             shape="Hexagon"
         else:
             shape="Circle"
         return shape

    def detectcol(c):                            #function to detect colour
         px=frame[cy,cx]
         if px[0]>=50:
             color="Blue"
         elif px[2]>=50:
             color="Red"
         else:
             color="Green"
         return color

    def detectcen(c):                          #function to detect centroid
        M=cv2.moments(c)
        cx=int(M["m10"]/M["m00"])
        cy=int(M["m01"]/M["m00"])
        return cx,cy
    lista=[]

    while(cap.isOpened()):    
        r,frame=cap.read()
        if r==True:
            i=i+1
            if i==202 or i==434:      ######## glitch in the video   frame 202 and 434
                continue
            gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            ret, thresh=cv2.threshold(gray,127,255,0)
            cv2.blur(gray,(50,50),0)
            image, contours, hierarchy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            cnt=contours[0]
            itercontours =contours[1:]
            
            if len(contours)==1:
                overlay_image = frame
                out.write(frame)
                continue
            
            elif len(contours)>1:
                for c in itercontours:
                    cx,cy=detectcen(c)
                    if (str(cx)+','+str(cy)) not in lista:
                        shape=detect(c)
                        color=detectcol(c)
                        x, y, w, h = cv2.boundingRect(c)
                        if color=='Red':
                            overlay_image=image_red
                        elif color=='Green':
                            overlay_image=image_green
                        elif color=='Blue':
                            overlay_image=image_blue
                        lista.insert(len(lista),str(cx)+','+str(cy))
                        writecsv(color,shape,(cx,cy))                
            
            g,t,e=frame[y:y+w, x:x+h,:].shape
            overlay_image =cv2.resize(overlay_image,(t,g))
            frame[y:y + w , x:x + h, :] = blend_transparent(frame[y:y + w, x:x + h, :], overlay_image)
            out.write(frame)
       
        if r==False:
            break
      
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return
    
#####################################################################################################
    #sample of overlay code for each frame
    #x,y,w,h = cv2.boundingRect(current_contour)
    #overlay_image = cv2.resize(image_red,(h,w))
    #frame[y:y+w,x:x+h,:] = blend_transparent(frame[y:y+w,x:x+h,:], overlay_image)
#######################################################################################################

#################################################################################################
# DO NOT EDIT!!!
#################################################################################################
#main where the path is set for the directory containing the test images
if __name__ == "__main__":
    main('F:/E Yantra/Set 3/Task 1/Task1B/2. Task_Description/Video/Video.mp4')
    
