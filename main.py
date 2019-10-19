import os
from flask import Flask, request, jsonify
from consumer_debt import ConsumerDebtCrawler
from criminal_record import CriminalRecordCrawler
from current_wanted import CurrentWantCrawler
from current_wanted_get import CurrentWantGetter
from server import app
from server import db
from models import ConsumerDebt, CriminalRecord, CurrentWanted

from selenium import webdriver
from selenium.webdriver.chrome.options import Options



options = Options()
# options.add_argument('--headless')
options.add_argument('--disable-gpu') 
# For no-gui operation system user to set chrome driver 
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')


@app.route('/start_crawler', methods=['GET'])
def start_crawler():
    driver = webdriver.Chrome(os.getcwd() + "/chromedriver", options = options)
    name = request.args.get('name')
    id_number = request.args.get('id_number')
    birthday = request.args.get('birthday')
    tenant_id = request.args.get('tenant_id')

    total_result = {}
    # consumber_debt_crawler = ConsumerDebtCrawler(ConsumerDebt, db, driver, name, id_number, tenant_id)
    # total_result['consumber_debt_result'] = consumber_debt_crawler.run()

    # criminal_record_crawler = CriminalRecordCrawler(CriminalRecord, db, driver, name, tenant_id)
    # total_result['criminal_record_result'] = criminal_record_crawler.run()

    current_want_getter = CurrentWantGetter(CurrentWanted, db, name, id_number, tenant_id)
    total_result['current_want_result'] = current_want_getter.run()

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