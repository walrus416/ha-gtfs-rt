from __future__ import annotations

import datetime
import http.client
import json
import logging
import urllib.parse
from typing import Any

#import voluptuous as vol
#import homeassistant.helpers.config_validation as cv

#from homeassistant.core import HomeAssistant
#from homeassistant.helpers.entity_platform import AddEntitiesCallback
#from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
#from homeassistant.util import Throttle

#from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity, SensorStateClass,
                                             #PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA)

import logging

_LOGGER = logging.getLogger(__name__)

CONF_APIKEY = 'api_key'
CONF_TRAINS = 'trains'
CONF_STOPID = 'stop_id'
CONF_LINE = 'line'
CONF_INTERVAL = 'update_interval'
CONF_GROUP = 'group'
CONF_SKIP_ARR_BRD = 'skip'
CONF_NAME = 'name'

ATTR_STOPID = 'Stop ID'
ATTR_STOPNAME = 'Stop Name'
ATTR_LINE = 'Line'
ATTR_DESTINATION = 'Destination'
ATTR_NEXT = 'Next Train'

ICON = 'mdi:train'
UPDATE_INTERVAL = datetime.timedelta(seconds=10)

"""
PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_APIKEY): cv.string,
        vol.Optional(CONFIG_SKIP_ARR_BRD, default=FALSE): cv.boolean,
        vol.Optional(CONFIG_NAME, default='WMATA Rail Station Sensor'): cv.string
        vol.Optional(CONF_TRAINS): [{
            vol.Required(CONF_STOPID): cv.string,
            vol.Required(CONF_GROUP): cv.string,
            vol.Optional(CONF_LINE): cv.string,
        }]
        
    }
)
"""


if __name__ == '__main__':
    pass
