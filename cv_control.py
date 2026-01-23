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
    target = 40
    arm.move_joint(3, target)

    done = False

    while not done:
        pos = arm.get_current_position()  # may raise or return None
        print(pos)
        time.sleep(0.3)
        print(((pos["joint3"]) - target))

        if (abs((pos["joint3"]) - target)) <= 1.1:
            done = True

    arm.set_stepper_delay(num=3, delay=1000)
    arm.move_joint(3, -10)


    time.sleep(10)


    # arm.set_stepper_delay(num=1, delay=4000)
    # arm.set_stepper_delay(num=2, delay=4000)
    # arm.set_stepper_delay(num=3, delay=4000)

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
