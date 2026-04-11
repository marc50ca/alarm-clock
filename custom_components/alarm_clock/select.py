"""Select platform for Alarm Clock — media player picker.

Creates one select entity per config entry that lets the user choose which
media player the alarm fires on.  The selection is persisted via RestoreEntity
and pushed to the coordinator so the change takes effect immediately without
reloading the integration.
"""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CONF_MEDIA_PLAYER, DEFAULT_MEDIA_PLAYER, DOMAIN
from .coordinator import AlarmClockCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AlarmClockCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AlarmMediaPlayerSelect(coordinator, entry)], True)


class AlarmMediaPlayerSelect(SelectEntity, RestoreEntity):
    """Lets the user pick which media player the alarm fires on."""

    _attr_should_poll = False
    _attr_icon = "mdi:speaker"

    def __init__(
        self,
        coordinator: AlarmClockCoordinator,
        entry: ConfigEntry,
    ) -> None:
        self._coordinator = coordinator
        self._entry = entry

        self._attr_name = f"{entry.title} Media Player"
        self._attr_unique_id = f"{entry.entry_id}_media_player_select"

        # Seed options and current value from the config entry so the entity
        # is valid even before async_added_to_hass refreshes from live state.
        default_mp = coordinator._get_config(CONF_MEDIA_PLAYER, DEFAULT_MEDIA_PLAYER)
        self._attr_options: list[str] = [default_mp] if default_mp else []
        self._attr_current_option: str | None = default_mp or None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _refresh_options(self) -> None:
        """Re-build the options list from current HA state."""
        players = sorted(self.hass.states.async_entity_ids("media_player"))
        if not players:
            # Fall back to the configured default so the entity isn't empty.
            configured = self._coordinator._get_config(
                CONF_MEDIA_PLAYER, DEFAULT_MEDIA_PLAYER
            )
            players = [configured] if configured else []
        self._attr_options = players
        if self._attr_current_option not in players:
            self._attr_current_option = players[0] if players else None
        # Keep coordinator in sync
        if self._attr_current_option:
            self._coordinator.media_player_override = self._attr_current_option

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._refresh_options()

        # Restore previously selected player
        if last := await self.async_get_last_state():
            if last.state and last.state not in ("unknown", "unavailable"):
                if last.state in self._attr_options:
                    self._attr_current_option = last.state
                else:
                    # The stored entity may not exist yet — add it temporarily
                    self._attr_options = sorted({*self._attr_options, last.state})
                    self._attr_current_option = last.state

        # Push restored value to coordinator
        if self._attr_current_option:
            self._coordinator.media_player_override = self._attr_current_option

        # Refresh option list when media_player entities appear or disappear
        @callback
        def _on_state_changed(event) -> None:
            if event.data.get("entity_id", "").startswith("media_player."):
                self._refresh_options()
                self.async_write_ha_state()

        self.async_on_remove(
            self.hass.bus.async_listen("state_changed", _on_state_changed)
        )

        self._coordinator.add_listener(self._async_refresh)

    async def async_will_remove_from_hass(self) -> None:
        self._coordinator.remove_listener(self._async_refresh)

    def _async_refresh(self) -> None:
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # SelectEntity interface
    # ------------------------------------------------------------------

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        self._coordinator.media_player_override = option
        self._coordinator._notify_listeners()
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Presentation
    # ------------------------------------------------------------------

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": self._entry.title,
            "manufacturer": "Custom Integration",
            "model": "Alarm Clock",
        }
