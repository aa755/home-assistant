"""Support for Lutron lights."""
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS, DOMAIN, SUPPORT_BRIGHTNESS, Light)
from homeassistant.components.lutron import (
    LutronDevice, LUTRON_DEVICES, LUTRON_GROUPS, LUTRON_CONTROLLER)

DEPENDENCIES = ['lutron']

_LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup Lutron lights."""
    area_devs = {}
    devs = []
    for (area_name, device) in hass.data[LUTRON_DEVICES]['light']:
        dev = LutronLight(hass, area_name, device,
                          hass.data[LUTRON_CONTROLLER])
        area_devs.setdefault(area_name, []).append(dev)
        devs.append(dev)
    add_devices(devs, True)

    for area in area_devs:
        if area not in hass.data[LUTRON_GROUPS]:
            continue
        grp = hass.data[LUTRON_GROUPS][area]
        ids = list(grp.tracking) + [dev.entity_id for dev in area_devs[area]]
        grp.update_tracked_entity_ids(ids)

    return True


def to_lutron_level(level):
    """Convert the given HASS light level (0-255) to Lutron (0.0-100.0)."""
    return float((level * 100) / 255)


def to_hass_level(level):
    """Convert the given Lutron (0.0-100.0) light level to HASS (0-255)."""
    return int((level * 255) / 100)


class LutronLight(LutronDevice, Light):
    """Representation of a Lutron Light, including dimmable."""

    def __init__(self, hass, area_name, lutron_device, controller):
        """Initialize the light."""
        self._prev_brightness = None
        LutronDevice.__init__(self, hass, DOMAIN, area_name, lutron_device,
                              controller)

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    @property
    def brightness(self):
        """Return the brightness of the light."""
        new_brightness = to_hass_level(self._lutron_device.last_level())
        if new_brightness != 0:
            self._prev_brightness = new_brightness
        return new_brightness

    def turn_on(self, **kwargs):
        """Turn the light on."""
        if ATTR_BRIGHTNESS in kwargs and self._lutron_device.is_dimmable:
            brightness = kwargs[ATTR_BRIGHTNESS]
        elif self._prev_brightness == 0:
            brightness = 255 / 2
        else:
            brightness = self._prev_brightness
        self._prev_brightness = brightness
        self._lutron_device.level = to_lutron_level(brightness)

    def turn_off(self, **kwargs):
        """Turn the light off."""
        self._lutron_device.level = 0

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attr = {}
        attr['Lutron Integration ID'] = self._lutron_device.id
        return attr

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._lutron_device.last_level() > 0

    def update(self):
        """Called when forcing a refresh of the device."""
        if self._prev_brightness is None:
            self._prev_brightness = to_hass_level(self._lutron_device.level)
