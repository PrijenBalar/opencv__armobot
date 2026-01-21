import cv2
import numpy as np


#video capture
vc = cv2.VideoCapture(0)

#read video capture
while cv2.waitKey(1) <0 :
    hasFrame, frame = vc.read()
    print(hasFrame)
    print(frame)

#fixed size the web cam
    frame = frame[0:800,0:800]

#resize the frame
    frame = cv2.resize(frame,(100,100))

    height, width ,depth = frame.shape

    for h in range(height):
        for w in range(width):
            for d in range(depth):
                frame[h,w,d] = 144-frame[h,w,d]

    frame = cv2.resize(frame, (500, 500),interpolation = cv2.INTER_NEAREST)
    cv2.putText(frame, "WEB CAM MEME", (5,25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1 )

    cv2.imshow("meme",frame)

answer = input("Do you want to save the meme?")
if answer.lower() == "yes":
    name = input("Name of your meme :")+".jpg"
    cv2.imwrite(name, frame)
    print("Meme saved successfully!")
else:
    print("Okay Thank You — meme not saved.")
