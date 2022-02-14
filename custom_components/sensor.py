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

from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity, SensorStateClass)

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass: HomeAssistant,
                   config: ConfigType,
                   add_entities: AddEntitiesCallback,
                   discovery_info: DiscoveryInfoType | None = None) -> None:
    """ Setup sensor platform"""
    add_entities([StationSensor()])

class StationSensor()

