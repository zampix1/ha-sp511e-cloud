"""Sensor platform for FairyNest SP511E."""

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
from .coordinator import FairyNestCoordinator

PERCENT = "%"


@dataclass(frozen=True, kw_only=True)
class FairyNestSensorDescription(SensorEntityDescription):
    value_fn: Callable[[FairyNestCoordinator], Any]


SENSORS: tuple[FairyNestSensorDescription, ...] = (
    FairyNestSensorDescription(
        key="power",
        name="Power",
        value_fn=lambda c: c.state.get("p"),
    ),
    FairyNestSensorDescription(
        key="effect",
        name="Effect",
        value_fn=lambda c: MODE_TO_EFFECT.get(int(c.state.get("m", -1)), f"Mode {c.state.get('m')}").title(),
    ),
    FairyNestSensorDescription(
        key="brightness",
        name="Brightness",
        native_unit_of_measurement=PERCENT,
        value_fn=lambda c: c.state.get("bn"),
    ),
    FairyNestSensorDescription(
        key="speed",
        name="Speed",
        native_unit_of_measurement=PERCENT,
        value_fn=lambda c: c.state.get("s"),
    ),
    FairyNestSensorDescription(
        key="color_hex",
        name="Color Hex",
        value_fn=lambda c: f"#{int(c.state.get('c', 0)):06X}",
    ),
    FairyNestSensorDescription(
        key="music_sensitivity",
        name="Music Sensitivity",
        native_unit_of_measurement=PERCENT,
        value_fn=lambda c: c.state.get("ms"),
    ),
    FairyNestSensorDescription(
        key="device_ip",
        name="Device IP",
        value_fn=lambda c: c.device.get("ip"),
    ),
    FairyNestSensorDescription(
        key="ssid",
        name="SSID",
        value_fn=lambda c: c.device.get("ssid"),
    ),
    FairyNestSensorDescription(
        key="last_command",
        name="Last Command",
        value_fn=lambda c: c.last_command_result.get("command_name") or "none",
    ),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: FairyNestCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FairyNestSensor(coordinator, entry, description) for description in SENSORS])


class FairyNestSensor(CoordinatorEntity[FairyNestCoordinator], SensorEntity):
    """FairyNest SP511E sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FairyNestCoordinator,
        entry: ConfigEntry,
        description: FairyNestSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "FairyNest",
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
