"""Config flow for the Alarm Clock integration."""
from __future__ import annotations

import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_HOLIDAY_CALENDAR,
    CONF_MEDIA_PLAYER,
    CONF_MP3_URL,
    CONF_WORKDAY_SENSOR,
    DEFAULT_MEDIA_PLAYER,
    DOMAIN,
)


def _mp_default(defaults: dict, hass=None) -> Any:
    """Return the best default for the media player field.

    Priority:
      1. Previously saved value (from a reconfigure / options flow).
      2. DEFAULT_MEDIA_PLAYER if that entity actually exists in HA right now.
      3. vol.UNDEFINED — leaves the field blank so HA never validates "" as an
         entity ID (which triggers "not a valid entity ID / UUID").
    """
    saved = defaults.get(CONF_MEDIA_PLAYER)
    if saved:
        return saved

    # Only pre-fill the default if the entity actually exists; otherwise the
    # EntitySelector will raise a validation error on first load.
    if hass and hass.states.get(DEFAULT_MEDIA_PLAYER):
        return DEFAULT_MEDIA_PLAYER

    return vol.UNDEFINED


def _build_schema(defaults: dict, hass=None) -> vol.Schema:
    """Build the shared schema used by both config and options flows."""

    schema: dict = {}

    # ── Media player ────────────────────────────────────────────────
    schema[vol.Required(CONF_MEDIA_PLAYER, default=_mp_default(defaults, hass))] = (
        selector.EntitySelector(
            selector.EntitySelectorConfig(domain="media_player", multiple=False)
        )
    )

    # ── MP3 path ────────────────────────────────────────────────────
    # TextSelectorType.TEXT (not URL) so /local/ paths are accepted.
    schema[vol.Required(CONF_MP3_URL, default=defaults.get(CONF_MP3_URL, "/local/alarm.mp3"))] = (
        selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        )
    )

    # ── Workday sensor (optional) ────────────────────────────────────
    # Never pass default="" — EntitySelector validates it and throws.
    wd = defaults.get(CONF_WORKDAY_SENSOR) or None
    schema[vol.Optional(CONF_WORKDAY_SENSOR, default=wd if wd else vol.UNDEFINED)] = (
        selector.EntitySelector(
            selector.EntitySelectorConfig(domain="binary_sensor", multiple=False)
        )
    )

    # ── Holiday calendar (optional) ──────────────────────────────────
    hc = defaults.get(CONF_HOLIDAY_CALENDAR) or None
    schema[vol.Optional(CONF_HOLIDAY_CALENDAR, default=hc if hc else vol.UNDEFINED)] = (
        selector.EntitySelector(
            selector.EntitySelectorConfig(domain="calendar", multiple=False)
        )
    )

    return vol.Schema(schema)


def _clean(user_input: dict) -> dict:
    """Drop blank / None values before storing."""
    return {k: v for k, v in user_input.items() if v not in (None, "")}


class AlarmClockConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial setup UI."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input.get("name", "Alarm Clock").strip() or "Alarm Clock"
            await self.async_set_unique_id(name.lower().replace(" ", "_"))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=name, data=_clean(user_input))

        name_field = vol.Schema({
            vol.Required("name", default="Alarm Clock"): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
            ),
        })
        full_schema = vol.Schema({
            **name_field.schema,
            **_build_schema({}, self.hass).schema,
        })

        return self.async_show_form(step_id="user", data_schema=full_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return AlarmClockOptionsFlow(config_entry)


class AlarmClockOptionsFlow(config_entries.OptionsFlow):
    """Reconfigure media player, MP3 path, and workday sensor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=_clean(user_input))

        defaults = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(defaults, self.hass),
        )
