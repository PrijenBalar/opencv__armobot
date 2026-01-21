import cv2
import mediapipe as mp
import time
import requests
import math

class CameraVision:
    def __init__(self , url = 0):
        self.url = url
        self.cap = cv2.VideoCapture(url)
        self.frame = None

    def read(self):
        ret, frame = self.cap.read()
        self.frame = frame

        return frame
    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def show(self):
        if self.frame is not None:
            cv2.imshow("Cam " + str(self.url), self.frame)

