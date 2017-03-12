"""
Support for TPLink lights.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/light.tplink/
"""
import logging
from datetime import timedelta
from pyHS100 import SmartBulb
from homeassistant.const import (CONF_HOST, CONF_NAME)
import homeassistant.util as util
import homeassistant.util.color as color_util
from homeassistant.components.light import (
    Light, ATTR_BRIGHTNESS, ATTR_COLOR_TEMP, ATTR_RGB_COLOR, ATTR_TRANSITION,
    ATTR_XY_COLOR, SUPPORT_BRIGHTNESS, SUPPORT_COLOR_TEMP, SUPPORT_RGB_COLOR,
    SUPPORT_TRANSITION, SUPPORT_XY_COLOR)

#REQUIREMENTS = ['pyHS100==0.2.3']

_LOGGER = logging.getLogger(__name__)

SUPPORT_TPLINK = (SUPPORT_BRIGHTNESS | SUPPORT_COLOR_TEMP)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup WeMo bridges and register connected lights."""
    from pyHS100 import SmartBulb
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    add_devices([TPLinkSmartBulb(SmartBulb(host), name)], True)


class TPLinkSmartBulb(SmartBulb):
    """Representation of a TPLink Smart Plug switch."""

    def __init__(self, smartplug, name):
        """Initialize the switch."""
        self.smartbulb = smartplug

        # Use the name set on the device if not set
        if name is None:
            self._name = self.smartbulb.alias
        else:
            self._name = name

        self._state = None
        _LOGGER.debug("Setting up TP-Link Smart Plug")

    @property
    def name(self):
        """Return the name of the Smart Plug, if any."""
        return self._name

    def turn_on(self, **kwargs):
        """Turn the light on."""

        if ATTR_COLOR_TEMP in kwargs:
            colortemp = kwargs[ATTR_COLOR_TEMP]
            self.smartbulb.color_temp=colortemp

        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs.get(ATTR_BRIGHTNESS, self.brightness or 255)
            self.smartbulb.brightness=brightness

        self.smartbulb.state=self.smartbulb.BULB_STATE_ON

    def turn_off(self):
        """Turn the switch off."""
        self.smartbulb.state=self.smartbulb.BULB_STATE_OFF

    @property
    def color_temp(self):
        """Return the color temperature of this light in mireds."""
        return self.smartbulb.color_temp

    @property
    def is_on(self):
        """True if device is on."""
        return self.smartbulb.state == \
                self.smartbulb.BULB_STATE_ON

    def update(self):
        from pyHS100 import (SmartBulb, SmartPlugException)
        """Update the TP-Link switch's state."""
        try:
            self._state = self.smartbulb.state == \
                self.smartbulb.BULB_STATE_ON

        except (SmartPlugException, OSError) as ex:
            _LOGGER.warning('Could not read state for %s: %s', self.name, ex)

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_TPLINK

