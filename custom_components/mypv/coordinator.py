"""Coordinator for polling a my-PV device."""

from datetime import timedelta
import logging

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api_client import MyPVApiError, MyPVClient
from .const import DOMAIN, WIFI_METER_NAME

_LOGGER = logging.getLogger(__name__)


class MYPVDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Fetch live and protected data through one persistent API session."""

    def __init__(self, hass: HomeAssistant, *, config: dict, options: dict) -> None:
        self._host = config[CONF_HOST]
        self._info: dict | None = None
        self._data_endpoint = "data.jsn"
        self.client = MyPVClient(self._host, config.get("password"))

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} {self._host}",
            update_interval=timedelta(seconds=10),
        )

    async def _async_update_data(self) -> dict:
        try:
            if self._info is None:
                self._info = await self.client.async_get_info()
                if self._info.get("device") == WIFI_METER_NAME:
                    self._data_endpoint = "monitorjson"

            data = await self.client.async_get_runtime(self._data_endpoint)
            setup: dict = {}
            if self._data_endpoint != "monitorjson":
                try:
                    setup = await self.client.async_get_setup(force_refresh=True)
                except MyPVApiError as err:
                    # Live sensors remain useful on older devices and when a
                    # password has not yet been supplied.
                    _LOGGER.debug("Protected setup data unavailable for %s: %s", self._host, err)

            return {"data": data, "info": self._info, "setup": setup}
        except MyPVApiError as err:
            raise UpdateFailed(str(err)) from err

    async def async_shutdown(self) -> None:
        """Release the persistent client session when the config entry unloads."""
        await self.client.async_close()
