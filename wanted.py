import os
import pytesseract
import logging 
import urllib.request as urllib2
import time
import pymysql
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s : %(message)s', 
                    filename='wanted.log') 

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu') 
# For no-gui operation system user to set chrome driver 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(os.getcwd() + "/chromedriver", options = options)

def get_captcha(driver):
    img = driver.find_element_by_xpath(".//*[@id='reload-img']")
    with open('captcha.png', 'wb') as file:
        file.write(img.screenshot_as_png)    
    logging.info("Save Image")                                                                         
    img = Image.open('captcha.png')   
    return pytesseract.image_to_string(img) 

def fill_data(driver, captcha):
    wanted_name = driver.find_element_by_id("QS_NAME")
    wanted_id = driver.find_element_by_id("QS_ID")
    answer = driver.find_element_by_id("answer")

    wanted_name.clear()
    wanted_id.clear()
    answer.clear()

    wanted_name.send_keys("施宏勳")
    wanted_id.send_keys("A125146302")
    answer.send_keys(captcha)

    driver.find_element_by_id("queryBtn").click()

    logging.info("Submit form")
    elements = driver.find_elements_by_xpath("//*[contains(text(), 'Ok')]")

    return elements

try:
    driver.get('''https://iweb2.npa.gov.tw/NpaE8Server/CE_Query.jsp''')
    captcha = get_captcha(driver)
    logging.info("captcha is " + captcha)  
    elements = fill_data(driver, captcha)
    time.sleep(1)

    count = 0
    while len(elements) != 0 and count <= 5:
        logging.info("retry Submit form")
        logging.info("No. " + str(count))
        driver.find_element_by_id("smartAlertClose").click()
        time.sleep(1)
        captcha = get_captcha(driver)
        logging.info("new captcha is " + captcha)
        elements = fill_data(driver, captcha)
        count+=1

    result = driver.find_element_by_id('E8_WT_UNIT_NM').text
    logging.info("Result: " + result)


except Exception as e:
    driver.quit()
    logging.error("error: " + str(e))
    print(e)
    
