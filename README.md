# Focus Flow

A browser-based focus app: ambient sound mixer + calming animated scene + Pomodoro timer + task checklist.

Built with Django templates, vanilla JS, CSS, and local audio loops.

## Features

- **Timer** — Pomodoro-style focus/break timer with configurable durations. State persists across page reloads via `localStorage`.
- **Sound Mixer** — 3 local audio tracks (Flowers, Daydreams, Purple Dream) with independent volume sliders. Mix your own session.
- **Scene** — Canvas particle animation with a day/night palette toggle.
- **Tasks** — Add, check off, and delete session tasks. No page reloads (JSON API).

## Tech

- Python 3.13, Django 6.1
- SQLite database
- numpy + scipy for audio processing
- Pure HTML/CSS/JS frontend

## Setup

```bash
cd "Desktop/week 1"
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Then open http://127.0.0.1:8000 in your browser.

## Project structure

```
.
├── docs/
│   ├── SCOPE.md        # Original scope brief
│   ├── BUGFIXES.md     # Bug reports and fixes
│   └── BACKLOG.md      # Product backlog
├── scripts/
│   ├── generate_audio.py          # Fallback: synthesize CC0 ambient loops
│   └── import_desktop_audio.py    # Import desktop MP3s as loopable WAVs
├── core/                          # Django app
│   ├── models.py                  # Task, SessionStats
│   ├── views.py                   # JSON endpoints for tasks + session count
│   ├── urls.py
│   ├── templates/core/index.html  # Main page
│   ├── static/core/css/           # scene.css, ui.css
│   ├── static/core/js/            # scene.js, audio.js, timer.js, tasks.js
│   └── static/core/audio/         # flowers.wav, daydreams.wav, purpledream.wav
└── studywithme/                   # Django project
```

## Testing

```bash
.venv/bin/python manage.py test
```

Tests cover the JSON endpoints (`add_task`, `toggle_task`, `delete_task`, `session_complete`) and the models. See `core/tests.py`.

