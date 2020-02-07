# Room Presence

This component lets you define rooms in your house and assign sensors that will trigger the presence occupied status (and clear when they are clear). A switch called "Presence Hold" will be created for each room you add that will prevent the occupancy status to change. This is really useful when you are watching TV sitting still and you don't want the room to be marked clear when your motion sensor stops detecting you, or when you're sleep and you don't want your lights coming up when you move. There's a parameter that defines which sensors will trigger/clear "Presence Hold" automatically.

Finally, you can create automations that triggers on room occupancy ON / OFF (like turning on and off your lights) without the need of manually coding a lot of automations for each room you have.

## Configuration
```
room:
  living_room:
    name: "Living Room"
    presence_sensors:
      - binary_sensor.motion_living_room
      - media_player.living_room_alexa
      - binary_sensor.door_living_room
      - binary_sensor.tv_living_room
    presence_hold_sensors:
      - binary_sensor.tv_living_room
      - media_player.living_room_alexa
    icon: 'mdi:sofa'
    on_states:
      - on
      - playing
      - home
    clear_timeout: 30
```

### Dealing with discovery
Room component needs to hook entity states at load time and discovered components are usually not available when room starts. In order to cope with that, it's recommended to group your discoverable presence sensors into groups and add those groups into the `presence_sensors` entry.

If you wanna get fancy, you can create a template `binary_sensor` so you can have it be a proper motion sensor:
```
group:
  motion_living_room:
    name: Motion (Living Room)
    entities:
      - binary_sensor.motion_meistersensor_living_room
      - binary_sensor.zooz_zse40_gamma_motion
      - group.motion_dining_room
      - binary_sensor.motion_blueiris_living_room
      - binary_sensor.motion_blueiris_bookshelf

binary_sensor:
  - platform: template
    sensors:
      motion_living_room:
        friendly_name: "Motion (Living Room)"
        device_class: motion
        value_template: "{{ is_state('group.motion_living_room', 'on') }}"
```

### Default Options
* `clear_timeout`: 5 (seconds)
* `on_states`: `on`, `home` and `playing`

## Issues? 
Please report any issues or feature requests on the `Issues` area.
