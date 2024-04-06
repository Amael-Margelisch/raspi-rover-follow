import cv2 as cv

capture = cv.VideoCapture(0)
haar_cascade = cv.CascadeClassifier('haar_face.xml')
isTrue, frame = capture.read()
height, width = frame.shape[:2]
min_tolerance = (min(height, width) // 2) - 4

print(f"Before specifying a tolerance for tracking, please ensure it does not exceed half of the height or width of your screen. Additionally, avoid selecting a tolerance that lands exactly at the middle of the lower dimension to form a non-line rectangle. Your current resolution is {height} pixels (height) and {width} pixels (width).")
print(f"The minimum tolerance value you can enter is {min_tolerance} pixels. (Disclaimer: You're correct that this may not exactly be half of the screen, but we've hardcoded a minimum 4-pixel width/height for the rectangle.)")

tole = input(f"What tolerance (in pixels) would you like to set? ")
corx, cory = int(tole), int(tole)
card = 0

while True:
    
    isTrue, frame = capture.read()
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    face_rect = haar_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5, minSize=(150,150))

    # Trace boundary
    cv.rectangle(frame, (corx, cory), (width-corx, height-cory), (0, 128, 255), 2)

    # Trace corners
    cv.rectangle(frame, (0, 0), (corx, cory), (0, 255, 0), 2)
    cv.rectangle(frame, (0,  height-cory), (corx, height), (0, 255, 0), 2)
    cv.rectangle(frame, (width-corx,  0), (width, cory), (0, 255, 0), 2)
    cv.rectangle(frame, (width-corx,  height-cory), (width, height), (0, 255, 0), 2)

    for (x,y,w,h) in face_rect:

        # Trace moving entities
        cv.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 1)
        cv.circle(frame, (x + (w // 2), y + (h // 2)), 1, (0, 212, 255), 4)

        '''
# asserting position using the rectangle tracing points (Archive)

        if x < corx :
            print('LEFT')d
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
            #print('Center)
            pos = 0

        elif x + (w // 2) < corx and y + (h // 2) < cory:
            #print('LeftUP')
            pos = 5

        elif x + (w // 2) > width-corx and y + (h // 2) < cory:
            #print('RightUp')
            pos = 6

        elif x + (w // 2) < corx and y + (h // 2) > height-cory:
            #print('LeftDown')
            pos = 7

        elif x + (w // 2) > width-corx and y + (h // 2) > height-cory:
            #print('RightDown')
            pos = 8

        elif x + (w // 2) < corx :
            #print('LEFT')
            pos = 4

        elif y + (h // 2) < cory:
            #print('UP')
            pos = 1

        elif x + (w // 2) > width-corx:
            #print('RIGHT')
            pos = 3

        elif y + (h // 2) > height-cory:
            #print('DOWN')
            pos = 2
            
        if pos != card:
            print(pos)
            card = pos
        elif pos == card:
            card = pos

        cv.imshow(f'Livetracking- Tol={tole}-Y=center_detection-O=boundaries_set_Tol-P=zone_det (q=quit)', frame)

    if cv.waitKey (20) & 0xFF==ord('q'):
        break

capture.release()
cv.destroyAllWindows()

cv.waitKey(0)
