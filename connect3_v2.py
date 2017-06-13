# import the necessary packages
from pyimagesearch.shapedetector import ShapeDetector
from pyimagesearch.colorlabeler import ColorLabeler
import argparse
import imutils
import cv2
from time import sleep
import numpy as np
import picamera
import RPi.GPIO as GPIO
from array import array
import smbus
from array import array
 
 
address = 0x04                          #arduino i2c adresi
bus = smbus.SMBus(1)
arrived_flag1=False
arrived_flag2=False
renk_kontrol=False
gripped_block=False
not_gripped_block=False
board_tamkarsi=False
placed_block=False
win_game=False
startgame=False
block_renk="None"
nextstep=0
boardisthere=False

#pinler
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)         #arduinodan gelen pinler
GPIO.setup(12,GPIO.IN)  
GPIO.setup(13,GPIO.IN) 
GPIO.setup(8,GPIO.OUT)
GPIO.setup(10,GPIO.OUT)       
GPIO.setup(15,GPIO.OUT)                                 #sagdan sola 15 16 18 22 yesil ledler
GPIO.setup(16,GPIO.OUT)       
GPIO.setup(18,GPIO.OUT)     
GPIO.setup(22,GPIO.OUT)                             
GPIO.setup(40,GPIO.OUT)                                 #ufak isik      
GPIO.setup(38,GPIO.OUT)                                 #ufak isik groundu          
GPIO.setup(19,GPIO.OUT)       
GPIO.setup(35,GPIO.IN)                                  #red-blue read                                  
GPIO.setwarnings(False)
 
red_blue_switch=0                                           #default olarak red oynuyor
red_blue_switch=GPIO.input(35)  
 
 
GPIO.output(10,GPIO.LOW)
GPIO.output(8,GPIO.LOW)                         # 8 buyuk isigin groundu 10 + bacak
GPIO.output(40,GPIO.LOW)
GPIO.output(38,GPIO.LOW)                        
GPIO.output(19,GPIO.LOW)                        #yesil ledlerin groundu
 
 
GPIO.output(15,GPIO.HIGH)
GPIO.output(16,GPIO.HIGH)
GPIO.output(18,GPIO.HIGH)               #baslangicta yesil ledleri bir saniye yak   
GPIO.output(22,GPIO.HIGH)
 
sleep(1)
 
GPIO.output(15,GPIO.LOW)
GPIO.output(16,GPIO.LOW)
GPIO.output(18,GPIO.LOW)                #yesil ledleri sondur isini yapmaya basla
GPIO.output(22,GPIO.LOW)
 
#camera definitions
 
camera= picamera.PiCamera()
camera.resolution = (1024, 960)
#camera.start_preview(fullscreen=False, window = (100, 20, 640, 480))
camera.brightness=55
 
 
def writeNumber(value):                 
     
    bus.write_byte(address, value)
    return -1
 
def readNumber():
    number = bus.read_byte(address)
    # number = bus.read_byte_data(address, 1)
    return number
 
def blockdetection():
    topbottom=0
    belesci=0
    detected="none"
    center=0
	par1_low_black=0
    par2_low_black=0
    par3_low_black=0
    par1_high_black=180
    par2_high_black=255
    par3_high_black=130
 
 
    #red filter definitions
 
    """par1_low_red=160
    par2_low_red=100
    par3_low_red=50
    par1_high_red=180
    par2_high_red=255
    par3_high_red=255"""
     
    par1_low_red=0
    par2_low_red=50
    par3_low_red=50
    par1_high_red=15
    par2_high_red=255
    par3_high_red=255
 
    """par11_low_red=160
    par22_low_red=50
    par33_low_red=50
    par11_high_red=180
    par22_high_red=255
    par33_high_red=255"""
 
     
 
    #blue filter definitions
 
    par1_low_blue=65
    par2_low_blue=50
    par3_low_blue=50
    par1_high_blue=105
    par2_high_blue=255
    par3_high_blue=255
       
    #yellow filter definitions
    par1_low_yellow=20
    par2_low_yellow=120
    par3_low_yellow=100
    par1_high_yellow=30
    par2_high_yellow=255
    par3_high_yellow=255
 
    GPIO.output(10,GPIO.HIGH)
    camera.capture('image_block.png')
    GPIO.output(10,GPIO.LOW)
    #image=cv2.imread('image.png')
 
    frame=cv2.imread('image_block.png')
 
    #frame=cv2.imread('block.png')
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
 
    lower_red1 = np.array([par1_low_red,par2_low_red,par3_low_red])
    upper_red1 = np.array([par1_high_red,par2_high_red,par3_high_red])
 
     
    """lower_red2 = np.array([par11_low_red,par22_low_red,par33_low_red])
    upper_red2 = np.array([par11_high_red,par22_high_red,par33_high_red])"""
 
 
    lower_blue = np.array([par1_low_blue,par2_low_blue,par3_low_blue])
    upper_blue = np.array([par1_high_blue,par2_high_blue,par3_high_blue])
     
    lower_yellow = np.array([par1_low_yellow,par2_low_yellow,par3_low_yellow])
    upper_yellow = np.array([par1_high_yellow,par2_high_yellow,par3_high_yellow])
 
	lower_black = np.array([par1_low_black,par2_low_black,par3_low_black])
    upper_black = np.array([par1_high_black,par2_high_black,par3_high_black])
 
 
    black_mask = cv2.inRange(hsv, lower_black, upper_black)
	cv2.imwrite('black_mask.png',black_mask)
	
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
 
    red_mask = cv2.inRange(hsv, lower_red1, upper_red1)
    """red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
     
    red_mask = red_mask1 | red_mask2"""
     
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
    #cv2.imwrite('red_mask.png',red_mask)
 
    #image_red=cv2.imread('red_mask.png')
 
    #cv2.imwrite('blue_mask.png',blue_mask)
 
    #image_blue=cv2.imread('blue_mask.png')
 
 
 
    #filtrelenmis resmi eski rengine donusturme
 
    mahmut_red=cv2.bitwise_and(frame,frame, mask=red_mask)
     
    #cv2.imwrite("mahmut_red.png",mahmut_red)
 
    mahmut_blue=cv2.bitwise_and(frame,frame, mask=blue_mask)
    #cv2.imwrite("mahmut_blue.png",mahmut_blue)
 
    mahmut_yellow=cv2.bitwise_and(frame,frame, mask=yellow_mask)
    #cv2.imwrite("mahmut_yellow.png",mahmut_yellow)

 
    #mahmut_black=cv2.bitwise_and(frame,frame, mask=black_mask)
    mahmut_black=cv2.imread("black_mask.png")
	
	#BOARD CONTROL:
	
	
    resized_black = imutils.resize(mahmut_black, width=300)
 
    ratio = mahmut_black.shape[0] / float(resized_black.shape[0])
 
    # blur the resized image slightly, then convert it to both
    # grayscale and the L*a*b* color spaces
 
 
    blurblack_black = cv2.GaussianBlur(resized_black, (5, 5), 0)
    gray_black = cv2.cvtColor(blurblack_black, cv2.COLOR_BGR2GRAY)
    lab_black = cv2.cvtColor(blurblack_black, cv2.COLOR_BGR2LAB)
    thresh_black = cv2.threshold(gray_black, 60, 255, cv2.THRESH_BINARY)[1]
 
    # find contours in the thresholded image
    cnts5 = cv2.findContours(thresh_black.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts5 = cnts5[0] if imutils.is_cv2() else cnts5[1]
 
    # initialize the shape detector and color labeler
    sd = ShapeDetector()
    #cl = ColorLabeler()
	
	
    # loop over the contours
    for c in cnts5:

            temp_area_black=cv2.contourArea(c)
            if temp_area_black>3000:
				boardisthere=True
    
            
	if boardisthere=False:
		#RED circle detect etme
	 
	 
		resized_red = imutils.resize(mahmut_red, width=300)
	 
		ratio = mahmut_red.shape[0] / float(resized_red.shape[0])
	 
		# blur the resized image slightly, then convert it to both
		# grayscale and the L*a*b* color spaces
	 
	 
		blurred_red = cv2.GaussianBlur(resized_red, (5, 5), 0)
		gray_red = cv2.cvtColor(blurred_red, cv2.COLOR_BGR2GRAY)
		lab_red = cv2.cvtColor(blurred_red, cv2.COLOR_BGR2LAB)
		thresh_red = cv2.threshold(gray_red, 60, 255, cv2.THRESH_BINARY)[1]
	 
		# find contours in the thresholded image
		cnts = cv2.findContours(thresh_red.copy(), cv2.RETR_EXTERNAL,
				cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]
	 
		# initialize the shape detector and color labeler
		sd = ShapeDetector()
		#cl = ColorLabeler()
		 
	 
		# loop over the contours
		for c in cnts:
				# compute the center of the contour
				M = cv2.moments(c)
				if M["m00"]!=0:
				 
					cX = int((M["m10"] / M["m00"]) * ratio)
					cY = int((M["m01"] / M["m00"]) * ratio)
					topmost = tuple(c[c[:,:,1].argmin()][0])
					bottommost = tuple(c[c[:,:,1].argmax()][0])
					topbottom=bottommost[1]-topmost[1]
					topbottom=int(topbottom*(7.5)/6.5)
					 
					 
					area_red=cv2.contourArea(c)
					if area_red>400:
						# detect the shape of the contour and label the color
						shape = sd.detect(c)
						#color = cl.label(lab_red, c)
						color="red"
						 
						 
						# multiply the contour (x, y)-coordinates by the resize ratio,
						# then draw the contours and the name of the shape and labeled
						# color on the image
						c = c.astype("float")
						c *= ratio
						c = c.astype("int")
						text = "{} {}".format(color, shape)
						cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
						cv2.putText(frame, text, (cX, cY),
								cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
					 
						 
						#compare the detected shape
						if text=="red circle":
							if topbottom>belesci: 
								detected=text
								belesci=topbottom
								center=cX
				 
		#YELLOW rect detect etme
	 
		resized_yellow = imutils.resize(mahmut_yellow, width=300)
	 
		ratio = mahmut_yellow.shape[0] / float(resized_yellow.shape[0])
	 
		# blur the resized image slightly, then convert it to both
		# grayscale and the L*a*b* color spaces
	 
	 
		blurred_yellow = cv2.GaussianBlur(resized_yellow, (5, 5), 0)
		gray_yellow = cv2.cvtColor(blurred_yellow, cv2.COLOR_BGR2GRAY)
		lab_yellow = cv2.cvtColor(blurred_yellow, cv2.COLOR_BGR2LAB)
		thresh_yellow = cv2.threshold(gray_yellow, 60, 255, cv2.THRESH_BINARY)[1]
	 
	 
	 
		# find contours in the thresholded image
		cnts3 = cv2.findContours(thresh_yellow.copy(), cv2.RETR_EXTERNAL,
				cv2.CHAIN_APPROX_SIMPLE)
		cnts3 = cnts3[0] if imutils.is_cv2() else cnts3[1]
	 
		# initialize the shape detector and color labeler
		sd = ShapeDetector()
		#cl = ColorLabeler()
	 
		# loop over the contours
		for c in cnts3:
				# compute the center of the contour
				M = cv2.moments(c)
				if M["m00"]!=0:
				 
					cX = int((M["m10"] / M["m00"]) * ratio)
					cY = int((M["m01"] / M["m00"]) * ratio)
					topmost = tuple(c[c[:,:,1].argmin()][0])
					bottommost = tuple(c[c[:,:,1].argmax()][0])
					topbottom=bottommost[1]-topmost[1]
					area_yellow=cv2.contourArea(c)
					if area_yellow>400:
						# detect the shape of the contour and label the color
						shape = sd.detect(c)
						#color = cl.label(lab_yellow, c)
						color="yellow"
						 
						 
						# multiply the contour (x, y)-coordinates by the resize ratio,
						# then draw the contours and the name of the shape and labeled
						# color on the image
						c = c.astype("float")
						c *= ratio
						c = c.astype("int")
						text = "{} {}".format(color, shape)
						cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
						cv2.putText(frame, text, (cX, cY),
								cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
						 
						#compare the detected shape
						if text=="yellow square":
							if topbottom>belesci: 
								detected=text
								belesci=topbottom
								center=cX
							 
		#BLUE circle detect etme
	 
		resized_blue = imutils.resize(mahmut_blue, width=300)
	 
	 
		ratio = mahmut_blue.shape[0] / float(resized_blue.shape[0])
	 
		# blur the resized image slightly, then convert it to both
		# grayscale and the L*a*b* color spaces
	 
	 
	 
	 
		blurred_blue = cv2.GaussianBlur(resized_blue, (5, 5), 0)
		gray_blue = cv2.cvtColor(blurred_blue, cv2.COLOR_BGR2GRAY)
		lab_blue = cv2.cvtColor(blurred_blue, cv2.COLOR_BGR2LAB)
		thresh_blue = cv2.threshold(gray_blue, 60, 255, cv2.THRESH_BINARY)[1]
	 
	 
	 
		# find contours in the thresholded image
		cnts2 = cv2.findContours(thresh_blue.copy(), cv2.RETR_EXTERNAL,
				cv2.CHAIN_APPROX_SIMPLE)
		cnts2 = cnts2[0] if imutils.is_cv2() else cnts2[1]
	 
		# initialize the shape detector and color labeler
		sd = ShapeDetector()
		#cl = ColorLabeler()
	 
		# loop over the contours
		for c in cnts2:
				# compute the center of the contour
				M = cv2.moments(c)
				if M["m00"]!=0:
					 
					cX = int((M["m10"] / M["m00"]) * ratio)                         
					cY = int((M["m01"] / M["m00"]) * ratio)
					topmost = tuple(c[c[:,:,1].argmin()][0])
					bottommost = tuple(c[c[:,:,1].argmax()][0])
					topbottom=bottommost[1]-topmost[1]
					topbottom=int(topbottom*(7.5)/6.5)
					 
					 
					area_blue=cv2.contourArea(c)
					if area_blue>400:
						 
						# detect the shape of the contour and label the color
						shape = sd.detect(c)
						#color = cl.label(lab_blue, c)
						color="blue"
						 
						# multiply the contour (x, y)-coordinates by the resize ratio,
						# then draw the contours and the name of the shape and labeled
						# color on the image
						c = c.astype("float")
						c *= ratio
						c = c.astype("int")
						text = "{} {}".format(color, shape)
						cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
						cv2.putText(frame, text, (cX, cY),
								cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)              
						#compare the detected shape
						if text=="blue circle":
							if topbottom>belesci: 
								detected=text
								belesci=topbottom
								center=cX
                             
                             
    cv2.imwrite('frame_both.png',frame)
    return (detected,center,topbottom)
                 
def errorcontrol_block():
     
    sample1=["none",0]
    sample2=["none",0]
     
     
    sample1=blockdetection()
     
    sleep(1)
     
    sample2=blockdetection()
    print("sample1 is:" , sample1)
    print("sample2 is:" , sample2)
     
     
    if(sample1[0]==sample2[0]):
        if(abs(sample1[1]-sample2[1])<20):
            return (sample1[0],sample1[1])
    else:
        errorcontrol()
     
def flagdetection():
     
     
    belesci2=0
    returncenter_flag=0
    center_flag=0
     
     
    #red filter definitions
    par1_low_red=0
    par2_low_red=50
    par3_low_red=50
    par1_high_red=15
    par2_high_red=255
    par3_high_red=255
     
    GPIO.output(10,GPIO.HIGH)
    camera.capture('image_flag.png')
    #image=cv2.imread('image.png')
    GPIO.output(10,GPIO.LOW)
     
     
    frame=cv2.imread('image_flag.png')
     
    #frame=cv2.imread('flag.png')
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
 
    lower_red = np.array([par1_low_red,par2_low_red,par3_low_red])
    upper_red = np.array([par1_high_red,par2_high_red,par3_high_red])
 
 
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
 
 
    #filtrelenmis resmi eski rengine donusturme
 
    mahmut_red=cv2.bitwise_and(frame,frame, mask=red_mask)
     
    #cv2.imwrite("mahmut_red.png",mahmut_red)
    #RED kare dikdortgen detect etme
 
    resized_red = imutils.resize(mahmut_red, width=300)
 
    ratio = mahmut_red.shape[0] / float(resized_red.shape[0])
 
    # blur the resized image slightly, then convert it to both
    # grayscale and the L*a*b* color spaces
 
 
    blurred_red = cv2.GaussianBlur(resized_red, (5, 5), 0)
    gray_red = cv2.cvtColor(blurred_red, cv2.COLOR_BGR2GRAY)
    lab_red = cv2.cvtColor(blurred_red, cv2.COLOR_BGR2LAB)
    thresh_red = cv2.threshold(gray_red, 60, 255, cv2.THRESH_BINARY)[1]
 
    # find contours in the thresholded image
    cnts4 = cv2.findContours(thresh_red.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts4 = cnts4[0] if imutils.is_cv2() else cnts4[1]
 
    # initialize the shape detector and color labeler
    sd = ShapeDetector()
    cl = ColorLabeler()
 
    # loop over the contours
    for c in cnts4:
            # compute the center of the contour
            M = cv2.moments(c)
            if M["m00"]!=0:
             
                cX = int((M["m10"] / M["m00"]) * ratio)
                cY = int((M["m01"] / M["m00"]) * ratio)
            area_red2=cv2.contourArea(c)
            if area_red2>400:
                # detect the shape of the contour and label the color
                shape = sd.detect(c)
                #color = cl.label(lab_red, c)
                color="red"
                # multiply the contour (x, y)-coordinates by the resize ratio,
                # then draw the contours and the name of the shape and labeled
                # color on the image
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")
                text = "{} {}".format(color, shape)
                cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                cv2.putText(frame, text, (cX, cY),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
             
                 
                #compare the detected shape             
                if text=="red square":
                    if area_red2>belesci2:
                        returncenter_flag=cX
    cv2.imwrite("flag.png",frame)                   
    return(returncenter_flag)
 
def flag_arduinodata():
     
    flag_center=flagdetection()
     
    #("flag center:",flag_center)
 
 
    if flag_center==0:
        writeNumber(253)                    #253 no detection
        print("gelen_flag_nodetection:",readNumber())
        sleep(1)
        flag_arduinodata()
    elif flag_center<507:
        writeNumber(250)                    #250 sola don
        print("gelen_flag_saga_don:",readNumber())
        fark_flag=int((512-flag_center)/3)
        sleep(0.1)
        writeNumber(fark_flag)
        print("answer_flag_fark:",readNumber())
         
 
    elif flag_center>517:
        writeNumber(251)                    #251 saga don
        print("gelen_flag_sola_don:",readNumber())
        fark_flag=int((flag_center-512)/3)
        sleep(0.1)
        writeNumber(fark_flag)
        print("answer_flag_fark:",readNumber())
    else:
        writeNumber(252)                    #252 go go go
        print("gelen_flag_go_go_go:",readNumber())
         
def block_arduinodata():
    beles=[]
    beles=blockdetection()
    print(beles)
 
    if beles[0]=="red circle":
        writeNumber(247)
        print("red circle")
        print("gelen red circle:",readNumber())
    elif beles[0]=="blue circle":
        writeNumber(248)
        print("blue circle")
        print("gelen blue circle:",readNumber())
    elif beles[0]=="yellow square":
        writeNumber(249)
        print("yellow square")
        print("gelen yellow square:",readNumber())
 
    sleep(1)
 
 
    if beles[1]==0:
        writeNumber(253)                    #253 no detection
        print("gelen_nodetection:",readNumber())
        sleep(1)
        block_arduinodata()
    elif beles[1]<507:
        writeNumber(250)                    #250 sag don
        print("gelen_saga_don:",readNumber())
        fark=int((512-beles[1])/3)
        sleep(0.1)
        writeNumber(fark)
        print("gelen_fark:",readNumber())
         
 
    elif beles[1]>517:
        writeNumber(251)                    #251 sol don
        print("gelen_sola_don:",readNumber())
        fark=int((beles[1]-512)/3)
        sleep(0.1)
        writeNumber(fark)
        print("answer_fark:",readNumber())
    else:
        writeNumber(252)                    #252 go go go
        print("gelen_go_go_go:",readNumber())
         
    return(beles[0])
         
def arduino_read():
 
    inp1=0
    inp2=0
    inp3=0
     
    arduino_gelen_data=False
 
    while arduino_gelen_data==False:
        inp1=GPIO.input(11)
        #print(inp1)
        inp2=GPIO.input(12)
        #print(inp2)
        inp3=GPIO.input(13)
        #print(inp3)
         
         
        if inp1==0 and inp2==0 and inp3==1:
            print("input is 001")
            #arrived_flag1=True
            arduino_gelen_data=True
            break
        elif inp1==0 and inp2==1 and inp3==0:
            print("input is 010")
            #arrived_flag2=True
            arduino_gelen_data=True
        elif inp1==0 and inp2==1 and inp3==1:
            print("input is 011")
            #gripped_block=True
            arduino_gelen_data=True
        elif inp1==1 and inp2==0 and inp3==1:
            print("input is 101")
            #placed_block=True
            arduino_gelen_data=True
        elif inp1==1 and inp2==1 and inp3==1:
            print("input is 111")
            #renk_kontrol=True
            arduino_gelen_data=True
        elif inp1==1 and inp2==1 and inp3==0:
            print("input is 110")
            #board_tamkarsi=True
            arduino_gelen_data=True
        elif inp1==1 and inp2==0 and inp3==0:
            print("input is 100")
            #not_gripped_block=True
            arduino_gelen_data=True
    return(inp1,inp2,inp3)
 
def boarddetection():
     
     
    par1_low_black=0
    par2_low_black=0
    par3_low_black=0
    par1_high_black=180
    par2_high_black=255
    par3_high_black=130
         
     
    left_df=1024
    right_df=0
    wide_df=0
    height_df=0
    bottom_df=0
    top_df=0
    wide=0
    height=0
     
    GPIO.output(10,GPIO.HIGH)
    camera.capture('image_board.png')
    #image=cv2.imread('image.png')
    GPIO.output(10,GPIO.LOW)
     
    frame=cv2.imread('image_board.png')
    
    #frame=cv2.imread('image_board.png')
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
 
    lower_black = np.array([par1_low_black,par2_low_black,par3_low_black])
    upper_black = np.array([par1_high_black,par2_high_black,par3_high_black])
 
 
    black_mask = cv2.inRange(hsv, lower_black, upper_black)
 
        
    cv2.imwrite('black_mask.png',black_mask)
 
 
    #filtrelenmis resmi eski rengine donusturme
 
    #mahmut_black=cv2.bitwise_and(frame,frame, mask=black_mask)
    mahmut_black=cv2.imread("black_mask.png")
 
    #black circle detect etme
 
 
 
    resized_black = imutils.resize(mahmut_black, width=300)
 
    ratio = mahmut_black.shape[0] / float(resized_black.shape[0])
 
    # blur the resized image slightly, then convert it to both
    # grayscale and the L*a*b* color spaces
 
 
    blurblack_black = cv2.GaussianBlur(resized_black, (5, 5), 0)
    gray_black = cv2.cvtColor(blurblack_black, cv2.COLOR_BGR2GRAY)
    lab_black = cv2.cvtColor(blurblack_black, cv2.COLOR_BGR2LAB)
    thresh_black = cv2.threshold(gray_black, 60, 255, cv2.THRESH_BINARY)[1]
 
    # find contours in the thresholded image
    cnts5 = cv2.findContours(thresh_black.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts5 = cnts5[0] if imutils.is_cv2() else cnts5[1]
 
    # initialize the shape detector and color labeler
    sd = ShapeDetector()
    #cl = ColorLabeler()
 
    # loop over the contours
    for c in cnts5:
            # compute the center of the contour
            M = cv2.moments(c)
            if M["m00"]!=0:
             
                cX = int((M["m10"] / M["m00"]) * ratio)
                cY = int((M["m01"] / M["m00"]) * ratio)
                 
                leftmost = tuple(c[c[:,:,0].argmax()][0]) 
                rightmost = tuple(c[c[:,:,0].argmin()][0]) 
                 
                lm_x= int(leftmost[0]*ratio)
                rm_x= int(rightmost[0]*ratio)
                wide= lm_x-rm_x
                 
                bottommost = tuple(c[c[:,:,1].argmin()][0]) 
                topmost = tuple(c[c[:,:,1].argmax()][0]) 
                 
                 
                bm_y= int(bottommost[1]*ratio)
                tm_y= int(topmost[1]*ratio)
                height=tm_y-bm_y
                 
                 
                 
 
                 
                 
            area_black=cv2.contourArea(c)
            if area_black>1000:
                if height> (wide/2):
                 
                    #print(lm_x,rm_x,wide,bm_y,tm_y,height)
                     
                    # detect the shape of the contour and label the color
                    shape = sd.detect(c)
                    #color = cl.label(lab_black, c)
                    color="mahmut"
                    # multiply the contour (x, y)-coordinates by the resize ratio,
                    # then draw the contours and the name of the shape and labeled
                    # color on the image
                    c = c.astype("float")
                    c *= ratio
                    c = c.astype("int")
                    text = "{} {}".format(color, shape)
                    cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                    cv2.putText(frame, text, (cX, cY),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                 
                     
                    #compare the detected shape
                     
                    if wide>wide_df: 
                        wide_df=wide
                        left_df=lm_x
                        right_df=rm_x
                         
                        height_df=height
                        bottom_df=bm_y
                        top_df=tm_y
                         
                         
                         
                         
    cv2.imwrite("black_output.png",frame)
         
    print(left_df,right_df,wide_df,bottom_df,top_df,height_df)
    return(left_df,right_df,wide_df,bottom_df,top_df,height_df)
 
def boardortalama():
     
    boardonmiddle=False
    #boarddetection()
 
    #board kenarlari 20-1004 arasinda olana kadar don
 
 
    while boardonmiddle==False:             #boardu ortalayana kadar don
         
        sleep(1)
        board_result=boarddetection()           #array 0-->left, 1--> right,2--> fark 
         
        if board_result[1]==0:                  #no detection
            if board_result[0]==1024:
                writeNumber(253)                        #253 no detection
                print("gelen_board_nodetection:",readNumber())
             
             
        elif board_result[1]<20:                 #en sol pixel 20 dan kucukse sola don
            writeNumber(240)                        #240 saga don   boardu ortalayamiyorum
            print("gelen_boardortalama_saga_don:",readNumber())
             
             
        elif board_result[0]>1004:                   #en sag pixel 1004 den buyukse saga don
            writeNumber(239)                        #239 sola don  boardu ortalayamiyorum
            print("gelen_boardortalama_sola_don:",readNumber())
             
             
        else:
            boardonmiddle=True
            #print("ortada")
            return(board_result)

def boardkarsinagec():
	
	board_karsi=boardortalama()
	
	sag_fark=board_karsi[1]
	sol_fark=1024-board_karsi[0]
	
	if sol_fark>(sag_fark+10):
		donme=int((sol_fark-sag_fark)/5)
		print(donme)
		writeNumber(donme)					#saga donme miktarı daha fazla
	elif sag_fark>(sol_fark+10):
		donme=int(sag_fark-sol_fark)/5
		print(donme)
		writeNumber(donme)					#saga donme miktarı daha az
	else:	
		writeNumber(45)					#saga donme miktarı
	     
def boardread_red():
     
    return_read_center_red={}
     
    for k in range (0,11):
        for j in range (0,11):
            return_read_center_red[k,j]=0
    i=0
 
    #red filter definitions
 
    par1_low_red=0
    par2_low_red=50
    par3_low_red=50
    par1_high_red=15
    par2_high_red=255
    par3_high_red=255
      
    """camera= picamera.PiCamera()
    camera.resolution = (1024, 960)
    #camera.start_preview(fullscreen=False, window = (100, 20, 640, 480))
    camera.brightness=57
 
    camera.capture('image_boardread_red.png')
    #image=cv2.imread('image.png')
"""
    frame=cv2.imread('image_board.png')
     
     
    #frame=cv2.imread('board2.png')
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
 
    lower_red = np.array([par1_low_red,par2_low_red,par3_low_red])
    upper_red = np.array([par1_high_red,par2_high_red,par3_high_red])
 
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
     
 
    #filtrelenmis resmi eski rengine donusturme
 
    mahmut_red=cv2.bitwise_and(frame,frame, mask=red_mask)
     
    #cv2.imwrite("mahmut_red.png",mahmut_red)
     
    #RED circle detect etme
 
 
    resized_red = imutils.resize(mahmut_red, width=300)
 
    ratio = mahmut_red.shape[0] / float(resized_red.shape[0])
 
    # blur the resized image slightly, then convert it to both
    # grayscale and the L*a*b* color spaces
 
 
    blurred_red = cv2.GaussianBlur(resized_red, (5, 5), 0)
    gray_red = cv2.cvtColor(blurred_red, cv2.COLOR_BGR2GRAY)
    lab_red = cv2.cvtColor(blurred_red, cv2.COLOR_BGR2LAB)
    thresh_red = cv2.threshold(gray_red, 60, 255, cv2.THRESH_BINARY)[1]
 
    # find contours in the thresholded image
    cnts6 = cv2.findContours(thresh_red.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts6 = cnts6[0] if imutils.is_cv2() else cnts6[1]
 
    # initialize the shape detector and color labeler
    sd = ShapeDetector()
    cl = ColorLabeler()
 
    # loop over the contours
    for c in cnts6:
            # compute the center of the contour
            M = cv2.moments(c)
            if M["m00"]!=0:
             
                cX = int((M["m10"] / M["m00"]) * ratio)
                cY = int((M["m01"] / M["m00"]) * ratio)
                topmost = tuple(c[c[:,:,1].argmin()][0])
                bottommost = tuple(c[c[:,:,1].argmax()][0])
                topbottom=bottommost[1]-topmost[1]
            area_red=cv2.contourArea(c)
            if area_red>300:
                # detect the shape of the contour and label the color
                shape = sd.detect(c)
                #color = cl.label(lab_red, c)
                color="red"
                # multiply the contour (x, y)-coordinates by the resize ratio,
                # then draw the contours and the name of the shape and labeled
                # color on the image
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")
                text = "{} {}".format(color, shape)
                cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                cv2.putText(frame, text, (cX, cY),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
             
                 
                #compare the detected shape
                if text=="red circle":
                    return_read_center_red [i,0]=cX
                    return_read_center_red [i,1]=cY
                    i=i+1
     
         
                     
    cv2.imwrite('frame_readed_red.png',frame)
    return (return_read_center_red)
  
def boardread_blue():
     
    return_read_center_blue={}
     
    for k in range (0,11):
        for m in range (0,11):
            return_read_center_blue[k,m]=0
    j=0
 
    #blue filter definitions
 
    par1_low_blue=65
    par2_low_blue=50
    par3_low_blue=50
    par1_high_blue=105
    par2_high_blue=255
    par3_high_blue=255
     
     
     
    """camera= picamera.PiCamera()
    camera.resolution = (1024, 960)
    #camera.start_preview(fullscreen=False, window = (100, 20, 640, 480))
    camera.brightness=57
 
    camera.capture('image_boardread_blue.png')"""
    #image=cv2.imread('image.png')
 
    frame=cv2.imread('image_board.png')
    #frame=cv2.imread('board.png')
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
 
    lower_blue = np.array([par1_low_blue,par2_low_blue,par3_low_blue])
    upper_blue = np.array([par1_high_blue,par2_high_blue,par3_high_blue])
     
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
 
 
    #filtrelenmis resmi eski rengine donusturme
    mahmut_blue=cv2.bitwise_and(frame,frame, mask=blue_mask)
    #cv2.imwrite("mahmut_.png",mahmut_blue)
                         
    #BLUE circle detect etme
 
    resized_blue = imutils.resize(mahmut_blue, width=300)
 
 
    ratio = mahmut_blue.shape[0] / float(resized_blue.shape[0])
 
    # blur the resized image slightly, then convert it to both
    # grayscale and the L*a*b* color spaces
 
 
 
 
    blurred_blue = cv2.GaussianBlur(resized_blue, (5, 5), 0)
    gray_blue = cv2.cvtColor(blurred_blue, cv2.COLOR_BGR2GRAY)
    lab_blue = cv2.cvtColor(blurred_blue, cv2.COLOR_BGR2LAB)
    thresh_blue = cv2.threshold(gray_blue, 60, 255, cv2.THRESH_BINARY)[1]
 
 
 
    # find contours in the thresholded image
    cnts2 = cv2.findContours(thresh_blue.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts2 = cnts2[0] if imutils.is_cv2() else cnts2[1]
 
    # initialize the shape detector and color labeler
    sd = ShapeDetector()
    cl = ColorLabeler()
 
    # loop over the contours
    for c in cnts2:
            # compute the center of the contour
            M = cv2.moments(c)
            if M["m00"]!=0:
                 
                cX = int((M["m10"] / M["m00"]) * ratio)                         
                cY = int((M["m01"] / M["m00"]) * ratio)
                topmost = tuple(c[c[:,:,1].argmin()][0])
                bottommost = tuple(c[c[:,:,1].argmax()][0])
                topbottom=bottommost[1]-topmost[1]
            area_blue=cv2.contourArea(c)
            if area_blue>300:
                 
                # detect the shape of the contour and label the color
                shape = sd.detect(c)
                #color = cl.label(lab_blue, c)
                color="blue"
                # multiply the contour (x, y)-coordinates by the resize ratio,
                # then draw the contours and the name of the shape and labeled
                # color on the image
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")
                text = "{} {}".format(color, shape)
                cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                cv2.putText(frame, text, (cX, cY),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)              
                #compare the detected shape
                if text=="blue circle":
                    return_read_center_blue [j,0] = cX
                    return_read_center_blue [j,1] = cY
                    j=j+1
                         
                             
    cv2.imwrite('frame_readed_blue.png',frame)
     
    """for k in range (0,11):
        for m in range (0,11):
            if return_read_center_blue[k,m]!=0:
     
                print (return_read_center_blue[k,m])
                print (k,m)"""
    return (return_read_center_blue)
 
def matchplaces(m,kat):
     
    if m==1:
        return(1)
    elif m==2:
        if kat==1:
            return(2)
        elif kat==3:
            return(12)
        else:
            return(0)
    elif m==3:
        if kat==1:
            return(3)
        elif kat==3:
            return(13)
        elif kat==5:
            return(19)
        else:
            return(0)
    elif m==4:
        if kat==1:
            return(4)
        elif kat==3:
            return(14)
        elif kat==5:
            return(20)
        else:
            return(0)
    elif m==5:
        if kat==1:
            return(5)
        elif kat==3:
            return(15)
        else:
            return(0)
    elif m==6:
        return(6)
    elif m==7:
        return(7)
    elif m==8:
        if kat==2:
            return(8)
        elif kat==4:
            return (16)
        else:
            return(0)
    elif m==9:
        if kat==2:
            return(9)
        elif kat==4:
            return (17)
        elif kat==6:
            return (21)
        else:
            return(0) 
    elif m==10:
        if kat==2:
            return(10)
        elif kat==4:
            return(18)
        else:
            return(0)
    elif m==10:
        return(11)
    else:
         return(0)
         
def placeblock():
     
 
     
     
    board_target_center_x = np.arange(22)       #default olarak target in x degerleri 0
    for k in range(1,21):
        board_target_center_x[k]=0
     
    board_target_center_y = np.arange(7)        #default olarak target in y degerleri 0
    for k in range(1,6):
        board_target_center_y[k]=0
     
    readedsample = np.arange(21)        #default olarak sample nin tum elemanlari 0
    for k in range(1,21):
        readedsample[k]=0
     
     

    board_pixels=boardortalama()      #board_pixel in 0-->left , 1-->right, 2-->wide, 3-->bottom
                                        # 4-->top, 5-->height
     
     
    #boarddaki yerlerin dinamik x koordinatlari
     
    board_target_center_x[1]=board_pixels[0]-int((board_pixels[2]*0.0596))
    board_target_center_x[2]=board_pixels[0]-int((board_pixels[2]*0.2365))
    board_target_center_x[3]=board_pixels[0]-int((board_pixels[2]*0.4134))
    board_target_center_x[4]=board_pixels[0]-int((board_pixels[2]*0.5996))
    board_target_center_x[5]=board_pixels[0]-int((board_pixels[2]*0.7672))
    board_target_center_x[6]=board_pixels[0]-int((board_pixels[2]*0.9441))
    board_target_center_x[7]=board_pixels[0]-int((board_pixels[2]*0.1527))
    board_target_center_x[8]=board_pixels[0]-int((board_pixels[2]*0.3296))
    board_target_center_x[9]=board_pixels[0]-int((board_pixels[2]*0.5065))
    board_target_center_x[10]=board_pixels[0]-int((board_pixels[2]*0.6853))
    board_target_center_x[11]=board_pixels[0]-int((board_pixels[2]*0.851))
    board_target_center_x[12]=board_target_center_x[2]
    board_target_center_x[13]=board_target_center_x[3]
    board_target_center_x[14]=board_target_center_x[4]
    board_target_center_x[15]=board_target_center_x[6]
    board_target_center_x[16]=board_target_center_x[8]
    board_target_center_x[17]=board_target_center_x[9]
    board_target_center_x[18]=board_target_center_x[10]
    board_target_center_x[19]=board_target_center_x[3]
    board_target_center_x[20]=board_target_center_x[4]
    board_target_center_x[21]=board_target_center_x[9]
     
     
     
    #boarddaki yerlerin dinamik y koordinatlari
     
    board_target_center_y[1]=board_pixels[3]+int((board_pixels[5]*0.1132))
    board_target_center_y[2]=board_pixels[3]+int((board_pixels[5]*0.2818))
    board_target_center_y[3]=board_pixels[3]+int((board_pixels[5]*0.4503))
    board_target_center_y[4]=board_pixels[3]+int((board_pixels[5]*0.6189))
    board_target_center_y[5]=board_pixels[3]+int((board_pixels[5]*0.7875))
    board_target_center_y[6]=board_pixels[3]+int((board_pixels[5]*0.09561))
     
     
    readed_center_red={}
    readed_center_blue={}
     
    for i in range (0,11):
        for k in range(0,2):
            readed_center_red[i,k]=0
            readed_center_blue[i,k]=0
     
    readed_center_red=boardread_red()
     
    readed_center_blue=boardread_blue()
     
     
     
     
    #redi yerlestirme
     
    for k in range(0,11):
        for m in range (1,6):
            temp_y_fark = readed_center_red[k,1]-board_target_center_y[m]
            if (abs(temp_y_fark))<20:
                for l in range (1,11):
                    temp_x_fark = readed_center_red[k,0]-board_target_center_x[l]
                    if (abs(temp_x_fark))<20:
                        if red_blue_switch==0:
                            if matchplaces(l,m)!=0:
                                readedsample[matchplaces(l,m)-1]=2                  #x y degerleri eslesti
                        else:
                            if matchplaces(l,m)!=0:
                                readedsample[matchplaces(l,m)-1]=1
    #blue yerlestirme
     
     
    for k in range(0,11):
        for m in range (1,6):
            temp_y_fark = readed_center_blue[k,1]-board_target_center_y[m]
            if (abs(temp_y_fark))<20:
                for l in range (1,11):
                    temp_x_fark = readed_center_blue[k,0]-board_target_center_x[l]
                    if (abs(temp_x_fark))<20:                    
                        if red_blue_switch==0:
                            if matchplaces(l,m)!=0:
                                readedsample[matchplaces(l,m)-1]=1                  #x y degerleri eslesti
                        else:
                            if matchplaces(l,m)!=0:
                                readedsample[matchplaces(l,m)-1]=2
     
 
    alg_return=[]               
     
    print("readed sample:",readedsample)
                     
    alg_return=alg_table(readedsample)
    last_center=board_target_center_x[alg_return[0]]
     
    if alg_return[1]==1:
        win_game=True
     
    print(alg_return)
    #look up to table and decide to which pixel is target
     
    if alg_return[0]==1:
        writeNumber(241)                            #kat 1
         
    elif alg_return[0]==2:
        writeNumber(241)
             
    elif alg_return[0]==3:
        writeNumber(241)
     
    elif alg_return[0]==4:
        writeNumber(241)
     
    elif alg_return[0]==5:
        writeNumber(241)
     
    elif alg_return[0]==6:
        writeNumber(241)
     
     
     
    elif alg_return[0]==7:
        writeNumber(242)                            #kat 2
     
    elif alg_return[0]==8:
        writeNumber(242)
     
    elif alg_return[0]==9:
        writeNumber(242)
     
    elif alg_return[0]==10:
        writeNumber(242)
     
    elif alg_return[0]==11:
        writeNumber(242)
     
     
     
     
    elif alg_return[0]==12:                             
        writeNumber(243)                            #kat 3
     
    elif alg_return[0]==13:                                 
        writeNumber(243)
     
    elif alg_return[0]==14:
        writeNumber(243)
     
    elif alg_return[0]==15:
        writeNumber(243)
         
         
         
    elif alg_return[0]==16:
        writeNumber(244)                            #kat 4
         
    elif alg_return[0]==17:
        writeNumber(244)
         
    elif alg_return[0]==18:
        writeNumber(244)        
             
             
             
    elif alg_return[0]==19:
        writeNumber(245)                            #kat 5
     
    elif alg_return[0]==20:
        writeNumber(245)
     
    elif alg_return[0]==21:
        writeNumber(246)                            #kat 6
     
     
    #bulamazsa 0 yollar
     
    elif alg_return[0]==0:
        writeNumber(243)                            #kat 6
             
    else:                                                           #bi sey bulamazsa ortaya koy
        writeNumber(243)                                            #3. kattan birak, gripper kirilmasin
        last_center=board_target_center_x[9]
 
 
    sleep(1)
     
    ### targetin centerini arduinoya gonderme
     
     
     
    if last_center<507:
        writeNumber(250)                    #250 sag don
        print("gelen_board_saga_don:",readNumber())
        fark=int((512-last_center)/3)
        sleep(0.1)
        writeNumber(fark)
        print("answer_board_fark:",readNumber())
         
 
    elif last_center>517:
        writeNumber(251)                    #251 sol don
        print("gelen_board_sola_don:",readNumber())
        fark=int((last_center-512)/3)
        sleep(0.1)
        writeNumber(fark)
        print("answer_board_fark:",readNumber())
    else:
        writeNumber(252)                    #252 go go go
        print("gelen_board_go_go_go:",readNumber)
 
def alg_table(coming_sample):
     
    input_array=[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0, 0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  0,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  1,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  2,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  2,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  2,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  2,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  2,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 0,  2,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  0,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  1,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  1,  0,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  1,  2,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  1,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 1,  2,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  0,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  0,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  0,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  2,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  2,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [0, 2,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  0,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  1,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  1,  0,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  1,  1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  1,  2,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  1,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  1,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 0,  2,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  0,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  0,  0,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  0,  2,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  0,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  0,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  0,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  0,  2,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 1,  2,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  0,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  1,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  2,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  2,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  2,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  2,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [1, 2,  2,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  0,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  0,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  0,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  1,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  2,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  2,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 0,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  1,  2,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  0,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  1,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  1,  0,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  1,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  1,  0,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  1,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  1,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  1,  2,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  2,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  2,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  2,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  2,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  2,  1,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  2,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 1,  2,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 2,  0,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 2,  0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 2,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 2,  1,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 2,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 2,  1,  0,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 2,  1,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 2,  1,  1,  2,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [2, 2,  1,  2,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],     
        [0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,1,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [2,1,1,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,1,1,2,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [1,2,2,1,1,2,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [1,2,2,1,1,2,0,2,1,1,0,0,0,0,0,0,0,0,0,0,0],
        [1,2,2,1,1,2,0,2,0,1,1,0,0,0,1,0,0,0,0,0,0],
        [1,2,2,1,1,2,2,2,0,1,1,1,0,0,1,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,2,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,2,2,1,2,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,2,2,1,2,1,0,2,1,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,2,2,1,2,1,2,2,1,0,0,1,0,0,0,0,0,0,0,0,0],
        [1,2,2,1,2,1,2,2,1,0,0,0,1,0,0,0,0,0,0,0,0],
        [1,2,2,1,2,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
        [1,2,2,1,2,1,2,1,0,1,0,1,0,0,0,0,0,0,0,0,0]     
        ];
    output_array=[[3,0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [3, 0],
        [5, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [4, 0],
        [5, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [5, 0],
        [6, 0],
        [2, 0],
        [5, 0],
        [5, 0],
        [2, 0],
        [2, 0],
        [2, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [2, 0],
        [5, 0],
        [6, 0],
        [2, 0],
        [2, 0],
        [2, 1],
        [3, 0],
        [5, 0],
        [4, 0],
        [4, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [5, 0],
        [5, 0],
        [3, 0],
        [3, 0],
        [3, 1],
        [4, 0],
        [4, 0],
        [4, 1],
        [5, 0],
        [5, 1],
        [6, 1],
        [1, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 1],
        [5, 0],
        [5, 0],
        [1, 0],
        [6, 0],
        [1, 0],
        [5, 1],
        [9, 0],
        [9, 0],
        [9, 0],
        [3, 0],
        [3, 0],
        [4, 0],
        [3, 0],
        [5, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 1],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [5, 0],
        [5, 0],
        [6, 0],
        [1, 0],
        [5, 0],
        [6, 0],
        [4, 1],
        [1, 1],
        [1, 1],
        [5, 0],
        [2, 0],
        [4, 0],
        [4, 0],
        [5, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 1],
        [2, 0],
        [2, 0],
        [4, 1],
        [2, 0],
        [2, 0],
        [5, 1],
        [2, 0],
        [6, 1],
        [2, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 1],
        [2, 0],
        [2, 0],
        [2, 0],
        [2, 0],
        [2, 0],
        [2, 1],
        [2, 1],
        [2, 1],
        [3, 0],
        [3, 0],
        [3, 0],
        [4, 1],
        [3, 0],
        [5, 1],
        [3, 0],
        [3, 1],
        [3, 1],
        [3, 1],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 1],
        [4, 1],
        [5, 0],
        [6, 0],
        [9, 0],
        [5, 1],
        [5, 1],
        [6, 0],
        [9, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 1],
        [3, 1],
        [3, 1],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [5, 0],
        [6, 0],
        [9, 0],
        [9, 0],
        [5, 0],
        [5, 0],
        [6, 0],
        [9, 0],
        [10,0],
        [4, 0],
        [4, 1],
        [4, 1],
        [5, 0],
        [5, 0],
        [6, 0],
        [9, 0],
        [8, 0],
        [2, 0],
        [2, 0],
        [4, 0],
        [2, 0],
        [5, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [2, 0],
        [2, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [5, 0],
        [5, 0],
        [2, 0],
        [2, 0],
        [5, 0],
        [2, 0],
        [2, 0],
        [2, 0],
        [2, 1],
        [2, 1],
        [2, 1],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [3, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [5, 0],
        [5, 0],
        [6, 0],
        [9, 0],
        [9, 0],
        [4, 0],
        [4, 0],
        [4, 0],
        [5, 0],
        [5, 0],
        [6, 0],
        [9, 0],
        [9, 0],
        [9, 0],
        [3, 1],
        [3, 1],
        [3, 1],
        [4, 0],
        [4, 0],
        [4, 0],
        [5, 0],
        [5, 0],
        [9, 0],
        [9, 0],     
        [4,0],
        [3,0],
        [1,0],
        [6,0],
        [6,0],
        [2,0],
        [8,0],
        [13,1],
        [7,0],
        [9,0],
        [3,0],
        [2,0],
        [5,0],
        [8,0],
        [7,0],
        [13,1],
        [12,1],
        [7,0],
        [9,0] ];
     
     
     
    current_case=[coming_sample[0],coming_sample[1],coming_sample[2],coming_sample[3],
        coming_sample[4],coming_sample[5],coming_sample[6],coming_sample[7],
        coming_sample[8],coming_sample[9],coming_sample[10],coming_sample[11],
        coming_sample[12],coming_sample[13],coming_sample[14],coming_sample[15],
        coming_sample[16],coming_sample[17],coming_sample[18],coming_sample[19],
        coming_sample[20]]
     
     
    def_ret=[0,0]
     
    if(current_case in input_array):
        index=input_array.index(current_case)
        print ("return algoritma:",output_array[index])
        return(output_array[index])
    else:
        return (def_ret)
   
def renkcontrol():
     
     
    #red filter definitions
    par1_low_red=0
    par2_low_red=50
    par3_low_red=50
    par1_high_red=15
    par2_high_red=255
    par3_high_red=255
     
    #blue filter definitions
 
    par1_low_blue=65
    par2_low_blue=50
    par3_low_blue=50
    par1_high_blue=105
    par2_high_blue=255
    par3_high_blue=255
     
    GPIO.output(40,GPIO.HIGH)
    camera.capture('renkcontrol.png')
    #image=cv2.imread('image.png')
    GPIO.output(40,GPIO.LOW)
     
     
    frame=cv2.imread('renkcontrol.png')
     
    crop_frame=frame[50:400 , 300:700]
     
    cv2.imwrite("crop_frame.png", crop_frame)
     
     
     
    hsv = cv2.cvtColor(crop_frame,cv2.COLOR_BGR2HSV)
 
    lower_red = np.array([par1_low_red,par2_low_red,par3_low_red])
    upper_red = np.array([par1_high_red,par2_high_red,par3_high_red])
 
     
 
    lower_blue = np.array([par1_low_blue,par2_low_blue,par3_low_blue])
    upper_blue = np.array([par1_high_blue,par2_high_blue,par3_high_blue])
     
     
 
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
     
 
    #filtrelenmis resmi eski rengine donusturme
 
    mahmut_red=cv2.bitwise_and(crop_frame,crop_frame, mask=red_mask)
    mahmut_blue=cv2.bitwise_and(crop_frame,crop_frame, mask=blue_mask)
     
    #cv2.imwrite("mahmut_red.png",mahmut_red)
    #cv2.imwrite("mahmut_blue.png",mahmut_blue)
     
    #KIRMIZI RENK SORGULAMA
     
 
    resized_red = imutils.resize(mahmut_red, width=300)
    resized_blue = imutils.resize(mahmut_blue, width=300)
 
    ratio = mahmut_red.shape[0] / float(resized_red.shape[0])
     
    # blur the resized image slightly, then convert it to both
    # grayscale and the L*a*b* color spaces
 
 
    blurred_red = cv2.GaussianBlur(resized_red, (5, 5), 0)
    gray_red = cv2.cvtColor(blurred_red, cv2.COLOR_BGR2GRAY)
    lab_red = cv2.cvtColor(blurred_red, cv2.COLOR_BGR2LAB)
    thresh_red = cv2.threshold(gray_red, 60, 255, cv2.THRESH_BINARY)[1]
 
    # find contours in the thresholded image
    cnts9 = cv2.findContours(thresh_red.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts9 = cnts9[0] if imutils.is_cv2() else cnts9[1]
 
    # initialize the shape detector and color labeler
    sd = ShapeDetector()
    cl = ColorLabeler()
     
 
    # loop over the contours
    for c in cnts9:
            # compute the center of the contour
            M = cv2.moments(c)
            if M["m00"]!=0:
             
                cX = int((M["m10"] / M["m00"]) * ratio)
                cY = int((M["m01"] / M["m00"]) * ratio)
            area_red2=cv2.contourArea(c)
            if area_red2>400:
                # detect the shape of the contour and label the color
                shape = sd.detect(c)
                color = cl.label(lab_red, c)
                print(color)
                if color=="red":
                    writeNumber(247)
                    print("gelen_renkkontrol kirmizi:",readNumber())
                    return("red")               
         
                 
    #MAVi RENK SORGULAMA
    resized_blue = imutils.resize(mahmut_blue, width=300)
 
 
    ratio = mahmut_blue.shape[0] / float(resized_blue.shape[0])
 
    # blur the resized image slightly, then convert it to both
    # grayscale and the L*a*b* color spaces
 
 
 
 
    blurred_blue = cv2.GaussianBlur(resized_blue, (5, 5), 0)
    gray_blue = cv2.cvtColor(blurred_blue, cv2.COLOR_BGR2GRAY)
    lab_blue = cv2.cvtColor(blurred_blue, cv2.COLOR_BGR2LAB)
    thresh_blue = cv2.threshold(gray_blue, 60, 255, cv2.THRESH_BINARY)[1]
 
 
 
    # find contours in the thresholded image
    cnts10 = cv2.findContours(thresh_blue.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
    cnts10 = cnts10[0] if imutils.is_cv2() else cnts10[1]
 
    # initialize the shape detector and color labeler
    sd = ShapeDetector()
    cl = ColorLabeler()
 
    # loop over the contours
    for c in cnts10:
            # compute the center of the contour
            M = cv2.moments(c)
            if M["m00"]!=0:
                 
                cX = int((M["m10"] / M["m00"]) * ratio)                         
                cY = int((M["m01"] / M["m00"]) * ratio)
                area_blue=cv2.contourArea(c)
                if area_blue>400:    
                    # detect the shape of the contour and label the color
                    shape = sd.detect(c)
                    color = cl.label(lab_red, c)
                    print(color)
                    if color=="blue":
                        writeNumber(248)
                        print("gelen_renkkontrol mavi:",readNumber())
                        return("blue")  
      
def gofirstflag():
	placed_block=False
	while placed_block==False:
		print("101 beklim")
        #arduinodan blocku biraktim haberi bekle            
        if(arduino_read()==(1,0,1)):
            GPIO.output(15,GPIO.HIGH)
            placed_block=True
            flag_arduinodata()              #1.flage git
            GPIO.output(15,GPIO.LOW)     

def gosecondflag():
	gripped_block=False
	not_gripped_block=True
	while gripped_block==False and not_gripped_block==False:
        print("011 beklim")
        #arduinodan block aldim haberi bekle        
        if(arduino_read()==(0,1,1)):
            GPIO.output(18,GPIO.HIGH)
            gripped_block=True
            flag_arduinodata()              #2. kez flage git
            GPIO.output(18,GPIO.LOW)
            
        if(arduino_read()==(1,0,0)):		#block dustu  
            not_gripped_block=True
             
def goblock():
	arrived_flag1=False
	 while arrived_flag1==False:
        print(arduino_read())   
        #arduinodan 1. flage gittim haberi bekle            
        if(arduino_read()==(0,0,1)):
            GPIO.output(22,GPIO.HIGH)           #en soldaki ledi yak
            block_renk=block_arduinodata()              #blocka git 
            GPIO.output(22,GPIO.LOW)            #en soldaki ledi sondur
            arrived_flag1=True            

def saricontrol():
	renk_kontrol=False
	while renk_kontrol==False:
            if (arduino_read()==(1,1,1)):       
                GPIO.output(18,GPIO.HIGH)
                print("111 geldi renkcontrol yapacam")
                renk_kontrol=True
                renkcontrol()
                print("renk kontrol yaptim")
                GPIO.output(18,GPIO.LOW)            

def goboard():
	while arrived_flag2==False and not_gripped_block==False:
		print("010 beklim")
        #arduinodan flage 2. kez gittim haberi bekle            
        if(arduino_read()==(0,1,0)):
            GPIO.output(16,GPIO.HIGH)
            arrived_flag2=True
            boardkarsinagec()					#board karsisina gec
            GPIO.output(16,GPIO.LOW)
        if(arduino_read()==(1,0,0)):		#block dustu  
            not_gripped_block=True

def placeit():
	while board_tamkarsi==False and not_gripped_block=True:
		print("110 beklim")
		#arduinodan board karsisina gectim haberi bekle            
        if(arduino_read()==(1,1,0)):
            GPIO.output(16,GPIO.HIGH)
            board_tamkarsi=True
            placeblock()                        #block yerlestir
            GPIO.output(16,GPIO.LOW)
        if(arduino_read()==(1,0,0)):		#block dustu  
            not_gripped_block=True
                           
while win_game==False:              #oyunu kazanana kadar oyna
     
         
    arrived_flag1=False
    arrived_flag2=False
    renk_kontrol=False
    gripped_block=False
    placed_block=False
     
     
    if startgame==False: 
		flag_arduinodata()              #(step1)1.flage git (1 kereligine)
		startgame=True
		nextstep=2
         
    if nextstep==2:
		goblock()							#(step2)blocka git  
		nextstep=3
		if block_renk=="yellow square":		#(step2.1)sariysa renk kontrol et
			saricontrol()
    
    if nextstep==3:
		gosecondflag()						#(step 3)2. flage git 
		nextstep=4
		if(not_gripped_block==True)			#eger dustuyse step 2 ye don
			nextstep=2
    
	if nextstep==4:
		goboard()							#(step 4) board karsisina gec
		nextstep=5
		if (not_gripped_block==True)		#eger dustuyse step 2 ye don
			nextstep=2
	
	if nextstep==5:
		placeit()							#(step 5) blocku yerlestir
		nextstep=1
		if (not_gripped_block==True)		#eger dustuyse step 2 ye don
			nextstep=2
	if nextstep==1:
		gofirstflag()						#(step 1) basa don
		nextstep=2
     
     
print("Ankaranin baglari")  
