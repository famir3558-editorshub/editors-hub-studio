// Small sounds and the party popper: made in the page (no sound files). Off with localStorage "eh-sounds" = "off".
// Browsers only play sound after the page has been clicked or tapped once, so the first event on an untouched page is silent.
(function () {
  let ctx = null;
  const on = () => { try { return localStorage.getItem("eh-sounds") !== "off"; } catch (e) { return true; } };
  function ac() {
    if (!ctx) { const A = window.AudioContext || window.webkitAudioContext; if (!A) return null; ctx = new A(); }
    if (ctx.state === "suspended") ctx.resume().catch(() => {});
    return ctx;
  }
  // a sound the browser blocked (the page hasn't been clicked yet) plays on the first click, if that comes soon
  let pending = null;
  ["pointerdown", "keydown", "touchend"].forEach((ev) => window.addEventListener(ev, () => {
    if (!on()) return;
    const c = ac();
    if (pending && c) { const p = pending; pending = null; if (Date.now() - p.at < 10000) (c.state === "running" ? Promise.resolve() : c.resume()).then(() => { try { SOUNDS[p.name](); } catch (e) {} }).catch(() => {}); }
  }, { passive: true }));
  function tone(f, t0, dur, vol, type) {
    const c = ac(); if (!c) return;
    const o = c.createOscillator(), g = c.createGain(), t = c.currentTime + t0;
    o.type = type || "sine"; o.frequency.setValueAtTime(f, t);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.012); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g).connect(c.destination); o.start(t); o.stop(t + dur + 0.05);
  }
  function pop() {
    const c = ac(); if (!c) return;
    const n = c.createBufferSource(), b = c.createBuffer(1, Math.floor(c.sampleRate * 0.18), c.sampleRate), d = b.getChannelData(0);
    for (let i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / d.length, 3);
    n.buffer = b; const g = c.createGain(); g.gain.value = 0.12; const hp = c.createBiquadFilter(); hp.type = "highpass"; hp.frequency.value = 1800;
    n.connect(hp).connect(g).connect(c.destination); n.start();
  }
  const SOUNDS = {
    update() { tone(1318.5, 0, 0.12, 0.06); tone(1760, 0.05, 0.16, 0.04); },
    ask() { tone(659.3, 0, 0.28, 0.09); tone(987.8, 0.14, 0.36, 0.08); },
    draft() { pop(); [523.3, 659.3, 784, 1046.5].forEach((f, i) => tone(f, 0.12 + i * 0.085, 0.42, 0.07, "triangle")); },
    approved() { pop(); [392, 523.3, 659.3, 784].forEach((f, i) => tone(f, 0.1 + i * 0.1, 0.3, 0.07, "triangle")); [523.3, 659.3, 784, 1046.5].forEach((f) => tone(f, 0.55, 0.9, 0.05, "triangle")); },
  };
  let last = {};
  function play(name) {
    if (!on() || !SOUNDS[name]) return;
    const now = Date.now(); if (now - (last[name] || 0) < 700) return;  // a burst of the same event plays once
    last[name] = now;
    const c = ac();
    if (!c) return;
    if (c.state !== "running") { pending = { name, at: now }; c.resume().then(() => { if (c.state === "running" && pending && pending.name === name) { pending = null; try { SOUNDS[name](); } catch (e) {} } }).catch(() => {}); return; }
    try { SOUNDS[name](); } catch (e) {}
  }
  // the party popper: confetti from both bottom corners, with a card in the middle
  function confetti(text) {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const cv = document.createElement("canvas");
    cv.style.cssText = "position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;z-index:9999";
    document.body.appendChild(cv);
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    cv.width = innerWidth * dpr; cv.height = innerHeight * dpr;
    const x = cv.getContext("2d"), cols = ["#e5192b", "#ff5a66", "#fbf3f4", "#fcd34d", "#8a0b18", "#ffb3ba"];
    let parts = [];
    const count = innerWidth < 600 ? 60 : 90, k = dpr * Math.max(0.7, Math.min(1.4, innerHeight / 700));
    for (const side of [0, 1]) for (let i = 0; i < count; i++) parts.push({ x: side ? cv.width - 20 : 20, y: cv.height - 10,
      vx: (side ? -1 : 1) * (0.35 + Math.random() * 0.6) * (9 + Math.random() * 10) * k, vy: -(16 + Math.random() * 12) * k,
      r: (4 + Math.random() * 6) * dpr, c: cols[i % cols.length], s: Math.random() * 6, w: Math.random() * 0.3 + 0.1, life: 0 });
    let card = null;
    if (text) {
      card = document.createElement("div");
      card.textContent = text;
      card.style.cssText = "position:fixed;left:50%;top:42%;transform:translate(-50%,-50%) scale(.9);opacity:0;transition:all .35s cubic-bezier(.2,.7,.2,1);" +
        "background:rgba(20,12,14,.92);border:1px solid rgba(255,255,255,.16);border-radius:18px;padding:16px 22px;color:#fbf3f4;font:600 17px Sora,-apple-system,'Segoe UI',sans-serif;" +
        "box-shadow:0 18px 50px rgba(229,25,43,.35);z-index:10000;pointer-events:none;white-space:nowrap";
      document.body.appendChild(card);
      requestAnimationFrame(() => { card.style.opacity = "1"; card.style.transform = "translate(-50%,-50%) scale(1)"; });
      setTimeout(() => { card.style.opacity = "0"; card.style.transform = "translate(-50%,-50%) scale(.9)"; setTimeout(() => card.remove(), 400); }, 2400);
    }
    (function step() {
      x.clearRect(0, 0, cv.width, cv.height);
      for (const p of parts) {
        p.vy += 0.45 * k; p.vx *= 0.99; p.x += p.vx; p.y += p.vy; p.s += p.w; p.life++;
        x.save(); x.translate(p.x, p.y); x.rotate(p.s); x.fillStyle = p.c; x.globalAlpha = Math.max(0, 1 - p.life / 150); x.fillRect(-p.r / 2, -p.r / 4, p.r, p.r / 2); x.restore();
      }
      parts = parts.filter((p) => p.life < 150 && p.y < cv.height + 60);
      if (parts.length) requestAnimationFrame(step); else cv.remove();
    })();
  }
  window.EHFX = {
    play, confetti,
    celebrate(kind, text) {
      const now = Date.now(); if (now - (window.EHFX._party || 0) < 6000) return;  // the bell and the review page can both see the same draft
      window.EHFX._party = now; play(kind === "approved" ? "approved" : "draft"); confetti(text);
    },
    on, set(v) { try { localStorage.setItem("eh-sounds", v ? "on" : "off"); } catch (e) {} if (v) ac(); },
  };
})();
