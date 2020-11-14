import os
from flask import Flask, request, jsonify
from consumer_debt import ConsumerDebtCrawler
from criminal_record import CriminalRecordCrawler
from current_wanted import CurrentWantCrawler
from domestic import DomesticCrawler
from fuel_penalty import FuelPenaltyCrawler
from traffic_penalty import TrafficPenaltyCrawler
from wanted import WantedCrawler
from criminal import CriminalCrawler
from identifier_checker import IdentifierChecker
from missing_person import MissingPersonCrawler
from server import app, db
from models import ConsumerDebt, CriminalRecord, CurrentWanted, Domestic, FuelPenaltyBasic, FuelPenaltyExpire, TrafficPenalty, Wanted, Criminal, MissingPerson

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from dotenv import load_dotenv
load_dotenv(dotenv_path='/home/johnliu/flaskapp/.env')

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu') 
# For no-gui operation system user to set chrome driver 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


@app.route('/crawler/start_crawler', methods=['GET'])
def start_crawler():
    token = request.headers.get('Token')
    total_result = {}
    if token == os.getenv("TOKEN"):
        driver = webdriver.Chrome(os.getcwd() + '/chromedriver', options = options)

        name = request.args.get('name')
        id_number = request.args.get('id_number')
        birth_date = request.args.get('birth_date')
        tenant_id = request.args.get('tenant_id')
        try:
            if ( birth_date != None and id_number != None ):
                fuel_penalty_crawler = FuelPenaltyCrawler(FuelPenaltyBasic, FuelPenaltyExpire, db, driver, id_number, birth_date, tenant_id)
                total_result['fuel_penalty'] = fuel_penalty_crawler.run()

                traffic_penalty_crawler = TrafficPenaltyCrawler(TrafficPenalty, db, driver, id_number, birth_date, tenant_id)
                total_result['traffic_penalty'] = traffic_penalty_crawler.run()

            if ( name != None and id_number != None ):
                # consumer_debt_crawler = ConsumerDebtCrawler(ConsumerDebt, db, driver, name, id_number, tenant_id)
                # total_result['consumer_debt'] = consumer_debt_crawler.run()
                total_result['consumer_debt'] = False

                # domestic_crawler = DomesticCrawler(Domestic, db, driver, name, id_number, tenant_id)
                # total_result['domestic'] = domestic_crawler.run()
                total_result['domestic'] = False

                wanted_crawler = WantedCrawler(Wanted, db, driver, name, id_number, tenant_id)
                total_result['wanted'] = wanted_crawler.run()

            if ( name != None or id_number != None ):
                criminal_crawler = CriminalCrawler(Criminal, db, driver, name, id_number, tenant_id)
                total_result['criminal'] = criminal_crawler.run()

                missing_person_crawler = MissingPersonCrawler(MissingPerson, db, driver, name, id_number, tenant_id)
                total_result['missing_person'] = missing_person_crawler.run()

            if ( name != None ):
                criminal_record_crawler = CriminalRecordCrawler(CriminalRecord, db, driver, name, tenant_id)
                criminal_record_crawler.run()
            driver.close()
        except Exception:
            total_result['error'] = True
            driver.close()
    else:
        total_result['msg'] = 'invalid'

    return jsonify(total_result)

@app.route('/crawler/tenant_check_crawler', methods=['GET'])
def tenant_check_crawler():
    driver = webdriver.Chrome(os.getcwd() + '/chromedriver', options = options)

    id_number = request.args.get('id_number')
    birthday = request.args.get('birth_date')

    total_result = {}

    identifier_checker = IdentifierChecker(db, driver, id_number, birthday)
    total_result['result'] = identifier_checker.run()
    
    driver.close()
    return jsonify(total_result)

@app.route('/crawler/start_current_wanted_crawler', methods=['GET'])
def start_current_wanted_crawler():

    driver = webdriver.Chrome(os.getcwd() + "/chromedriver", options = options)
    current_want_crawler = CurrentWantCrawler(CurrentWanted, db)
    result = current_want_crawler.run()

    driver.close()
    return jsonify(result)

@app.route('/', methods=['GET'])
def home():
    return 'success'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
