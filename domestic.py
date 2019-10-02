import logging 
import os
import time
import re
import urllib.request as urllib2
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup 

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s : %(message)s', 
                    filename='domestic.log') 

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu') 
# For no-gui operation system user to set chrome driver 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(os.getcwd() + "/chromedriver", options = options)

def parse_date(date):
    date_list = date.split('/')
    date_list[0] = str(int(date_list[0]) + 1911)
    return date_list[0] + '-' + date_list[1] + '-' + date_list[2]

try:
    driver.get('''http://domestic.judicial.gov.tw/abbs/wkw/WHD9HN01.jsp''')

    name = driver.find_element_by_name("clnm")
    id_number = driver.find_element_by_name("idno")

    name.clear()
    id_number.clear()

    name.send_keys("戴文堅")
    id_number.send_keys("U120277765")

    logging.info("Start to query: " + "戴文堅")

    driver.find_element_by_name("Button").click()
    time.sleep(1)
    logging.info("On query result page")

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    criminal_rows = soup.find_all("tr")
    logging.info("Start to enumerate criminal rows")
    for idx, criminal_row in enumerate(criminal_rows):
        if idx <= 8:
            continue
        else:
            data = criminal_row.select('td')
            if len(data) < 6:
                break
            logging.info("Get data for title: " + data[1].text)
            court = data[1].text.strip()
            title = "".join(data[2].text.strip().split())
            post_date = parse_date(data[3].text).strip()
            publish_date = parse_date(data[4].text).strip()
            content = data[5].text.strip()
            print(court)
            print(title)
            print(post_date)
            print(publish_date)
            print(content)
    driver.quit()
except Exception as e:
    driver.quit()
    logging.error("error: " + str(e))
    print(e)