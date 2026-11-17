// Voice calls between friends, the same code on the phone app and the studio's Chat tab (served at /app/call.js; the
// studio keeps an identical copy as web/call.js). The voice goes straight between the two (WebRTC); the service only
// passes the connection messages (call-signal / call-poll) and rings the other side.
//   EHCall.setup({ api: (op, body) => Promise<json>, onEnd: () => {} })   then   EHCall.start(pid, name)
(function () {
  if (window.EHCall) return;
  const S = { api: null, onEnd: null, call: null, pc: null, stream: null, after: 0, poll: null, queue: [], offer: null, handled: new Set(), muted: false, tick: null, tone: null, lock: null };
  const style = document.createElement("style");
  style.textContent = `
#ehcall{position:fixed;inset:0;z-index:99;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:calc(env(safe-area-inset-top) + 60px) 24px calc(env(safe-area-inset-bottom) + 48px);
  background:radial-gradient(circle at 50% 30%,rgba(229,25,43,.45),rgba(8,4,5,.97) 62%);color:#fff;font-family:Sora,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px)}
#ehcall[hidden]{display:none}
#ehcall .who{display:flex;flex-direction:column;align-items:center;gap:14px;text-align:center}
#ehcall .av{width:112px;height:112px;border-radius:50%;display:grid;place-items:center;font-size:46px;font-weight:700;background:linear-gradient(135deg,#ff5a66,#e5192b 55%,#8a0b18);box-shadow:0 0 0 0 rgba(229,25,43,.6)}
#ehcall.ringing .av{animation:ehpulse 1.6s infinite}
@keyframes ehpulse{70%{box-shadow:0 0 0 26px rgba(229,25,43,0)}100%{box-shadow:0 0 0 0 rgba(229,25,43,0)}}
#ehcall h2{margin:0;font-size:28px;font-weight:600}
#ehcall .st{font-size:16px;opacity:.8;font-variant-numeric:tabular-nums}
#ehcall .row{display:flex;gap:28px;align-items:flex-end}
#ehcall button{width:72px;height:72px;border-radius:50%;border:0;font-size:28px;color:#fff;cursor:pointer;background:rgba(255,255,255,.14);display:grid;place-items:center}
#ehcall button small{display:block;font-size:12px;margin-top:6px;opacity:.85}
#ehcall .lab{display:flex;flex-direction:column;align-items:center;gap:8px;font-size:13px;opacity:.9}
#ehcall .end{background:#e5192b;box-shadow:0 10px 30px rgba(229,25,43,.55)}
#ehcall .ok{background:#22c55e;box-shadow:0 10px 30px rgba(34,197,94,.45)}
#ehcall .on{background:#fff;color:#111}
`;
  document.head.appendChild(style);
  const box = document.createElement("div");
  box.id = "ehcall"; box.hidden = true;
  const audio = document.createElement("audio");
  audio.autoplay = true; audio.setAttribute("playsinline", "");
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const ready = () => { if (!box.isConnected) { document.body.appendChild(box); document.body.appendChild(audio); } };
  const clock = (s) => Math.floor(s / 60) + ":" + String(Math.floor(s % 60)).padStart(2, "0");

  function draw(state, text) {
    ready();
    const c = S.call; if (!c) return;
    box.hidden = false;
    box.className = state === "incoming" || state === "outgoing" ? "ringing" : "";
    const btn = (cls, id, icon, label) => `<span class="lab"><button class="${cls}" id="${id}" aria-label="${label}">${icon}</button>${label}</span>`;
    const buttons = state === "incoming" ? btn("end", "ehDecline", "✕", "Decline") + btn("ok", "ehAnswer", "📞", "Answer")
      : state === "done" ? "" : btn(S.muted ? "on" : "", "ehMute", S.muted ? "🔇" : "🎙", S.muted ? "Unmute" : "Mute") + btn("end", "ehEnd", "✕", "End");
    box.innerHTML = `<div class="who"><div class="av">${esc((c.name || "?").trim().slice(0, 1).toUpperCase())}</div><h2>${esc(c.name)}</h2><div class="st" id="ehSt">${esc(text)}</div></div><div class="row">${buttons}</div>`;
    const on = (id, f) => { const b = document.getElementById(id); if (b) b.onclick = f; };
    on("ehAnswer", answer); on("ehDecline", () => hangup("Declined")); on("ehEnd", () => hangup("Call ended"));
    on("ehMute", () => { S.muted = !S.muted; if (S.stream) S.stream.getAudioTracks().forEach((t) => (t.enabled = !S.muted)); draw("active", document.getElementById("ehSt").textContent); });
  }
  function status(text) { const e = document.getElementById("ehSt"); if (e) e.textContent = text; }

  // a soft ring (incoming) or ring-back (outgoing), made in the browser; it may stay silent until the page has been touched
  function tone(kind) {
    stopTone();
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const beep = () => {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.frequency.value = kind === "in" ? 660 : 440; g.gain.value = 0;
        o.connect(g); g.connect(ctx.destination); o.start();
        const t = ctx.currentTime; g.gain.linearRampToValueAtTime(kind === "in" ? 0.25 : 0.08, t + 0.05); g.gain.linearRampToValueAtTime(0, t + (kind === "in" ? 0.9 : 1.4)); o.stop(t + 1.5);
      };
      beep();
      S.tone = { ctx, timer: setInterval(beep, kind === "in" ? 1600 : 3000) };
      if (kind === "in" && navigator.vibrate) navigator.vibrate([400, 300, 400]);
    } catch (e) { S.tone = null; }
  }
  function stopTone() { if (S.tone) { clearInterval(S.tone.timer); try { S.tone.ctx.close(); } catch (e) {} S.tone = null; } }

  async function mic() {
    S.stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
    S.stream.getAudioTracks().forEach((t) => (t.enabled = !S.muted));
    try { navigator.wakeLock.request("screen").then((l) => { if (S.stream) S.lock = l; else l.release(); }).catch(() => {}); } catch (e) {}  // keeps the screen on; never waited for
  }
  function connect(iceServers) {
    const pc = (S.pc = new RTCPeerConnection({ iceServers }));
    S.stream.getTracks().forEach((t) => pc.addTrack(t, S.stream));
    pc.onicecandidate = (e) => { if (e.candidate) signal("ice", e.candidate.toJSON()); };
    pc.ontrack = (e) => { audio.srcObject = e.streams[0]; audio.play().catch(() => {}); };
    pc.onconnectionstatechange = () => {
      if (pc.connectionState === "connected") live();
      if (pc.connectionState === "failed") hangup("Couldn't connect. Try again, or on Wi-Fi.");
    };
    return pc;
  }
  const signal = (kind, data) => S.api("call-signal", { call: S.call.id, kind, data }).catch(() => {});
  async function take(sig) {
    const pc = S.pc;
    if (sig.kind === "offer") { S.offer = sig.data; return; }
    if (!pc) { S.queue.push(sig); return; }
    if (sig.kind === "answer" && !pc.currentRemoteDescription) { await pc.setRemoteDescription(sig.data); for (const q of S.queue.splice(0)) await take(q); return; }
    if (sig.kind === "ice") { if (!pc.remoteDescription) S.queue.push(sig); else await pc.addIceCandidate(sig.data).catch(() => {}); }
  }
  function polling(every) {
    clearInterval(S.poll);
    S.poll = setInterval(async () => {
      const c = S.call; if (!c || !c.id || c.polling) return;
      c.polling = true;
      try {
        const r = await S.api("call-poll", { call: c.id, after: S.after });
        if (S.call !== c) return;
        for (const s of r.signals || []) { S.after = Math.max(S.after, s.id); await take(s); }
        if (["missed", "declined", "ended"].includes(r.state)) finish(r.state === "missed" ? (c.dir === "out" ? "No answer" : "Missed call") : r.state === "declined" ? "Declined" : "Call ended");
        else if (r.state === "active" && c.dir === "out" && !c.live) status("Connecting…");
      } catch (e) { if (/gone/i.test(e.message || "")) finish("Call ended"); }
      finally { c.polling = false; }
    }, every);
  }
  function live() {
    const c = S.call; if (!c || c.live) return;
    c.live = Date.now(); stopTone(); draw("active", "0:00");
    clearInterval(S.tick); S.tick = setInterval(() => status(clock((Date.now() - c.live) / 1000)), 1000);
    polling(2500);
  }

  async function start(pid, name) {
    if (S.call) return;
    S.call = { id: null, dir: "out", name, pid }; S.after = 0; S.queue = []; S.offer = null; S.muted = false;
    draw("outgoing", "Calling…");
    try { await mic(); } catch (e) { return finish("Allow the microphone to make calls"); }
    try {
      const r = await S.api("call-start", { pid });
      if (!S.call) return;
      S.call.id = r.call;
      tone("out");
      const pc = connect(r.iceServers);
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      await signal("offer", { type: offer.type, sdp: offer.sdp });
      status("Ringing…");
      polling(900);
    } catch (e) { finish(e.message || "The call couldn't start"); }
  }
  async function incoming(call) {
    if (S.call || S.handled.has(call.id)) return;
    S.call = { id: call.id, dir: "in", name: call.from.username, pid: call.from.pid }; S.after = 0; S.queue = []; S.offer = null; S.muted = false;
    draw("incoming", "Voice call");
    tone("in");
    polling(1200);  // gathers the caller's offer, and notices if they hang up
  }
  async function answer() {
    const c = S.call; if (!c) return;
    stopTone(); draw("active", "Connecting…");
    try { await mic(); } catch (e) { return hangup("Allow the microphone to answer calls"); }
    try {
      const a = await S.api("call-answer", { call: c.id });
      for (let i = 0; i < 20 && !S.offer && S.call === c; i++) {  // the offer usually came while it rang
        const r = await S.api("call-poll", { call: c.id, after: S.after });
        for (const s of r.signals || []) { S.after = Math.max(S.after, s.id); await take(s); }
        if (!S.offer) await new Promise((ok) => setTimeout(ok, 500));
      }
      if (!S.offer) return hangup("Couldn't connect");
      const pc = connect(a.iceServers);
      await pc.setRemoteDescription(S.offer);
      for (const q of S.queue.splice(0)) await take(q);
      const ans = await pc.createAnswer();
      await pc.setLocalDescription(ans);
      await signal("answer", { type: ans.type, sdp: ans.sdp });
      polling(900);
    } catch (e) { hangup(e.message || "Couldn't connect"); }
  }
  async function hangup(text) {
    const c = S.call;
    if (c && c.id) S.api("call-end", { call: c.id }).catch(() => {});
    finish(text);
  }
  function finish(text) {
    const c = S.call; if (!c) return;
    if (c.id) S.handled.add(c.id);
    clearInterval(S.poll); clearInterval(S.tick); stopTone();
    try { if (S.pc) S.pc.close(); } catch (e) {}
    if (S.stream) S.stream.getTracks().forEach((t) => t.stop());
    try { if (S.lock) S.lock.release(); } catch (e) {}
    S.pc = S.stream = S.lock = null; audio.srcObject = null;
    draw("done", (c.live ? clock((Date.now() - c.live) / 1000) + " · " : "") + text);
    S.call = null;
    setTimeout(() => { if (!S.call) box.hidden = true; }, 1800);
    if (S.onEnd) S.onEnd();
  }

  // a call ringing for this person: looked for every few seconds while the page is open (and at once when asked)
  async function checkRing() {
    if (!S.api || S.call || document.hidden) return;
    try { const r = await S.api("ring", {}); if (r.call) incoming(r.call); } catch (e) {}
  }
  window.EHCall = {
    setup(opts) { S.api = opts.api; S.onEnd = opts.onEnd || null; clearInterval(S.ringer); S.ringer = setInterval(checkRing, opts.every || 3000); checkRing(); },
    start, checkRing, busy: () => !!S.call,
  };
})();
