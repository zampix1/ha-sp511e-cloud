"""Diagnostics support for SP511E."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_ACCOUNT,
    CONF_PASSWORD,
    CONF_SESSION_SID,
    CONF_SESSION_TOKEN,
    DOMAIN,
)

TO_REDACT = {
    CONF_ACCOUNT,
    CONF_PASSWORD,
    CONF_SESSION_SID,
    CONF_SESSION_TOKEN,
    "account",
    "password",
    "sid",
    "token",
    "session",
    "hashKey",
    "deviceCode",
    "productKey",
    "bindToken",
    "userId",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry with sensitive data redacted."""

    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    coordinator_data: dict[str, Any] = {}
    if coordinator is not None:
        coordinator_data = {
            "device": getattr(coordinator, "device", {}),
            "state": getattr(coordinator, "state", {}),
            "last_command_result": getattr(coordinator, "last_command_result", {}),
            "last_update_success": getattr(coordinator, "last_update_success", None),
        }

    return async_redact_data(
        {
            "entry": {
                "title": entry.title,
                "data": dict(entry.data),
                "options": dict(entry.options),
            },
            "coordinator": coordinator_data,
        },
        TO_REDACT,
    )
