import os
import time
import re
import traceback
from bs4 import BeautifulSoup 
from dotenv import load_dotenv
from datetime import datetime
from captcha import Captcha
load_dotenv()

class IdentifierChecker():

    def __init__(self, db, driver, id_number, birthday):
        self.db = db
        self.driver = driver
        self.id_number = id_number
        self.birthday = birthday
        self.count = 0

    def parse_date(self, date):
        date_list = re.split('年|月|日',date)
        date_list[0] = str(int(date_list[0]) + 1911)
        if int(date_list[1]) < 10:
            date_list[1] = '0' + str(date_list[1])
        if int(date_list[2]) < 10:
            date_list[2] = '0' + str(date_list[2])

        return date_list[0] + '-' + date_list[1] + '-' + date_list[2]
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
        driver.find_element_by_id("m3_warning").click()
        time.sleep(2)
        driver.find_element_by_id("search1").click()
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        form_text_ele = soup.select('#validateStr1')
        id_error_ele = soup.select('#id1-error')
        header_elem = soup.select('#headerMessage')
      
        if len(form_text_ele) != 0 and form_text_ele[0].text == '驗證碼輸入錯誤':
          captcha_error = 1
        else:
          captcha_error = 0

        if len(id_error_ele) != 0 and id_error_ele[0].text == '身分證或居留證格式錯誤':
          data_error = 1
        elif len(header_elem) != 0 and header_elem[0].text == '請確認您輸入的證號及生日是否正確。':
          data_error = 1
        else:
          data_error = 0        
        return captcha_error, data_error
    def run(self):
        try:
            print('identifier start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay''')
            captcha_parser = Captcha(self.driver, 'pickimg1')
            captcha = captcha_parser.parse() 
            captcha_error, data_error = self.fill_data(self.driver, captcha)
            time.sleep(1)
            count = 0
            print('data_error' + str(data_error))
            print('captcha_error' + str(captcha_error))
            if data_error != 0:
                return False
            while captcha_error != 0 and count < 5:
              if count == 5:
                print('captcha error too much times')
                return False
              time.sleep(1)
              captcha = captcha_parser.parse()
              captcha_error, data_error = self.fill_data(self.driver, captcha)
              count+=1
          

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
    
