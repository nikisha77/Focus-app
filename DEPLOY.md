# Deploying Focus Flow to GitHub Pages

GitHub Pages serves **static files only** — it cannot run Python/Django. So we
export the static site (HTML, CSS, JS, audio) and push it to a `gh-pages` branch.

## Option A — Static export (recommended for homework)

1. **Create a static export** of the app:
   ```bash
   .venv/bin/python manage.py collectstatic --noinput
   ```
   This copies all static files into `static/`. Your app is now just HTML + assets.

2. **Create a `gh-pages` branch**:
   ```bash
   git checkout -b gh-pages
   ```

3. **Commit only the static files**:
   ```bash
   git add static/
   git commit -m "Deploy static site"
   git push origin gh-pages
   ```

4. **Enable GitHub Pages**:
   - Go to your repo → Settings → Pages
   - Source: `gh-pages` branch, `/ (root)`
   - Save. Your app will be live at `https://<username>.github.io/<repo>/`

## Option B — Django on a cloud platform

For a full Django deployment (server-side, with database):

1. **Create a `Procfile`**:
   ```bash
   web: gunicorn studywithme.wsgi
   ```
2. **Add `runtime.txt`**:
   ```
   python-3.13
   ```
3. **Push to Heroku**:
   ```bash
   heroku create
   git push heroku main
   ```
4. **Or push to Render** — add `render.yaml`:
   ```yaml
   services:
     - type: web
       name: focus-flow
       env: python
       buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
       startCommand: gunicorn studywithme.wsgi
       envVars:
         - key: SECRET_KEY
           generate: true
   ```

## Notes

- Audio files are ~2 MB total — fine for Pages.
- The timer state uses `localStorage` — works client-side, no server needed.
- Task data uses Django models + SQLite — only works in Option B.