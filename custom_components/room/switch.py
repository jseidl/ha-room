DEPENDENCIES = ['room', 'switch']

import logging

from time import sleep

from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.components.switch import SwitchDevice
from homeassistant.helpers.event import track_state_change
from homeassistant.const import (STATE_ON, STATE_OFF)

_LOGGER = logging.getLogger(__name__)

SLEEP_TIME = .3 # second

DOMAIN = "room"    
ENTITY_ID_FORMAT = DOMAIN + ".{}"
DATA_ROOM = "room_data"

def setup_platform(
    hass, config, add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    
    rooms = hass.data.get(DATA_ROOM)

    for room in rooms:   
        add_entities([RoomPresenceHoldSwitch(hass, room)], True)

#def setup_entry(hass, config_entry, add_devices):
#    add_devices([RoomPresenceHoldSwitch(hass, {})], True)

class RoomPresenceHoldSwitch(SwitchDevice, RestoreEntity):
    def __init__(self, hass, room):
        """Initialize the presence hold switch."""

        self.room = room      
        self.hass = hass
        self._name = f"Presence Hold ({self.room.name})"
        self._icon = 'mdi:car-brake-hold'
        self._state = None
        self._attributes = {}

        track_state_change(hass, self.room.presence_hold_sensors, self.update_switch)

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name
        
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
        if self._icon is not None:
            return self._icon
        return None

    def turn_on(self, **kwargs):
        """Turn on presence hold."""
        self._state = True
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn off presence hold."""
        self._state = False
        self.schedule_update_ha_state()

    async def async_added_to_hass(self):
        """Call when entity about to be added to hass."""
        # If not None, we got an initial value.
        await super().async_added_to_hass()
        if self._state is not None:
            return

        state = await self.async_get_last_state()
        self._state = state and state.state == STATE_ON

    def update_switch(self, entity_id, from_state, to_state):
        try:
            _LOGGER.debug(entity_id + " change from " + str(from_state) + " to " + str(to_state))

            # If trigger sensor is also a presence_sensor, wait until room is marked occupied
            if to_state.state == STATE_ON:
                if entity_id in self.room.presence_sensors:
                    while True:
                        if self.hass.states.get(self.room.sensor_id).state == STATE_ON:
                            break
                        sleep(SLEEP_TIME)

            # Loop over all entities and check their state
            for sensor in self.room.presence_hold_sensors:

                if self.hass.states.get(sensor).state in self.room.on_states:
                    self._state = True
                    self.schedule_update_ha_state()
                    return

            #@TODO add who triggered as attribute
            
            self._state = False
            self.schedule_update_ha_state()
            
        except:
            pass