from homeassistant.components.number import NumberEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfTemperature, CONF_HOST, CONF_DEVICE
import logging

from .const import DOMAIN, DATA_COORDINATOR, DEFAULT_MAX_VALUE, DEFAULT_MIN_VALUE, DEFAULT_MODE, DEFAULT_STEP, WIFI_METER_NAME
from .coordinator import MYPVDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the WWBoost number entity."""
    device_name = entry.data[CONF_DEVICE]
    if device_name != WIFI_METER_NAME:
        coordinator: MYPVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
        host = entry.data[CONF_HOST]
        if "ww1boost" in coordinator.data.get("setup", {}):
            async_add_entities([WWBoost(coordinator, host, entry.title)])

class WWBoost(CoordinatorEntity, NumberEntity):
    """Representation of the WWBoost number entity"""

    def __init__(self, coordinator, host, name):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._device_name = name
        self._host = host
        self._min_value = DEFAULT_MIN_VALUE
        self._max_value = DEFAULT_MAX_VALUE
        self._value = float(self.coordinator.data.get("setup", {}).get("ww1boost", 500)) / 10
        self._step = DEFAULT_STEP
        self._unit_of_measurement = UnitOfTemperature.CELSIUS
        self._mode = DEFAULT_MODE
        self.serial_number = self.coordinator.data.get("info", {}).get("sn", "unknown")
        self._model = self.coordinator.data.get("info", {}).get("device", "unknown")
        self._number = f"ww1boost_{self._host}"
        self._name = f"Hot Water Assurance {self._host}"

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
        return f"{self.serial_number}_{self._number}"

    @property
    def name(self):
        """Return the display name of this entity."""
        return self._name

    @property
    def native_min_value(self):
        """Return the minimum value of this number."""
        return self._min_value

    @property
    def native_max_value(self):
        """Return the maximum value of this number."""
        return self._max_value

    @property
    def native_value(self):
        """Return the current value of this number."""
        return self._value
    
    @property
    def native_step(self):
        """Return the step size for this number."""
        return self._step
    
    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement for this number."""
        return self._unit_of_measurement
    
    @property
    def mode(self):
        """Return mode of this entity"""
        return self._mode

    def _handle_coordinator_update(self) -> None:
        """Use the central coordinator instead of registering a second poller."""
        self._value = self.coordinator.data.get("setup", {}).get("ww1boost", 500) / 10
        super()._handle_coordinator_update()

    async def async_set_native_value(self, value: float):
        """Set a new value for this number."""
        if self._min_value <= value <= self._max_value:
            await self.coordinator.client.async_set_setup_parameter("ww1boost", round(value * 10))
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Value %s is out of range [%s, %s]", value, self._min_value, self._max_value)
