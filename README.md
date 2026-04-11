# ⏰ Alarm Clock — Home Assistant Integration

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Validate](https://github.com/marc50ca/alarm-clock/actions/workflows/validate.yml/badge.svg)](https://github.com/marc50ca/alarm-clock/actions/workflows/validate.yml)
[![HA Version](https://img.shields.io/badge/Home%20Assistant-2023.6%2B-blue)](https://www.home-assistant.io)

A weekly alarm clock for Home Assistant with per-day scheduling, workday detection, MP3 playback on any media player, and a custom Lovelace dashboard card.

---

## Repository Structure

```
ha-alarm-clock/
├── .github/
│   └── workflows/
│       └── validate.yml          ← HACS + hassfest CI
├── brand/
│   ├── icon.png                  ← Required by HACS (256×256 px)
│   └── icon@2x.png               ← Recommended (512×512 px)
├── custom_components/
│   └── alarm_clock/              ← Installed by HACS
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── coordinator.py
│       ├── config_flow.py
│       ├── time.py
│       ├── switch.py
│       ├── sensor.py
│       ├── strings.json
│       └── translations/
│           └── en.json
├── alarm-clock-card.js           ← Lovelace card (copy manually to www/)
├── hacs.json
└── README.md
```

---

## Installation

### Step 1 — Install the Integration via HACS

1. Open HACS → **Integrations** → ⋮ → **Custom repositories**
2. Paste your GitHub repository URL, category **Integration** → **Add**
3. Search **Alarm Clock** → **Download**
4. **Restart Home Assistant**

**Manual alternative:** Copy `custom_components/alarm_clock/` to `config/custom_components/`, then restart HA.

---

### Step 2 — Configure the Integration

**Settings → Devices & Services → Add Integration → Alarm Clock**

| Field | Description |
|---|---|
| **Name** | Integration name. Default `Alarm Clock` gives entity prefix `alarm_clock`. |
| **Media Player** | Audio output device. Defaults to `media_player.echo1`. |
| **MP3 File Path** | Path to your alarm sound, e.g. `/local/alarm.mp3` |
| **Workday Sensor** *(optional)* | A `binary_sensor` from the [Workday integration](https://www.home-assistant.io/integrations/workday/). Leave blank if unused. |

> Reconfigure any time: **Settings → Devices & Services → Alarm Clock → Configure**

---

### Step 3 — Install the Lovelace Card

The card is not installed automatically by HACS — copy it manually once.

Copy `alarm-clock-card.js` from the repository to your HA `www` folder:

```
config/
└── www/
    └── alarm-clock-card.js
```

Register it as a Lovelace resource:

**Settings → Dashboards → ⋮ → Resources → Add resource**

| Field | Value |
|---|---|
| URL | `/local/alarm-clock-card.js` |
| Resource type | `JavaScript module` |

Or in `configuration.yaml`:
```yaml
lovelace:
  resources:
    - url: /local/alarm-clock-card.js
      type: module
```

**Hard-refresh your browser** (`Ctrl+Shift+R` / `Cmd+Shift+R`) after adding the resource.

---

### Step 4 — Add the Card

Edit a dashboard → **Add Card** → search **Alarm Clock Card**, or paste YAML:

```yaml
type: custom:alarm-clock-card
```

If the card shows "integration not detected":

```yaml
type: custom:alarm-clock-card
prefix: alarm_clock
```

The prefix matches your integration's entity prefix. For name **"Alarm Clock"** it is `alarm_clock`. Confirm by checking entity names under **Settings → Devices & Services → Alarm Clock**.

---

### Step 5 — Serve Your MP3

```
config/
└── www/
    └── alarm.mp3
```

Use `/local/alarm.mp3` as the MP3 path. Test with `http://your-ha-ip:8123/local/alarm.mp3`.

---

## Card Options

```yaml
type: custom:alarm-clock-card
title: "Bedroom Alarm"    # Header title  (default: "Alarm Clock")
prefix: alarm_clock       # Entity prefix (auto-detected if omitted)
snooze_minutes: 10        # Snooze length in minutes (default: 10)
```

---

## Entities Created

For integration name **"Alarm Clock"** (prefix: `alarm_clock`):

```
time.alarm_clock_monday_time      … time.alarm_clock_sunday_time
switch.alarm_clock_monday_enabled … switch.alarm_clock_sunday_enabled
switch.alarm_clock_workday_only
sensor.alarm_clock_next_alarm
```

---

## Workday Integration

1. Install the [Workday integration](https://www.home-assistant.io/integrations/workday/)
2. Note its binary sensor entity ID (e.g. `binary_sensor.workday_sensor`)
3. In **Alarm Clock → Configure**, select it as the Workday Sensor
4. Enable `switch.alarm_clock_workday_only` (or use the 💼 toggle on the card)

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Card shows "integration not detected" | Add `prefix: alarm_clock` to the card YAML |
| Config error "not a valid entity ID" | Leave **Workday Sensor** blank if you don't use the Workday integration |
| Alarm doesn't fire | Check the day's switch is **on** and the time is set. Check HA logs for `alarm_clock` errors |
| No sound | Visit `http://your-ha-ip:8123/local/alarm.mp3` to verify the file is accessible |
| Card missing from picker | Hard-refresh (`Ctrl+Shift+R`) and check the resource URL is exactly `/local/alarm-clock-card.js` |
| HACS validation fails | Ensure `manifest.json` has no `homeassistant` key and all six required fields are present |
