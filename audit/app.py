import connexion
from connexion import NoContent
import json
import datetime
import swagger_ui_bundle
import yaml
import logging
import logging.config
from pykafka import KafkaClient

with open('app_config.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('audit_log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

def getAuditMerch(index):
    """Get audit trail for merch"""
    # ok
    hostname = hostname = "%s:%d" % (app_config["kafka"]["hostname"],app_config["kafka"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["kafka"]["topic"])]
    
    # here we reset the offset on the start so that we retrieve message 
    # from the beginning of the topic
    # to prevent the for loop from blocking, we set the timeout 
    # to 0.1 second
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)
    logger.info("retrieving merch audit trail at %d" % index)
    message_dict = {}
    start = 1 
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'merch inventory':
                message_dict[start] = msg
                start += 1
        return message_dict[index] , 200
    except:
        logger.error("No more messages")
    logger.error("could not find merch audit trail at %d" % index)

    return {"message":"Not Found"}, 404

def getAuditFood(index):
    """Get audit trail for food"""
    # ok
    hostname = hostname = "%s:%d" % (app_config["kafka"]["hostname"],app_config["kafka"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["kafka"]["topic"])]
    
    # here we reset the offset on the start so that we retrieve message 
    # from the beginning of the topic
    # to prevent the for loop from blocking, we set the timeout 
    # to 0.1 second
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,consumer_timeout_ms=1000)
    logger.info("retrieving food audit trail at %d" % index)
    message_dict = {}
    start = 1 
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'food inventory':
                message_dict[start] = msg
                start += 1
        return message_dict[index] , 200
    except:
        logger.error("No more messages")
    logger.error("could not find food audit trail at %d" % index)

    return {"message":"Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('STEVENCHANG420-RetailFoodAPI_Template-1.0.0.yaml',
            strict_validation=True,
            validate_responses=True)

if __name__ == '__main__':
    app.run(port=8110)