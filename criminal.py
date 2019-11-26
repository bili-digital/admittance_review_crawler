import os
import pytesseract
import logging 
import urllib.request as urllib2
import time
import pymysql
import base64
import requests
import re
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup 
from dotenv import load_dotenv

load_dotenv()

class CriminalCrawler():

    def __init__(self, model, db, driver, name, id_number, tenant_id):
        self.driver= driver
        self.name = name
        self.id_number = id_number
        self.tenant_id = tenant_id
        self.db = db
        self.model = model

      # logging.basicConfig(level=logging.DEBUG, 
      #              format='%(asctime)s - %(levelname)s : %(message)s', 
      #              filename='criminal_record.log') 

    def get_captcha(self, driver):
        img = driver.find_element_by_xpath(".//*[@id='imgCaptcha']")
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
        name = driver.find_element_by_name("txtname")
        name.clear()
        name.send_keys(self.name)
        id_number = driver.find_element_by_name("txtId")
        id_number.clear()
        id_number.send_keys(self.id_number)
        answer = driver.find_element_by_name("txtCaptcha")
        answer.clear()
        answer.send_keys(captcha)
        submit = driver.find_element_by_name("submit")
        submit.click()
        time.sleep(2)
        alert = driver.switch_to.alert

        return alert

    def parse_date(self, date):
        date_list = date.split('.')
        date_list[0] = str(int(date_list[0]) + 1911)
        return date_list[0] + '-' + date_list[1] + '-' + date_list[2]

    def run(self):
        try:
            self.driver.get('''http://service.moj.gov.tw/criminal/index.asp''')
            checkbox = self.driver.find_element_by_name("doChk")
            checkbox.click()
            button = self.driver.find_element_by_name("cmdQuery")
            button.click()
            time.sleep(2)

            captcha = self.get_captcha(self.driver)
            # logging.info("captcha is " + captcha)  
            alert = self.fill_data(self.driver, captcha)
            print(alert.text)
            if(alert.text == '無符合的通緝犯'):
                alert.accept()
                self.model.create(status="normal", tenant_id=self.tenant_id)
            else:
                alert.accept()
                self.model.create(status="abnormal", tenant_id=self.tenant_id)  
            # logging.info("Criminal Record Crawler Finished")             
            return True
        except Exception as e:
            self.model.create(status="abnormal", tenant_id=self.tenant_id)  
            # logging.error("error: " + str(e))
            print(e)
            return False