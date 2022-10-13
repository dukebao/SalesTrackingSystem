import connexion
from connexion import NoContent
import json
import datetime
import swagger_ui_bundle
import connexion
from connexion import NoContent
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

TABLE_NAME_OPTIONS = ['merch_inventory', 'food_inventory']
MAX_VALUES_ALLOWED_IN_DB = 10
EVENT_FILE_OUT = 'data.json'

with open('app_config.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

STORAGE_MERCH_URL = app_config['storage_merch']['url']
STORAGE_FOOD_URL = app_config['storage_food']['url']

with open('receiver_log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


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


# function to handle endpoint
def addmerchInventory(body):
    trace = str(uuid.uuid4())
    body['trace_id'] = trace
    headers = {'Content-Type': 'application/json'}
    res = requests.post(
        STORAGE_MERCH_URL, json=body, headers=headers)

    logger.info(f'Merch Receiver Service : trace_id: {trace} status code {res.status_code}')
    return res.text, res.status_code


def addfoodInventory(body):
    trace = str(uuid.uuid4())
    body['trace_id'] = trace
    headers = {'Content-Type': 'application/json'}
    res = requests.post(STORAGE_FOOD_URL,
                        json=body, headers=headers)

    logger.info(f'Food Receiver Service : trace_id: {trace} status code {res.status_code}')

    return res.text, res.status_code


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('STEVENCHANG420-RetailFoodAPI_Template-1.0.0.yaml',
            strict_validation=True,
            validate_responses=True)

if __name__ == '__main__':

    app.run(port=8080)
