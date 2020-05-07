import os
import pytesseract
import logging 
import urllib.request as urllib2
import time
import pymysql
import base64
import requests
import re
import traceback
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup 
from dotenv import load_dotenv
from datetime import datetime

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
        img = driver.find_element_by_xpath(".//*[@id='valiCode']")
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
        name = driver.find_element_by_name("CriminalName")
        name.clear()
        name.send_keys(self.name or '')
        id_number = driver.find_element_by_name("CriminalIdNo")
        id_number.clear()
        id_number.send_keys(self.id_number or '')
        answer = driver.find_element_by_name("WaitValidateCode")
        answer.clear()
        answer.send_keys(captcha)
        submit = driver.find_element_by_id("QueryButton")
        submit.click()
        time.sleep(1)
        alert = driver.switch_to.alert

        return alert

    def parse_date(self, date):
        date_list = date.split('.')
        date_list[0] = str(int(date_list[0]) + 1911)
        return date_list[0] + '-' + date_list[1] + '-' + date_list[2]

    def run(self):
        try:
            print('crawler start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''https://service.moj.gov.tw/CriminalWanted''')
            checkbox = self.driver.find_element_by_xpath('//label[@for="PrecautionsAccepted"]')
            checkbox.click()
            time.sleep(1)

            captcha = self.get_captcha(self.driver)
            # logging.info("captcha is " + captcha)  
            alert = self.fill_data(self.driver, captcha)
            count = 0
            while alert.text == '驗證碼不正確!' and count <= 5:
              # logging.info("retry Submit form")
              # logging.info("No. " + str(count))
                time.sleep(1)
                alert.accept() 
                captcha = self.get_captcha(self.driver)
              # logging.info("new captcha is " + captcha)
                alert = self.fill_data(self.driver, captcha)
                count+=1
                print(alert.text)

            print(alert.text)
            if(alert.text == '查無資料'):
                alert.accept()
                self.model.create(status="normal", tenant_id=self.tenant_id)
            else:
                alert.accept()
                self.model.create(status="abnormal", tenant_id=self.tenant_id)  
            # logging.info("Criminal Record Crawler Finished")             
            return True
        except Exception:
            self.model.create(status="abnormal", tenant_id=self.tenant_id) 
            # logging.error("error: " + str(e))
            lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
            print(lastCallStack)
            return False