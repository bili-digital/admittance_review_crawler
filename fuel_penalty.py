import os
import time
import re
import traceback
from bs4 import BeautifulSoup 
from dotenv import load_dotenv
from datetime import datetime
from captcha import Captcha
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
        self.count = 0


    def parse_date(self, date):
        date_list = re.split('年|月|日',date)
        if len(date_list) > 1:
          date_list[0] = str(int(date_list[0]) + 1911)
          if int(date_list[1]) < 10:
              date_list[1] = '0' + str(date_list[1])
          if int(date_list[2]) < 10:
              date_list[2] = '0' + str(date_list[2])
          result = date_list[0] + '-' + date_list[1] + '-' + date_list[2]
        else:
          result = '2000-01-01'
        return result
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
        driver.find_element_by_id("m3_note").click()
        time.sleep(2)
        driver.find_element_by_id("submit_btn").click()
        time.sleep(1)
        captcha_error = len(driver.find_elements_by_xpath("//*[contains(text(), '驗證碼輸入錯誤')]"))
        return captcha_error
    def run(self):
        try:
            print('fuel_penalty start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''https://www.mvdis.gov.tw/m3-emv-fee/fee/fuelFee''')
            captcha_parser = Captcha(self.driver, 'pickimg1')
            captcha = captcha_parser.parse() 
            captcha_error = self.fill_data(self.driver, captcha)
            time.sleep(1)

            count = 0
            while captcha_error == 1 and count <= 5:
                time.sleep(1)
                captcha = captcha_parser.parse()
                captcha_error = self.fill_data(self.driver, captcha)
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
                print(should_paid_date)
                print(amount)
                if datetime.now().strftime('%Y-%m-%d') > should_paid_date:
                  self.basic_model.create(transportation=transportation, car_number=car_number, period=period,
                                        should_paid_date=should_paid_date, supervisory_department=supervisory_department, 
                                        amount=amount, comment=comment,
                                        tenant_id=self.tenant_id)
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
                print(should_paid_date)
                print(amount)
                if datetime.now().strftime('%Y-%m-%d') > should_paid_date:
                  self.expire_model.create(transportation=transportation, car_number=car_number, bill_number=bill_number,
                                        should_paid_date=should_paid_date, supervisory_department=supervisory_department, 
                                        amount=amount, comment=comment, tenant_id=self.tenant_id)

            return True

        except AttributeError:
            lastCallStack = traceback.format_exc()
            print(lastCallStack)
            time.sleep(2)
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
    
