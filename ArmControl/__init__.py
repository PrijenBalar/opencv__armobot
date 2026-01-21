import requests


class ArmControl:
    def __init__(self, url = "http://192.168.4.1/"):
        self.base_url = url
        model = "Niryo"
        print("Arm Control")

    def open_gripper(self):
        end_point = "gripper?action=open"

        url = self.base_url + end_point
        response = requests.get(url)
        return response

    def close_gripper(self):
        end_point = "gripper?action=close"

        url = self.base_url + end_point
        response = requests.get(url)
        return response

