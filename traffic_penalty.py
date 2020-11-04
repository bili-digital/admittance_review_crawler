import os
import time
import re
import traceback
from bs4 import BeautifulSoup 
from dotenv import load_dotenv
from datetime import datetime
from captcha import Captcha
load_dotenv()


class TrafficPenaltyCrawler():
    def __init__(self, model, db, driver, id_number, birthday, tenant_id):
        self.db = db
        self.model = model
        self.driver = driver
        self.id_number = id_number
        self.birthday = birthday
        self.tenant_id = tenant_id
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

        time.sleep(1)
        driver.find_element_by_id("m3_warning").click()
        time.sleep(1)

        driver.find_element_by_id("search1").click()

        elements = driver.find_elements_by_xpath("//*[contains(text(), '線上繳費')]")
        return elements
    def run(self):
        try:
            print('traffic penalty start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay''')
            captcha_parser = Captcha(self.driver, 'pickimg1')
            captcha = captcha_parser.parse()

            elements = self.fill_data(self.driver, captcha)
            time.sleep(1)

            count = 0
            while len(elements) == 0 and count <= 5:
                time.sleep(1)
                captcha_parser = Captcha(self.driver, 'pickimg1')
                captcha = captcha_parser.parse()
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
                content = content.translate(str.maketrans('', '', ' \n\t\r'))
                self.model.create(violation_date=violation_date, content=content, amount=amount,
                                  should_paid_date=should_paid_date, tenant_id=self.tenant_id)
              if len(next_button) > 0:
                href = next_button[0]['href']
                self.driver.get('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay' + href)
              else:
                fetch = False
            
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
                  content = content.translate(str.maketrans('', '', ' \n\t\r'))
                  self.model.create(violation_date=violation_date, content=content, amount=amount,
                                    should_paid_date=should_paid_date, tenant_id=self.tenant_id)
                if len(next_button) > 0:
                  href = next_button[0]['href']
                  self.driver.get('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay' + href)
                else:
                  legal_fetch = False
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
    
