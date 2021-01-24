import hassapi as hass
import time

#
# App to implement Lutron Pico Remote control of lighting
# Args:
#
# sensor: sensor to monitor e.g. sensor.pico0
# entity: the light or light group to control e.g. light.bulb0
# brightness_lower: minimum bulb brigtness
# brightness_upper: maximum bulb brigtness
#
#
# Release Notes
#
# Version 1.0:
#   Initial Version

# State IDs
PICO_IDLE_ID          = 0
PICO_ON_BUTTON_ID     = 1
PICO_OFF_BUTTON_ID    = 4
PICO_CENTER_BUTTON_ID = 2
PICO_UP_BUTTON_ID     = 8
PICO_DOWN_BUTTON_ID   = 16

# Defaults
DEFAULT_DIM_DELAY     = 0.05
DEFAULT_DIM_INCREMENT = 5

class PicoControl(hass.Hass):

  def initialize(self):
    self.listen_state(self.state_change, self.args['sensor'])

  def noop(self):
    pass

  def on(self):
    self.turn_on(self.args['entity'])

  def off(self):
    self.turn_off(self.args['entity'])

  def up(self):
    self.adjust_brightness('up')

  def down(self):
    self.adjust_brightness('down')
  
  def stop(self):
    pass

  def get_light_entities(self, entity):
    entity_type = entity.split('.')[0]

    # Just add a single light to the list if the entity is a light
    if entity_type == 'light':
      return [entity]
    
    # Get all lights in the group
    elif entity_type == 'group':
      return [match for match in self.get_state(entity, attribute = 'all')['attributes']['entity_id'] if match.startswith('light.')]

    # Return empty list
    else:
      return []

  def get_average_brightness(self, entity):
    def get_brightness(light):
      brightness = self.get_state(light, attribute='brightness')
      if isinstance(brightness, int):
        return self.get_state(light, attribute='brightness')
      else:
        return None

    lights = self.get_light_entities(entity)
    brightnesses = [brightness for brightness in list(map(get_brightness, lights)) if isinstance(brightness, int)]
    return round(sum(brightnesses) / len(brightnesses))

  def adjust_brightness(self, direction):
    activated_button = PICO_UP_BUTTON_ID if direction == 'up' else PICO_DOWN_BUTTON_ID
    entity           = self.args['entity']
    sensor           = self.args['sensor']
    min_brightness   = self.args['min_brightness']
    max_brightness   = self.args['max_brightness']
    dim_delay        = self.args.get('dim_delay', DEFAULT_DIM_DELAY)
    dim_interval     = self.args.get('dim_interval', DEFAULT_DIM_INCREMENT)

    # Lights must be on first to acquire brightness
    self.turn_on(entity)

    # Try acquiring brightness a few times while lights wait to turn on
    for x in range(0, 5):
      try:
        brightness = self.get_average_brightness(entity)
        break
      except:
        time.sleep(dim_delay)

    # Continue adjusting brightness while up or down button is pressed
    while int(self.get_state(sensor)) == activated_button:
      
      # Determine next brightness setting
      brightness = brightness + dim_interval if direction == 'up' else brightness - dim_interval
      brightness = min_brightness if brightness < min_brightness else brightness
      brightness = max_brightness if brightness > max_brightness else brightness

      # Set the new brightness
      self.turn_on(entity, brightness=str(brightness))

      time.sleep(dim_delay)

  def state_change(self, entity, attribute, old, new, kwargs):
    self.pico_actions[new](self)

  pico_actions = {
    '0'  : stop,
    '1'  : on,
    '2'  : noop,
    '4'  : off,
    '8'  : up,
    '16' : down
  }
