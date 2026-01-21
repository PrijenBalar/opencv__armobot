import cv2
import numpy as np

#loading the image
image = cv2.imread("blinking_guy.jpg")
print(image.shape)

#seting the opencv window
cv2.namedWindow("meme_window", cv2.WINDOW_NORMAL)
cv2.resizeWindow("meme_window", 1000, 500)

#adding text:cv2.putText(image,text,(x,y),font,font_scale,color,line_thickness)
cv2.putText(image,"This is MEME Text",(0,15),cv2.FONT_ITALIC,0.5,(0,0,0),2)
cv2.putText(image,"This is MEME Text",(0,15),cv2.FONT_ITALIC,0.5,(255,255,255),1)

#convert image color format and color scheme
print(image[0,0])
#print(image[0,0])
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
print(image[0,0])
image = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
print(image[0,0])

#displaying the image
cv2.imshow("meme_window", image)
cv2.waitKey(0)

#save your meme
answer = input("Do you want save the meme? (yes/no)")
if answer.lower()== "yes":
    name = input("Name your meme: ")+".jpg"
    cv2.imwrite(name, image)
    print("Meme saved successfully!")
else:
    print("Okay Thank You — meme not saved.")

