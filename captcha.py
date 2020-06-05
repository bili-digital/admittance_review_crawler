import os
import base64
import requests
import time
from io import BytesIO
from PIL import Image


class Captcha():
    def __init__(self, driver, img_element):
        self.driver = driver
        self.img_element = img_element

    def parse(self):
        try: 
            img = self.driver.find_element_by_xpath(".//*[@id='pickimg1']")
            with open('captcha.png', 'wb') as file:
                file.write(img.screenshot_as_png)   
          # logging.info("Save Image")  
            buffer = BytesIO()
            image = Image.open('captcha.png')
            image.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")     

            data = {
                "clientKey": os.getenv("ANTI_CAPTCHA_KEY"),
                "task": {
                    "type": "ImageToTextTask",
                    "body": img_str,
                    "phrase":False,
                    "case": True,
                    "numeric": 2,
                    "math": 0,
                    "minLength": 4,
                    "maxLength": 4
                }
            }
            r = requests.post("https://api.anti-captcha.com/createTask", json=data)
            r.raise_for_status()
            print(r.json())
            if r.json()['errorId'] == 2:
              print(r.json())
              self.parse()
            else:
              task_id = r.json()['taskId']
              ret = ""
              while True:
                  data = {
                      "clientKey": os.getenv("ANTI_CAPTCHA_KEY"),
                      'taskId': task_id
                  }
                  r = requests.post("https://api.anti-captcha.com/getTaskResult", json=data)
                  r.raise_for_status()
                  if r.json()['status'] == 'ready':
                      ret = r.json()['solution']['text']
                      break
                  print('trying')
                # logging.info("tring")  
                  time.sleep(5)
              return ret
        except:
            raise AttributeError('captcha error')

