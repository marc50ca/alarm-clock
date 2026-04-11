/**
 * alarm-clock-card  v2.4.0
 *
 * Installation:
 *   1. Copy this file to:  config/www/alarm-clock-card.js
 *   2. Add Lovelace resource:
 *        url: /local/alarm-clock-card.js
 *        type: module
 *   3. Add card:
 *        type: custom:alarm-clock-card
 */

const DAYS      = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"];
const DAY_SHORT = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
const DAY_FULL  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];

const STYLES = `
  :host {
    display: block !important;
    width: 100% !important;
    box-sizing: border-box !important;
  }

  .card-root {
    display: block;
    width: 100%;
    box-sizing: border-box;
    background: var(--ha-card-background, var(--card-background-color, #fff));
    border-radius: var(--ha-card-border-radius, 12px);
    border: var(--ha-card-border-width, 1px) solid var(--ha-card-border-color, var(--divider-color, #e0e0e0));
    box-shadow: var(--ha-card-box-shadow, none);
    overflow: hidden;
    font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
    color: var(--primary-text-color, #212121);
  }

  /* Header */
  .hdr {
    background: var(--primary-color, #6200ee);
    padding: 14px 16px;
    display: flex;
    flex-direction: row;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    box-sizing: border-box;
    width: 100%;
  }
  .hdr-icon { font-size: 22px; flex-shrink: 0; line-height: 1; }
  .hdr-titles { flex: 1 1 120px; min-width: 0; }
  .hdr-title { font-size: 15px; font-weight: 700; color: #fff; margin: 0; line-height: 1.3; }
  .hdr-sub   { font-size: 11px; color: rgba(255,255,255,0.75); margin: 2px 0 0; }
  .next-badge {
    background: rgba(0,0,0,0.22); border-radius: 10px;
    padding: 6px 12px; text-align: center; flex-shrink: 0;
  }
  .next-lbl { font-size: 9px; text-transform: uppercase; letter-spacing: 0.7px; color: rgba(255,255,255,0.6); }
  .next-val { font-size: 14px; font-weight: 800; color: #fff; white-space: nowrap; line-height: 1.3; }
  .next-eta { font-size: 10px; color: rgba(255,255,255,0.8); }
  .action-btns { display: flex; flex-direction: row; gap: 8px; flex-shrink: 0; }
  .btn {
    display: inline-flex; align-items: center; gap: 5px;
    border: none; border-radius: 8px; padding: 8px 12px;
    font-family: inherit; font-size: 12px; font-weight: 700;
    cursor: pointer; white-space: nowrap; text-transform: uppercase; letter-spacing: 0.3px;
    transition: opacity 0.15s, transform 0.1s; line-height: 1;
  }
  .btn:active { transform: scale(0.95); }
  .btn:hover  { opacity: 0.85; }
  .btn-stop   { background: #e53935; color: #fff; }
  .btn-snooze { background: #f9a825; color: #3e2700; }
  .btn-snooze.snoozed { animation: snooze-blink 1.6s ease-in-out infinite; }
  @keyframes snooze-blink { 0%,100%{opacity:1} 50%{opacity:0.55} }

  /* Snooze countdown bar */
  .snooze-bar {
    display: flex; flex-direction: row; align-items: center;
    justify-content: space-between; gap: 12px;
    padding: 9px 16px; box-sizing: border-box; width: 100%;
    background: rgba(249,168,37,0.1);
    border-top: 2px solid rgba(249,168,37,0.4);
  }
  .snooze-info { display: flex; flex-direction: row; align-items: center; gap: 10px; }
  .snooze-cd   { font-size: 20px; font-weight: 800; color: #f9a825; min-width: 52px; }
  .snooze-lbl  { font-size: 12px; color: var(--secondary-text-color, #757575); }
  .snooze-cancel {
    background: transparent; border: 1.5px solid #e53935; color: #e53935;
    border-radius: 6px; padding: 4px 10px; font-size: 11px; font-weight: 700;
    text-transform: uppercase; cursor: pointer; font-family: inherit;
  }

  /* Day column styles (non-layout — layout is inline) */
  .day-col {
    background: var(--secondary-background-color, #f5f5f5);
    border-radius: 10px;
    padding: 12px 8px 10px;
    border: 2px solid transparent;
    position: relative;
    box-sizing: border-box;
    transition: border-color 0.2s;
  }
  .day-col.is-today   { outline: 2px solid var(--primary-color, #6200ee); outline-offset: -3px; }
  .day-col.is-enabled { border-color: var(--success-color, #00a86b); }
  .day-col.is-blocked { border-color: #ff9800; opacity: 0.72; }
  .today-pip {
    position: absolute; top: 5px; right: 6px;
    font-size: 8px; font-weight: 800; text-transform: uppercase;
    color: var(--primary-color, #6200ee); letter-spacing: 0.4px;
  }
  .day-pill {
    width: 38px; height: 38px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 800; cursor: pointer;
    transition: transform 0.12s; flex-shrink: 0;
    border: none;
  }
  .day-pill:active  { transform: scale(0.88); }
  .day-pill.enabled { background: var(--success-color, #00a86b); color: #fff; }
  .day-pill.disabled{ background: var(--disabled-text-color, #bdbdbd); color: #fff; }
  .day-pill.blocked { background: #ff9800; color: #fff; }
  .day-name {
    font-size: 11px; font-weight: 600; white-space: nowrap; text-align: center;
    color: var(--secondary-text-color, #757575);
  }
  .day-col.is-enabled .day-name { color: var(--primary-text-color, #212121); }
  input[type="time"] {
    font-family: inherit; font-size: 14px; font-weight: 700;
    color: var(--primary-text-color, #212121);
    background: var(--ha-card-background, var(--card-background-color, #fff));
    border: 1.5px solid var(--divider-color, #e0e0e0);
    border-radius: 8px; padding: 6px 4px;
    width: 88px; text-align: center; outline: none; cursor: pointer;
    -webkit-appearance: none; box-sizing: border-box; display: block;
    transition: border-color 0.2s;
  }
  input[type="time"]:focus  { border-color: var(--primary-color, #6200ee); }
  input[type="time"].active { border-color: var(--success-color, #00a86b); color: var(--success-color, #00a86b); }
  input[type="time"]:disabled { opacity: 0.32; cursor: default; }
  .chip {
    font-size: 10px; font-weight: 700; border-radius: 20px;
    padding: 2px 9px; white-space: nowrap; text-align: center;
    background: var(--disabled-text-color, #bdbdbd); color: #fff;
  }
  .chip.on      { background: var(--success-color, #00a86b); color: #fff; }
  .chip.blocked { background: #ff9800; color: #fff; }

  /* Toggle */
  .toggle       { position: relative; width: 42px; height: 24px; flex-shrink: 0; cursor: pointer; display: block; }
  .toggle input { opacity: 0; width: 0; height: 0; position: absolute; }
  .t-track {
    position: absolute; inset: 0; border-radius: 12px;
    background: var(--disabled-text-color, #bdbdbd); transition: background 0.2s;
  }
  .toggle input:checked + .t-track { background: var(--success-color, #00a86b); }
  .t-thumb {
    position: absolute; top: 3px; left: 3px;
    width: 18px; height: 18px; border-radius: 50%;
    background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    transition: transform 0.2s; pointer-events: none;
  }
  .toggle input:checked ~ .t-thumb { transform: translateX(18px); }
  .wd-toggle input:checked + .t-track { background: #ff9800; }

  /* Audio bar */
  .audio-bar {
    display: flex; flex-direction: row; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 10px;
    padding: 10px 16px; box-sizing: border-box; width: 100%;
    border-top: 1px solid var(--divider-color, #e0e0e0);
    background: var(--secondary-background-color, #f5f5f5);
  }
  .mp-select {
    font-family: inherit; font-size: 12px; font-weight: 600;
    background: var(--ha-card-background, var(--card-background-color, #fff));
    border: 1.5px solid var(--divider-color, #e0e0e0);
    border-radius: 8px; padding: 5px 8px; margin-top: 3px;
    color: var(--primary-text-color, #212121);
    max-width: 220px; cursor: pointer; outline: none; display: block;
    transition: border-color 0.2s;
  }
  .mp-select:focus { border-color: var(--primary-color, #6200ee); }
  .btn-test { background: #1565c0; color: #fff; }

  /* Bottom bar */
  .bottom-bar {
    display: flex; flex-direction: row; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 10px;
    padding: 10px 16px; box-sizing: border-box; width: 100%;
    border-top: 1px solid var(--divider-color, #e0e0e0);
  }
  .gates-wrap { display: flex; flex-direction: row; align-items: center; gap: 16px; flex-wrap: wrap; }
  .wd-wrap { display: flex; flex-direction: row; align-items: center; gap: 10px; }
  .wd-icon {
    width: 28px; height: 28px; border-radius: 50%;
    background: var(--disabled-text-color, #bdbdbd);
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0; transition: background 0.2s;
  }
  .wd-icon.on  { background: #ff9800; }
  .hol-icon.on { background: #e53935; }
  .wd-title    { font-size: 12px; font-weight: 600; color: var(--primary-text-color, #212121); }
  .wd-desc     { font-size: 10px; color: var(--secondary-text-color, #757575); margin-top: 1px; }
  .wd-desc.on  { color: #ff9800; }
  .hol-desc.on { color: #e53935; }
  .hol-toggle input:checked + .t-track { background: #e53935; }
  .summary     { font-size: 11px; color: var(--secondary-text-color, #757575); flex: 1; text-align: right; min-width: 80px; }
  .summary strong { color: var(--primary-text-color, #212121); }

  /* Error / info */
  .msg {
    padding: 24px 20px; text-align: center;
    color: var(--secondary-text-color, #757575);
    font-size: 13px; line-height: 1.6;
  }
  .msg code {
    background: var(--secondary-background-color, #f5f5f5);
    padding: 1px 5px; border-radius: 4px; font-size: 12px;
  }
`;

class AlarmClockCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._config = null;
    this._prefix = null;
    this._snoozeTimer = null;
    this._snoozeEnd = null;
    this._snoozeInterval = null;
  }

  setConfig(config) {
    this._config = config;
    // If prefix is explicitly set in config, lock it in immediately
    if (config.prefix) this._prefix = config.prefix;
    this._render();
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }

  static getStubConfig() { return { type: "custom:alarm-clock-card" }; }
  getCardSize() { return 5; }

  // ── Prefix resolution ───────────────────────────────────────────────
  // Tries multiple strategies so the card works out-of-the-box without
  // the user needing to set prefix: manually.

  _resolvePrefix() {
    // 1. Explicit config always wins
    if (this._config?.prefix) return this._config.prefix;

    if (!this._hass) return null;
    const states = this._hass.states;

    // 2. Scan time entities for anything ending in _monday_time
    //    and confirm a matching switch exists
    for (const id of Object.keys(states)) {
      if (id.startsWith("time.") && id.endsWith("_monday_time")) {
        const candidate = id.slice(5, -12); // strip "time." and "_monday_time"
        if (states[`switch.${candidate}_monday_enabled`]) {
          return candidate;
        }
      }
    }

    // 3. Try common default prefix names directly
    for (const p of ["alarm_clock", "alarm_clock_2", "my_alarm", "bedroom_alarm"]) {
      if (states[`time.${p}_monday_time`] && states[`switch.${p}_monday_enabled`]) {
        return p;
      }
    }

    return null;
  }

  // ── Entity helpers ──────────────────────────────────────────────────
  _s(id)             { return this._hass?.states[id]; }
  _timeEnt(day)      { return this._s(`time.${this._prefix}_${day}_time`); }
  _switchEnt(day)    { return this._s(`switch.${this._prefix}_${day}_enabled`); }
  _wdOnly()          { return this._s(`switch.${this._prefix}_workday_only`); }
  _skipHolidays()    { return this._s(`switch.${this._prefix}_skip_holidays`); }
  _nextAlarm()       { return this._s(`sensor.${this._prefix}_next_alarm`); }
  _mpSelect()        { return this._s(`select.${this._prefix}_media_player`); }

  // ── Resolve the active media player entity ID ───────────────────────
  _activeMediaPlayer() {
    return this._mpSelect()?.state
        || this._nextAlarm()?.attributes?.media_player
        || this._config?.media_player;
  }

  // ── HA service calls ────────────────────────────────────────────────
  _svc(domain, service, data) { this._hass?.callService(domain, service, data); }
  _toggleSwitch(id, state)    { this._svc("switch", state === "on" ? "turn_off" : "turn_on", { entity_id: id }); }
  _setTime(id, val)           { this._svc("time", "set_value", { entity_id: id, time: val + ":00" }); }
  _setMpOption(entityId, opt) { this._svc("select", "select_option", { entity_id: entityId, option: opt }); }

  _stopAlarm() {
    const mp = this._activeMediaPlayer();
    if (mp) this._svc("media_player", "media_stop", { entity_id: mp });
  }

  _testAlarm() {
    const mp  = this._activeMediaPlayer();
    const url = this._nextAlarm()?.attributes?.mp3_url || this._config?.mp3_url;
    if (mp && url) this._svc("media_player", "play_media", { entity_id: mp, media_content_id: url, media_content_type: "music" });
  }

  _snooze() {
    this._stopAlarm();
    this._clearSnooze();
    const mins = this._config?.snooze_minutes ?? 10;
    this._snoozeEnd = new Date(Date.now() + mins * 60 * 1000);
    this._snoozeTimer = setTimeout(() => {
      const mp  = this._activeMediaPlayer();
      const url = this._nextAlarm()?.attributes?.mp3_url || this._config?.mp3_url;
      if (mp && url) this._svc("media_player", "play_media", { entity_id: mp, media_content_id: url, media_content_type: "music" });
      this._clearSnooze();
      this._render();
    }, mins * 60 * 1000);
    this._snoozeInterval = setInterval(() => this._tickCountdown(), 1000);
    this._render();
  }

  _clearSnooze(rerender = false) {
    clearTimeout(this._snoozeTimer);
    clearInterval(this._snoozeInterval);
    this._snoozeTimer = this._snoozeEnd = this._snoozeInterval = null;
    if (rerender) this._render();
  }

  _tickCountdown() {
    const el = this.shadowRoot.querySelector(".snooze-cd");
    if (!el || !this._snoozeEnd) return;
    const rem = Math.max(0, Math.round((this._snoozeEnd - Date.now()) / 1000));
    el.textContent = `${String(Math.floor(rem / 60)).padStart(2,"0")}:${String(rem % 60).padStart(2,"0")}`;
  }

  // ── Render ──────────────────────────────────────────────────────────
  _render() {
    if (!this._hass) return;

    const prefix = this._resolvePrefix();
    const shadow = this.shadowRoot;
    shadow.innerHTML = "";

    const style = document.createElement("style");
    style.textContent = STYLES;
    shadow.appendChild(style);

    const root = document.createElement("div");
    root.className = "card-root";

    if (!prefix) {
      // Show a helpful diagnostic — list all time entities found so user
      // can see what prefix to use
      const timeEntities = Object.keys(this._hass.states)
        .filter(id => id.startsWith("time."))
        .slice(0, 10)
        .join(", ") || "none found";

      root.innerHTML = `
        <div class="msg">
          ⏰ <strong>Alarm Clock integration not detected.</strong><br><br>
          Add <code>prefix: alarm_clock</code> to the card config<br>
          (replace <code>alarm_clock</code> with your integration name).<br><br>
          <small>Time entities visible: ${timeEntities}</small>
        </div>`;
      shadow.appendChild(root);
      return;
    }

    this._prefix = prefix;

    const nextState  = this._nextAlarm();
    const attrs      = nextState?.attributes ?? {};
    const nextValue  = nextState?.state ?? "—";
    const title      = this._config?.title ?? "Alarm Clock";
    const snoozeMins = this._config?.snooze_minutes ?? 10;
    const isSnoozed  = !!this._snoozeEnd;

    // ── Header ──────────────────────────────────────────────────────
    const hdr = document.createElement("div");
    hdr.className = "hdr";
    hdr.innerHTML = `
      <div class="hdr-icon">⏰</div>
      <div class="hdr-titles">
        <div class="hdr-title">${title}</div>
        <div class="hdr-sub">Weekly alarm schedule</div>
      </div>
      <div class="next-badge">
        <div class="next-lbl">Next alarm</div>
        <div class="next-val">${nextValue !== "No alarm set" ? nextValue : "None set"}</div>
        ${attrs.time_until ? `<div class="next-eta">in ${attrs.time_until}</div>` : ""}
      </div>
      <div class="action-btns">
        <button class="btn btn-snooze${isSnoozed ? " snoozed" : ""}" id="btn-snooze">
          💤 ${isSnoozed ? "Snoozed" : `${snoozeMins}m`}
        </button>
        <button class="btn btn-stop" id="btn-stop">⏹ Stop</button>
      </div>`;
    root.appendChild(hdr);

    // ── Snooze bar ──────────────────────────────────────────────────
    if (isSnoozed) {
      const rem = Math.max(0, Math.round((this._snoozeEnd - Date.now()) / 1000));
      const bar = document.createElement("div");
      bar.className = "snooze-bar";
      bar.innerHTML = `
        <div class="snooze-info">
          <span style="font-size:18px">💤</span>
          <span class="snooze-cd">${String(Math.floor(rem/60)).padStart(2,"0")}:${String(rem%60).padStart(2,"0")}</span>
          <span class="snooze-lbl">Replaying alarm in ${snoozeMins} min</span>
        </div>
        <button class="snooze-cancel" id="btn-cancel-snooze">Cancel</button>`;
      root.appendChild(bar);
    }

    // ── Horizontal day columns ───────────────────────────────────────
    // The scroll wrapper and track use only inline styles — this is the
    // only reliable way to guarantee layout inside HA's shadow DOM tree,
    // since any external stylesheet can override <style> block rules.
    const scroll = document.createElement("div");
    scroll.style.cssText = [
      "display:block",
      "width:100%",
      "overflow-x:auto",
      "overflow-y:visible",
      "-webkit-overflow-scrolling:touch",
      "padding:14px 12px 12px",
      "box-sizing:border-box",
    ].join(";");

    const track = document.createElement("div");
    track.style.cssText = [
      "display:flex",
      "flex-direction:row",
      "flex-wrap:nowrap",
      "align-items:stretch",
      "gap:10px",
      "min-width:100%",
      "width:max-content",
      "box-sizing:border-box",
    ].join(";");

    const wdOnly     = this._wdOnly();
    const isWdOnly   = wdOnly?.state === "on";
    const wdSensorId = wdOnly?.attributes?.workday_sensor ?? null;
    const wdSensorSt = wdSensorId ? this._s(wdSensorId) : null;
    const todayIdx   = (new Date().getDay() + 6) % 7; // Mon=0…Sun=6

    DAYS.forEach((day, idx) => {
      const timeEnt = this._timeEnt(day);
      const swEnt   = this._switchEnt(day);
      if (!timeEnt || !swEnt) return;

      const isEnabled = swEnt.state === "on";
      const raw       = timeEnt.state;
      const curTime   = raw && raw !== "unavailable" ? raw.slice(0,5) : "07:00";
      const isToday   = idx === todayIdx;
      const isBlocked = isWdOnly && (isToday && wdSensorSt ? wdSensorSt.state !== "on" : idx >= 5);

      const colCls = ["day-col",
        isEnabled && !isBlocked ? "is-enabled" : "",
        isBlocked  ? "is-blocked" : "",
        isToday    ? "is-today"   : "",
      ].filter(Boolean).join(" ");

      const pillCls = "day-pill " + (isBlocked ? "blocked" : isEnabled ? "enabled" : "disabled");
      const chipCls = "chip "     + (isBlocked ? "blocked" : isEnabled ? "on"      : "");
      const chipLbl = isBlocked   ? "blocked"  : isEnabled ? "on"       : "off";

      const col = document.createElement("div");
      col.className = colCls;
      // Inline layout styles that cannot be overridden by HA
      col.style.cssText = [
        "display:flex",
        "flex-direction:column",
        "align-items:center",
        "gap:8px",
        "flex:1 0 100px",
        "min-width:100px",
        "max-width:140px",
        "box-sizing:border-box",
      ].join(";");

      col.innerHTML = `
        ${isToday ? `<div class="today-pip">Today</div>` : ""}
        <button class="${pillCls}" data-te="${swEnt.entity_id}" data-ts="${swEnt.state}">${DAY_SHORT[idx]}</button>
        <span class="day-name">${DAY_FULL[idx]}</span>
        <input type="time"
               class="${isEnabled && !isBlocked ? "active" : ""}"
               value="${curTime}"
               data-entity="${timeEnt.entity_id}"
               ${!isEnabled ? "disabled" : ""}>
        <label class="toggle">
          <input type="checkbox"
                 data-entity="${swEnt.entity_id}"
                 data-state="${swEnt.state}"
                 ${isEnabled ? "checked" : ""}>
          <div class="t-track"></div>
          <div class="t-thumb"></div>
        </label>
        <span class="${chipCls}">${chipLbl}</span>`;

      track.appendChild(col);
    });

    scroll.appendChild(track);
    root.appendChild(scroll);

    // ── Audio bar ───────────────────────────────────────────────────
    const mpSelectEnt = this._mpSelect();
    const mpOptions   = mpSelectEnt?.attributes?.options ?? [];
    const mpCurrent   = mpSelectEnt?.state ?? "";

    const audioBar = document.createElement("div");
    audioBar.className = "audio-bar";
    audioBar.innerHTML = `
      <div class="wd-wrap" style="flex:1;min-width:0">
        <div class="wd-icon" style="background:#1565c0;flex-shrink:0">🔊</div>
        <div style="min-width:0">
          <div class="wd-title">Audio Device</div>
          ${mpSelectEnt ? `
            <select class="mp-select" data-entity="${mpSelectEnt.entity_id}">
              ${mpOptions.map(o =>
                `<option value="${o}"${o === mpCurrent ? " selected" : ""}>${o.replace("media_player.", "").replace(/_/g, " ")}</option>`
              ).join("")}
            </select>` : `<div class="wd-desc">Configure in integration options</div>`}
        </div>
      </div>
      <button class="btn btn-test" id="btn-test">▶ Test</button>`;
    root.appendChild(audioBar);

    // ── Bottom bar ──────────────────────────────────────────────────
    const isWdOn  = wdOnly?.state === "on";
    const wdDesc  = wdSensorSt
      ? (wdSensorSt.state === "on" ? "Today is a workday ✓" : "Today is not a workday")
      : (wdSensorId ? "Sensor configured" : "No sensor configured");

    const skipHolEnt  = this._skipHolidays();
    const isHolSkip   = skipHolEnt?.state === "on";
    const isHoliday   = skipHolEnt?.attributes?.today_is_holiday === true;
    const holName     = skipHolEnt?.attributes?.holiday_name;
    const holCalId    = skipHolEnt?.attributes?.holiday_calendar;
    const holDesc     = holName
      ? `Today: ${holName}`
      : isHoliday
        ? "Today is a holiday"
        : holCalId ? "No holiday today ✓" : "No calendar configured";

    const active  = attrs.active_schedule ?? [];
    const summary = active.length === 0
      ? "No alarms enabled"
      : `<strong>${active.length}</strong> active · ` +
        active.map(a => `${a.day.slice(0,3)} ${a.time}`).join(" · ");

    const bottom = document.createElement("div");
    bottom.className = "bottom-bar";
    bottom.innerHTML = `
      <div class="gates-wrap">
        <div class="wd-wrap">
          <div class="wd-icon${isWdOn ? " on" : ""}">💼</div>
          <div>
            <div class="wd-title">Workday Only</div>
            <div class="wd-desc${isWdOn ? " on" : ""}">${wdDesc}</div>
          </div>
          ${wdOnly ? `
            <label class="toggle wd-toggle" style="margin-left:4px">
              <input type="checkbox"
                     data-entity="${wdOnly.entity_id}"
                     data-state="${wdOnly.state}"
                     ${isWdOn ? "checked" : ""}>
              <div class="t-track"></div>
              <div class="t-thumb"></div>
            </label>` : `<span style="font-size:10px;color:var(--secondary-text-color,#757575);margin-left:4px">Not configured</span>`}
        </div>
        ${skipHolEnt ? `
        <div class="wd-wrap">
          <div class="wd-icon hol-icon${isHoliday && isHolSkip ? " on" : ""}">🏖️</div>
          <div>
            <div class="wd-title">Skip Holidays</div>
            <div class="wd-desc hol-desc${isHoliday && isHolSkip ? " on" : ""}">${holDesc}</div>
          </div>
          <label class="toggle hol-toggle" style="margin-left:4px">
            <input type="checkbox"
                   data-entity="${skipHolEnt.entity_id}"
                   data-state="${skipHolEnt.state}"
                   ${isHolSkip ? "checked" : ""}>
            <div class="t-track"></div>
            <div class="t-thumb"></div>
          </label>
        </div>` : ""}
      </div>
      <div class="summary">${summary}</div>`;
    root.appendChild(bottom);

    shadow.appendChild(root);

    // ── Wire up events ────────────────────────────────────────────
    shadow.getElementById("btn-stop")?.addEventListener("click", () => this._stopAlarm());
    shadow.getElementById("btn-snooze")?.addEventListener("click", () =>
      isSnoozed ? this._clearSnooze(true) : this._snooze()
    );
    shadow.getElementById("btn-cancel-snooze")?.addEventListener("click", () => this._clearSnooze(true));
    shadow.getElementById("btn-test")?.addEventListener("click", () => this._testAlarm());

    shadow.querySelectorAll("input[type='checkbox']").forEach(cb =>
      cb.addEventListener("change", () => this._toggleSwitch(cb.dataset.entity, cb.dataset.state))
    );
    shadow.querySelectorAll("input[type='time']").forEach(ti =>
      ti.addEventListener("change", () => this._setTime(ti.dataset.entity, ti.value))
    );
    shadow.querySelectorAll("button.day-pill").forEach(p =>
      p.addEventListener("click", () => this._toggleSwitch(p.dataset.te, p.dataset.ts))
    );
    shadow.querySelectorAll("select.mp-select").forEach(sel =>
      sel.addEventListener("change", () => this._setMpOption(sel.dataset.entity, sel.value))
    );
  }
}

customElements.define("alarm-clock-card", AlarmClockCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "alarm-clock-card",
  name: "Alarm Clock Card",
  description: "Full-width horizontal weekly alarm scheduler with snooze, stop, workday/holiday detection, audio device picker, and MP3 playback.",
  preview: false,
});

console.info(
  "%c ALARM-CLOCK-CARD %c v2.4.0 ",
  "color:#fff;background:#6200ee;font-weight:700;padding:2px 8px;border-radius:4px 0 0 4px",
  "color:#6200ee;background:#f5f5f5;font-weight:700;padding:2px 8px;border-radius:0 4px 4px 0"
);
