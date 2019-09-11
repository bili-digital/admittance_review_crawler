import requests
import logging 
from bs4 import BeautifulSoup 

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s : %(message)s', 
                    filename='current_wanted.log') 

response = requests.get('https://www.cib.gov.tw/Wanted')
source_code = BeautifulSoup(response.text, 'html.parser')
data = source_code.find_all('div', 'notification-page__link')
for data_row in data:
    logging.info("Get data")
    name = data_row.contents[0].strip()
    id_number = data_row.contents[2].strip()
