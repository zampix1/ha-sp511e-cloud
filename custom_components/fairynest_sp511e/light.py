"""Light platform for FairyNest SP511E."""

from __future__ import annotations

from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import EFFECTS, MODE_TO_EFFECT, brightness_device_to_ha, brightness_ha_to_device, int_to_rgb
from .const import DOMAIN
from .coordinator import FairyNestCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: FairyNestCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FairyNestSP511ELight(coordinator, entry)])


class FairyNestSP511ELight(CoordinatorEntity[FairyNestCoordinator], RestoreEntity, LightEntity):
    """FairyNest SP511E light entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = [name.title() for name in EFFECTS]

    def __init__(self, coordinator: FairyNestCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_light"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "FairyNest",
            "model": "SP511E",
        }

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state is not None and last_state.attributes:
            if (brightness := last_state.attributes.get("brightness")) is not None:
                device_brightness = brightness_ha_to_device(int(brightness))
                if device_brightness is not None:
                    self.coordinator.state["bn"] = device_brightness
            if (rgb := last_state.attributes.get("rgb_color")) is not None and len(rgb) == 3:
                self.coordinator.state["c"] = (int(rgb[0]) << 16) | (int(rgb[1]) << 8) | int(rgb[2])

    @property
    def is_on(self) -> bool:
        return bool(int(self.coordinator.state.get("p", 0)))

    @property
    def brightness(self) -> int | None:
        return brightness_device_to_ha(self.coordinator.state.get("bn"))

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        color = self.coordinator.state.get("c")
        return int_to_rgb(int(color)) if color is not None else None

    @property
    def color_mode(self) -> ColorMode:
        return ColorMode.RGB

    @property
    def effect(self) -> str | None:
        mode = self.coordinator.state.get("m")
        if mode is None:
            return None
        effect = MODE_TO_EFFECT.get(int(mode))
        return effect.title() if effect else f"Mode {mode}"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "mode": self.coordinator.state.get("m"),
            "speed": self.coordinator.state.get("s"),
            "music_sensitivity": self.coordinator.state.get("ms"),
            "device_ip": self.coordinator.device.get("ip"),
            "ssid": self.coordinator.device.get("ssid"),
            "last_command": self.coordinator.last_command_result,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_power(True, "light_turn_on")
        if ATTR_RGB_COLOR in kwargs:
            await self.coordinator.async_color(tuple(int(v) for v in kwargs[ATTR_RGB_COLOR]), "light_rgb")
        if ATTR_BRIGHTNESS in kwargs:
            brightness = brightness_ha_to_device(kwargs[ATTR_BRIGHTNESS])
            if brightness is not None:
                await self.coordinator.async_brightness(brightness, "light_brightness")
        if ATTR_EFFECT in kwargs:
            await self.coordinator.async_effect(str(kwargs[ATTR_EFFECT]), "light_effect")

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_power(False, "light_turn_off")
