import requests
import logging 
import traceback
from bs4 import BeautifulSoup 


class CurrentWantCrawler():

    def __init__(self, model, db):
        self.db = db
        self.model = model

      # logging.basicConfig(level=logging.DEBUG, 
      #              format='%(asctime)s - %(levelname)s : %(message)s', 
      #              filename='current_wanted.log') 

    def run(self):
        try:
            response = requests.get('https://www.cib.gov.tw/Wanted')
            source_code = BeautifulSoup(response.text, 'html.parser')
            data = source_code.find_all('div', 'notification-page__link')
            for data_row in data:
                name = data_row.contents[0].strip()
                id_number = data_row.contents[2].strip()
                path = data_row['href']
                detail_response = requests.get('https://www.cib.gov.tw{}'.format(path))
                detail_source_code = BeautifulSoup(detail_response.text, 'html.parser')
                table_rows = detail_source_code.select('li.article__item')
                for table_row in table_rows:
                    if(table_row.text.find('查尋緝原因') != -1):
                      reason = table_row.select('div.article__content')[0].text
                      result = self.db.session.query(self.model).filter(self.model.name ==name, 
                                                                    self.model.id_number == id_number).all()
                      if(len(result) > 0):
                        pass
                      else:
                        self.model.create(name=name, id_number=id_number, reason=reason)
            
            return True
        except Exception:
            # logging.error("error: " + str(e))
            lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
            print(lastCallStack)
            return False
            
