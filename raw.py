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

TABLE_NAME_OPTIONS = ['merch_inventory','food_inventory']
MAX_VALUES_ALLOWED_IN_DB = 10
EVENT_FILE_OUT = 'data.json'

def write_to_json(timestamp,body):
    event = {}
    event['timestamp'] = str(timestamp)
    event['eventMessage']=f'Inventory updated, {body} added to database !'

    db = json.load(open(EVENT_FILE_OUT, 'r'))
    print(len(db))
    if len(db) < MAX_VALUES_ALLOWED_IN_DB:
        db.insert(0,event)
    else :
        db.pop()
        db.insert(0,event)
    with open(EVENT_FILE_OUT, 'w') as outfile:
        json.dump(db, outfile)
    

# function to handle endpoint 
def addmerchInventory(body):
    print(f'writing to json {body}')
    timestamp = datetime.datetime.now()
    write_to_json(timestamp,body)
    print(body, TABLE_NAME_OPTIONS[0])
    add_to_database(body,TABLE_NAME_OPTIONS[0])
    return NoContent, 201

def addfoodInventory(body):
    print(f'writing to json {body}')
    timestamp = datetime.datetime.now()
    write_to_json(timestamp,body)
    add_to_database(body,TABLE_NAME_OPTIONS[1])
    return NoContent, 201

def add_to_database(body,table_name):
    session = DB_SESSION()
    if table_name == TABLE_NAME_OPTIONS[0]:
        print(f'adding merch to database {body}')
        merch = Merch(body['SKU'],body['merchPrice'],body['merchQuantity'],body['merchName'])
        session.add(merch)
    elif table_name == TABLE_NAME_OPTIONS[1]:
        print(f'adding food to database {body}')
        food = Food(body['foodName'],body['foodPrice'],body['foodQuantity'],body['expirationDate'])
        session.add(food)
    session.commit()
    session.close()



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('STEVENCHANG420-RetailFoodAPI_Template-1.0.0.yaml',
            strict_validation = True,
            validate_responses = True)
DB_ENGINE = create_engine("sqlite:///inventory.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

if __name__ == '__main__':

    app.run(port=8090)