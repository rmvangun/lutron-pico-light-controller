## App configuration

```yaml
pico_control:
  module                       : pico_control
  class                        : PicoControl
  sensor                       : sensor.pico0
  entity                       : light.bulb0
  input_number                 : input_number.pico0_favorite
  min_brightness               : 25
  max_brightness               : 255
  dim_delay                    : 0.05
  dim_interval                 : 5
  favorite_long_press_duration : 3
```

key | optional | type | default | description
-- | -- | -- | -- | --
`module` | False | string | | `pico_control`
`class` | False | string | | `PicoControl`
`sensor` | False | string | | Pico switch to monitor
`entity` | False | string | | The light or light group to control 
`input_number` | True | string | | An input_number used to store a favorite brightness persistently
`min_brightness` | False | number | | Minimum bulb brigtness
`max_brightness` | False | number | | Maximum bulb brigtness
`dim_delay` | True | number | 0.05 | The seconds to wait between each incremental brightness change while dimming
`dim_interval` | True | number | 5 | The incremental change in brightness while dimming
`favorite_long_press_duration` | True | number | 3 | Number of seconds the favorite button must be held to qualify as a "long press"