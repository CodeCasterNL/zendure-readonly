import logging
import aiohttp
import asyncio

from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)


class ZendureCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, host: str):
        self.host = host
        self._session: aiohttp.ClientSession = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name="zendure",
            update_interval=timedelta(seconds=1),  # tune as needed
        )

    async def _async_update_data(self):
        url = f"{self.host}/properties/report"

        try:
            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                text = await resp.text()

                # Structured debug log per cycle
                _LOGGER.debug(
                    "Zendure update cycle | url=%s status=%s content_type=%s body=%s",
                    url,
                    resp.status,
                    resp.headers.get("Content-Type"),
                    text[:1000],  # prevent log flooding
                )

                if resp.status != 200:
                    raise UpdateFailed(f"HTTP {resp.status} from {url}")

                try:
                    data = await resp.json(content_type=None)
                except Exception as e:
                    _LOGGER.error(
                        "Zendure JSON parse error | url=%s error=%s raw=%s",
                        url,
                        e,
                        text[:1000],
                    )
                    raise UpdateFailed("Invalid JSON response") from e

                # Optional: log normalized top-level keys for quick inspection
                if isinstance(data, dict):
                    _LOGGER.debug(
                        "Zendure parsed payload keys | %s",
                        list(data.keys()),
                    )

                return data

        except asyncio.TimeoutError as e:
            raise UpdateFailed(f"Timeout fetching {url}") from e
        except aiohttp.ClientError as e:
            raise UpdateFailed(f"Client error fetching {url}: {e}") from e