"""Config flow for NUT Full integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_PORT, DEFAULT_SCAN_INTERVAL, DOMAIN
from .nut_client import NutClient, NutError

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default="localhost"): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_USERNAME, default=""): str,
        vol.Optional(CONF_PASSWORD, default=""): str,
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=5, max=300)
        ),
    }
)


def _get_ups_list(host: str, port: int, username: str, password: str) -> list[str]:
    with NutClient(
        host=host,
        port=port,
        username=username or None,
        password=password or None,
    ) as client:
        return list(client.list_ups().keys())


async def _async_get_ups_list(
    hass: HomeAssistant, host: str, port: int, username: str, password: str
) -> list[str]:
    return await hass.async_add_executor_job(_get_ups_list, host, port, username, password)


class NutFullConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for NUT Full."""

    VERSION = 1

    def __init__(self) -> None:
        self._host: str = ""
        self._port: int = DEFAULT_PORT
        self._username: str = ""
        self._password: str = ""
        self._scan_interval: int = DEFAULT_SCAN_INTERVAL
        self._ups_list: list[str] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._host = user_input[CONF_HOST]
            self._port = user_input[CONF_PORT]
            self._username = user_input.get(CONF_USERNAME, "")
            self._password = user_input.get(CONF_PASSWORD, "")
            self._scan_interval = user_input[CONF_SCAN_INTERVAL]

            try:
                self._ups_list = await _async_get_ups_list(
                    self.hass,
                    self._host,
                    self._port,
                    self._username,
                    self._password,
                )
            except NutError as err:
                _LOGGER.error("NUT error: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error connecting to NUT server")
                errors["base"] = "cannot_connect"
            else:
                if not self._ups_list:
                    errors["base"] = "no_ups_found"
                elif len(self._ups_list) == 1:
                    return self._create_entry(self._ups_list[0])
                else:
                    return await self.async_step_ups()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_ups(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self._create_entry(user_input["ups_name"])

        schema = vol.Schema({vol.Required("ups_name"): vol.In(self._ups_list)})
        return self.async_show_form(step_id="ups", data_schema=schema)

    def _create_entry(self, ups_name: str) -> FlowResult:
        return self.async_create_entry(
            title=f"{ups_name} @ {self._host}",
            data={
                CONF_HOST: self._host,
                CONF_PORT: self._port,
                CONF_USERNAME: self._username,
                CONF_PASSWORD: self._password,
                CONF_SCAN_INTERVAL: self._scan_interval,
                "ups_name": ups_name,
            },
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Allow editing scan interval after setup via the Options button."""
        return NutFullOptionsFlow(config_entry)


class NutFullOptionsFlow(config_entries.OptionsFlow):
    """Options flow — lets you change the scan interval without re-adding the integration."""

    def __init__(self, config_entry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_interval = self._config_entry.data.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    int, vol.Range(min=5, max=300)
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
