import os
import pytesseract
import logging 
import urllib.request as urllib2
import time
import pymysql
import base64
import requests
import traceback
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class WantedCrawler():
    def __init__(self, model, db, driver, name, id_number, tenant_id):
        self.db = db
        self.model = model
        self.driver = driver
        self.name = name
        self.id_number = id_number
        self.tenant_id = tenant_id


      # logging.basicConfig(level=logging.DEBUG, 
      #                      format='%(asctime)s - %(levelname)s : %(message)s', 
      #                      filename='wanted.log') 

    def get_captcha(self, driver):
        img = driver.find_element_by_xpath(".//*[@id='reload-img']")
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
          # logging.info("tring")  
            time.sleep(5)
            print('tring')
        return ret

    def fill_data(self, driver, captcha):
        wanted_name = driver.find_element_by_id("QS_NAME")
        wanted_id = driver.find_element_by_id("QS_ID")
        answer = driver.find_element_by_id("answer")

        wanted_name.clear()
        wanted_id.clear()
        answer.clear()
        print(captcha)
        wanted_name.send_keys(self.name)
        wanted_id.send_keys(self.id_number)
        answer.send_keys(captcha)

        driver.find_element_by_id("queryBtn").click()

      # logging.info("Submit form")
        time.sleep(2)
        elements = driver.find_elements_by_xpath("//*[contains(text(), 'Ok')]")
        return elements
    def run(self):
        try:
            self.driver.get('''https://iweb2.npa.gov.tw/NpaE8Server/CE_Query.jsp''')
            captcha = self.get_captcha(self.driver)
          # logging.info("captcha is " + captcha)  
            elements = self.fill_data(self.driver, captcha)
            time.sleep(1)

            count = 0
            while len(elements) != 0 and count <= 5:
              # logging.info("retry Submit form")
              # logging.info("No. " + str(count))
                self.driver.find_element_by_id("smartAlertClose").click()
                time.sleep(1)
                captcha = self.get_captcha(self.driver)
              # logging.info("new captcha is " + captcha)
                elements = self.fill_data(self.driver, captcha)
                count+=1

            result = self.driver.find_element_by_id('E8_WT_UNIT_NM').text
            self.model.create(status=result, tenant_id=self.tenant_id)
          # logging.info("Wanted Finished")
            return True

        except Exception:
          # logging.error("error: " + str(e))
            lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
            print(lastCallStack)
            return False
    
