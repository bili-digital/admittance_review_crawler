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
from datetime import datetime

class MissingPersonCrawler():
    def __init__(self, model, db, driver, name, id_number, tenant_id):
        self.db = db
        self.model = model
        self.driver = driver
        self.name = name
        self.id_number = id_number
        self.tenant_id = tenant_id

    def get_captcha(self, driver):
        img = driver.find_element_by_xpath(".//*[@id='reload-img']")
        with open('captcha.png', 'wb') as file:
            file.write(img.screenshot_as_png)
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
            time.sleep(5)
            print('tring')
        return ret

    def fill_data(self, driver, captcha):
        name = driver.find_element_by_id("QS_NAME")
        id_number = driver.find_element_by_id("QS_ID")
        answer = driver.find_element_by_id("answer")

        name.clear()
        id_number.clear()
        answer.clear()
        name.send_keys(self.name or '')
        id_number.send_keys(self.id_number or '')
        answer.send_keys(captcha)

        driver.find_element_by_id("queryBtn").click()

        time.sleep(5)
        elements = driver.find_elements_by_xpath("//*[contains(text(), '驗證碼輸入錯誤')]")
        return elements
    def run(self):
        try:
            print('missing person start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''https://iweb2.npa.gov.tw/NpaE8Server/NK_Query.jsp''')
            captcha = self.get_captcha(self.driver) 
            elements = self.fill_data(self.driver, captcha)
            time.sleep(1)
            count = 0
            while len(elements) != 0 and count <= 5:
                buttons = self.driver.find_elements_by_class_name("btn.btn-default")
                buttons[-1].click()
                time.sleep(1)
                captcha = self.get_captcha(self.driver)
                elements = self.fill_data(self.driver, captcha)
                count+=1
            
            result = self.driver.find_element_by_id('tabResult').text
            if result.find('符合查詢資料共0筆') != -1:
              status = '查無資料'
            else:
              status = '有失蹤紀錄'
            self.model.create(status=status, tenant_id=self.tenant_id)
            return True

        except Exception:
            print(traceback.format_exc())
            return False
    
