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

load_dotenv()

class FuelPenaltyCrawler():

    def __init__(self, basic_model, expire_model, db, driver, id_number, birthday, tenant_id):
        self.db = db
        self.basic_model = basic_model
        self.expire_model = expire_model
        self.driver = driver
        self.id_number = id_number
        self.birthday = birthday
        self.tenant_id = tenant_id

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
    def fill_data(self, driver, captcha):
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
        driver.find_element_by_id("m3_warning").click()
        time.sleep(2)
        driver.find_element_by_id("submit_btn").click()
      # logging.info("Submit form")
        time.sleep(1)
        captcha_error = len(driver.find_elements_by_xpath("//*[contains(text(), '驗證碼輸入錯誤')]"))
        data_error = len(driver.find_elements_by_xpath("//*[contains(text(), '請確認您輸入的證號及生日是否正確。')]"))
        return captcha_error, data_error
    def run(self):
        try:
            self.driver.get('''https://www.mvdis.gov.tw/m3-emv-fee/fee/fuelFee''')
            captcha = self.get_captcha(self.driver)
          # logging.info("captcha is " + captcha)  
            captcha_error, data_error = self.fill_data(self.driver, captcha)
            time.sleep(1)

            count = 0
            if data_error ==1:
                return False
            while captcha_error == 1 and count <= 5:
              # logging.info("retry Submit form")
              # logging.info("No. " + str(count))
                time.sleep(1)
                captcha = self.get_captcha(self.driver)
              # logging.info("new captcha is " + captcha)
                captcha_error, data_error = self.fill_data(self.driver, captcha)
                count+=1
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            basic_amount_rows = soup.select('#info tr.even, #info tr.odd')
            expired_amount_rows = soup.select('#info2 tr.even, #info2 tr.odd')
            for idx, row in enumerate(basic_amount_rows):
                data = row.select('td')
                transportation = data[1].text.strip()
                car_number = data[2].text.strip()
                period = data[3].text.strip()
                should_paid_date = self.parse_date(data[4].text.strip())
                supervisory_department = data[5].text.strip()
                amount = data[6].text.strip()
                comment = data[7].contents[0].strip()
                print(transportation)
                print(car_number)
                print(period)
                print(should_paid_date)
                print(supervisory_department)
                print(amount)
                print(comment)
                self.basic_model.create(transportation=transportation, car_number=car_number, period=period,
                                      should_paid_date=should_paid_date, supervisory_department=supervisory_department, 
                                      amount=amount, comment=comment,
                                      tenant_id=self.tenant_id)
              # logging.info("Basic Fuel Finished")
            for idx, row in enumerate(expired_amount_rows):
                data = row.select('td')
                transportation = data[0].text.strip()
                car_number = data[1].text.strip()
                bill_number = data[2].text.strip()
                supervisory_department = data[3].text.strip()
                should_paid_date = self.parse_date(data[4].text.strip())
                amount = data[5].text.strip()
                comment = data[6].contents[0].strip()
                print(transportation)
                print(car_number)
                print(bill_number)
                print(supervisory_department)
                print(should_paid_date)
                print(amount)
                print(comment)
                self.expire_model.create(transportation=transportation, car_number=car_number, bill_number=bill_number,
                                      should_paid_date=should_paid_date, supervisory_department=supervisory_department, 
                                      amount=amount, comment=comment, tenant_id=self.tenant_id)
              # logging.info("Expire Fuel Finished")

            return True

        except Exception:
          # logging.error("error: " + str(e))
            lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
            print(lastCallStack)
            return False
    
