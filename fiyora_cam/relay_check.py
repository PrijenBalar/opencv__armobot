import requests
import time
url = "http://192.168.0.205"


while True:
    response = requests.get(url + "/on")
    print(response.status_code)
    print(response.text)

    time.sleep(0.5)

    res = requests.get(url + "/off")
    print(res.status_code)
    print(res.text)
    time.sleep(0.5)


