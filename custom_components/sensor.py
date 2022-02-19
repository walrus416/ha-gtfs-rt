from __future__ import annotations

import datetime
import http.client
import json
import logging
import urllib.parse
from typing import Any

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util import Throttle

from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity, SensorStateClass,
                                             PLATFORM_SCHEMA as SENSOR_PLATFORM_SCHEMA)

_LOGGER = logging.getLogger(__name__)

CONF_APIKEY = 'api_key'
CONF_TRAINS = 'trains'
CONF_NAME = 'name'
CONF_STATION_CODE = 'stop_code'
CONF_GROUP = 'group'
CONF_LINE = 'line'
CONF_TRAIN_NUMBER = 'train_number'
CONF_OFFSET = 'offset'

ATTR_ARRIVING_IN = 'Arriving In'
ATTR_STOP_CODE = 'Stop Code'
ATTR_STOP_NAME = 'Stop Name'
ATTR_LINE = 'Line'
ATTR_DESTINATION = 'Destination'

ICON = 'mdi:train'
UPDATE_INTERVAL = datetime.timedelta(seconds=10)


PLATFORM_SCHEMA = SENSOR_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_APIKEY): cv.string,
        vol.Required(CONF_TRAINS): [{
            vol.Optional(CONF_NAME, default=f'Stop {CONF_STATION_CODE} Metro Sensor'): cv.string,
            vol.Required(CONF_STATION_CODE): cv.string,
            vol.Required(CONF_GROUP): cv.positive_int,
            vol.Optional(CONF_LINE): cv.string,
            vol.Optional(CONF_TRAIN_NUMBER, default=1): cv.positive_int,
            vol.Optional(CONF_OFFSET): cv.positive_int,
        }]
    }
)


def setup_platform(hass, config, add_devices, discovery_info=None):
    station_data = WMATAStationData(
        api_key=config.get(CONF_APIKEY),
        station_code=config.get(CONF_STATION_CODE)
    )

    sensors = []

    for train in config.get(CONF_TRAINS):
        sensors.append(TrainSensor(
            name=config.get(CONF_NAME),
            station_data=station_data,
            group=config.get(CONF_GROUP),
            train_number=config.get(CONF_TRAIN_NUMBER),
            offset=config.get(CONF_OFFSET),
            line=config.get(CONF_LINE)
        ))

    add_devices(sensors)


class TrainSensor(SensorEntity):
    """ The actual sensor """
    def __init__(self, name, station_data,  group, train_number=1, offset=None, line=None):
        """ Initialize the sensor """

        self.data = station_data._trains

        self._name = name
        self._group = group
        self._train_number = train_number
        self._offset = offset
        self._line = line

        self.update()

    def update(self):
        self.data.update()
        self._get_train_data()

    def _get_train_data(self):
        """ Filters train data down according to provided parameters. """
        train_data = self.data

        empty_train_data = {
            'Car': '-',
            'Destination': '-',
            'DestinationCode': '-',
            'DestinationName': '-',
            'Group': '-',
            'Line': '-',
            'LocationCode': '-',
            'LocationName': '-',
            'Min': '-',
        }

        filtered = list(filter(lambda d: d['Group'] == self._group, train_data))

        if self._offset is not None:
            offset_list = ['BRD', 'ARR', 'DLY', '---', '']

            filtered = list(filter(lambda d: d['Min'] not in offset_list, filtered))
            filtered = list(filter(lambda d: int(d['Min']) >= self._offset, filtered))

        if self._line is not None:
            filtered = list(filter(lambda d: d['Line'] == self._line, filtered))

        try:
            filtered_final = filtered[self._train_number - 1]
        except IndexError:
            return empty_train_data

        return filtered_final

    @property
    def name(self):
        return self.name

    @property
    def state(self):
        """ Returns the sensor state"""
        train_data = self._get_train_data()
        return train_data

    @property
    def device_state_attributes(self):
        """ Returns the sensor state attributes"""
        train_data = self._get_train_data()

        attrs = {
            ATTR_ARRIVING_IN: train_data['Min'],
            ATTR_STOP_CODE: train_data['LocationCode'],
            ATTR_STOP_NAME: train_data['LocationName'],
            ATTR_DESTINATION: train_data['DestinationName'],
            ATTR_LINE: train_data['Line'],
        }

    @property
    def unit_of_measurement(self):
        return 'min'

    @property
    def icon(self):
        return ICON


class WMATAStationData(object):
    """ Handles data retrieval to minimize API Calls"""
    def __init__(self, api_key, station_code):
        """ Initialize the obj """
        self.api_key = api_key
        self.station_code = station_code

        self._headers = {
            'api_key': api_key
        }
        self._update_url = f'/StationPrediction.svc/json/GetPrediction/{station_code}?%s'

        self._trains = []

    def update(self):
        self._update_trains()

    @Throttle(UPDATE_INTERVAL)
    def _update_trains(self):
        """ Get the train information for the station"""
        try:
            params = urllib.parse.urlencode({})
            conn = http.client.HTTPSConnection('api.wmata.com')
            conn.request('GET', self._update_url % params, '{body}', self._headers)
            response = conn.getresponse()
            station_data = json.loads(response.read().decode('utf-8'))
            conn.close()

        except Exception as err:
            _LOGGER.error(f'Unable to fetch station update, got: {err}')

        station_data = {k.lower(): v for k, v in station_data.items()}
        if 'message' in station_data:
            try:
                status_code = station_data['statuscode']
            except KeyError:
                status_code = ''

            error_msg = station_data['message']
            _LOGGER.error(f'Update error, WMATA API returned {status_code}: {error_msg}')

        else:
            self._trains = station_data['trains']


if __name__ == '__main__':
    station = WMATAStationData(api_key='8b9a7a21d4cb4a38925d9cc45d0d5e59', station_code='B03')
    station._update_trains()

    train = TrainSensor(name='hello', train_data=station, train_number=1, line='RD', group='1')
    train = train._get_train_data()

    print(train)

    train = TrainSensor(name='hello', train_data=station, train_number=2, line='RD', group='1')
    train = train._get_train_data()

    print(train)

    train = TrainSensor(name='hello', train_data=station, train_number=3, line='RD', group='1')
    train = train._get_train_data()

    print(train)

    train = TrainSensor(name='hello', train_data=station, train_number=4, line='RD', group='1')
    train = train._get_train_data()

    print(train)
