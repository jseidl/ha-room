"""Room platform for Homme Assistant."""
import logging

import voluptuous as vol

from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import load_platform
from homeassistant.const import (
    ATTR_ENTITY_ID, CONF_NAME, STATE_ON,
    STATE_OFF, SERVICE_TURN_ON, SERVICE_TURN_OFF)

_LOGGER = logging.getLogger(__name__)

DOMAIN = "room"
ENTITY_ID_FORMAT = DOMAIN + ".{}"
SENSOR_DOMAIN = "binary_sensor"
SENSOR_ENTITY_ID_FORMAT = SENSOR_DOMAIN + ".room_{}"
SWITCH_DOMAIN = "switch"
SWITCH_ENTITY_ID_FORMAT = SWITCH_DOMAIN + ".presence_hold_{}"

DATA_ROOM = "room_data"

# Configuration parameters
CONF_PRESENCE_SENSORS  = "presence_sensors" # cv.entities_id
CONF_PRESENCE_HOLD_SENSORS  = "presence_hold_sensors" # cv.entities_id
CONF_ON_STATES  = "on_states" # cv.list
CONF_CLEAR_TIMEOUT  = "clear_timeout" # cv.positive_int
CONF_UPDATE_INTERVAL  = "update_interval" # cv.positive_int
CONF_ICON = "icon" # cv.string

# Defaults
DEFAULT_ICON = 'mdi:sofa'
DEFAULT_CLEAR_TIMEOUT = 5
DEFAULT_UPDATE_INTERVAL = 30
DEFAULT_ON_STATES = ['on','home','playing']
# Config Schema
CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                cv.slug: vol.Any(
                    {
                        vol.Required(CONF_NAME): cv.string,
                        vol.Required(CONF_PRESENCE_SENSORS): cv.entity_ids,
                        vol.Optional(CONF_PRESENCE_HOLD_SENSORS, default=[]): cv.entity_ids,
                        vol.Optional(CONF_ON_STATES, default=DEFAULT_ON_STATES): cv.ensure_list,
                        vol.Optional(CONF_CLEAR_TIMEOUT, default=DEFAULT_CLEAR_TIMEOUT): cv.positive_int,
                        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): cv.positive_int,
                        vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string,
                    },
                    None,
                )
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    """Set up rooms."""

    load_platform(hass, 'switch', DOMAIN, {}, config)
    load_platform(hass, 'binary_sensor', DOMAIN, {}, config)

    rooms = []

    for room_id, room_config in config[DOMAIN].items():
        if not room_config:
            room_config = {}

        name = room_config.get(CONF_NAME)
        presence_sensors = room_config.get(CONF_PRESENCE_SENSORS)
        presence_hold_sensors = room_config.get(CONF_PRESENCE_HOLD_SENSORS)
        on_states = room_config.get(CONF_ON_STATES)
        clear_timeout = room_config.get(CONF_CLEAR_TIMEOUT)
        update_interval = room_config.get(CONF_UPDATE_INTERVAL)
        icon = room_config.get(CONF_ICON)

        rooms.append(Room(hass, room_id, name, presence_sensors, presence_hold_sensors, on_states, update_interval, clear_timeout, icon))

    hass.data[DATA_ROOM] = rooms

    return True

class Room(object):
    """Representation of a room."""

    def __init__(self, hass, room_id, name, presence_sensors, presence_hold_sensors, on_states, update_interval, clear_timeout, icon):
        """Initialize a room."""
        self.hass = hass
        self.room_id = room_id
        self.name = name

        self.sensor_id = SENSOR_ENTITY_ID_FORMAT.format(room_id)
        self.switch_id = SWITCH_ENTITY_ID_FORMAT.format(room_id)        
        
        self.presence_sensors = presence_sensors
        self.presence_hold_sensors = presence_hold_sensors
        self.on_states = on_states
        self.clear_timeout = clear_timeout
        self.update_interval = update_interval
        self.icon = icon