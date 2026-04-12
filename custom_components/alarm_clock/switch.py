"""Switch platform for Alarm Clock.

Creates:
  • One enable/disable switch per day of the week.
  • One "Workday Only" switch that gates all alarms against the configured
    binary_sensor.workday sensor (from the Home Assistant Workday integration).
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DAY_NAMES, DAYS, DOMAIN
from .coordinator import AlarmClockCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create per-day switches and the workday-only switch."""
    coordinator: AlarmClockCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SwitchEntity] = [
        AlarmEnabledSwitch(coordinator, entry, day, DAY_NAMES[idx])
        for idx, day in enumerate(DAYS)
    ]
    entities.append(MasterEnableSwitch(coordinator, entry))
    entities.append(WorkdayOnlySwitch(coordinator, entry))
    entities.append(SkipHolidaysSwitch(coordinator, entry))

    async_add_entities(entities, True)


# ---------------------------------------------------------------------------
# Per-day alarm enable switch
# ---------------------------------------------------------------------------

class AlarmEnabledSwitch(SwitchEntity, RestoreEntity):
    """Enables or disables the alarm for a specific day of the week."""

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

        self._attr_name = f"{entry.title} {day_name} Enabled"
        self._attr_unique_id = f"{entry.entry_id}_{day}_enabled"
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            self._attr_is_on = last_state.state == "on"
        self._coordinator.alarm_enabled[self._day] = self._attr_is_on
        self._coordinator.add_listener(self._async_refresh)

    async def async_will_remove_from_hass(self) -> None:
        self._coordinator.remove_listener(self._async_refresh)

    def _async_refresh(self) -> None:
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        self._coordinator.alarm_enabled[self._day] = True
        self._coordinator._notify_listeners()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self._coordinator.alarm_enabled[self._day] = False
        self._coordinator._notify_listeners()
        self.async_write_ha_state()

    @property
    def icon(self) -> str:
        return "mdi:alarm-check" if self._attr_is_on else "mdi:alarm-off"

    @property
    def extra_state_attributes(self) -> dict:
        alarm_time = self._coordinator.alarm_times.get(self._day)
        return {
            "day": self._day,
            "alarm_time": alarm_time.strftime("%H:%M") if alarm_time else None,
        }

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Custom Integration",
            "model": "Alarm Clock",
        }


# ---------------------------------------------------------------------------
# Master enable switch
# ---------------------------------------------------------------------------

class MasterEnableSwitch(SwitchEntity, RestoreEntity):
    """When ON, alarms can fire normally. When OFF, all alarms are paused
    without touching any per-day settings, times, or other gates."""

    _attr_should_poll = False

    def __init__(
        self,
        coordinator: AlarmClockCoordinator,
        entry: ConfigEntry,
    ) -> None:
        self._coordinator = coordinator
        self._entry = entry

        self._attr_name = f"{entry.title} Alarms Enabled"
        self._attr_unique_id = f"{entry.entry_id}_master_enabled"
        self._attr_is_on = True  # Default: alarms active

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            self._attr_is_on = last_state.state != "off"
        self._coordinator.master_enabled = self._attr_is_on
        self._coordinator.add_listener(self._async_refresh)

    async def async_will_remove_from_hass(self) -> None:
        self._coordinator.remove_listener(self._async_refresh)

    def _async_refresh(self) -> None:
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        self._coordinator.master_enabled = True
        self._coordinator._notify_listeners()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self._coordinator.master_enabled = False
        self._coordinator._notify_listeners()
        self.async_write_ha_state()

    @property
    def icon(self) -> str:
        return "mdi:alarm" if self._attr_is_on else "mdi:alarm-off"

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Custom Integration",
            "model": "Alarm Clock",
        }


# ---------------------------------------------------------------------------
# Workday-only gate switch
# ---------------------------------------------------------------------------

class WorkdayOnlySwitch(SwitchEntity, RestoreEntity):
    """When ON, alarms only fire on days where the workday sensor is 'on'."""

    _attr_should_poll = False
    _attr_icon = "mdi:briefcase-clock"

    def __init__(
        self,
        coordinator: AlarmClockCoordinator,
        entry: ConfigEntry,
    ) -> None:
        self._coordinator = coordinator
        self._entry = entry

        self._attr_name = f"{entry.title} Workday Only"
        self._attr_unique_id = f"{entry.entry_id}_workday_only"
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            self._attr_is_on = last_state.state == "on"
        self._coordinator.workday_only = self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        self._coordinator.workday_only = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self._coordinator.workday_only = False
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict:
        ws = self._coordinator.workday_sensor
        attrs: dict = {"workday_sensor": ws}
        if ws:
            state = self.hass.states.get(ws)
            attrs["workday_sensor_state"] = state.state if state else "unavailable"
        return attrs

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Custom Integration",
            "model": "Alarm Clock",
        }


# ---------------------------------------------------------------------------
# Skip public holidays gate switch
# ---------------------------------------------------------------------------

class SkipHolidaysSwitch(SwitchEntity, RestoreEntity):
    """When ON, alarms are skipped on days where the holiday calendar is active."""

    _attr_should_poll = False
    _attr_icon = "mdi:calendar-remove"

    def __init__(
        self,
        coordinator: AlarmClockCoordinator,
        entry: ConfigEntry,
    ) -> None:
        self._coordinator = coordinator
        self._entry = entry

        self._attr_name = f"{entry.title} Skip Holidays"
        self._attr_unique_id = f"{entry.entry_id}_skip_holidays"
        self._attr_is_on = False

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if last_state := await self.async_get_last_state():
            self._attr_is_on = last_state.state == "on"
        self._coordinator.skip_holidays = self._attr_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._attr_is_on = True
        self._coordinator.skip_holidays = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._attr_is_on = False
        self._coordinator.skip_holidays = False
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict:
        hc = self._coordinator.holiday_calendar
        attrs: dict = {"holiday_calendar": hc}
        if hc:
            state = self.hass.states.get(hc)
            attrs["holiday_calendar_state"] = state.state if state else "unavailable"
            if state and state.state == "on":
                attrs["today_is_holiday"] = True
                # HA calendar entities expose the event name in 'message' or 'description'
                for key in ("message", "description", "summary"):
                    name = (state.attributes or {}).get(key)
                    if name:
                        attrs["holiday_name"] = name
                        break
        return attrs

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Custom Integration",
            "model": "Alarm Clock",
        }
