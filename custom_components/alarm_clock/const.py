"""Constants for the Alarm Clock integration."""

DOMAIN = "alarm_clock"
PLATFORMS = ["time", "switch", "sensor", "select"]

# Config entry keys
CONF_MEDIA_PLAYER = "media_player"
CONF_MP3_URL = "mp3_url"
CONF_WORKDAY_SENSOR = "workday_sensor"
CONF_HOLIDAY_CALENDAR = "holiday_calendar"

# Defaults
DEFAULT_MEDIA_PLAYER = "media_player.echo1"

# Days of the week (index matches Python's datetime.weekday(): Mon=0, Sun=6)
DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

DAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

DEFAULT_ALARM_TIME_HOUR = 7
DEFAULT_ALARM_TIME_MINUTE = 0
