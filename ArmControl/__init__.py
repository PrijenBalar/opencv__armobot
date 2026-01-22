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

    def move_joint(self,num=0,angle=0):
        end_point = "stepper?num="+ str(num) +"&angle=" + str(angle)
        url = self.base_url + end_point
        response = requests.get(url)
        return response

    def get_current_position(self):




        requests.post(f"{BASE_URL}/stepper?num=2&angle={angle}", timeout=5)

