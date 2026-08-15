"""Authenticated local API client for my-PV devices."""
from __future__ import annotations

from collections.abc import Mapping
import ssl
from typing import Any
import aiohttp


class MyPVApiError(Exception):
    """A my-PV response could not be used."""


class MyPVClient:
    """Talk to one local my-PV device and retain its login cookie."""

    def __init__(self, host: str, password: str | None = None, timeout: int = 10) -> None:
        self._host = host
        self._password = password or None
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._setup_cache: dict[str, Any] | None = None
        # my-PV devices use a local, self-signed HTTPS certificate for the
        # protected setup API.  HTTPS is still used; only CA verification is
        # disabled because an appliance certificate cannot be trusted by HA.
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        self._session = aiohttp.ClientSession(
            timeout=self._timeout,
            connector=aiohttp.TCPConnector(ssl=ssl_context),
            # aiohttp otherwise rejects cookies set by an IP address. my-PV
            # devices are normally configured by their local IP address.
            cookie_jar=aiohttp.CookieJar(unsafe=True),
        )

    async def _request(
        self,
        protocol: str,
        method: str,
        endpoint: str,
        *,
        data: Mapping[str, Any] | None = None,
        params: Mapping[str, Any] | None = None,
        expect_json: bool = True,
    ) -> dict[str, Any]:
        url = f"{protocol}://{self._host}/{endpoint.lstrip('/')}"
        headers = {"Accept": "application/json", "User-Agent": "Home Assistant my-PV"}
        if protocol == "https":
            headers.update({"Origin": f"https://{self._host}", "Referer": f"https://{self._host}/"})
        try:
            async with self._session.request(method, url, data=data, params=params, headers=headers) as response:
                if response.status >= 400:
                    body = await response.text()
                    raise MyPVApiError(f"{method} {endpoint} returned HTTP {response.status}: {body[:120]}")
                if not expect_json:
                    await response.read()
                    return {}
                try:
                    result = await response.json(content_type=None)
                except (aiohttp.ClientError, ValueError) as err:
                    raise MyPVApiError(f"{method} {endpoint} did not return JSON") from err
        except aiohttp.ClientError as err:
            raise MyPVApiError(f"Unable to reach {self._host}: {err}") from err
        if not isinstance(result, dict):
            raise MyPVApiError(f"{method} {endpoint} returned unexpected JSON")
        return result

    async def async_get_runtime(self, endpoint: str = "data.jsn") -> dict[str, Any]:
        return await self._request("http", "GET", endpoint)

    async def async_get_info(self) -> dict[str, Any]:
        return await self._request("http", "GET", "mypv_dev.jsn")

    async def async_login(self) -> None:
        if not self._password:
            raise MyPVApiError("A password is required to read or change setup data")
        await self._request(
            "https", "POST", "auth.jsn", data={"pw": self._password}, expect_json=False
        )

    async def async_get_setup(self, *, force_refresh: bool = False) -> dict[str, Any]:
        if self._setup_cache is not None and not force_refresh:
            return self._setup_cache
        await self.async_login()
        self._setup_cache = await self._request("https", "GET", "setup.jsn")
        return self._setup_cache

    async def async_set_setup_parameter(self, parameter: str, value: Any) -> None:
        setup = dict(await self.async_get_setup(force_refresh=True))
        setup[parameter] = value
        await self.async_post_setup(setup)

    async def async_post_setup(self, setup: Mapping[str, Any]) -> None:
        if not self._password:
            raise MyPVApiError("A password is required to change setup data")
        payload = dict(setup)
        payload["pw"] = self._password
        await self.async_login()
        await self._request("https", "POST", "setup.jsn", data=payload)
        self._setup_cache = dict(setup)

    async def async_set_runtime_parameter(self, parameter: str, value: Any) -> None:
        await self._request("http", "GET", "data.jsn", params={parameter: value})

    async def async_close(self) -> None:
        await self._session.close()
