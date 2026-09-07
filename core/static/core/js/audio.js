// Ambient mixer: per-track volume sliders, layered playback from local tracks.
(function () {
  const audios = {};
  const status = document.getElementById("audio-status");

  function setStatus(msg) {
    if (status) status.textContent = msg;
  }

  function init() {
    document.querySelectorAll("audio[id^='audio-']").forEach((el) => {
      const name = el.id.replace("audio-", "");
      audios[name] = el;
      el.volume = 0;
    });

    document.querySelectorAll("input[data-track]").forEach((slider) => {
      slider.addEventListener("input", onSlider);
    });

    document.getElementById("audio-stop").addEventListener("click", stopAll);
  }

  function onSlider(e) {
    const slider = e.target;
    const name = slider.dataset.track;
    const audio = audios[name];
    if (!audio) return;
    const value = Number(slider.value);
    audio.volume = value / 100;

    if (value > 0 && audio.paused) {
      const p = audio.play();
      if (p && p.then) {
        p.then(() => setStatus(`Now playing ${name}`))
         .catch((err) => setStatus(`Could not play ${name}: ${err.message}`));
      }
    } else if (value === 0 && !audio.paused) {
      audio.pause();
    }
  }

  function stopAll() {
    document.querySelectorAll("input[data-track]").forEach((s) => {
      s.value = 0;
    });
    Object.values(audios).forEach((a) => { a.pause(); a.currentTime = 0; });
    setStatus("Stopped.");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();