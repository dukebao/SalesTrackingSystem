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
import requests
import yaml
import logging
import uuid
import logging.config
from flask import Flask, request, jsonify

TABLE_NAME_OPTIONS = ['merch_inventory', 'food_inventory']

with open('storage_config.yml', 'r') as f:
    storage_config = yaml.safe_load(f.read())
STORAGE_SETTING = storage_config['datastore'] # for local storage
STORAGE_SETTING = storage_config['cloudstore'] # for cloud storage
print(STORAGE_SETTING)

with open('app_config.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

STORAGE_MERCH_URL = app_config['storage_merch']['url']
STORAGE_FOOD_URL = app_config['storage_food']['url']

with open('storage_log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(
    f"mysql+pymysql://{STORAGE_SETTING['user']}:{STORAGE_SETTING['password']}@{STORAGE_SETTING['hostname']}:{STORAGE_SETTING['port']}/{STORAGE_SETTING['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def write_to_json(timestamp, body):
    event = {}
    event['timestamp'] = str(timestamp)
    event['eventMessage'] = f'Inventory updated, {body} added to database !'

    db = json.load(open(EVENT_FILE_OUT, 'r'))
    print(len(db))
    if len(db) < MAX_VALUES_ALLOWED_IN_DB:
        db.insert(0, event)
    else:
        db.pop()
        db.insert(0, event)
    with open(EVENT_FILE_OUT, 'w') as outfile:
        json.dump(db, outfile)

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
                    body['foodQuantity'], body['expirationDate'],body['trace_id'])
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
    logger.info(f'Merch Storage Service : trace_id: {body["trace_id"]} write to database inventory table merch_inventory')
    return success_message


def addfoodInventory(body):
    print(request.json)
    body = request.json
    add_to_database(body, TABLE_NAME_OPTIONS[1])
    success_message = {'message': 'food inventory added',
                       'status': 201, 'content': request.json}
    logger.info(f'Food Storage Service : trace_id: {body["trace_id"]} write to database inventory table food_inventory')
    return success_message

def getMerchStats():
    print(request.args['timestamp'])
    timestamp = request.args['timestamp']

    result = queryDbStats(timestamp, TABLE_NAME_OPTIONS[0])
    print(result)
    print('='*50)
    success_message = {
        'message': 'merch inventory stats',
        'status': 200,
        'content': json.dumps(result)
    }

    print(success_message)

    return success_message

def getFoodStats():
    print(request.args['timestamp'])
    timestamp = request.args['timestamp']

    result = queryDbStats(timestamp, TABLE_NAME_OPTIONS[1])
    success_message = {
        'message': 'food inventory stats',
        'status': 200,
        'content': json.dumps(result)
    }
    return success_message

def queryDbStats(timestamp, table_name):
    session = DB_SESSION()
    
    print(f'querying merch stats from database')
    sql_query = 'SELECT * FROM inventory.%s WHERE date_added >= "%s"' % (table_name,timestamp)

    result = session.execute(sql_query)
    session.close()
    result_list = []

    if table_name == TABLE_NAME_OPTIONS[0]:
        for row in result:
            result_list.append({'SKU': row[0], 'merchPrice': row[1], 'merchQuantity': row[2], 'merchName': row[3], 'date_added': str(row[4]), 'trace_id': row[5]})
    else :
        for row in result:
            result_list.append({'foodName': row[0], 'foodPrice': row[1], 'foodQuantity': row[2], 'expirationDate': str(row[3]), 'date_added': str(row[4]), 'trace_id': row[5]})

    return result_list



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('STEVENCHANG420-RetailFoodAPI_Template-1.0.0.yaml',
            strict_validation=True,
            validate_responses=True)

if __name__ == '__main__':

    app.run(port=8090)
