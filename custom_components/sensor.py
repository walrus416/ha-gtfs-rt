import datetime
import http.client
import json
import logging
import urllib.parse

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, ATTR_LONGITUDE, ATTR_LATITUDE)
import homeassistant.util.dt as dt_util
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

ATTR_LOCATION = "Location"
ATTR_LINE = "Line"
ATTR_ETA = "ETA"
ATTR_CAR = "Car"
ATTR_DEST = "Destination"

CONF_API_KEY = 'api_key'
CONF_STATION = 'station'
CONF_LINE = 'line'

DEFAULT_NAME = 'WMATA Trains'

MIN_UPDATE = datetime.timedelta(seconds=10)
TIME_STR_FORMAT = "%H:%M"

API_KEY = '8b9a7a21d4cb4a38925d9cc45d0d5e59'

_LOGGER = logging.getLogger(__name__)


class Train:
    def __init__(self, car, dest, group, line, location, eta):
        self.car = car
        self.dest = dest
        self.group = group
        self.line = line
        self.location = location
        self.eta = eta


def main():
    """ Business Logic """
    train_dict = fetch_train_data()
    train_objects = train_data_to_objects(train_dict)


def train_data_to_objects(train_data):
    """
    Turns the train dictionary into objects
    """
    train_objs = []  # Initialize an empty list for the objects
    for train in train_data['Trains']:
        train_object = Train(car=train['Car'], dest=train['Destination'],
                             group=train['Group'], line=train['Line'],
                             location=train['LocationName'], eta=train['Min'])
        train_objs.append(train_object)

    return train_objs


def fetch_train_data():
    """
    Gets JSON data for all station predictions from the WMATA API
    """
    try:
        headers = {
            'api_key': API_KEY
        }
        params = urllib.parse.urlencode({})
        conn = http.client.HTTPConnection('api.wmata.com')
        conn.request("GET", "/StationPrediction.svc/json/GetPrediction/All?%s" % params, "{body}", headers)
        response = conn.getresponse()
        train_dict = response.read()
        train_dict = json.loads(train_dict)
        conn.close()
    except Exception as e:
        print(e)

    return train_dict


if __name__ == '__main__':
    main()
