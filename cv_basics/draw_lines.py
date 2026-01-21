import cv2

image = cv2.imread("images/mike.jpg")
image = cv2.resize(image,(500,500))
cv2.line(image,(190,100),(310,103),(0,0,0),2)
cv2.imshow("mike",image)
cv2.waitKey(0)