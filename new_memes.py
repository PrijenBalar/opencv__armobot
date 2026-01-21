import cv2
import numpy as np

image = cv2.imread("mike.jpg")

height,width,channels = image.shape
#image[y,x,z]
for h in range(height):
    for w in range(width):
        for c in range(channels):
            #print("Before Change",image[h,w,c])
            image[h,w,c] = 255 - image[h,w,c]
            #print("After Change",image[h,w,c])

image = cv2.resize(image,(500,500),interpolation = cv2.INTER_NEAREST)
cv2.putText(image,"New MEME",(170,480),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2)

cv2.imshow("Mike MEME",image)
cv2.waitKey(0)