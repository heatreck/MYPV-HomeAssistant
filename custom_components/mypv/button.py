import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import CONF_HOST, CONF_DEVICE

from .const import DOMAIN, DATA_COORDINATOR, WIFI_METER_NAME, BOOST_BUTTON_NAME

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the boost button"""
    device_name = entry.data[CONF_DEVICE]
    if device_name != WIFI_METER_NAME:
        coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
        if "boostactive" in coordinator.data.get("data", {}):
            async_add_entities([
                MYPVButton(hass, coordinator, "mdi:heat-wave", BOOST_BUTTON_NAME, entry.title),
            ])

class MYPVButton(CoordinatorEntity, ButtonEntity):
    def __init__(self, hass, coordinator, icon, name, deviceName) -> None:
        """Initialize the button"""
        super().__init__(coordinator)
        self._hass = hass
        self._icon = icon
        self._name = name
        self._device_name = deviceName
        self._model = self.coordinator.data["info"]["device"]
        self.serial_number = str(self.coordinator.data["info"].get("sn", deviceName))
        self._button = self.name

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
        return f"{self.serial_number}_{self._button.lower().replace(' ', '_')}"

    async def async_press(self) -> None:
        """Handle button press."""
        boost_active = bool(self.coordinator.data.get("data", {}).get("boostactive", False))
        await self.coordinator.client.async_set_runtime_parameter("bststrt", int(not boost_active))
        await self.coordinator.async_request_refresh()
