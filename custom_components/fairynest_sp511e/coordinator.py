"""Coordinator for SP511E."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    SP511ECloudAuthError,
    SP511ECloudClient,
    Session,
    command_for_effect,
    rgb_to_int,
)
from .const import (
    CONF_ACCOUNT,
    CONF_COUNTRY_CODE,
    CONF_DEVICE_SELECTOR,
    CONF_PASSWORD,
    CONF_SESSION_SID,
    CONF_SESSION_TOKEN,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class SP511ECoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches state and serializes writes."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: SP511ECloudClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL_SECONDS),
        )
        self.entry = entry
        self.client = client
        self._lock = asyncio.Lock()
        self.session = Session(
            sid=str(entry.data.get(CONF_SESSION_SID, "")),
            token=str(entry.data.get(CONF_SESSION_TOKEN, "")),
        )
        self.state: dict[str, Any] = {"p": 0, "bn": 100, "c": 0xFF0E9A, "m": 200, "ms": 100, "rgb": 0, "s": 57}
        self.device: dict[str, Any] = {}
        self.last_command_result: dict[str, Any] = {}

    @property
    def selector(self) -> str | None:
        return self.entry.options.get(CONF_DEVICE_SELECTOR) or self.entry.data.get(CONF_DEVICE_SELECTOR)

    @property
    def account(self) -> str:
        return str(self.entry.data.get(CONF_ACCOUNT, ""))

    @property
    def password(self) -> str:
        return str(self.entry.data.get(CONF_PASSWORD, ""))

    @property
    def country_code(self) -> str:
        return str(self.entry.data.get(CONF_COUNTRY_CODE, "1"))

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            snapshot = await self.hass.async_add_executor_job(
                self.client.get_snapshot,
                self.session,
                self.selector,
                self.state,
            )
        except SP511ECloudAuthError:
            await self.async_refresh_session()
            snapshot = await self.hass.async_add_executor_job(
                self.client.get_snapshot,
                self.session,
                self.selector,
                self.state,
            )
        except Exception as exc:  # noqa: BLE001 - HA wraps the detail in UpdateFailed.
            raise UpdateFailed(str(exc)) from exc

        self.device = snapshot.device
        self.state = snapshot.state
        return {"device": self.device, "state": self.state, "last_command": self.last_command_result}

    async def async_refresh_session(self) -> None:
        if not self.account or not self.password:
            raise SP511ECloudAuthError("Missing account/password for session refresh")
        session = await self.hass.async_add_executor_job(
            self.client.login,
            self.account,
            self.password,
            self.country_code,
        )
        self.session = session
        data = dict(self.entry.data)
        data[CONF_SESSION_SID] = session.sid
        data[CONF_SESSION_TOKEN] = session.token
        self.hass.config_entries.async_update_entry(self.entry, data=data)

    async def async_send(self, name: str, value: Any, reason: str = "homeassistant") -> None:
        async with self._lock:
            await self.async_request_refresh()
            hash_key = self.device.get("hashKey")
            if not isinstance(hash_key, str) or not hash_key:
                raise UpdateFailed("Selected SP511E device does not expose hashKey")
            pre_state = dict(self.state)
            try:
                response = await self.hass.async_add_executor_job(
                    self.client.send_command,
                    self.session,
                    hash_key,
                    name,
                    value,
                )
            except SP511ECloudAuthError:
                await self.async_refresh_session()
                response = await self.hass.async_add_executor_job(
                    self.client.send_command,
                    self.session,
                    hash_key,
                    name,
                    value,
                )
            self._apply_optimistic_state(name, value)
            self.last_command_result = {
                "source": "homeassistant",
                "reason": reason,
                "command_name": name,
                "value": value,
                "success": response.get("code") == 200,
                "response": {"code": response.get("code"), "desc": response.get("desc")},
                "pre_state": pre_state,
                "post_state": dict(self.state),
            }
            self.hass.bus.async_fire(f"{DOMAIN}_command", self.last_command_result)
            self.async_set_updated_data({"device": self.device, "state": self.state, "last_command": self.last_command_result})

    async def async_power(self, power: bool, reason: str = "power") -> None:
        await self.async_send("SPLED.Power", 1 if power else 0, reason)

    async def async_brightness(self, brightness: int, reason: str = "brightness") -> None:
        await self.async_send("SPLED.SetBrightness", max(1, min(100, int(brightness))), reason)

    async def async_speed(self, speed: int, reason: str = "speed") -> None:
        await self.async_send("SPLED.Speed", max(1, min(100, int(speed))), reason)

    async def async_music_sensitivity(self, sensitivity: int, reason: str = "music_sensitivity") -> None:
        await self.async_send("SPLED.MusicSensitivity", max(1, min(100, int(sensitivity))), reason)

    async def async_color(self, rgb: tuple[int, int, int], reason: str = "color") -> None:
        await self.async_send("SPLED.Color", rgb_to_int(rgb), reason)

    async def async_effect(self, effect: str, reason: str = "effect") -> None:
        name, value = command_for_effect(effect)
        await self.async_send(name, value, reason)

    async def async_restore_standard(self) -> None:
        await self.async_power(True, "restore_standard")
        await self.async_brightness(100, "restore_standard")
        await self.async_speed(57, "restore_standard")
        await self.async_effect("rainbow", "restore_standard")

    def _apply_optimistic_state(self, name: str, value: Any) -> None:
        if name == "SPLED.Power":
            self.state["p"] = 1 if int(value) else 0
        elif name == "SPLED.SetBrightness":
            self.state["bn"] = int(value)
        elif name == "SPLED.Speed":
            self.state["s"] = int(value)
        elif name == "SPLED.MusicSensitivity":
            self.state["ms"] = int(value)
        elif name == "SPLED.Color":
            self.state["c"] = int(value)
        elif name == "SPLED.Mode":
            self.state["m"] = int(value)
