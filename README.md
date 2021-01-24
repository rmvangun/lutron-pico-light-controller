# Lutron Pico Light Controller

*Use your [Lutron 3-Button with Raise/Lower Pico Remote](https://www.lutron.com/en-US/Products/Pages/Components/PicoWirelessController/Models.aspx#3-Button%20with%20Raise/Lower) to dim lights and store favorites*

## Installation

This app is best installed using
[HACS](https://github.com/custom-components/hacs), so that you can easily track
and download updates.

Alternatively, you can download the `pico_control` directory from inside the `apps` directory here to your
local `apps` directory, then add the configuration to enable the `pico_control`
module.

## How it works

This app responds to button presses on the [Lutron 3-Button with Raise/Lower Pico Remote](https://www.lutron.com/en-US/Products/Pages/Components/PicoWirelessController/Models.aspx#3-Button%20with%20Raise/Lower) to turn on or off lights, dim lights up or down, and store/retrieve a "favorite" setting.

You can pass either a single `light` entity or a `group` that contains dimmable lights. _Development Note: An attempt was made to allow for a comma-separated list of lights, but limitations with async programming in Appdaemon made the dimming action insufficiently performant._

Using the "favorites" feature is optional. If you provide an `input_number`, this will be used to store the current brightness level when long pressing the center button. A short press will use this value to set the lights to that brightness level. If you do not provide an `input_number`, the center button will set the lights to 50% brightness by default.

When controlling a group of lights, their average brightness will be calculated and used as a starting point when a dimming action begins.

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

## Issues/Feature Requests

Please submit issues and feature requests using Github issues. Some features I've considered include:

- The ability to optionally pass an `action` to trigger when hitting the center button
- Storing the individual brightness and state of lights and switches in a group to favorites, not just the average brightness
- Support for other Lutron Pico remote types

## Contributing

PRs are welcome! If you add or change how configuration parameters work, please update the validations to ensure that misconfigurations are reported.