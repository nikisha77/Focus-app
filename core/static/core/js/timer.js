// Pomodoro timer + day/night palette toggle + localStorage persistence.
(function () {
  const STORAGE_KEY = "focusflow_timer";

  let mode = "focus";
  let remaining = 25 * 60;
  let intervalId = null;
  let running = false;
  let startTime = null;

  const display = document.getElementById("timer-display");
  const modeBadge = document.getElementById("timer-mode-badge");
  const startBtn = document.getElementById("timer-start");
  const resetBtn = document.getElementById("timer-reset");
  const focusInput = document.getElementById("focus-min");
  const breakInput = document.getElementById("break-min");
  const sessionCountEl = document.getElementById("session-count");
  const paletteBtn = document.getElementById("palette-toggle");
  const paletteIcon = paletteBtn ? paletteBtn.querySelector(".palette-icon") : null;

  function getCsrf() {
    const m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? m[1] : "";
  }

  function fmt(secs) {
    const m = Math.floor(secs / 60).toString().padStart(2, "0");
    const s = (secs % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  }

  function serialize() {
    return JSON.stringify({
      mode,
      remaining,
      running,
      startTime,
      focusMin: focusInput.value,
      breakMin: breakInput.value,
    });
  }

  function save() {
    try {
      localStorage.setItem(STORAGE_KEY, serialize());
    } catch (e) {}
  }

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return;
      const data = JSON.parse(raw);
      if (!data || typeof data !== "object") return;

      mode = data.mode === "break" ? "break" : "focus";
      remaining = Number(data.remaining) || (Number(data.focusMin) || 25) * 60;
      running = Boolean(data.running);
      startTime = Number(data.startTime) || null;

      if (data.focusMin) focusInput.value = data.focusMin;
      if (data.breakMin) breakInput.value = data.breakMin;

      if (running && startTime) {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        remaining = Math.max(0, remaining - elapsed);
        if (remaining <= 0) {
          onComplete(false);
          return;
        }
        start();
      }
    } catch (e) {}
  }

  function clear() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch (e) {}
  }

  function render() {
    display.textContent = fmt(remaining);
    if (modeBadge) {
      modeBadge.textContent = mode === "focus" ? "Focus" : "Break";
    }
    startBtn.textContent = running ? "Pause" : "Start";
  }

  function tick() {
    remaining -= 1;
    if (remaining <= 0) {
      onComplete(true);
      return;
    }
    save();
    render();
  }

  function onComplete(notify) {
    clearInterval(intervalId);
    running = false;
    startTime = null;
    chime();
    if (mode === "focus") {
      if (notify) notifyServer();
      mode = "break";
      remaining = Number(breakInput.value) * 60;
    } else {
      mode = "focus";
      remaining = Number(focusInput.value) * 60;
    }
    save();
    render();
  }

  function chime() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.frequency.value = 660;
      o.connect(g);
      g.connect(ctx.destination);
      g.gain.setValueAtTime(0.0001, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.3, ctx.currentTime + 0.05);
      g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 1.2);
      o.start();
      o.stop(ctx.currentTime + 1.3);
    } catch (e) {}
  }

  function notifyServer() {
    fetch("/session/complete/", {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "X-CSRFToken": getCsrf(),
        "X-Requested-With": "XMLHttpRequest",
      },
    })
      .then((r) => r.json())
      .then((d) => {
        if (d.completed_sessions != null) sessionCountEl.textContent = d.completed_sessions;
      })
      .catch(() => {});
  }

  function start() {
    if (running) return;
    if (remaining <= 0) reset();
    intervalId = setInterval(tick, 1000);
    running = true;
    startTime = Date.now();
    save();
    render();
  }

  function pause() {
    clearInterval(intervalId);
    running = false;
    startTime = null;
    save();
    render();
  }

  function reset() {
    clearInterval(intervalId);
    running = false;
    startTime = null;
    mode = "focus";
    remaining = Number(focusInput.value) * 60;
    clear();
    render();
  }

  function togglePalette() {
    const isDay = document.body.classList.toggle("palette-day");
    document.body.classList.toggle("palette-night", !isDay);
    if (paletteIcon) paletteIcon.textContent = isDay ? "☀" : "☾";
  }

  startBtn.addEventListener("click", () => (running ? pause() : start()));
  resetBtn.addEventListener("click", reset);
  paletteBtn.addEventListener("click", togglePalette);

  focusInput.addEventListener("change", () => {
    if (mode === "focus" && !running) {
      remaining = Number(focusInput.value) * 60;
      save();
    }
    render();
  });
  breakInput.addEventListener("change", () => {
    if (mode === "break" && !running) {
      remaining = Number(breakInput.value) * 60;
      save();
    }
    render();
  });

  load();
  render();
})();