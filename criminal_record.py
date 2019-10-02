import logging 
import os
import time
import urllib.request as urllib2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup 

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s : %(message)s', 
                    filename='criminal_record.log') 

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu') 
# For no-gui operation system user to set chrome driver 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(os.getcwd() + "/chromedriver", options = options)

def parse_date(date):
    date_list = date.split('.')
    date_list[0] = str(int(date_list[0]) + 1911)
    return date_list[0] + '-' + date_list[1] + '-' + date_list[2]

try:
    driver.get('''https://law.judicial.gov.tw/FJUD/default.aspx''')
    name = driver.find_element_by_id("txtKW")
    name.clear()
    name.send_keys("施宏勳")
    logging.info("Start to query: " + "施宏勳")

    driver.find_element_by_id("btnSimpleQry").click()
    time.sleep(1)
    logging.info("On query result page")

    iframe = driver.find_element_by_id("iframe-data")
    iframe_url = iframe.get_attribute('src')
    response = urllib2.urlopen(iframe.get_attribute('src'))
    logging.info("Get iframe page")
    iframe_soup = BeautifulSoup(response, 'html.parser')

    criminal_rows = iframe_soup.find_all("tr")
    logging.info("Start to enumerate criminal rows")
    for idx, criminal_row in enumerate(criminal_rows):
        if criminal_row.get("class", None) != None or idx == 0:
            continue
        else:
            data = criminal_row.select('td')
            logging.info("Get data for title: " + data[1].text)
            title = data[1].text
            judge_date = parse_date(data[2].text)
            reason = data[3].text
            print(title)
    driver.quit()
except Exception as e:
    driver.quit()
    logging.error("error: " + str(e))
    print(e)