"""Button platform for SP511E."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SP511ECoordinator


@dataclass(frozen=True, kw_only=True)
class SP511EButtonDescription(ButtonEntityDescription):
    action: Callable[[SP511ECoordinator], Awaitable[None]]


async def _refresh(coordinator: SP511ECoordinator) -> None:
    await coordinator.async_request_refresh()


async def _restore_standard(coordinator: SP511ECoordinator) -> None:
    await coordinator.async_restore_standard()


async def _all_off(coordinator: SP511ECoordinator) -> None:
    await coordinator.async_power(False, "button_all_off")


BUTTONS: tuple[SP511EButtonDescription, ...] = (
    SP511EButtonDescription(key="refresh", name="Refresh", action=_refresh),
    SP511EButtonDescription(key="restore_standard", name="Restore Standard", action=_restore_standard),
    SP511EButtonDescription(key="all_off", name="All Off", action=_all_off),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SP511ECoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SP511EButton(coordinator, entry, description) for description in BUTTONS])


class SP511EButton(CoordinatorEntity[SP511ECoordinator], ButtonEntity):
    """Button control for SP511E."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SP511ECoordinator,
        entry: ConfigEntry,
        description: SP511EButtonDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}_button"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "SP511E",
            "model": "SP511E",
        }

    async def async_press(self) -> None:
        await self.entity_description.action(self.coordinator)
