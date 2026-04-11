"""Coordinator for the Alarm Clock integration."""
from __future__ import annotations

import logging
from datetime import datetime, time as dt_time, timedelta
from typing import Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .const import (
    CONF_HOLIDAY_CALENDAR,
    CONF_MEDIA_PLAYER,
    CONF_MP3_URL,
    CONF_WORKDAY_SENSOR,
    DAYS,
    DEFAULT_MEDIA_PLAYER,
)

_LOGGER = logging.getLogger(__name__)


class AlarmClockCoordinator:
    """Manages alarm state and triggers for all days of the week."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        # Per-day alarm times (None = not set)
        self.alarm_times: dict[str, dt_time | None] = {day: dt_time(7, 0) for day in DAYS}
        # Per-day enabled state
        self.alarm_enabled: dict[str, bool] = {day: False for day in DAYS}
        # Workday-only gate
        self.workday_only: bool = False
        # Public holiday gate
        self.skip_holidays: bool = False
        # Media player override (set by the select entity; takes precedence over config entry)
        self.media_player_override: str | None = None

        self._unsubscribe: Callable | None = None
        self._listeners: list[Callable] = []

    # ------------------------------------------------------------------
    # Config properties (read from entry data, falling back to options)
    # ------------------------------------------------------------------

    def _get_config(self, key: str, default=None):
        """Return value from options first, then data."""
        return self.entry.options.get(key, self.entry.data.get(key, default))

    @property
    def media_player(self) -> str:
        if self.media_player_override is not None:
            return self.media_player_override
        return self._get_config(CONF_MEDIA_PLAYER, DEFAULT_MEDIA_PLAYER)

    @property
    def mp3_url(self) -> str:
        return self._get_config(CONF_MP3_URL, "")

    @property
    def workday_sensor(self) -> str | None:
        val = self._get_config(CONF_WORKDAY_SENSOR)
        return val if val else None

    @property
    def holiday_calendar(self) -> str | None:
        val = self._get_config(CONF_HOLIDAY_CALENDAR)
        return val if val else None

    # ------------------------------------------------------------------
    # Setup / Teardown
    # ------------------------------------------------------------------

    async def async_setup(self) -> None:
        """Register a time-change listener that fires every minute."""
        self._unsubscribe = async_track_time_change(
            self.hass,
            self._check_alarms,
            second=0,
        )
        _LOGGER.debug("Alarm clock coordinator started for entry %s", self.entry.entry_id)

    @callback
    def async_unload(self) -> None:
        """Cancel the time-change listener."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None

    # ------------------------------------------------------------------
    # Alarm checking
    # ------------------------------------------------------------------

    @callback
    def _check_alarms(self, now: datetime) -> None:
        """Called every minute; fires alarm if conditions are met."""
        local_now = dt_util.as_local(now)
        current_time = local_now.time().replace(second=0, microsecond=0)
        current_day = DAYS[local_now.weekday()]  # Mon=0 … Sun=6

        # ---- Workday gate ------------------------------------------------
        if self.workday_only and self.workday_sensor:
            state = self.hass.states.get(self.workday_sensor)
            if state is None or state.state != "on":
                _LOGGER.debug(
                    "Alarm clock: workday gate blocked alarm on %s", current_day
                )
                self._notify_listeners()
                return

        # ---- Holiday gate ------------------------------------------------
        if self.skip_holidays and self.holiday_calendar:
            cal_state = self.hass.states.get(self.holiday_calendar)
            if cal_state is not None and cal_state.state == "on":
                _LOGGER.debug(
                    "Alarm clock: holiday gate blocked alarm on %s", current_day
                )
                self._notify_listeners()
                return

        # ---- Per-day check -----------------------------------------------
        if self.alarm_enabled.get(current_day):
            alarm_time = self.alarm_times.get(current_day)
            if alarm_time is not None:
                alarm_clean = alarm_time.replace(second=0, microsecond=0)
                if current_time == alarm_clean:
                    _LOGGER.info(
                        "Alarm clock: FIRING alarm for %s at %s", current_day, alarm_clean
                    )
                    self._fire_alarm(current_day)

        self._notify_listeners()

    def _fire_alarm(self, day: str) -> None:
        """Play the configured MP3 on the configured media player."""
        media_player = self.media_player
        mp3_url = self.mp3_url

        if not media_player:
            _LOGGER.warning("Alarm clock: no media player configured – alarm not played")
            return
        if not mp3_url:
            _LOGGER.warning("Alarm clock: no MP3 URL configured – alarm not played")
            return

        self.hass.async_create_task(
            self.hass.services.async_call(
                "media_player",
                "play_media",
                {
                    "entity_id": media_player,
                    "media_content_id": mp3_url,
                    "media_content_type": "music",
                },
            )
        )

    # ------------------------------------------------------------------
    # Next alarm calculation
    # ------------------------------------------------------------------

    def get_next_alarm(self) -> datetime | None:
        """Return the next scheduled alarm as a timezone-aware datetime."""
        now = dt_util.now()
        current_weekday = now.weekday()  # 0 = Monday

        for offset in range(8):  # up to a full week ahead
            check_weekday = (current_weekday + offset) % 7
            day = DAYS[check_weekday]

            if not self.alarm_enabled.get(day):
                continue

            alarm_time = self.alarm_times.get(day)
            if alarm_time is None:
                continue

            candidate_date = now.date() + timedelta(days=offset)
            candidate_dt = dt_util.as_local(
                datetime.combine(candidate_date, alarm_time)
            )

            if candidate_dt > now:
                return candidate_dt

        return None

    # ------------------------------------------------------------------
    # Listener management (entities subscribe to coordinate state updates)
    # ------------------------------------------------------------------

    def add_listener(self, listener: Callable) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def remove_listener(self, listener: Callable) -> None:
        try:
            self._listeners.remove(listener)
        except ValueError:
            pass

    def _notify_listeners(self) -> None:
        for listener in self._listeners:
            try:
                listener()
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Error notifying alarm clock listener")
