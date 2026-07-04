"""Number platform for SP511E."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SP511ECoordinator

PERCENT = "%"


@dataclass(frozen=True, kw_only=True)
class SP511ENumberDescription(NumberEntityDescription):
    state_key: str
    setter: Callable[[SP511ECoordinator, int], Awaitable[None]]


async def _set_brightness(coordinator: SP511ECoordinator, value: int) -> None:
    await coordinator.async_brightness(value, "number_brightness")


async def _set_speed(coordinator: SP511ECoordinator, value: int) -> None:
    await coordinator.async_speed(value, "number_speed")


async def _set_music_sensitivity(coordinator: SP511ECoordinator, value: int) -> None:
    await coordinator.async_music_sensitivity(value, "number_music_sensitivity")


NUMBERS: tuple[SP511ENumberDescription, ...] = (
    SP511ENumberDescription(
        key="brightness",
        name="Brightness",
        state_key="bn",
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENT,
        mode=NumberMode.SLIDER,
        setter=_set_brightness,
    ),
    SP511ENumberDescription(
        key="speed",
        name="Speed",
        state_key="s",
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENT,
        mode=NumberMode.SLIDER,
        setter=_set_speed,
    ),
    SP511ENumberDescription(
        key="music_sensitivity",
        name="Music Sensitivity",
        state_key="ms",
        native_min_value=1,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENT,
        mode=NumberMode.SLIDER,
        setter=_set_music_sensitivity,
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SP511ECoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SP511ENumber(coordinator, entry, description) for description in NUMBERS])


class SP511ENumber(CoordinatorEntity[SP511ECoordinator], NumberEntity):
    """Numeric control for SP511E."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SP511ECoordinator,
        entry: ConfigEntry,
        description: SP511ENumberDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}_number"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "SP511E",
            "model": "SP511E",
        }

    @property
    def native_value(self) -> int | None:
        value = self.coordinator.state.get(self.entity_description.state_key)
        return int(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        await self.entity_description.setter(self.coordinator, int(round(value)))
