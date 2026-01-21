import cv2

image = cv2.imread("images/mike.jpg")
image = cv2.resize(image,(500,500))
cv2.rectangle(image,(170,95),(320,220),(0,0,0),2)
cv2.imshow("mike",image)
cv2.waitKey(0)