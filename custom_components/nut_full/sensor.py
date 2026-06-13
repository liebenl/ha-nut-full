"""Sensor platform for NUT Full — one sensor per NUT variable."""
from __future__ import annotations

import logging
import re

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    EntityCategory,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NutFullDataCoordinator
from .const import DIAGNOSTIC_PREFIXES, DOMAIN, VARIABLE_META

_LOGGER = logging.getLogger(__name__)

# Device classes that support a measurement state class
_MEASUREMENT_DEVICE_CLASSES = {
    SensorDeviceClass.BATTERY,
    SensorDeviceClass.CURRENT,
    SensorDeviceClass.ENERGY,
    SensorDeviceClass.FREQUENCY,
    SensorDeviceClass.POWER,
    SensorDeviceClass.TEMPERATURE,
    SensorDeviceClass.VOLTAGE,
    SensorDeviceClass.DURATION,
}


def _slugify(nut_var: str) -> str:
    """Turn a NUT variable name into a valid entity slug."""
    return re.sub(r"[^a-z0-9_]", "_", nut_var.lower())


def _is_numeric(value: str) -> bool:
    """Return True if the value looks numeric."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors — one per NUT variable returned by the UPS."""
    coordinator: NutFullDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    ups_name = entry.data["ups_name"]

    # Build device info from coordinator data (available after first refresh)
    data = coordinator.data or {}

    device_info = DeviceInfo(
        identifiers={(DOMAIN, f"{host}:{port}:{ups_name}")},
        name=data.get("ups.model", ups_name),
        manufacturer=data.get("ups.mfr", data.get("device.mfr", "Unknown")),
        model=data.get("ups.model", data.get("device.model", ups_name)),
        sw_version=data.get("ups.firmware", None),
        serial_number=data.get("ups.serial", data.get("device.serial", None)),
    )

    entities = [
        NutFullSensor(
            coordinator=coordinator,
            nut_var=var_name,
            device_info=device_info,
            ups_name=ups_name,
        )
        for var_name in data.keys()
    ]

    _LOGGER.info(
        "NUT Full: creating %d sensors for %s @ %s:%s",
        len(entities),
        ups_name,
        host,
        port,
    )
    async_add_entities(entities)


class NutFullSensor(CoordinatorEntity, SensorEntity):
    """A sensor that represents a single NUT variable."""

    def __init__(
        self,
        coordinator: NutFullDataCoordinator,
        nut_var: str,
        device_info: DeviceInfo,
        ups_name: str,
    ) -> None:
        """Initialise sensor."""
        super().__init__(coordinator)
        self._nut_var = nut_var
        self._ups_name = ups_name
        self._attr_device_info = device_info

        # Unique ID scoped to the UPS + variable
        host = coordinator.host
        port = coordinator.port
        self._attr_unique_id = f"{DOMAIN}_{host}_{port}_{ups_name}_{_slugify(nut_var)}"

        # Friendly name: replace dots and underscores with spaces, title-case
        readable = nut_var.replace(".", " ").replace("_", " ").title()
        self._attr_name = readable

        # Pull metadata from our map (exact match first, then None)
        meta = VARIABLE_META.get(nut_var, {})
        self._attr_native_unit_of_measurement = meta.get("unit")
        self._attr_icon = meta.get("icon", "mdi:information-outline")

        dc_str = meta.get("device_class")
        if dc_str:
            try:
                self._attr_device_class = SensorDeviceClass(dc_str)
            except ValueError:
                self._attr_device_class = None
        else:
            self._attr_device_class = None

        # Assign state class for numeric measurement sensors
        if (
            self._attr_device_class in _MEASUREMENT_DEVICE_CLASSES
            and self._attr_native_unit_of_measurement is not None
        ):
            self._attr_state_class = SensorStateClass.MEASUREMENT
        else:
            self._attr_state_class = None

        # Mark device-info variables as diagnostic
        if any(nut_var.startswith(p) for p in DIAGNOSTIC_PREFIXES):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        else:
            self._attr_entity_category = None

    @property
    def native_value(self) -> str | float | None:
        """Return current value of this NUT variable."""
        if self.coordinator.data is None:
            return None
        raw = self.coordinator.data.get(self._nut_var)
        if raw is None:
            return None
        # Return numeric float when possible for measurement sensors
        if self._attr_state_class == SensorStateClass.MEASUREMENT and _is_numeric(raw):
            return float(raw)
        return raw

    @property
    def extra_state_attributes(self) -> dict:
        """Expose the raw NUT variable name as an attribute for reference."""
        return {"nut_variable": self._nut_var}
