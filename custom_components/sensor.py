from __future__ import annotations

import datetime
import http.client
import json
import logging
import urllib.parse

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.helpers.config_validation as cv

ATTR_LOCATION = "Location"
ATTR_LINE = "Line"
ATTR_ETA = "ETA"
ATTR_CAR = "Car"
ATTR_DEST = "Destination"

CONF_API_KEY = 'api_key'
CONF_STATION_CODE = 'B04'
CONF_LINE = 'RD'

DEFAULT_NAME = 'WMATA Trains'

MIN_UPDATE = datetime.timedelta(seconds=10)
TIME_STR_FORMAT = "%H:%M"

API_KEY = '8b9a7a21d4cb4a38925d9cc45d0d5e59'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_STATION_CODE): cv.string,
    vol.Optional(CONF_LINE): cv.string
})


_LOGGER = logging.getLogger(__name__)


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:

    train_sensors = fetch_train_data()

    add_entities(train_sensors)


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
