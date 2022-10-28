import connexion
from connexion import NoContent
import json
import datetime
import swagger_ui_bundle
import connexion
from connexion import NoContent
import json
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
from pykafka import KafkaClient


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
    kafka_config = app_config['kafka']

    host_info = f"{kafka_config['hostname']}:{kafka_config['port']}"
    client = KafkaClient(
        hosts=host_info)
    topic = client.topics[str.encode(kafka_config['topic'])]
    producer = topic.get_sync_producer()
    msg = {"type": "merch inventory",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f'Merch Receiver Service : trace_id: {trace} status code 201')

    return msg, 201


def addfoodInventory(body):
    trace = str(uuid.uuid4())
    body['trace_id'] = trace
    headers = {'Content-Type': 'application/json'}
    kafka_food_config = app_config['kafka']
    print(kafka_food_config)
    print(body)
    host_info = f"{kafka_food_config['hostname']}:{kafka_food_config['port']}"
    client = KafkaClient(
        hosts=host_info)
    topic = client.topics[str.encode(kafka_food_config['topic'])]
    producer = topic.get_sync_producer()
    msg = {"type": "food inventory",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
           "payload": body}
    msg_str = json.dumps(msg)
    print(msg_str)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f'Food Receiver Service : trace_id: {trace} status code 201')

    return msg, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('STEVENCHANG420-RetailFoodAPI_Template-1.0.0.yaml',
            strict_validation=True,
            validate_responses=True)

if __name__ == '__main__':

    app.run(port=8080)
