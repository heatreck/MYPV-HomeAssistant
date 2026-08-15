"""Switch entity"""

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_HOST, CONF_DEVICE

from .const import DOMAIN, DATA_COORDINATOR, WIFI_METER_NAME
from .coordinator import MYPVDataUpdateCoordinator

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the toggle switch."""
    device_name = entry.data[CONF_DEVICE]
    if device_name != WIFI_METER_NAME:
        coordinator: MYPVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
        host = entry.data[CONF_HOST]
        if "devmode" in coordinator.data.get("setup", {}):
            async_add_entities([ToggleSwitch(coordinator, host, entry.title)], True)

class ToggleSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, host, name):
        """Initialize the switch"""
        super().__init__(coordinator)
        self._device_name = name
        self._name = "Device State"
        self._host = host
        self._switch = f"device_state_{self._host}"
        self._icon = "mdi:power"
        self._is_on = bool(self.coordinator.data.get("setup", {}).get("devmode", False))
        self._model = self.coordinator.data["info"]["device"]
        self.serial_number = str(self.coordinator.data["info"].get("sn", host))
    
    @property
    def is_on(self):
        if self.coordinator.data:
            self._is_on = bool(self.coordinator.data.get("setup", {}).get("devmode", False))
        return self._is_on

    @property
    def name(self):
        return self._name
    
    @property
    def icon(self):
        return self._icon
    
    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": self._device_name,
            "manufacturer": "my-PV",
            "model": self._model,
        }
    
    @property
    def unique_id(self):
        """Return unique id based on device serial and variable."""
        return f"{self.serial_number}_{self._switch}"
    
    async def async_turn_on(self):
        await self.async_toggle_switch(1)
        self._is_on = True
        await self.coordinator.async_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self):
        await self.async_toggle_switch(0)
        self._is_on = False
        await self.coordinator.async_refresh()
        self.async_write_ha_state()
    
    async def async_toggle_switch(self, mode):
        await self.coordinator.client.async_set_setup_parameter("devmode", mode)
