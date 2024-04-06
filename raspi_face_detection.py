import cv2 as cv
from picamera2 import Picamera2
from buildhat import Motor
from buildhat import MotorPair

camot = Motor('D')          # camera motor
pimot = Motor('C')          # pivot motor
pair = MotorPair('A', 'B')  # movement/driving motor

picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280,720)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()

card = 0
max_amplitude_motpiv = 0
amplitude_motcam_high = 0
amplitude_motcam_low = 0

haar_cascade = cv.CascadeClassifier('/home/amael/haar_face.xml') # path to file (this part only work on raspberry-pi)
height, width = 720, 1280 # resolution of picamera2
min_tolerance = (min(height, width) // 2) - 4


print(f"Before specifying a tolerance for tracking, please ensure it does not exceed half of the height or width of your screen. Additionally, avoid selecting a tolerance that lands exactly at the middle of the lower dimension to form a non-line rectangle. Your current resolution is {height} pixels (height) and {width} pixels (width).")
print(f"The minimum tolerance value you can enter is {min_tolerance} pixels. (Disclaimer: You're correct that this may not exactly be half of the screen, but we've hardcoded a minimum 4-pixel width/height for the rectangle.)")

tole = input(f"What tolerance (in pixels) would you like to set? -> ")
corx, cory = int(tole), int(tole)

while True:
    frame = picam2.capture_array()
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    face_rect = haar_cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=4, minSize=(80,80)) # function to tweak for the quality and conditions of object detection
    
    # Trace boundary
    cv.rectangle(frame, (corx, cory), (width-corx, height-cory), (0, 255, 255), 3)

    # Trace the 4 corners
    cv.rectangle(frame, (0, 0), (corx, cory), (255, 255, 0), 2)
    cv.rectangle(frame, (0,  height-cory), (corx, height), (255, 255, 0), 2)
    cv.rectangle(frame, (width-corx,  0), (width, cory), (255, 255, 0), 2)
    cv.rectangle(frame, (width-corx,  height-cory), (width, height), (255, 255, 0), 2)

    for (x,y,w,h) in face_rect:
        # Trace moving entities
        cv.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)
        cv.circle(frame, (x + (w // 2), y + (h // 2)), 1, (255, 255, 0), 4)

        '''
# asserting position using the rectangle tracing points (Archive)

        if x < corx :
            print('LEFT')
        if y < cory:
            print('UP')
        if x + w > width-corx:
            print('RIGHT')
        if y + h > height-cory:
            print('DOWN')
        '''

# asserting position by the center of the area drawn by the detected object 

        pos = -1 # error signal / no object detected
        
        if x + (w // 2) > corx and y + (h // 2) > cory and x + (w // 2) < width-corx and  y + (h // 2) < height-cory:
            
            lr1_mot, lr2_mot = 0, 0
            up1_mot, up2_mot = 0, 0
             
            if pimot.get_aposition() > 0: # if camera is tilted to the right - instruction for movement motor to correct heading (turning right)
                # first motor negative degrees
                lr1_mot = (10 * max_amplitude_motpiv * 2) * (-1)
                # second motor positive degrees
                lr2_mot = (10 * max_amplitude_motpiv * 2)
                
            elif pimot.get_aposition() < 0: # if camera is tilted to the left - instruction for movement motor to correct heading (turning left)
                # first motor positive degrees and second motor positive degrees
                # When camera turn x degrees motor movement must turn for 2x (experimental values -> is currently working on)

                lr1_mot = 10 * max_amplitude_motpiv * 2
                lr2_mot = 10 * max_amplitude_motpiv * 2
           
            ''' 
            #If unindexed that part make the robot react when target is up or down from the boundaries area by either reversing or advancing

            if camot.get_aposition() > 0: # camera look up
                up1_mot = -30
                up2_mot = -30
                
            elif camot.get_aposition() < 0: # camera look down
                up1_mot = 30
                up2_mot = 30
            '''
             
            print('// AllRobot Alignment To Target')

            '''
            # Optional additional informations

            print(pimot.get_aposition(), ' = pos. abs. deg. motor C')
            print(camot.get_aposition(), ' = pos. abs. deg. motor D')
            print(max_amplitude_motcam_high,'//', max_amplitude_motcam_low, ' = cam slope (first = 0 -> h, second = 0 -> l')
            '''
            
            pimot.run_to_position(0)
            max_amplitude_motpiv = 0
            
            if lr1_mot != 0 or lr2_mot != 0:    
                pair.run_for_degrees(lr1_mot, lr2_mot) #execute turn
                
            if up1_mot != 0 or up2_mot != 0:    
                pair.run_for_degrees(up1_mot, up2_mot) #execute retreat to take distance or advance to close the gap 
                
            pos = 0

# secondary positions instructions
            
        elif x + (w // 2) < corx and y + (h // 2) < cory:
            print('LeftUP')
            pos = 5

        elif x + (w // 2) > width-corx and y + (h // 2) < cory:
            print('RightUp')
            pos = 6

        elif x + (w // 2) < corx and y + (h // 2) > height-cory:
            print('LeftDown')
            pos = 7

        elif x + (w // 2) > width-corx and y + (h // 2) > height-cory:
            print('RightDown')
            pos = 8

# main positions instructions
            
        elif x + (w // 2) < corx : # left
            
            if max_amplitude_motpiv <= 6:
                pimot.run_for_degrees(-10)
                max_amplitude_motpiv += 1
            elif max_amplitude_motpiv >= 6:
                pimot.run_to_position(0)
                max_amplitude_motpiv = 0
                pair.run_for_degrees(-30, 30)
                
            pos = 4
            
        elif y + (h // 2) < cory: # up
            
            if amplitude_motcam_high <= 25:
                camot.run_for_degrees(5)
                amplitude_motcam_high += 1
                amplitude_motcam_low -= 1
            elif amplitude_motcam_high >= 25:
                camot.run_to_position(0, 10)
                amplitude_motcam_high = 0
                amplitude_motcam_low = 0
                pair.run_for_degrees(-90, -90, 10)

            pos = 1
            
        elif x + (w // 2) > width-corx: # right
            
            if max_amplitude_motpiv <= 6:
                pimot.run_for_degrees(10)
                max_amplitude_motpiv += 1
            elif max_amplitude_motpiv >= 6:
                pimot.run_to_position(0)
                max_amplitude_motpiv = 0
                pair.run_for_degrees(30, 30)
                
            pos = 3
            
        elif y + (h // 2) > height-cory: # down
            
            if amplitude_motcam_low <= 25:
                camot.run_for_degrees(-5)
                amplitude_motcam_low += 1
                amplitude_motcam_high -= 1
            elif amplitude_motcam_low >= 25:
                camot.run_to_position(0, 10)
                amplitude_motcam_low = 0
                amplitude_motcam_high = 0
                pair.run_for_degrees(90, -90, 10)
              
            pos = 2
            
            
        if pos != card:
            print(pos, ' = direction-index')
            card = pos
        elif pos == card:
            card = pos

        cv.imshow(f'Livetracking- Tol={tole}-Y=center_detection-O=boundaries_set-G=zone_det (q=quit)', frame)

    if cv.waitKey (20) & 0xFF==ord('q'):
        pimot.run_to_position(0)
        camot.run_to_position(0)
        pair.run_to_position(0,0)
        print('End Of Process')
        break

cv.destroyAllWindows()
