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
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

TABLE_NAME_OPTIONS = ['merch_inventory', 'food_inventory']

with open('storage_config.yml', 'r') as f:
    storage_config = yaml.safe_load(f.read())
STORAGE_SETTING = storage_config['datastore'] # for local storage
STORAGE_SETTING = storage_config['cloudstore'] # for cloud storage
print(STORAGE_SETTING)
with open('app_config.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

logger = logging.getLogger('basicLogger')

STORAGE_MERCH_URL = app_config['storage_merch']['url']
STORAGE_FOOD_URL = app_config['storage_food']['url']

with open('storage_log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

DB_ENGINE = create_engine(
    f"mysql+pymysql://{STORAGE_SETTING['user']}:{STORAGE_SETTING['password']}@{STORAGE_SETTING['hostname']}:{STORAGE_SETTING['port']}/{STORAGE_SETTING['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


KAFKA_CONNECTION_RETRY = 10

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

def health():
    return {"status": "ok"}, 200

def getMerchStats():

    starttime = request.args['starttime']
    endtime = request.args['endtime']
    result = queryDbStats(starttime, endtime , TABLE_NAME_OPTIONS[0])
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
    starttime = request.args['starttime']
    endtime = request.args['endtime']
    result = queryDbStats(starttime, endtime , TABLE_NAME_OPTIONS[1])
    success_message = {
        'message': 'food inventory stats',
        'status': 200,
        'content': json.dumps(result)
    }
    return success_message

def queryDbStats(starttime, endtime ,table_name):
    session = DB_SESSION()
    
    print(f'querying merch stats from database')
    sql_query = 'SELECT * FROM inventory.%s WHERE date_added >= "%s" AND date_added <= "%s"' % (table_name,starttime, endtime)

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

def process_message():
    hostname = "%s:%d" % (app_config["kafka"]["hostname"],app_config["kafka"]["port"])

    # implement retry logic

    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["kafka"]["topic"])]
    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
    reset_offset_on_start=False,
    auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == 'merch inventory': # Change this to your event type
        # Store the event1 (i.e., the payload) to the DB
            add_to_database(payload, TABLE_NAME_OPTIONS[0])
    
            # Commit the message so that it is not read again
        elif msg["type"] == "food inventory": # Change this to your event type
        # Store the event2 (i.e., the payload) to the DB
        # Commit the new message as being read
            add_to_database(payload, TABLE_NAME_OPTIONS[1])
 
        consumer.commit_offsets()

def kafka_connection_retry():
    hostname = "%s:%d" % (app_config["kafka"]["hostname"],app_config["kafka"]["port"])
    current_retry = 0 # for retrying kafka connection
    while current_retry < KAFKA_CONNECTION_RETRY:
        print('trying to connect to kafka')
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[app_config["kafka"]["topic"]]
            consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                auto_offset_reset=OffsetType.LATEST,
                reset_offset_on_start=True,
                consumer_timeout_ms=100)
            break
        except Exception as e:
            logger.error("Error connecting to kafka %s" % e)
            current_retry += 1
    if current_retry == KAFKA_CONNECTION_RETRY:
        logger.error("Failed to connect to kafka")
        exit(1)
    else:
        logger.info("Connected to kafka !!!")
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('STEVENCHANG420-RetailFoodAPI_Template-1.0.0.yaml',
            strict_validation=True,
            validate_responses=True)



if __name__ == '__main__':
    kafka_connection_retry()
    t1 = Thread(target=process_message)
    t1.setDaemon(True)
    t1.start()
    
    app.run(port=8090)
