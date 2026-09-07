# Study With Me — Scope (Option B)

A browser-based focus app: ambient sound mixer + calming animated scene + Pomodoro timer + task checklist.

**Tech stack:** Django (templates) + HTML/CSS/vanilla JS + SQLite
**Timeline:** ~1 week

---

## Core Features

### 1. Animated Calming Scene
- Full-screen background scene built with CSS/canvas
- Particles (e.g. raindrops or floating motes) animated via `requestAnimationFrame` or CSS
- Subtle day/night palette toggle (warm vs cool gradient)
- Lightweight, no external assets

### 2. Ambient Sound Mixer
- 4–5 ambient streams, each on an independent audio element:
  - Rain
  - Lofi beat
  - Cafe ambience
  - White noise
  - Fireplace/crackling
- **Per-track volume slider** (0–100) — this is the "customization" requirement
- Master play/pause
- All tracks layer simultaneously (user mixes their own session)
- Streams sourced from free public audio URLs

### 3. Pomodoro Timer
- Configurable focus duration (default 25 min) and break duration (default 5 min)
- Start / pause / reset controls
- Audio chime on session end
- **Completed session count persisted to SQLite** (no full history view yet — just a count)

### 4. Task Checklist
- Add / check off / delete tasks for the current session
- Tasks saved to Django DB (one model: `Task` with `text`, `done`, `created_at`)
- New tasks each session; old ones archived but visible in a simple list

---

## Out of Scope (for this version)

- Multiple scene presets (just one good scene)
- User accounts / login
- Streak charts, statistics, history views
- Saving named "mix presets" the user can recall
- Mobile-specific layout (responsive but desktop-first)

---

## Data Model (SQLite)

```
Task
  - id (PK)
  - text (str)
  - done (bool)
  - created_at (datetime)

SessionStats
  - id (PK, singleton)
  - completed_sessions (int)
```

---

## Project Structure (planned)

```
studywithme/
  manage.py
  studywithme/        # Django project
    settings.py
    urls.py
  core/               # App: views, models, templates
    models.py
    views.py
    urls.py
    templates/
      base.html
      index.html
    static/
      css/scene.css
      js/scene.js
      js/audio.js
      js/timer.js
      js/tasks.js
```

---

## Milestones

1. Django project skeleton + index page renders scene
2. Animated scene working (particles + palette toggle)
3. Audio mixer with per-track volume sliders
4. Pomodoro timer with SQLite-backed session count
5. Task checklist with add/check/delete
6. Final polish: layout, keyboard shortcuts, demo data