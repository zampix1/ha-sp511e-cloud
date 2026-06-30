"""SP511E custom integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .api import EFFECTS, SP511ECloudClient
from .const import DOMAIN, PLATFORMS
from .coordinator import SP511ECoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a SP511E config entry."""
    hass.data.setdefault(DOMAIN, {})
    coordinator = SP511ECoordinator(hass, entry, SP511ECloudClient())
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a SP511E config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


def _coordinator_from_call(hass: HomeAssistant, call: ServiceCall) -> SP511ECoordinator:
    entry_id = call.data.get("entry_id")
    coordinators = {key: value for key, value in hass.data.get(DOMAIN, {}).items() if isinstance(value, SP511ECoordinator)}
    if entry_id:
        try:
            return coordinators[str(entry_id)]
        except KeyError as exc:
            raise HomeAssistantError(f"Unknown SP511E entry_id: {entry_id}") from exc
    if len(coordinators) != 1:
        raise HomeAssistantError("Pass entry_id when more than one SP511E device is configured")
    return next(iter(coordinators.values()))


def _async_register_services(hass: HomeAssistant) -> None:
    if hass.data[DOMAIN].get("_services_registered"):
        return

    async def set_effect(call: ServiceCall) -> None:
        await _coordinator_from_call(hass, call).async_effect(str(call.data["effect"]), "service_set_effect")

    async def set_speed(call: ServiceCall) -> None:
        await _coordinator_from_call(hass, call).async_speed(int(call.data["speed"]), "service_set_speed")

    async def set_music_sensitivity(call: ServiceCall) -> None:
        await _coordinator_from_call(hass, call).async_music_sensitivity(
            int(call.data["sensitivity"]),
            "service_set_music_sensitivity",
        )

    async def restore_standard(call: ServiceCall) -> None:
        await _coordinator_from_call(hass, call).async_restore_standard()

    async def all_off(call: ServiceCall) -> None:
        await _coordinator_from_call(hass, call).async_power(False, "service_all_off")

    async def refresh(call: ServiceCall) -> None:
        await _coordinator_from_call(hass, call).async_request_refresh()

    entry_field: dict[Any, Any] = {vol.Optional("entry_id"): cv.string}
    hass.services.async_register(
        DOMAIN,
        "set_effect",
        set_effect,
        schema=vol.Schema({**entry_field, vol.Required("effect"): vol.In(sorted(EFFECTS))}),
    )
    hass.services.async_register(
        DOMAIN,
        "set_speed",
        set_speed,
        schema=vol.Schema({**entry_field, vol.Required("speed"): vol.All(vol.Coerce(int), vol.Range(min=1, max=100))}),
    )
    hass.services.async_register(
        DOMAIN,
        "set_music_sensitivity",
        set_music_sensitivity,
        schema=vol.Schema({**entry_field, vol.Required("sensitivity"): vol.All(vol.Coerce(int), vol.Range(min=1, max=100))}),
    )
    hass.services.async_register(DOMAIN, "restore_standard", restore_standard, schema=vol.Schema(entry_field))
    hass.services.async_register(DOMAIN, "all_off", all_off, schema=vol.Schema(entry_field))
    hass.services.async_register(DOMAIN, "refresh", refresh, schema=vol.Schema(entry_field))
    hass.data[DOMAIN]["_services_registered"] = True
