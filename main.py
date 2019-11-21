import os
from flask import Flask, request, jsonify
from consumer_debt import ConsumerDebtCrawler
from criminal_record import CriminalRecordCrawler
from current_wanted import CurrentWantCrawler
from current_wanted_get import CurrentWantGetter
from domestic import DomesticCrawler
from fuel_penalty import FuelPenaltyCrawler
from traffic_penalty import TrafficPenaltyCrawler
from wanted import WantedCrawler
from server import app, db
from models import ConsumerDebt, CriminalRecord, CurrentWanted, Domestic, FuelPenaltyBasic, FuelPenaltyExpire, TrafficPenalty, Wanted

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


@app.route('/start_crawler', methods=['GET'])
def start_crawler():
    os.chdir(os.getenv('PRODUCTION_PATH'))
    driver = webdriver.Chrome(os.getenv('DRIVER_PATH'), options = options)

    name = request.args.get('name')
    id_number = request.args.get('id_number')
    birthday = request.args.get('birth_date')
    tenant_id = request.args.get('tenant_id')

    total_result = {}
    consumber_debt_crawler = ConsumerDebtCrawler(ConsumerDebt, db, driver, name, id_number, tenant_id)
    total_result['consumber_debt_result'] = consumber_debt_crawler.run()

    #criminal_record_crawler = CriminalRecordCrawler(CriminalRecord, db, driver, name, tenant_id)
    #total_result['criminal_record_result'] = criminal_record_crawler.run()

    current_want_getter = CurrentWantGetter(CurrentWanted, db, name, id_number, tenant_id)
    total_result['current_want_result'] = current_want_getter.run()

    domestic_crawler = DomesticCrawler(Domestic, db, driver, name, id_number, tenant_id)
    total_result['domestic_crawler_result'] = domestic_crawler.run()

    fuel_penalty_crawler = FuelPenaltyCrawler(FuelPenaltyBasic, FuelPenaltyExpire, db, driver, id_number, birthday, tenant_id)
    total_result['fuel_penalty_crawler_result'] = fuel_penalty_crawler.run()

    traffic_penalty_crawler = TrafficPenaltyCrawler(TrafficPenalty, db, driver, id_number, birthday, tenant_id)
    total_result['traffic_penalty_crawler_result'] = traffic_penalty_crawler.run()

    wanted_crawler = WantedCrawler(Wanted, db, driver, name, id_number, tenant_id)
    total_result['wanted_crawler_result'] = wanted_crawler.run()

    driver.close()
    return jsonify(total_result)

@app.route('/start_current_wanted_crawler', methods=['GET'])
def start_current_wanted_crawler():

    driver = webdriver.Chrome(os.getcwd() + "/chromedriver", options = options)
    current_want_crawler = CurrentWantCrawler(CurrentWanted, db)
    result = current_want_crawler.run()

    driver.close()
    return jsonify(result)
if __name__ == "__main__":
    app.run(port=5000, debug=True)
