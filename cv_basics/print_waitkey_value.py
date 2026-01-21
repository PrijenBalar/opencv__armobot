import cv2

vc = cv2.VideoCapture(0)

while True:
    ret, frame = vc.read()
    key = cv2.waitKey(1)
    key_text = str(key)
    cv2.putText(frame,"Key value is :"+key_text,(0,15),cv2.FONT_ITALIC,0.5,(0,0,0),2)
    cv2.imshow("frame",frame)
    if key==27:
        break