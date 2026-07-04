"""Config flow for SP511E."""

from __future__ import annotations

import hashlib
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .api import SP511ECloudAuthError, SP511ECloudClient, pick_device
from .const import (
    CONF_ACCOUNT,
    CONF_COUNTRY_CODE,
    CONF_DEVICE_SELECTOR,
    CONF_PASSWORD,
    CONF_SESSION_SID,
    CONF_SESSION_TOKEN,
    DEFAULT_COUNTRY_CODE,
    DEFAULT_DEVICE_SELECTOR,
    DOMAIN,
)


class SP511ECloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a SP511E config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            client = SP511ECloudClient()
            try:
                session = await self.hass.async_add_executor_job(
                    client.login,
                    user_input[CONF_ACCOUNT],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_COUNTRY_CODE],
                )
                devices = await self.hass.async_add_executor_job(client.get_devices, session)
                device = pick_device(devices, user_input.get(CONF_DEVICE_SELECTOR))
            except SP511ECloudAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001 - config flow maps unknown cloud failures to cannot_connect.
                errors["base"] = "cannot_connect"
            else:
                raw_unique = str(device.get("deviceCode") or device.get("hashKey") or user_input[CONF_ACCOUNT])
                unique_id = hashlib.sha256(raw_unique.encode("utf-8")).hexdigest()[:16]
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                title = str(device.get("name") or "SP511E")
                data = dict(user_input)
                data[CONF_SESSION_SID] = session.sid
                data[CONF_SESSION_TOKEN] = session.token
                return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ACCOUNT): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_COUNTRY_CODE, default=DEFAULT_COUNTRY_CODE): str,
                    vol.Optional(CONF_DEVICE_SELECTOR, default=DEFAULT_DEVICE_SELECTOR): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return SP511EOptionsFlow(config_entry)


class SP511EOptionsFlow(config_entries.OptionsFlow):
    """Options flow."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DEVICE_SELECTOR,
                        default=self.config_entry.data.get(CONF_DEVICE_SELECTOR, DEFAULT_DEVICE_SELECTOR),
                    ): str
                }
            ),
        )
