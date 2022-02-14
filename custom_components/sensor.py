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


def setup_platform(hass, config, add_devices, discover_info=None):
    data = StationData(api_key=config.get(CONF_APIKEY),
                       stop_id=config.get(CONF_STOPID),
                       group=config.get(CONF_GROUP),
                       skip_arr_brd=config.get(CONF_SKIP_ARR_BRD),
                       line=config.get(CONF_LINE))
    sensors = []

    for train in config.get(CONF_TRAINS):
        sensors.append(StationSensor(
            data,
            train.get(CONF_STOPID),
            train.get(CONF_LINE),
            train.get(CONF_NAME),
        ))

    add_devices(sensors)


class StationSensor(object):
    """ Implementation of the sesnor """

    def __init__(self, station_data_obj, name):
        self.station_data_obj = station_data_obj
        station_data_obj.update()

        self._name = name
        self._train_data = station_data_obj._trains
        
        self._stop_id = self._train_data[0]['LocationCode']
        self._stop_name = self._train_data[0]['LocationName']
        self._line = self._train_data[0]['Line']
        self._destination = self._train_data[0]['DestinationName']
        self._time_to_arrival = self._train_data[0]['Min']
        self.update()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        """ Returns sensor state """
        return self._time_to_arrival

    @property
    def device_state_attributes(self):
        """ Returns state attrinutes"""
        attrs = {
            ATTR_STOPID: self._stop_id,
            ATTR_STOPNAME: self._stop_name,
            ATTR_LINE: self._line,
            ATTR_DESTINATION: self._destination,
        }

        if len(self._train_data) > 1:
            attrs[ATTR_NEXT] = self._train_data[1]['Min']

        return attrs

    @property
    def unit_of_measurement(self):
        """ Returns the unit for the state """
        if self.state == 'ARR' or self.state == 'BRD':
            return ''
        else:
            return 'min'

    @property
    def icon(self):
        """ Returns the icon to use in the frontend"""
        return ICON

    def update(self):
        self.station_data_obj.update()


class StationData(object):
    """ For handling data retrieval"""

    def __init__(self, api_key, stop_id, group, skip_arr_brd, line=None):
        self.api_key = api_key
        self.stop_id = stop_id
        self.group = group
        self.skip_arr_brd = skip_arr_brd
        self.line = line

        self._headers = {
            'api_key': api_key,
        }

        self._request_url = f'/StationPrediction.svc/json/GetPrediction/{stop_id}?%s'
        self._trains = None

    def update(self):
        """ Update the object """
        all_trains = self._update_trains()
        self._filter_trains(all_trains)

    def _update_trains(self):
        """ Get all the trains in and out of the station"""
        params = urllib.parse.urlencode({})
        try:
            conn = http.client.HTTPConnection('api.wmata.com')
            conn.request('GET', self._request_url % params, '{body}', self._headers)
            response = conn.getresponse()
            train_data = json.loads(response.read())
            train_data = train_data['Trains']
        except Exception as err:
            _LOGGER.error(f"updating station got:{err}")

        return train_data

    def _filter_trains(self, train_data):
        """ Takes the data and uses the parameters to select which trains to show """

        if self.line is not None:
            train_data = [train for train in train_data if train['Line'] == self.line]

        if self.skip_arr_brd is True:
            train_data = [train for train in train_data if (train['Min'] != 'ARR' and train['Min'] != 'BRD')]

        train_data = [train for train in train_data if train['Group'] == self.group]

        self._trains = train_data


if __name__ == '__main__':
    station = StationData(api_key='8b9a7a21d4cb4a38925d9cc45d0d5e59', stop_id='B04', group='2', skip_arr_brd=False, line='RD')
    station.update()
    train = StationSensor(station, 'Name')
    print(train.device_state_attributes)
