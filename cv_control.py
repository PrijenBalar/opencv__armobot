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
    arm.move_joint(1,20)
    arm.move_joint(2, 23)
    arm.move_joint(3,25)

    time.sleep(1)
    arm.move_joint(1,-20)
    arm.move_joint(2, -23)
    arm.move_joint(3,-25)

    time.sleep(1)



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
