import connexion
from connexion import NoContent
import json
import datetime
import swagger_ui_bundle
import json
import datetime
import swagger_ui_bundle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from merch import Merch
from food import Food
from stats import SalesStats
import requests
import yaml
import logging
import uuid
import logging.config
from flask import Flask, request, jsonify
import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from flask_cors import CORS, cross_origin
import os 
import create_tables


TABLE_NAME_OPTIONS = ['merch_inventory', 'food_inventory']

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_config.yml"
    log_conf_file = "/config/processing_log_config.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_config.yml"
    log_conf_file = "processing_log_config.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')
    logger.info("App Conf File: %s" % app_conf_file)
    logger.info("Log Conf File: %s" % log_conf_file)

# with open('app_config.yml', 'r') as f:
#     app_config = yaml.safe_load(f.read())
# with open('processing_log_config.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)
#     logger = logging.getLogger('basicLogger')

storage_name = app_config['datastore']['filename']


STORAGE_MERCH_URL = app_config['storage_merch']['url']
STORAGE_FOOD_URL = app_config['storage_food']['url']



DB_ENGINE = create_engine(f"sqlite:///{storage_name}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def health():
    return {"status": "ok"}, 200

def add_to_database(body, table_name):
    session = DB_SESSION()
    if table_name == TABLE_NAME_OPTIONS[0]:
        print(f'adding merch to database {body}')
        merch = Merch(body['SKU'],
                      body['merchPrice'],
                      body['merchQuantity'],
                      body['merchName'],
                      body['trace_id'])
        session.add(merch)
    elif table_name == TABLE_NAME_OPTIONS[1]:
        print(f'adding food to database {body}')
        food = Food(body['foodName'], body['foodPrice'],
                    body['foodQuantity'], body['expirationDate'], body['trace_id'])
        session.add(food)
    session.commit()
    session.close()

# function to handle endpoint


def addmerchInventory(body):
    print(request.json)
    body = request.json

    add_to_database(body, TABLE_NAME_OPTIONS[0])

    success_message = {'message': 'merch inventory added',
                       'status': 201, 'content': request.json}
    logger.info(
        f'Merch Storage Service : trace_id: {body["trace_id"]} write to database inventory table merch_inventory')
    return success_message


def addfoodInventory(body):
    print(request.json)
    body = request.json
    add_to_database(body, TABLE_NAME_OPTIONS[1])
    success_message = {'message': 'food inventory added',
                       'status': 201, 'content': request.json}
    logger.info(
        f'Food Storage Service : trace_id: {body["trace_id"]} write to database inventory table food_inventory')
    return success_message

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


def populate_stats():
    """ Periodically update stats """
    logger.info('Populating stats')

    current_time = datetime.datetime.now(tz=pytz.UTC)
    print(current_time)
    test_start_time = '2022-10-06 23:33:45.594720'
    test_end_time = '2022-11-20 23:33:45.594720'
    # status_code, data = get_food_inventory(test_start_time,test_end_time )
    start_time = app_config['scheduler']['start_time']
    end_time = current_time
    print('='*50)
    print(start_time, end_time)
    print('='*50)
    status_code, data = get_food_inventory(start_time,end_time )
    # status_code , data = get_food_inventory(test_time) # for testing

    if status_code == 200:
        food_sales = calculate_food_sales(data)
        logger.info(f'Request Success ! INFO: Food sales: {food_sales}')
    else:
        logger.error(
            f'Request Failed ! ERROR : something happened when getting food stats')

    status_code, data = get_merch_inventory(start_time,end_time)
    # status_code, data = get_merch_inventory(test_time) # for testing
    if status_code == 200:
        merch_sales = calculate_merch_sales(data)
        logger.info(f'Request Success ! INFO: Merch sales: {merch_sales}')
    else:
        logger.error(
            f'Request Failed ! ERROR : something happened when getting merch stats')
    trace_id = str(uuid.uuid4())
    body = {'merchSales': merch_sales, 'foodSales': food_sales,
            'trace_id': trace_id, 'timestamp': current_time}
    logger.debug(f'INFO: body: {body}')
    write_to_database(body)

    # update start time 
    app_config['scheduler']['start_time'] = current_time
    with open('app_config.yml', 'w') as f:
        yaml.dump(app_config, f)
    logger.debug(f'INFO: updated start time: {current_time}')

    logger.debug(f'finish writting to database ,{body}')
    last_row = read_last_entry()
    logger.debug(f'last row in database: {last_row}')
    logger.info(f'INFO: finish populating stats')


def get_food_inventory(starttime=datetime.datetime.now(tz=pytz.UTC), endtime=datetime.datetime.now(tz=pytz.UTC)):
    url = STORAGE_FOOD_URL + '?starttime=' + str(starttime) + '&endtime=' + str(endtime)
    response = requests.get(url)
    # if status code is okay
    return response.status_code, response.json()


def get_merch_inventory(starttime=datetime.datetime.now(tz=pytz.UTC), endtime=datetime.datetime.now(tz=pytz.UTC)):
    url = STORAGE_MERCH_URL + '?starttime=' + str(starttime) + '&endtime=' + str(endtime)
    response = requests.get(url)
    # if status code is okay
    return response.status_code, response.json()


def calculate_food_sales(data):
    """this function calcualtes the total sales of food during this time period"""
    total_sales = 0
    food_data = json.loads(data['content'])
    for item in food_data:
        total_sales += float(item['foodPrice']) * float(item['foodQuantity'])
    return total_sales


def calculate_merch_sales(data):
    """this function calcualtes the total sales of merch during this time period"""
    total_sales = 0
    merch_data = json.loads(data['content'])
    for item in merch_data:
        total_sales += float(item['merchPrice']) * float(item['merchQuantity'])
    return total_sales


def write_to_database(body):
    session = DB_SESSION()
    stats = SalesStats(body['trace_id'], body['merchSales'],
                       body['foodSales'], body['timestamp'])
    session.add(stats)
    session.commit()
    session.close()


def read_last_entry():
    session = DB_SESSION()
    sql_query = 'select * from SalesStats order by timestamp desc limit 1;'
    result = session.execute(sql_query)
    result_list = []
    for row in result:
        result_list.append(row)
    session.close()
    return result_list

def total_sales():
    session = DB_SESSION()
    sql_query = 'select sum(merchSales) as merchSales, sum(foodSales) as foodSales , max(merchSales) as MaxMerchSales, max(foodSales) as MaxFoodSales from SalesStats;'
    result = session.execute(sql_query)
    timestamp = datetime.datetime.now(tz=pytz.UTC)
    for row in result:
        result_object = {'merchSales':int(row[0]), 'foodSales':int(row[1]),'maxMerchSales':int(row[2]) ,'maxFoodSales':int(row[3]) ,'timestamp':timestamp}

    session.close()
    return result_object
def stats():
    content = total_sales()
    print(content)
    return content, 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('STEVENCHANG420-RetailFoodAPI_Template-1.0.0.yaml',
            strict_validation=True,
            validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == '__main__':
    create_tables.create_tables()
    init_scheduler()
    app.run(port=8100, use_reloader=False)
