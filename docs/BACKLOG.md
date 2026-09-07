# Focus Flow — Product Backlog

Prioritized list of future work for the app. Items beyond the current MVP are intentionally deferred.

---

## How to read this backlog

- **Priority:** P0 = next sprint, P1 = soon, P2 = later, P3 = someday
- **Estimate:** rough complexity (XS / S / M / L / XL)
- **Status:** all items are `pending` unless marked `done`

---

## P0 — Polish & Stability (next sprint)

### B-01: Fix timer pause/resume state persistence ✅
- **Estimate:** S
- **Status:** done
- **Description:** The timer currently resets on page reload. Add `localStorage` persistence for `remaining`, `mode`, `running`, and `startTime` so a browser refresh does not lose an active session.
- **Acceptance:** Start timer → refresh page → timer shows correct remaining time and continues counting.

### B-02: Add keyboard shortcuts
- **Estimate:** XS
- **Description:** Space = start/pause timer, R = reset timer, N = toggle palette, Escape = stop all audio.
- **Acceptance:** Shortcuts work when no input is focused; do not conflict with task input typing.

### B-03: Improve audio mixing UX
- **Estimate:** M
- **Description:** Show per-track mute/unmute button next to each slider. Show a small waveform-style level indicator or at least the track name when playing.
- **Acceptance:** User can mute/unmute without dragging slider back to 0. Status text updates to current playing track(s).

### B-04: Add volume memory
- **Estimate:** XS
- **Description:** Save slider positions to `localStorage` so the user's preferred mix persists across sessions.
- **Acceptance:** Reload page → sliders retain previous values; audio resumes at those levels.

---

## P1 — Core Feature Enhancements

### B-05: Session history view
- **Estimate:** M
- **Description:** Replace the single `completed_sessions` counter with a session log: date, focus duration, break duration, tasks completed count. Display as a small table in the timer panel.
- **Acceptance:** Each completed focus session appends a row; the table shows the last 10–20 sessions.

### B-06: Task completion rate per session
- **Estimate:** S
- **Description:** When the timer completes a focus session, snapshot how many tasks were marked done during that session. Show "3/5 tasks completed" in the stats block.
- **Acceptance:** Stats update automatically when timer finishes; no manual refresh needed.

### B-07: Audio track presets
- **Estimate:** M
- **Description:** Let users save a named mix (e.g. "Deep Focus": Flowers 40%, Daydreams 20%, Purple Dream 10%) and recall it with one click. Store in `localStorage`.
- **Acceptance:** User can save/load/delete up to 5 presets.

### B-08: Visual scene selector
- **Estimate:** L
- **Description:** Add 2 more canvas scenes (e.g. floating clouds/particles, gentle waves). User picks from a small icon grid in the header.
- **Acceptance:** Scene transitions are smooth; each scene respects the day/night palette.

---

## P2 — Quality of Life

### B-09: Ambient notification sounds
- **Estimate:** S
- **Description:** Replace the oscillator chime with a softer, pre-generated bell/chime WAV (synthesized or imported). Add option to toggle sound on/off.
- **Acceptance:** Chime is pleasant at moderate volume; mute toggle works.

### B-10: Break mode auto-start
- **Estimate:** XS
- **Description:** When focus session ends, break timer starts automatically after a 5-second countdown. User can cancel.
- **Acceptance:** Behavior is toggleable via a checkbox in the timer panel.

### B-11: Responsive mobile layout
- **Estimate:** M
- **Description:** Optimize panels for narrow screens: collapsible sections, larger touch targets for sliders, bottom-fixed controls.
- **Acceptance:** App is usable on a 375px-wide viewport without horizontal scroll.

### B-12: PWA offline support
- **Estimate:** L
- **Description:** Add `manifest.json` and service worker so the app can be installed on mobile/desktop and run fully offline (audio + scene + timer + tasks).
- **Acceptance:** Chrome/Edge "Add to Home screen" works; all features work without network after first load.

---

## P3 — Nice-to-Haves / Research

### B-13: User accounts (optional)
- **Estimate:** XL
- **Description:** Django auth + per-user tasks and session history synced to the database instead of `localStorage`.
- **Acceptance:** Login/logout; tasks and history are isolated per user.

### B-14: Streaks and weekly stats
- **Estimate:** L
- **Description:** Calendar heatmap (GitHub-style) of focus sessions; current streak counter; weekly average.
- **Acceptance:** Stats are calculated from session history; streaks update correctly after a missed day.

### B-15: Custom audio upload
- **Estimate:** M
- **Description:** Let users upload their own MP3/WAV files as tracks. Store in user media library (localStorage as base64 or server-side if accounts exist).
- **Acceptance:** Uploaded files appear in the mixer and persist across reloads.

### B-16: Integration with study tools
- **Estimate:** XL
- **Description:** Optional integrations: Google Calendar (pre-fill tasks from calendar), Notion API (push completed tasks), Pomodone-style sync.
- **Acceptance:** One integration shipped end-to-end with clear setup instructions.

---

## Technical Debt

### T-01: Add type hints and mypy
- **Estimate:** M
- **Description:** Add type annotations to `views.py`, `models.py`, and JS modules. Run mypy in CI.
- **Acceptance:** `mypy` passes with no errors.

### T-02: Frontend test coverage
- **Estimate:** L
- **Description:** Write Playwright or Cypress tests for: timer start/pause/reset, task add/toggle/delete, audio slider play/pause, palette toggle.
- **Acceptance:** All critical user flows covered; tests pass in CI.

### T-03: Django test coverage
- **Estimate:** M
- **Description:** Write pytest tests for views (`add_task`, `toggle_task`, `delete_task`, `session_complete`) and models.
- **Acceptance:** Coverage > 80% for `core/views.py` and `core/models.py`.

### T-04: Replace oscillator chime with asset
- **Estimate:** S
- **Description:** The current chime is generated with Web Audio API. Replace with a short, pleasant WAV/OGG file for more consistent cross-browser behavior.
- **Acceptance:** Chime sounds identical in Chrome, Firefox, Safari.

---

## Icebox (no timeline)

- Multi-language support (i18n)
- Dark/light system preference auto-detection
- Shareable "focus room" links (WebRTC audio sync)
- Widgets / desktop widget for timer
- Export session data as CSV/JSON
