import hassapi as hass
import time
from datetime import datetime

#
# App to implement Lutron Pico Remote control of lighting
# Args:
#
# sensor                       : Sensor to monitor e.g. sensor.pico0
# entity                       : The light or light group to control e.g. light.bulb0
# input_number                 : An input number used to store a favorite brightness persistently; optional
# favorite_long_press_duration : Number of seconds the favorite button must be held to qualify as a "long press"; default 3
# min_brightness               : Minimum bulb brigtness
# max_brightness               : Maximum bulb brigtness
# dim_delay                    : The seconds to wait between each incremental brightness change while dimming; default 0.05
# dim_interval                 : The incremental change in brightness while dimming; default 5
#
# Release Notes
#
# Version 1.0:
#   Initial Version

# State IDs
PICO_IDLE_ID          = 0
PICO_ON_BUTTON_ID     = 1
PICO_CENTER_BUTTON_ID = 2
PICO_OFF_BUTTON_ID    = 4
PICO_UP_BUTTON_ID     = 8
PICO_DOWN_BUTTON_ID   = 16

# Defaults
DEFAULT_DIM_DELAY                    = 0.05
DEFAULT_DIM_INCREMENT                = 5
DEFAULT_FAVORITE_LONG_PRESS_DURATION = 3

class PicoControl(hass.Hass):

  ##############
  # Initialize #
  ##############

  def initialize(self):
    self.validate()
    self.listen_state(self.state_change, self.args['sensor'])

  ##################
  # Button Actions #
  ##################

  def on(self):
    self.turn_on(self.args['entity'], transition=0)

  def off(self):
    self.turn_off(self.args['entity'], transition=0)

  def center(self):
    self.favorite()

  def up(self):
    self.adjust_brightness('up')

  def down(self):
    self.adjust_brightness('down')
  
  def stop(self):
    pass

  def state_change(self, entity, attribute, old, new, kwargs):
      self.pico_actions[new](self)

  pico_actions = {
    '0'  : stop,
    '1'  : on,
    '2'  : center,
    '4'  : off,
    '8'  : up,
    '16' : down
  }

  ###########
  # Dimming #
  ###########

  def adjust_brightness(self, direction):
    entity           = self.args['entity']
    sensor           = self.args['sensor']
    min_brightness   = self.args['min_brightness']
    max_brightness   = self.args['max_brightness']
    dim_delay        = self.args.get('dim_delay', DEFAULT_DIM_DELAY)
    dim_interval     = self.args.get('dim_interval', DEFAULT_DIM_INCREMENT)
    activated_button = PICO_UP_BUTTON_ID if direction == 'up' else PICO_DOWN_BUTTON_ID

    # Lights must be on first to acquire brightness
    self.turn_on(entity, transition=0)

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
      self.turn_on(entity, brightness=str(brightness), transition=0)

      time.sleep(dim_delay)

  ############
  # Favorite #
  ############

  def favorite(self):
    entity              = self.args['entity']
    sensor              = self.args['sensor']
    input_number        = self.args.get('input_number', False)
    long_press_duration = self.args.get('favorite_long_press_duration', DEFAULT_FAVORITE_LONG_PRESS_DURATION)
    min_brightness      = self.args['min_brightness']
    max_brightness      = self.args['max_brightness']
    start_time          = datetime.now()

    # If input_number was given, perform long press store routine
    if input_number:

      # Count the duration in seconds of the long press
      while int(self.get_state(sensor)) == PICO_CENTER_BUTTON_ID:
        time.sleep(0.01)
      press_duration = (datetime.now() - start_time).total_seconds()

      # Store the current brightness
      if press_duration >= long_press_duration:
        brightness = self.get_average_brightness(entity)
        self.set_value(input_number, brightness)

      # Set the brightness to the stored value
      else:
        brightness = int(float(self.get_state(input_number)))
        self.turn_on(entity, brightness=str(brightness), transition=0)

    # Otherwise, just set a median brightness
    else:
      brightness = round((max_brightness - min_brightness) / 2 + min_brightness)
      self.turn_on(entity, brightness=str(brightness), transition=0)

  #############
  # Utilities #
  #############

  def get_light_entities(self, entity):
    entity_type = entity.split('.')[0]

    # Return a single light entity
    if entity_type == 'light':
      return [entity]
    
    # Return all light entities in a group
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

  ####################
  # Input Validation #
  ####################

  def validate(self):

    # sensor
    if type(self.args.get('sensor', False)) != str:
      raise ValueError('sensor must be a defined string')
    if self.args['sensor'].split('.')[0] != 'sensor':
      raise ValueError('sensor is invalid, example: sensor.my_pico')

    # entity
    if type(self.args.get('entity', False)) != str:
      raise ValueError('entity must be a defined string')
    if self.args['entity'].split('.')[0] != 'light' and self.args['entity'].split('.')[0] != 'group':
      raise ValueError('entity is invalid, example: light.my_light or group.my_lights')

    # input_number
    if self.args.get('input_number', False) and self.args['input_number'].split('.')[0] != 'input_number':
      raise ValueError('input_number is invalid, example: input_number.my_favorite')

    # favorite_long_press_duration
    if self.args.get('favorite_long_press_duration', False) and (type(self.args['favorite_long_press_duration']) != int or type(self.args['favorite_long_press_duration']) != float):
      raise ValueError('favorite_long_press_duration must be a number')

    # min_brightness
    if type(self.args.get('min_brightness', False)) != int:
      raise ValueError('min_brightness must be a defined integer')

    # max_brightness
    if type(self.args.get('max_brightness', False)) != int:
      raise ValueError('max_brightness must be a defined integer')

    # dim_delay
    if self.args.get('dim_delay', False) and (type(self.args['dim_delay']) != int or type(self.args['dim_delay']) != float):
      raise ValueError('dim_delay must be a number')

    # dim_interval
    if self.args.get('dim_interval', False) and type(self.args['dim_interval']) != int:
      raise ValueError('dim_interval must be an integer')
