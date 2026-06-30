"""Sensor platform for SP511E."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import MODE_TO_EFFECT
from .const import DOMAIN
from .coordinator import SP511ECoordinator

PERCENT = "%"


@dataclass(frozen=True, kw_only=True)
class SP511ESensorDescription(SensorEntityDescription):
    value_fn: Callable[[SP511ECoordinator], Any]


SENSORS: tuple[SP511ESensorDescription, ...] = (
    SP511ESensorDescription(
        key="power",
        name="Power",
        value_fn=lambda c: c.state.get("p"),
    ),
    SP511ESensorDescription(
        key="effect",
        name="Effect",
        value_fn=lambda c: MODE_TO_EFFECT.get(int(c.state.get("m", -1)), f"Mode {c.state.get('m')}").title(),
    ),
    SP511ESensorDescription(
        key="brightness",
        name="Brightness",
        native_unit_of_measurement=PERCENT,
        value_fn=lambda c: c.state.get("bn"),
    ),
    SP511ESensorDescription(
        key="speed",
        name="Speed",
        native_unit_of_measurement=PERCENT,
        value_fn=lambda c: c.state.get("s"),
    ),
    SP511ESensorDescription(
        key="color_hex",
        name="Color Hex",
        value_fn=lambda c: f"#{int(c.state.get('c', 0)):06X}",
    ),
    SP511ESensorDescription(
        key="music_sensitivity",
        name="Music Sensitivity",
        native_unit_of_measurement=PERCENT,
        value_fn=lambda c: c.state.get("ms"),
    ),
    SP511ESensorDescription(
        key="device_ip",
        name="Device IP",
        value_fn=lambda c: c.device.get("ip"),
    ),
    SP511ESensorDescription(
        key="ssid",
        name="SSID",
        value_fn=lambda c: c.device.get("ssid"),
    ),
    SP511ESensorDescription(
        key="last_command",
        name="Last Command",
        value_fn=lambda c: c.last_command_result.get("command_name") or "none",
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: SP511ECoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SP511ESensor(coordinator, entry, description) for description in SENSORS])


class SP511ESensor(CoordinatorEntity[SP511ECoordinator], SensorEntity):
    """SP511E sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SP511ECoordinator,
        entry: ConfigEntry,
        description: SP511ESensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "SP511E",
            "model": "SP511E",
        }

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.key != "last_command":
            return None
        return self.coordinator.last_command_result
