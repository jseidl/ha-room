DEPENDENCIES = ['room', 'binary_sensor']

import logging

from datetime import timedelta
from time import sleep

from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.helpers.event import track_state_change, call_later, track_time_interval 
from homeassistant.const import (STATE_ON, STATE_OFF)

_LOGGER = logging.getLogger(__name__)

SLEEP_TIME = .3 # seconds

DATA_ROOM = "room_data"
BINARY_SENSOR_DEVICE_CLASS = "occupancy"

def setup_platform(
    hass, config, add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    
    rooms = hass.data.get(DATA_ROOM)

    for room in rooms:   
        add_entities([RoomPresenceHoldBinarySensor(hass, room)], True)

def setup_entry(hass, config_entry, add_devices):
    add_devices([RoomPresenceHoldBinarySensor(hass, {})], True)

class RoomPresenceHoldBinarySensor(BinarySensorDevice, RestoreEntity):
    def __init__(self, hass, room):
        """Initialize the presence hold switch."""

        self.room = room      
        self.hass = hass
        self._name = f"Room ({self.room.name})"
        self._state = None
        self._attributes = {}

        track_state_change(hass, self.room.presence_sensors, self.update_room)
        delta = timedelta(seconds=self.room.update_interval)
        track_time_interval(self.hass, self.update_state, delta)

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name
        
    @property
    def should_poll(self):
        """If entity should be polled."""
        return False

    @property
    def device_state_attributes(self):
        """Return the attributes of the switch."""
        return self._attributes

    @property
    def is_on(self):
        """Return true if presence hold is on."""
        return self._state

    @property
    def icon(self):
        """Return the icon to be used for this entity."""
        if self.room.icon is not None:
            return self.room.icon
        return None

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return BINARY_SENSOR_DEVICE_CLASS

    async def async_added_to_hass(self):
        """Call when entity about to be added to hass."""
        # If not None, we got an initial value.
        await super().async_added_to_hass()
        if self._state is not None:
            return

        self.update_state()

    def update_room(self, entity_id, from_state, to_state):
        try:
            _LOGGER.debug(entity_id + " change from " + str(from_state) + " to " + str(to_state))

            # If sensor is also a presence_hold_sensors, wait for the switch to come off
            if to_state.state == STATE_OFF:
                if entity_id in self.room.presence_hold_sensors:
                    while True:
                        if self.hass.states.get(self.room.switch_id).state == STATE_OFF:
                            break
                        sleep(SLEEP_TIME)

            # If presence_hold is on, do nothing
            if self.hass.states.get(self.room.switch_id).state == STATE_ON:
                return

            self.update_state()
            self.schedule_update_ha_state()

            call_later(self.hass, self.room.clear_timeout, self.sensor_timeout)
            
        except:
            pass

    def sensor_timeout(self, event_time):
        """ Check if there are ON sensors, if not clears room."""
        # If presence_hold is on, do nothing
        if self.hass.states.get(self.room.switch_id).state == STATE_ON:
            return

        for sensor in self.room.presence_sensors:
            if self.hass.states.get(sensor).state in self.room.on_states:
                return

        self._state = False
        self.schedule_update_ha_state()

    def update_state(self, init=False):        
        # Loop over all entities and check their state
        for sensor in self.room.presence_sensors:

            if self.hass.states.get(sensor).state in self.room.on_states:
                self._state = True
                return
        
        if self.room.clear_timeout == 0 or init:
            self._state = False