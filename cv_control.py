from ArmControl import ArmControl
from CameraVision import CameraVision
import numpy as np
import cv2
import time
import requests



arms = [
    {
        "name": "Arm1",
        "url": "http://192.168.4.1/",
    },

]


cameras = [
    {
        "name": "Cam1",
        "url": 0,
    },
    {
        "name": "Cam2",
        "url": 1,
    }
]

for arm in arms:
    arm = ArmControl(arm["url"])
    print(arm.base_url)
    arm.set_stepper_delay(num=3, delay=2000)
    arm.move_joint(3, 500)

    time.sleep(10)
    arm.set_stepper_delay(num=3, delay=1000)
    arm.move_joint(3, 10)


    time.sleep(10)



# camvis = []
# for camera in cameras:
#     camvis.append(CameraVision(camera["url"]))
#
# while True:
#     for camvi in camvis:
#         camvi.read()
#         camvi.show()
#
#
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         for camvi in camvis:
#             camvi.release()
#         break
#
#
