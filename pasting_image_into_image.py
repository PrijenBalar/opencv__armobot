import cv2
import numpy as np


vc = cv2.VideoCapture(0)
hasFrame,frame = vc.read()
height,width,depth = frame.shape
print("FRAME SHAPE :",width,height)
frame = frame[105:-60,100:-135]


memeImage = cv2.imread("stonks.jpg")
memeImage = cv2.resize(memeImage,(150,100))
memeHeight,memeWidth,memeDepth = memeImage.shape
print("MEME SHAPE :",memeWidth,memeHeight)

indentY = 100
indentX = 50

while cv2.waitKey(1) < 0:
    hasFrame,frame = vc.read()
    frame = frame[0:-60,100:-135]
    frame[indentY:indentY+memeHeight,indentX:indentX+memeWidth]=memeImage

    cv2.imshow("Frame",frame)

answer = input("Do you want to save the meme?")
if answer.lower() == "yes":
    name = input("Name of your meme :")+".jpg"
    cv2.imwrite(name, frame)
    print("Meme saved successfully!")
else:
    print("Okay Thank You — meme not saved.")
