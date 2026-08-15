"""The my-PV integration."""

import logging
from homeassistant.const import CONF_MONITORED_CONDITIONS
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfFrequency,
    UnitOfTemperature,
)

from .const import (
    SENSOR_TYPES,
    DOMAIN,
    DATA_COORDINATOR,
    DEVICE_STATUS,
    WIFI_METER_NAME,
    WIFI_METER_SENSOR_TYPES,
    DEVICE_STATUS_AC_ELWA_E,
)
from .coordinator import MYPVDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)



async def async_setup_entry(hass, entry, async_add_entities):
    """Add or update my-PV entry."""
    coordinator: MYPVDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        DATA_COORDINATOR
    ]

    if CONF_MONITORED_CONDITIONS in entry.options:
        configured_sensors = entry.options[CONF_MONITORED_CONDITIONS]
    else:
        configured_sensors = entry.data[CONF_MONITORED_CONDITIONS]

    entities = []
    for sensor in configured_sensors:
        new_entity = MypvDevice(coordinator, sensor, entry.title)
        entities.append(new_entity)

    async_add_entities(entities)


class MypvDevice(CoordinatorEntity):
    """Representation of a my-PV device."""

    def __init__(self, coordinator, sensor_type, name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        if WIFI_METER_NAME in name:
            self._sensor = WIFI_METER_SENSOR_TYPES[sensor_type][0]
            self._unit_of_measurement = WIFI_METER_SENSOR_TYPES[sensor_type][1]
            self._icon = WIFI_METER_SENSOR_TYPES[sensor_type][2]
            self._data_source = WIFI_METER_SENSOR_TYPES[sensor_type][3]
        else:
            self._sensor = SENSOR_TYPES[sensor_type][0]
            self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
            self._icon = SENSOR_TYPES[sensor_type][2]
            self._data_source = SENSOR_TYPES[sensor_type][3]

        self._name = name
        self.type = sensor_type
        self.coordinator = coordinator
        self._last_value = None
        self.serial_number = str(self.coordinator.data["info"].get("sn", name))
        self.model = self.coordinator.data["info"].get("device", "my-PV")
        _LOGGER.debug(self.coordinator)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._name} {self._sensor}"

    @property
    def state(self):
        """Return the state of the device."""
        try:
            if "Datas" in self.type:
                wifiMeterList = self.type.split(";")
                state = self.coordinator.data[self._data_source][wifiMeterList[0]][
                    int(wifiMeterList[1])
                ][int(wifiMeterList[2])]
                return state

            state = self.coordinator.data[self._data_source][self.type]

            if self.type == "screen_mode_flag":
                state = DEVICE_STATUS.get(self.hass.config.language, "en")[state]

            if self.type == "status":
                state = DEVICE_STATUS_AC_ELWA_E.get(int(state))

            if self.type == "power_act":
                rel_out = self.coordinator.data[self._data_source].get("rel1_out")
                load_nom = self.coordinator.data[self._data_source].get("load_nom")
                if rel_out is not None and load_nom is not None:
                    state = (int(rel_out) * int(load_nom)) + int(state)

            self._last_value = state
        except (KeyError, TypeError, ValueError, IndexError) as err:
            _LOGGER.debug("Unable to read %s: %s", self.type, err)
            state = self._last_value
        if state is None:
            return state
        if not isinstance(state, int):
            return state
        if self._unit_of_measurement == UnitOfFrequency.HERTZ:
            return state / 1000
        if self._unit_of_measurement == UnitOfTemperature.CELSIUS:
            return state / 10
        if self._unit_of_measurement == UnitOfElectricCurrent.AMPERE:
            return state / 10
        return state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return icon."""
        return self._icon

    @property
    def unique_id(self):
        """Return unique id based on device serial and variable."""
        return f"{self.serial_number}_{self.type}"

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": self._name,
            "manufacturer": "my-PV",
            "model": self.model,
        }
