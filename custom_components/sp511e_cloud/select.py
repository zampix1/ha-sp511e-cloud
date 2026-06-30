"""Select platform for SP511E."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import EFFECTS, MODE_TO_EFFECT
from .const import DOMAIN
from .coordinator import SP511ECoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SP511ECoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SP511EEffectSelect(coordinator, entry)])


class SP511EEffectSelect(CoordinatorEntity[SP511ECoordinator], SelectEntity):
    """Effect selector for SP511E."""

    _attr_has_entity_name = True
    _attr_name = "Effect"
    _attr_options = [name.title() for name in EFFECTS]

    def __init__(self, coordinator: SP511ECoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_effect_select"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "SP511E",
            "model": "SP511E",
        }

    @property
    def current_option(self) -> str | None:
        mode = self.coordinator.state.get("m")
        if mode is None:
            return None
        effect = MODE_TO_EFFECT.get(int(mode))
        return effect.title() if effect else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_effect(option, "select_effect")
