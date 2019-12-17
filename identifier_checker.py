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

class IdentifierChecker():

    def __init__(self, db, driver, id_number, birthday):
        self.db = db
        self.driver = driver
        self.id_number = id_number
        self.birthday = birthday

      # logging.basicConfig(level=logging.DEBUG, 
      #              format='%(asctime)s - %(levelname)s : %(message)s', 
      #              filename='fuel_penalty.log') 

    def get_captcha(self, driver):
        img = driver.find_element_by_xpath(".//*[@id='pickimg1']")
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
        return ret
    def parse_date(self, date):
        date_list = re.split('年|月|日',date)
        date_list[0] = str(int(date_list[0]) + 1911)
        if int(date_list[1]) < 10:
            date_list[1] = '0' + str(date_list[1])
        if int(date_list[2]) < 10:
            date_list[2] = '0' + str(date_list[2])

        return date_list[0] + '-' + date_list[1] + '-' + date_list[2]
    def fill_fuel_data(self, driver, captcha):
        id_number = driver.find_element_by_id("idNo")
        birthday = driver.find_element_by_id("birthday")
        answer = driver.find_element_by_name("validateStr")

        id_number.clear()
        birthday.clear()
        answer.clear()
        id_number.send_keys(self.id_number)
        birthday.send_keys(self.birthday)
        answer.send_keys(captcha)
        # remove datepicker ui
        time.sleep(2)
        driver.find_element_by_id("pickimg1").click()
        time.sleep(2)
        driver.find_element_by_id("submit_btn").click()
      # logging.info("Submit form")
        time.sleep(1)
        captcha_error = len(driver.find_elements_by_xpath("//*[contains(text(), '驗證碼輸入錯誤')]"))
        if len(driver.find_elements_by_id("idNo-error")) != 0:
          if driver.find_elements_by_id("idNo-error")[0].text == '身分證或居留證格式錯誤':
            data_error = 1
          else:
            data_error = 0
        elif len(driver.find_elements_by_xpath("//*[contains(text(), '請確認您輸入的證號及生日是否正確。')]")):
          data_error = 1
        else:
          data_error = 0        
        return captcha_error, data_error
    def run(self):
        try:
            print('identifier start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''https://www.mvdis.gov.tw/m3-emv-fee/fee/fuelFee''')
            captcha = self.get_captcha(self.driver)
          # logging.info("captcha is " + captcha)  
            captcha_error, data_error = self.fill_fuel_data(self.driver, captcha)
            time.sleep(1)
            count = 0
            print(data_error)
            print(captcha_error)
            if data_error != 0:
                return False
            while captcha_error == 1 and count <= 5:
              # logging.info("retry Submit form")
              # logging.info("No. " + str(count))
                time.sleep(1)
                captcha = self.get_captcha(self.driver)
              # logging.info("new captcha is " + captcha)
                captcha_error, data_error = self.fill_fuel_data(self.driver, captcha)
                count+=1
          
              # logging.info("Expire Fuel Finished")

            return True

        except Exception:
          # logging.error("error: " + str(e))
            lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
            print(lastCallStack)
            return False
    
