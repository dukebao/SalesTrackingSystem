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
from flask import Flask, request, jsonify
import yaml
import logging
import uuid
import logging.config

TABLE_NAME_OPTIONS = ['merch_inventory', 'food_inventory']

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


app = Flask(__name__)


@app.route('/merch-inventory', methods=['POST'])
def add_merch_inventory():
    print(request.json)
    body = request.json
    add_to_database(body, TABLE_NAME_OPTIONS[0])
    success_message = {'message': 'merch inventory added',
                       'status': 201, 'content': request.json}
    logger.info(f'Merch Storage Service : trace_id: {body["trace_id"]} write to database inventory table merch_inventory')
    return success_message


@app.route('/food-inventory', methods=['POST'])
def add_food_inventory():
    print(request.json)
    body = request.json
    add_to_database(body, TABLE_NAME_OPTIONS[1])
    success_message = {'message': 'food inventory added',
                       'status': 201, 'content': request.json}
    logger.info(f'Food Storage Service : trace_id: {body["trace_id"]} write to database inventory table food_inventory')
    return success_message

with open('storage_config.yml', 'r') as f:
    storage_config = yaml.safe_load(f.read())
STORAGE_SETTING = storage_config['datastore']
print(STORAGE_SETTING)
#DB_ENGINE = create_engine("sqlite:///inventory.sqlite")
DB_ENGINE = create_engine(f"mysql+pymysql://{STORAGE_SETTING['user']}:{STORAGE_SETTING['password']}@{STORAGE_SETTING['hostname']}:{STORAGE_SETTING['port']}/{STORAGE_SETTING['db']}")

with open('storage_log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

if __name__ == '__main__':

    app.run(port=8090)
