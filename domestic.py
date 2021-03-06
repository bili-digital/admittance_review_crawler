import os
import time
import re
import traceback
from bs4 import BeautifulSoup 
from datetime import datetime
from selenium.webdriver.support.ui import Select

class DomesticCrawler():

    def __init__(self, model, db, driver, name, id_number, tenant_id):
        self.db = db
        self.model = model
        self.driver = driver
        self.name = name
        self.id_number = id_number
        self.tenant_id = tenant_id
 

    def parse_date(self, date):
        date_list = date.split('/')
        date_list[0] = str(int(date_list[0]) + 1911)
        return date_list[0] + '-' + date_list[1] + '-' + date_list[2]

    def run(self):
        try:
            print('domestic start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''http://domestic.judicial.gov.tw/abbs/wkw/WHD9HN01.jsp''')

            select = Select(self.driver.find_element_by_name('kdid'))
            name = self.driver.find_element_by_name("clnm")
            id_number = self.driver.find_element_by_name("idno")

            name.clear()
            id_number.clear()

            select.select_by_value("02 監護輔助宣告事件 N")
            name.send_keys(self.name)
            id_number.send_keys(self.id_number)


            self.driver.find_element_by_name("Button").click()
            time.sleep(1)


            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            criminal_rows = soup.find_all("tr")
            for idx, criminal_row in enumerate(criminal_rows):
                if idx <= 8:
                    continue
                else:
                    data = criminal_row.select('td')
                    if len(data) < 6:
                        break
                    court = data[1].text.strip()
                    title = "".join(data[2].text.strip().split())
                    post_date = self.parse_date(data[3].text).strip()
                    publish_date = self.parse_date(data[4].text).strip()
                    content = data[5].text.strip()
                    self.model.create(court=court, title=title, content=content,
                                      post_date=post_date, publish_date=publish_date, tenant_id=self.tenant_id)
            return True
        except Exception as e:
            if(str(e).find('unexpected alert open') != -1):
              return 'Id Error'
            else:
              lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
              print(lastCallStack)
              return False
