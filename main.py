import os
from flask import Flask, request, jsonify
from consumer_debt import ConsumerDebtCrawler
from server import app
from server import db
from models import ConsumerDebt

from selenium import webdriver
from selenium.webdriver.chrome.options import Options



options = Options()
options.add_argument('--headless')
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
    consumber_debt_crawler = ConsumerDebtCrawler(ConsumerDebt, db, driver, name, id_number, tenant_id)
    total_result['consumber_debt_result'] = consumber_debt_crawler.run()

    driver.close()
    return jsonify(total_result)

    
if __name__ == "__main__":
    app.run(port=5000)