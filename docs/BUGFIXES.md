# Bug Fixes — Round 1

Identified during initial user testing on 2026-09-07.

## Bug 1: Timer resets when adding a task

**Severity:** High
**Reported:** 2026-09-07

### Symptoms
- User starts the focus timer (e.g. `25:00` counting down).
- User adds a task in the "Session Tasks" panel.
- Page reloads and the timer returns to `25:00`, losing all elapsed time and the running state.

### Root Cause
Adding a task was implemented as a standard HTML form `POST` to Django, which returns a `302` redirect to `index`. The browser performs a full page reload. Since the timer state lives only in a JavaScript closure inside `timer.js`, that closure is destroyed on reload and the timer resets.

### Fix
Converted task CRUD to a JSON API consumed via `fetch()`:

- `core/views.py` — `add_task`, `toggle_task`, `delete_task` now return `JsonResponse` instead of `redirect`.
- `core/templates/core/index.html` — task list uses `<button data-action="...">` instead of per-row forms.
- `core/static/core/js/tasks.js` — new module handling add/toggle/delete via `fetch`, with CSRF token and DOM updates. No page reload.
- Task IDs are passed as `data-id` attributes; the empty-state placeholder (`#task-empty`) is added/removed dynamically.

The timer module (and audio mixer) now persist across task interactions.

---

## Bug 2: No audio playback

**Severity:** High
**Reported:** 2026-09-07

### Symptoms
- User drags an ambient track slider.
- No sound plays. Status text shows `Could not load ...` or stays silent.

### Root Cause
`core/static/core/js/audio.js` referenced hardcoded Pixabay CDN URLs that were guessed and did not resolve or were blocked by CORS. There was also no fallback path.

### Fix
Replaced external streams with **locally processed loops** from desktop MP3s:

- New script: `scripts/import_desktop_audio.py` imports 3 desktop MP3s:
  - `Colorful-Flowers(chosic.com).mp3` → `rain.wav`
  - `Daydreams-chosic.com_.mp3` → `lofi.wav`
  - `Ghostrifter-Official-Purple-Dream(chosic.com).mp3` → `cafe.wav`
- Each MP3 is converted to mono WAV at 22,050 Hz, then a 16-second middle section is extracted and crossfaded (2s head/tail) for seamless browser `loop` playback.
- Files saved to `core/static/core/audio/` and served directly by Django — no CORS, no network dependency at runtime.
- `core/templates/core/index.html` `<audio>` tags point to the local files.
- `core/static/core/js/audio.js` rewritten — `src` is in the markup, and `play()` errors are caught and reported via status text.
- Fallback generator: `scripts/generate_audio.py` still exists if pure synthesized CC0 audio is preferred, but is no longer the primary source.

---

## Bug 3: UI alignment and polish

**Severity:** Medium
**Reported:** 2026-09-07

### Symptoms
- Panels stacked in a single column with uneven spacing.
- Header typography felt heavy; section labels inconsistent.
- Audio track rows were cramped and the labels were hard to scan.
- Timer controls and inputs were visually unbalanced.
- No visual separation between completed-session count and the timer.

### Fix
- `core/static/core/css/ui.css` rewritten from scratch:
  - Two-column responsive grid: timer + audio on top, tasks full-width below; collapses to single column under 640px.
  - Consistent `--radius: 16px`, `--gap: 14px`, `--shadow` tokens.
  - Backdrop-blur panels with a soft radial overlay for depth.
  - Panel headers now include a small "badge" on the right (`Focus`, `5 tracks`, task count) for visual rhythm.
  - Audio tracks laid out as a 120px label column + range input with consistent dot indicator.
  - Timer display bumped to `4rem`, thin weight, tabular numerals, centered.
  - Buttons use a unified `.btn` system (`.primary`, `.ghost`, `.small`).
  - Stat block (`completed sessions`) moved into its own bordered section under the timer.
- `core/static/core/css/scene.css` slimmed to just canvas positioning.
- `core/templates/core/index.html` restructured to match the new layout, with semantic classes per panel.

---

## Files Changed

| File | Change |
| --- | --- |
| `core/views.py` | Task views return JSON; task list passes serialized list to template |
| `core/urls.py` | (unchanged — same endpoints, new return types) |
| `core/templates/core/index.html` | New layout, JSON-driven task list, local audio `src` |
| `core/static/core/css/scene.css` | Slimmed to canvas-only |
| `core/static/core/css/ui.css` | Full rewrite — grid layout, tokens, components |
| `core/static/core/js/audio.js` | Local audio paths, no external streams |
| `core/static/core/js/timer.js` | Badge updates, palette icon swap, CSRF on session-complete |
| `core/static/core/js/tasks.js` | New — fetch-based add/toggle/delete |
| `scripts/generate_audio.py` | Exists as fallback — pure synthesized CC0 audio, but desktop MP3s are primary |
| `scripts/import_desktop_audio.py` | New — imports 3 desktop MP3s, trims + crossfades into loopable WAVs |
| `core/static/core/audio/*.wav` | Now sourced from desktop MP3s (rain, lofi, cafe) |
| `requirements.txt` | New — `numpy`, `scipy` for audio processing |

---

## Verification

To verify in browser:

1. Start the timer, let it count down for 5–10 seconds.
2. Add a task — timer should **not** reset.
3. Drag any audio slider — sound should play, multiple tracks layer.
4. Toggle / delete tasks — no reload, count badge updates.
5. Click the day/night icon — palette + icon swap, scene particles adjust color.
6. Resize the window below 640px wide — panels stack to one column.