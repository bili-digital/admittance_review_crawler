import os
import time
import re
import traceback
from bs4 import BeautifulSoup 
from dotenv import load_dotenv
from datetime import datetime
from captcha import Captcha
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
load_dotenv()

class CriminalCrawler():

    def __init__(self, model, db, driver, name, id_number, tenant_id):
        self.driver= driver
        self.name = name
        self.id_number = id_number
        self.tenant_id = tenant_id
        self.db = db
        self.model = model
        self.count = 0
 
    def fill_data(self, driver, captcha):
        driver.get('''https://service.moj.gov.tw/CriminalWanted/QueryCriminalList/QueryCriminalResult?CriminalName={}&CriminalIdNo={}&WaitValidateCode={}'''.format(self.name or '', self.id_number or '',  captcha))

    def parse_date(self, date):
        date_list = date.split('.')
        date_list[0] = str(int(date_list[0]) + 1911)
        return date_list[0] + '-' + date_list[1] + '-' + date_list[2]

    def run(self):
        try:
            print('criminal start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''https://service.moj.gov.tw/CriminalWanted''')
            checkbox = self.driver.find_element_by_xpath('//label[@for="PrecautionsAccepted"]')
            checkbox.click()
            time.sleep(1)

            captcha_parser = Captcha(self.driver, 'valiCode')
            captcha = captcha_parser.parse() 

            self.fill_data(self.driver, captcha)
            WebDriverWait(self.driver, 4).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            if alert.text == '驗證碼不正確':
                alert.accept() 
                raise AttributeError

            print(alert.text)
            reason = ''
            if(alert.text == '無符合的通緝犯' or alert.text == '查無資料'):
                alert.accept()
                self.model.create(status="normal", reason=reason, tenant_id=self.tenant_id)
            else:
                alert.accept()
                reason = self.driver.page_source.split('\n            \n            \n                ')[-1].split('\n            ')[0]
                self.model.create(status="abnormal", reason=reason, tenant_id=self.tenant_id)  
            return True

        except (AttributeError, TimeoutException):
            if(self.driver.page_source.find(self.name) != -1):
                reason = self.driver.page_source.split('\n            \n            \n                ')[-1].split('\n            ')[0]
                self.model.create(status="abnormal", reason=reason, tenant_id=self.tenant_id)  
                return True
            else:
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