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


class TrafficPenaltyCrawler():
    def __init__(self, model, db, driver, id_number, birthday, tenant_id):
        self.db = db
        self.model = model
        self.driver = driver
        self.id_number = id_number
        self.birthday = birthday
        self.tenant_id = tenant_id

      # logging.basicConfig(level=logging.DEBUG, 
      #              format='%(asctime)s - %(levelname)s : %(message)s', 
      #              filename='trafic_penalty.log') 

    def parse_date(self, date):
        date_list = re.split('年|月|日',date)
        date_list[0] = str(int(date_list[0]) + 1911)
        if int(date_list[1]) < 10:
          date_list[1] = '0' + str(date_list[1])
        if int(date_list[2]) < 10:
          date_list[2] = '0' + str(date_list[2])

        return date_list[0] + '-' + date_list[1] + '-' + date_list[2]

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
            print('tring')
        return ret

    def fill_data(self, driver, captcha):
        id_number = driver.find_element_by_id("id1")
        birthday = driver.find_element_by_id("birthday")
        answer = driver.find_element_by_id("validateStr")

        id_number.clear()
        birthday.clear()
        answer.clear()

        id_number.send_keys(self.id_number)
        birthday.send_keys(self.birthday)
        answer.send_keys(captcha)

        # remove datepicker ui
        time.sleep(1)
        driver.find_element_by_id("m3_warning").click()
        time.sleep(1)

        driver.find_element_by_id("search1").click()

      # logging.info("Submit form")
        elements = driver.find_elements_by_xpath("//*[contains(text(), '線上繳費')]")
        return elements
    def run(self):
        try:
            self.driver.get('''https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay''')
            captcha = self.get_captcha(self.driver)
          # logging.info("captcha is " + captcha)  
            elements = self.fill_data(self.driver, captcha)
            time.sleep(1)

            count = 0
            while len(elements) == 0 and count <= 5:
              # logging.info("retry Submit form")
              # logging.info("No. " + str(count))
                time.sleep(1)
                captcha = self.get_captcha(self.driver)
              # logging.info("new captcha is " + captcha)
                elements = self.fill_data(self.driver, captcha)
                count+=1
            
            fetch = True
            while fetch:
              soup = BeautifulSoup(self.driver.page_source, 'html.parser')
              next_button = soup.select("#next")
              rows = soup.select('tr.even, tr.odd')
              for idx, row in enumerate(rows):
                data = row.select('td')
                violation_date = self.parse_date(data[1].text.strip())
                content = data[2].text.strip()
                amount = data[3].text.strip()
                should_paid_date = self.parse_date(data[4].text.strip())
                self.model.create(violation_date=violation_date, content=content, amount=amount,
                                  should_paid_date=should_paid_date, tenant_id=self.tenant_id)
              if len(next_button) > 0:
                href = next_button[0]['href']
                self.driver.get('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay' + href)
              else:
                fetch = False
              # logging.info("traffic Finished")
            
            legal = self.driver.find_element_by_name("legal") 
            legal.click()
            time.sleep(2)
            legal_fetch = True
            while legal_fetch:
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                next_button = soup.select("#next")
                rows = soup.select('tr.even, tr.odd')
                for idx, row in enumerate(rows):
                  data = row.select('td')
                  violation_date = self.parse_date(data[1].text.strip())
                  content = data[0].text.strip() + '、' + data[2].text.strip()
                  amount = data[3].text.strip()
                  should_paid_date = self.parse_date(data[4].text.strip())
                  self.model.create(violation_date=violation_date, content=content, amount=amount,
                                    should_paid_date=should_paid_date, tenant_id=self.tenant_id)
                if len(next_button) > 0:
                  href = next_button[0]['href']
                  self.driver.get('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay' + href)
                else:
                  legal_fetch = False
                # logging.info("traffic Finished")
                  return True

            
        except Exception:
          # logging.error("error: " + str(e))
            lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
            print(lastCallStack)
            return False
    
