from sqlalchemy import create_engine, MetaData
from sqlalchemy_utils import database_exists, create_database
from merch import Merch
from food import Food
import yaml

with open('storage_config.yml', 'r') as f:
  cfg = yaml.safe_load(f)

db_con = f"mysql+pymysql://{cfg['cloudstore']['user']}:{cfg['cloudstore']['password']}@{cfg['cloudstore']['hostname']}:{cfg['cloudstore']['port']}/{cfg['cloudstore']['db']}"
engine = create_engine(db_con, echo=True, future=True)

if not database_exists(engine.url):
    create_database(engine.url)
else:
  # Connect the database if exists.
  connection = engine.connect()

metadata = MetaData(engine)

Merch.metadata.create_all(engine)
Food.metadata.create_all(engine)