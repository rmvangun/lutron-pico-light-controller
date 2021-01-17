import hassapi as hass

# Constants
PICO_ON_BUTTON_ID     = 1
PICO_CENTER_BUTTON_ID = 2
PICO_OFF_BUTTON_ID    = 4
PICO_UP_BUTTON_ID     = 8
PICO_DOWN_BUTTON_ID   = 16

class PicoControl(hass.Hass):
    def initialize(self):

        self.log_notify("Pico Control Initialized")
        

