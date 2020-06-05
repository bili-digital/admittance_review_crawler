import os
import time
import traceback
from datetime import datetime
from captcha import Captcha
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WantedCrawler():
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
        name.send_keys(self.name)
        id_number.send_keys(self.id_number)
        answer.send_keys(captcha)

        driver.find_element_by_id("queryBtn").click()

    def run(self):
        try:
            print('wanted start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''https://iweb2.npa.gov.tw/NpaE8Server/CE_Query.jsp''')
            captcha_parser = Captcha(self.driver, 'reload-img')
            captcha = captcha_parser.parse() 
            self.fill_data(self.driver, captcha)
            time.sleep(1)
            WebDriverWait(self.driver, 4).until(EC.element_to_be_clickable((By.ID, 'E8_WT_UNIT_NM')))
            result = self.driver.find_element_by_id('E8_WT_UNIT_NM').text
            self.model.create(status=result, tenant_id=self.tenant_id)
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
            lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
            print(lastCallStack)
            return False
    
