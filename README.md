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

### Default Options
* `clear_timeout`: 5 (seconds)
* `on_states`: `on`, `home` and `playing`

## Issues? 
Please report any issues or feature requests on the `Issues` area.
