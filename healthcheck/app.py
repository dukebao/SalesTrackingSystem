import connexion
from connexion import NoContent
import json
import datetime
import connexion
from connexion import NoContent
import json
import swagger_ui_bundle
import requests
import yaml
import logging
import logging.config
from multiprocessing import Pool
import pytz
from flask_cors import CORS, cross_origin

with open('app_config.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

SERVICES_OBJECT = app_config['services']

with open('healthcheck_log_config.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# function to handle endpoint


def serviceHealthCeck(serviceobject):
    url = app_config['services'][serviceobject]
    print(url)
    try:
        r = requests.get(url, timeout=5)
        print(r)
        if r.status_code == 200:
            return {serviceobject: "UP"}
        else:
            return {serviceobject: "DOWN"}
    except requests.exceptions.RequestException as e:
        return {serviceobject: "DOWN"}

def writetojson(dict):
    with open('healthcheckdata.json', 'r+') as f:
        file_data = json.load(f)
        file_data.append(dict)
        f.seek(0)
        json.dump(file_data, f, indent=4)

def healthcheck():
    with Pool() as pool:
        status = pool.map(serviceHealthCeck, SERVICES_OBJECT)
    logger.info("performing health check ... ")
    result = {'Last Update': datetime.datetime.now(tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")}
    for i in status:
        result.update(i)
    writetojson(result)
    logger.info("health check completed")
    logger.info('health check result: %s', result)

    return result, 200


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('STEVENCHANG420-RetailFoodAPI_Template-1.0.0.yaml',
            strict_validation=True,
            validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
if __name__ == '__main__':
    app.run(port=8120)
