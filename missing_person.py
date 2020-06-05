import os
import time
import traceback
from PIL import Image
from io import BytesIO
from datetime import datetime
from captcha import Captcha
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MissingPersonCrawler():
    def __init__(self, model, db, driver, name, id_number, tenant_id):
        self.db = db
        self.model = model
        self.driver = driver
        self.name = name
        self.id_number = id_number
        self.tenant_id = tenant_id
        self.count = 0

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

    def run(self):
        try:
            print('missing person start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''https://iweb2.npa.gov.tw/NpaE8Server/NK_Query.jsp''')
            captcha_parser = Captcha(self.driver, 'reload-img')
            captcha = captcha_parser.parse() 
            self.fill_data(self.driver, captcha)

            WebDriverWait(self.driver, 4).until(EC.element_to_be_clickable((By.ID, 'tabResult')))
            result = self.driver.find_element_by_id('tabResult').text
            if result.find('符合查詢資料共0筆') != -1:
              status = '查無資料'
            else:
              status = '有失蹤紀錄'
            self.model.create(status=status, tenant_id=self.tenant_id)
            return True

        except (AttributeError, TimeoutException):
            lastCallStack = traceback.format_exc()
            print(lastCallStack)
            self.count += 1
            if self.count < 5:
                result = self.run()
                return result
            else:
                return False
            
        except Exception:
            lastCallStack = traceback.format_exc()
            print(lastCallStack)
            return False
    
