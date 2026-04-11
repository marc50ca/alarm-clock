"""Time platform for Alarm Clock – one time entity per day of the week."""
from __future__ import annotations

import logging
from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DEFAULT_ALARM_TIME_HOUR,
    DEFAULT_ALARM_TIME_MINUTE,
    DAY_NAMES,
    DAYS,
    DOMAIN,
)
from .coordinator import AlarmClockCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create one AlarmTimeEntity per day."""
    coordinator: AlarmClockCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        AlarmTimeEntity(coordinator, entry, day, DAY_NAMES[idx])
        for idx, day in enumerate(DAYS)
    ]
    async_add_entities(entities, True)


class AlarmTimeEntity(TimeEntity, RestoreEntity):
    """Stores and exposes the alarm time for a single day of the week."""

    _attr_should_poll = False

    def __init__(
        self,
        coordinator: AlarmClockCoordinator,
        entry: ConfigEntry,
        day: str,
        day_name: str,
    ) -> None:
        self._coordinator = coordinator
        self._entry = entry
        self._day = day
        self._day_name = day_name

        self._attr_name = f"{entry.title} {day_name} Time"
        self._attr_unique_id = f"{entry.entry_id}_{day}_time"
        self._attr_native_value: time = time(
            DEFAULT_ALARM_TIME_HOUR, DEFAULT_ALARM_TIME_MINUTE
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def async_added_to_hass(self) -> None:
        """Restore the last known alarm time from state machine."""
        await super().async_added_to_hass()

        if last_state := await self.async_get_last_state():
            raw = last_state.state
            if raw not in ("unknown", "unavailable", "None"):
                try:
                    parts = raw.split(":")
                    self._attr_native_value = time(int(parts[0]), int(parts[1]))
                except (ValueError, IndexError):
                    _LOGGER.debug("Could not restore time state %s for %s", raw, self._day)

        # Keep coordinator in sync
        self._coordinator.alarm_times[self._day] = self._attr_native_value
        # Refresh icon when enabled state changes
        self._coordinator.add_listener(self._async_refresh)

    async def async_will_remove_from_hass(self) -> None:
        self._coordinator.remove_listener(self._async_refresh)

    def _async_refresh(self) -> None:
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # TimeEntity interface
    # ------------------------------------------------------------------

    async def async_set_value(self, value: time) -> None:
        """Called by HA when the user changes the time via UI or service."""
        self._attr_native_value = value
        self._coordinator.alarm_times[self._day] = value
        self._coordinator._notify_listeners()
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Presentation
    # ------------------------------------------------------------------

    @property
    def icon(self) -> str:
        return (
            "mdi:alarm"
            if self._coordinator.alarm_enabled.get(self._day)
            else "mdi:alarm-off"
        )

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "day": self._day,
            "alarm_enabled": self._coordinator.alarm_enabled.get(self._day, False),
        }

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Custom Integration",
            "model": "Alarm Clock",
        }
