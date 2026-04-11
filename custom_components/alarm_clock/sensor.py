"""Sensor platform for Alarm Clock – shows the next scheduled alarm."""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import AlarmClockCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AlarmClockCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([NextAlarmSensor(coordinator, entry)], True)


class NextAlarmSensor(SensorEntity):
    """Shows when the next alarm will fire and how long until it does."""

    _attr_should_poll = False
    _attr_icon = "mdi:alarm-multiple"

    def __init__(
        self,
        coordinator: AlarmClockCoordinator,
        entry: ConfigEntry,
    ) -> None:
        self._coordinator = coordinator
        self._entry = entry

        self._attr_name = f"{entry.title} Next Alarm"
        self._attr_unique_id = f"{entry.entry_id}_next_alarm"

    async def async_added_to_hass(self) -> None:
        self._coordinator.add_listener(self._async_refresh)

    async def async_will_remove_from_hass(self) -> None:
        self._coordinator.remove_listener(self._async_refresh)

    def _async_refresh(self) -> None:
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # SensorEntity interface
    # ------------------------------------------------------------------

    @property
    def native_value(self) -> str:
        next_alarm = self._coordinator.get_next_alarm()
        if next_alarm is None:
            return "No alarm set"
        return next_alarm.strftime("%A %H:%M")

    @property
    def extra_state_attributes(self) -> dict:
        next_alarm: datetime | None = self._coordinator.get_next_alarm()
        attrs: dict = {
            "media_player": self._coordinator.media_player,
            "mp3_url": self._coordinator.mp3_url,
            "workday_only": self._coordinator.workday_only,
        }

        if next_alarm:
            now = dt_util.now()
            diff = next_alarm - now
            total_seconds = int(diff.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            attrs["next_alarm_iso"] = next_alarm.isoformat()
            attrs["time_until"] = f"{hours}h {minutes}m"

        # Build a human-readable summary of all enabled alarms
        schedule: list[dict] = []
        from .const import DAYS, DAY_NAMES
        for idx, day in enumerate(DAYS):
            if self._coordinator.alarm_enabled.get(day):
                t = self._coordinator.alarm_times.get(day)
                schedule.append(
                    {
                        "day": DAY_NAMES[idx],
                        "time": t.strftime("%H:%M") if t else "not set",
                    }
                )
        attrs["active_schedule"] = schedule

        return attrs

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Custom Integration",
            "model": "Alarm Clock",
        }
