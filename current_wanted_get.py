import logging 
import os
import time
import traceback


class CurrentWantGetter():

    def __init__(self, model, db, name, id_number, tenant_id):
        self.name = name
        self.id_number = id_number
        self.tenant_id = tenant_id
        self.db = db
        self.model = model

      # logging.basicConfig(level=logging.DEBUG, 
      #              format='%(asctime)s - %(levelname)s : %(message)s', 
      #              filename='criminal_record_get.log') 

    def run(self):
        try:
          # logging.info("Start to query: " + self.name + self.id_number)
            result = self.db.session.query(self.model).filter(self.model.name ==self.name, 
                                                              self.model.id_number == self.id_number).all()
          # logging.info("Criminal Record Getter Finished")
            if(len(result) > 0 ):
              return 'criminal'
            else:
              return True
        except Exception:
            # logging.error("error: " + str(e))
            lastCallStack = traceback.format_exc() #取得Call Stack的最後一筆資料
            print(lastCallStack)
            return False