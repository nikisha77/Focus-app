// Animated scene: rain/motes particles + palette-aware colors
(function () {
  const canvas = document.getElementById("scene-canvas");
  const ctx = canvas.getContext("2d");

  let width = 0;
  let height = 0;
  let particles = [];
  const COUNT = 110;

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  function isNight() {
    return document.body.classList.contains("palette-night");
  }

  function spawn() {
    return {
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 1.6 + 0.4,
      vy: Math.random() * 0.6 + 0.3,
      vx: -0.2 + Math.random() * 0.4,
      alpha: Math.random() * 0.5 + 0.2,
    };
  }

  function init() {
    resize();
    particles = [];
    for (let i = 0; i < COUNT; i++) particles.push(spawn());
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);

    const night = isNight();
    const color = night ? "220, 230, 255" : "255, 240, 220";

    for (let p of particles) {
      p.x += p.vx;
      p.y += p.vy;

      if (p.y > height) { p.y = -2; p.x = Math.random() * width; }
      if (p.x < -2) p.x = width + 2;
      if (p.x > width + 2) p.x = -2;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${color}, ${p.alpha})`;
      ctx.fill();
    }

    requestAnimationFrame(draw);
  }

  window.addEventListener("resize", () => {
    resize();
    particles = [];
    for (let i = 0; i < COUNT; i++) particles.push(spawn());
  });

  init();
  draw();
})();