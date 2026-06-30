"""Button platform for FairyNest SP511E."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FairyNestCoordinator


@dataclass(frozen=True, kw_only=True)
class FairyNestButtonDescription(ButtonEntityDescription):
    action: Callable[[FairyNestCoordinator], Awaitable[None]]


async def _refresh(coordinator: FairyNestCoordinator) -> None:
    await coordinator.async_request_refresh()


async def _restore_standard(coordinator: FairyNestCoordinator) -> None:
    await coordinator.async_restore_standard()


async def _all_off(coordinator: FairyNestCoordinator) -> None:
    await coordinator.async_power(False, "button_all_off")


BUTTONS: tuple[FairyNestButtonDescription, ...] = (
    FairyNestButtonDescription(key="refresh", name="Refresh", action=_refresh),
    FairyNestButtonDescription(key="restore_standard", name="Restore Standard", action=_restore_standard),
    FairyNestButtonDescription(key="all_off", name="All Off", action=_all_off),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: FairyNestCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FairyNestButton(coordinator, entry, description) for description in BUTTONS])


class FairyNestButton(CoordinatorEntity[FairyNestCoordinator], ButtonEntity):
    """Button control for FairyNest SP511E."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FairyNestCoordinator,
        entry: ConfigEntry,
        description: FairyNestButtonDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}_button"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "FairyNest",
            "model": "SP511E",
        }

    async def async_press(self) -> None:
        await self.entity_description.action(self.coordinator)
