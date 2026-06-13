"""NUT Full - Exposes ALL NUT variables as Home Assistant sensors."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL
from .nut_client import NutClient, NutError

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NUT Full from a config entry."""
    # Scan interval: options flow takes precedence over initial config data
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )

    coordinator = NutFullDataCoordinator(
        hass,
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        username=entry.data.get(CONF_USERNAME, ""),
        password=entry.data.get(CONF_PASSWORD, ""),
        ups_name=entry.data["ups_name"],
        scan_interval=scan_interval,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Unable to connect to NUT server: {err}") from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload when options change (e.g. scan interval updated)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class NutFullDataCoordinator(DataUpdateCoordinator):
    """Coordinator that fetches ALL variables from the NUT server."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        username: str,
        password: str,
        ups_name: str,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"NUT Full ({ups_name}@{host})",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.host = host
        self.port = port
        self.username = username or None
        self.password = password or None
        self.ups_name = ups_name

    async def _async_update_data(self) -> dict[str, str]:
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except NutError as err:
            raise UpdateFailed(f"NUT error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with NUT server: {err}") from err

    def _fetch_data(self) -> dict[str, str]:
        with NutClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
        ) as client:
            return client.list_vars(self.ups_name)
