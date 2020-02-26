DEPENDENCIES = ['room', 'switch' 'binary_sensor']

import logging

from datetime import timedelta, datetime
from time import sleep

from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.helpers.event import track_state_change, call_later, track_time_interval 
from homeassistant.const import STATE_ON, STATE_OFF, STATE_HOME

_LOGGER = logging.getLogger(__name__)

SLEEP_TIME = .3 # seconds

DATA_ROOM = "room_data"
BINARY_SENSOR_DEVICE_CLASS = "occupancy"

def setup_platform(
    hass, config, add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    
    rooms = hass.data.get(DATA_ROOM)

    for room in rooms:   
        add_entities([RoomPresenceBinarySensor(hass, room)], True)

def setup_entry(hass, config_entry, add_devices):
    add_devices([RoomPresenceBinarySensor(hass, {})], True)

class RoomPresenceBinarySensor(BinarySensorDevice, RestoreEntity):
    def __init__(self, hass, room):
        """Initialize the presence hold switch."""

        self.room = room      
        self.hass = hass
        self._name = f"Room ({self.room.name})"
        self._state = None
        self._attributes = {}
        self.last_off_time = datetime.utcnow()

        track_state_change(hass, self.room.presence_sensors, self.sensor_state_change)
        delta = timedelta(seconds=self.room.update_interval)
        track_time_interval(self.hass, self.update_room, delta)

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

        # Was having a race condition with the switch component of
        # this integration. Better leave commented and let the 
        # update_interval hook do the work
        #self.update_state()

    def sensor_state_change(self, entity_id, from_state, to_state):
        try:
            _LOGGER.debug(entity_id + " change from " + str(from_state) + " to " + str(to_state))

            # If sensor is also a presence_hold_sensors, wait for the switch to come off
            if to_state.state == STATE_OFF:

                self.last_off_time = datetime.utcnow() # Update last_off_time

                if entity_id in self.room.presence_hold_sensors:
                    while True:
                        if self.hass.states.get(self.room.switch_id).state == STATE_OFF:
                            break
                        sleep(SLEEP_TIME)

            self.update_state()
            
        except:
            pass

    def update_room(self, next_interval):

        self.update_state()

    def update_state(self):

        # If presence_hold is on, do nothing
        if self.hass.states.get(self.room.switch_id).state == STATE_ON:
            return

        room_state = self.get_room_state()

        if room_state:
            self._state = True
        else:
            
            clear_delta = timedelta(seconds=self.room.clear_timeout)
            last_clear = self.last_off_time
            clear_time = last_clear + clear_delta
            time_now = datetime.utcnow()

            if time_now >= clear_time:
                self._state = False

        self.schedule_update_ha_state()

    def get_room_state(self):        
        # Loop over all entities and check their state
        for sensor in self.room.presence_sensors:

            entity = self.hass.states.get(sensor)

            if not entity:
                _LOGGER.error(f"{sensor} entity is not found")
                continue

            if entity.state in self.room.on_states:
                return True

        return False
