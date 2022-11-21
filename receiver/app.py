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
from pykafka.common import OffsetType
import os 


KAFKA_CONNECTION_RETRY = 10

TABLE_NAME_OPTIONS = ['merch_inventory', 'food_inventory']
MAX_VALUES_ALLOWED_IN_DB = 10
EVENT_FILE_OUT = 'data.json'

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_config.yml"
    log_conf_file = "/config/receiver_log_config.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_config.yml"
    log_conf_file = "receiver_log_config.yml"
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')
    logger.info("App Conf File: %s" % app_conf_file)
    logger.info("Log Conf File: %s" % log_conf_file)

# with open('receiver_log_config.yml', 'r') as f:
#     log_config = yaml.safe_load(f.read())
#     logging.config.dictConfig(log_config)
#     logger = logging.getLogger('basicLogger')
# with open('app_config.yml', 'r') as f:
#     app_config = yaml.safe_load(f.read())

STORAGE_MERCH_URL = app_config['storage_merch']['url']
STORAGE_FOOD_URL = app_config['storage_food']['url']






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


def getMerchAudit(index):
    kafka_config = app_config['kafka']
    host_info = f"{kafka_config['hostname']}:{kafka_config['port']}"
    client = KafkaClient(hosts=host_info)
    topic = client.topics[str.encode(kafka_config["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving merch at index %d" % index)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
    except:
        logger.error("No more messages found")
    logger.error("Could not find merch at index %d" % index)
    return {"message": "Not Found"}, 404

def getFoodAudit(index):
    kafka_config = app_config['kafka']
    host_info = f"{kafka_config['hostname']}:{kafka_config['port']}"
    client = KafkaClient(hosts=host_info)
    topic = client.topics[str.encode(kafka_config["topic"])]
    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                            consumer_timeout_ms=1000)
    logger.info("Retrieving food at index %d" % index)
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
    except:
        logger.error("No more messages found")
    logger.error("Could not find food at index %d" % index)
    return {"message": "Not Found"}, 404        

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

def health():
    return {"status": "ok"}, 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('STEVENCHANG420-RetailFoodAPI_Template-1.0.0.yaml',
            strict_validation=True,
            validate_responses=True)

if __name__ == '__main__':
    kafka_connection_retry()
    app.run(port=8080)
