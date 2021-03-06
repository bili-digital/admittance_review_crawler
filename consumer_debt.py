import os
import time
import re
import traceback
from bs4 import BeautifulSoup
from datetime import datetime

class ConsumerDebtCrawler():

    def __init__(self, model, db, driver, name, id_number, tenant_id):
        self.driver= driver
        self.name = name
        self.id_number = id_number
        self.tenant_id = tenant_id
        self.db = db
        self.model = model


    def parse_date(self, date):
        date_list = date.split('/')
        date_list[0] = str(int(date_list[0]) + 1911)
        return date_list[0] + '-' + date_list[1] + '-' + date_list[2]

    def run(self):
        try:
            print('consumer debt start at:' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            self.driver.get('''http://cdcb.judicial.gov.tw/abbs/wkw/WHD9A01.jsp''')
            name = self.driver.find_element_by_name("clnm")
            id_number = self.driver.find_element_by_name("idno")

            name.clear()
            id_number.clear()

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
                    court = data[0].text.strip()
                    title = "".join(data[1].text.strip().split())
                    date = self.parse_date(data[2].text).strip()
                    content = data[3].text.strip()
                    self.model.create(court=court, title=title, date=date,
                                      content=content, tenant_id=self.tenant_id)

            return True
        except Exception:
            lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
            print(lastCallStack)
            return False

