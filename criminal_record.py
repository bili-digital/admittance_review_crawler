import logging 
import os
import time
import traceback
import urllib.request as urllib2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup 

class CriminalRecordCrawler():

    def __init__(self, model, db, driver, name, tenant_id):
        self.driver= driver
        self.name = name
        self.tenant_id = tenant_id
        self.db = db
        self.model = model

      # logging.basicConfig(level=logging.DEBUG, 
      #              format='%(asctime)s - %(levelname)s : %(message)s', 
      #              filename='criminal_record.log') 

    def parse_date(self, date):
        date_list = date.split('.')
        date_list[0] = str(int(date_list[0]) + 1911)
        return date_list[0] + '-' + date_list[1] + '-' + date_list[2]

    def run(self):
        try:
            self.driver.get('''https://law.judicial.gov.tw/FJUD/default.aspx''')
            name = self.driver.find_element_by_id("txtKW")
            name.clear()
            name.send_keys(self.name)
          # logging.info("Start to query: " + "施宏勳")

            self.driver.find_element_by_id("btnSimpleQry").click()
            time.sleep(1)
          # logging.info("On query result page")

            iframe = self.driver.find_element_by_id("iframe-data")
            response = urllib2.urlopen(iframe.get_attribute('src'))
          # logging.info("Get iframe page")
            iframe_soup = BeautifulSoup(response, 'html.parser')

            criminal_rows = iframe_soup.find_all("tr")
          # logging.info("Start to enumerate criminal rows")
            for idx, criminal_row in enumerate(criminal_rows):
                if criminal_row.get("class", None) != None or idx == 0:
                    continue
                else:
                    data = criminal_row.select('td')
                  # logging.info("Get data for title: " + data[1].text)
                    title = data[1].text
                    judge_date = self.parse_date(data[2].text)
                    reason = data[3].text
                    self.model.create(title=title, judge_date=judge_date, 
                                      reason=reason, tenant_id=self.tenant_id)
                  # logging.info("Criminal Record Crawler Finished")
            return True
        except Exception:
          # logging.error("error: " + str(e))
            lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
            print(lastCallStack)
            return False