import cv2
import numpy as np

image = cv2.imread("images/mike.jpg")
cv2.imshow("mike",image)

blur = cv2.GaussianBlur(image, (23,23), 0)
cv2.imshow("blur",blur)

cv2.waitKey(0)