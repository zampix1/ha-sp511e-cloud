"""SP511E Cloud custom integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .api import EFFECTS, SP511ECloudClient
from .const import DOMAIN, PLATFORMS
from .coordinator import SP511ECoordinator

CONF_ENTRY_ID = "entry_id"
_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up global SP511E Cloud services."""

    hass.data.setdefault(DOMAIN, {})
    await _async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an SP511E Cloud config entry."""

    hass.data.setdefault(DOMAIN, {})
    coordinator = SP511ECoordinator(hass, entry, SP511ECloudClient())
    hass.data[DOMAIN][entry.entry_id] = coordinator
    coordinator.async_set_updated_data(
        {
            "device": coordinator.device,
            "state": coordinator.state,
            "last_command": coordinator.last_command_result,
        }
    )
    await _async_register_services(hass)
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:  # noqa: BLE001 - keep command services available if an entity platform fails.
        _LOGGER.exception("Failed to set up SP511E entity platforms; command services remain available")
    hass.async_create_task(coordinator.async_refresh())
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an SP511E Cloud config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


def _coordinator_from_call(hass: HomeAssistant, call: ServiceCall) -> SP511ECoordinator:
    entry_id = call.data.get(CONF_ENTRY_ID)
    coordinators = {
        key: value
        for key, value in hass.data.get(DOMAIN, {}).items()
        if isinstance(value, SP511ECoordinator)
    }
    if entry_id:
        try:
            return coordinators[entry_id]
        except KeyError as exc:
            raise HomeAssistantError(f"Unknown SP511E entry_id: {entry_id}") from exc
    if len(coordinators) != 1:
        raise HomeAssistantError("Pass entry_id when more than one SP511E device is configured")
    return next(iter(coordinators.values()))


async def _async_register_services(hass: HomeAssistant) -> None:
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

    entry_field = {vol.Optional(CONF_ENTRY_ID): str}
    effect_schema = vol.Schema({**entry_field, vol.Required("effect"): vol.In(EFFECTS)})
    speed_schema = vol.Schema({**entry_field, vol.Required("speed"): vol.All(int, vol.Range(min=1, max=100))})
    sensitivity_schema = vol.Schema(
        {**entry_field, vol.Required("sensitivity"): vol.All(int, vol.Range(min=1, max=100))}
    )
    entry_schema = vol.Schema(entry_field)

    services = (
        ("set_effect", set_effect, effect_schema),
        ("set_speed", set_speed, speed_schema),
        ("set_music_sensitivity", set_music_sensitivity, sensitivity_schema),
        ("restore_standard", restore_standard, entry_schema),
        ("all_off", all_off, entry_schema),
        ("refresh", refresh, entry_schema),
    )
    for name, handler, schema in services:
        if not hass.services.has_service(DOMAIN, name):
            hass.services.async_register(DOMAIN, name, handler, schema=schema)

    hass.data[DOMAIN]["_services_registered"] = True
