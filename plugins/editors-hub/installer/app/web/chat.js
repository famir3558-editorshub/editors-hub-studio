// Chat on the computer: the owner's chats with friends, the same ones as on the phone app (through the online service)
const CHAT = { home: null, conv: null, service: "", timer: null, typedAt: 0 };
const chatApi = (op, body = {}) => api("POST", `/api/chat/${op}`, body);
const chatInitial = (s) => esc(String(s || "?").trim().slice(0, 1).toUpperCase());
const chatMedia = (u) => (u && u.startsWith("/") ? CHAT.service + u : u);
const chatTime = (ts) => new Date(ts * 1000).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
const chatAgo = (ts) => { const s = Date.now() / 1000 - ts; return s < 60 ? "now" : s < 3600 ? `${Math.floor(s / 60)}m` : s < 86400 ? `${Math.floor(s / 3600)}h` : new Date(ts * 1000).toLocaleDateString([], { month: "short", day: "numeric" }); };
const chatDay = (ts) => { const d = new Date(ts * 1000), t = new Date(), y = new Date(); y.setDate(t.getDate() - 1); return d.toDateString() === t.toDateString() ? "Today" : d.toDateString() === y.toDateString() ? "Yesterday" : d.toLocaleDateString([], { weekday: "long", month: "short", day: "numeric" }); };
const CHAT_EMOJI = ["👍", "❤️", "😂", "🔥", "😮", "🙏"];

async function chatLoadHome() {
  try {
    const r = await chatApi("home");
    CHAT.home = r; CHAT.service = r.service || CHAT.service;
    const n = r.friends.reduce((a, f) => a + (f.unread || 0), 0) + r.incoming.length;
    if ($("chatCount")) $("chatCount").textContent = n ? String(n) : "";
  } catch (e) { CHAT.err = e.message; }
}

function openChat() {
  chatLoadHome().then(drawChatList);
  clearInterval(CHAT.timer);
  CHAT.timer = setInterval(() => { if (S.tab !== "chat" || document.hidden) return; if (CHAT.conv) chatPoll(); else chatLoadHome().then(drawChatList); }, 4000);
}

function drawChatList() {
  const c = CHAT.home, box = $("chatList");
  if (!box) return;
  if (!c) { box.innerHTML = `<p class="muted">${esc(CHAT.err || "Loading…")}</p>`; return; }
  const row = (p, sub, extra = "", attr = "") => `<div class="chat-fr${CHAT.conv && CHAT.conv.pid === p.pid ? " on" : ""}" ${attr}><span class="chat-av">${chatInitial(p.username)}</span><span class="chat-tx"><b>${esc(p.username)}</b><small>${esc(sub)}</small></span>${extra}</div>`;
  let h = `<div class="row"><h3 style="margin:0">Chats</h3><div class="spacer"></div><button class="btn small primary" id="chatAdd">+ Add friend</button></div>`;
  if (c.incoming.length) h += `<p class="chat-sec">Friend requests</p>` + c.incoming.map((r) => row(r, "wants to be your friend", `<button class="btn small primary" data-cacc="${esc(r.pid)}">Accept</button><button class="btn small" data-cdec="${esc(r.pid)}">✕</button>`)).join("");
  h += `<p class="chat-sec">Friends</p>` + (c.friends.length ? c.friends.map((f) => {
    const l = f.last, pre = !l ? "Say hello 👋" : l.kind === "call" ? l.body : (l.mine ? "You: " : "") + (l.kind === "photo" ? "📷 Photo" : l.kind === "voice" ? "🎤 Voice note" : l.kind === "video" ? `🎬 ${l.body}` : l.body);
    return row(f, pre, `${l ? `<span class="faint chat-when">${chatAgo(l.at)}</span>` : ""}${f.unread ? `<span class="chat-un">${f.unread}</span>` : ""}`, `data-cconv="${esc(f.pid)}" role="button" tabindex="0"`);
  }).join("") : `<p class="muted">No friends yet: add one by their username or friend code.</p>`);
  if (c.outgoing.length) h += `<p class="chat-sec">Waiting for them</p>` + c.outgoing.map((r) => row(r, "Request sent", `<button class="btn small" data-ccan="${esc(r.pid)}">Cancel</button>`)).join("");
  if (c.blocked.length) h += `<p class="chat-sec">Blocked</p>` + c.blocked.map((r) => row(r, "Can't message you", `<button class="btn small" data-cunb="${esc(r.pid)}">Unblock</button>`)).join("");
  h += `<div class="chat-code"><small class="muted">Your friend code</small><b>${esc(c.me.code)}</b><small class="muted">or your username: <b>${esc(c.me.username)}</b></small><button class="btn small" id="chatCopy">Copy</button></div>`;
  box.innerHTML = h;
  $("chatAdd").onclick = chatAddFriend;
  $("chatCopy").onclick = async () => { try { await navigator.clipboard.writeText(`Add me on Editors.Hub: my friend code is ${c.me.code} (username ${c.me.username})`); toast("Copied"); } catch (e) { toast(c.me.code); } };
}

async function chatAddFriend() {
  const to = await ehPrompt("Their Editors.Hub username, or the friend code they gave you (like EH-7K2P9Q). They need the phone app too.", "", { title: "Add a friend", ok: "Send request" });
  if (!to || !to.trim()) return;
  try {
    const r = await chatApi("request", { to: to.trim() });
    toast(r.friends ? `You and ${r.username} are friends now` : `Request sent to ${r.username}`);
    await chatLoadHome(); drawChatList();
  } catch (e) { toast(e.message, true); }
}

async function chatOpen(pid) {
  CHAT.conv = { pid, messages: [], seen: 0, reactions: {}, loading: true };
  drawChatList(); drawChatConv();
  try { Object.assign(CHAT.conv, await chatApi("messages", { pid }), { loading: false }); }
  catch (e) { toast(e.message, true); CHAT.conv = null; }
  drawChatConv(true);
  chatLoadHome().then(drawChatList);
}

async function chatPoll(force) {
  const c = CHAT.conv; if (!c || c.loading) return;
  const after = c.messages.length ? c.messages[c.messages.length - 1].id : 0;
  try {
    const r = await chatApi("messages", { pid: c.pid, after });
    if (CHAT.conv !== c) return;
    const rkey = JSON.stringify(r.reactions || {});
    const changed = force || r.messages.length || r.seen !== c.seen || rkey !== c.rkey || r.typing !== c.typing;
    c.messages.push(...r.messages.filter((m) => !c.messages.some((x) => x.id === m.id))); c.seen = r.seen;
    for (const k of Object.keys(c.reactions || {})) if (+k >= r.reactFrom) delete c.reactions[k];
    c.reactions = { ...(c.reactions || {}), ...(r.reactions || {}) }; c.rkey = rkey; c.typing = r.typing;
    if (changed) drawChatMsgs(r.messages.length > 0);
  } catch (e) { /* tries again in a moment */ }
}

function chatBubble(m) {
  const cls = `chat-bub ${m.mine ? "me" : "them"}`, mid = `data-cmsg="${m.id}"`;
  if (m.call) return `<div class="chat-day">📞 ${m.call.state === "ended" ? `Voice call · ${Math.floor(m.call.secs / 60)}:${String(m.call.secs % 60).padStart(2, "0")}` : m.call.state === "declined" ? "Call declined" : "Missed call"} · ${chatTime(m.at)}</div>`;
  if (m.voice) return `<div class="${cls} voice" ${mid}>🎤 <audio controls preload="none" src="${esc(chatMedia(m.voice))}"></audio></div>`;
  if (m.photo) return `<div class="${cls} ph" ${mid}><a href="${esc(chatMedia(m.photo))}" target="_blank" rel="noopener"><img src="${esc(chatMedia(m.photo))}" alt="Photo" loading="lazy"></a></div>`;
  if (m.video) return `<a class="${cls} vid" ${mid} href="${esc(m.video.url)}" target="_blank" rel="noopener"><span class="chat-pl">▶</span><span><b>${esc(m.video.name)}</b><small>${esc(m.video.client ? m.video.client + " · " : "")}Open the review link</small></span></a>`;
  return `<div class="${cls}" ${mid}>${esc(m.text)}</div>`;
}

function drawChatMsgs(toEnd) {
  const c = CHAT.conv, box = $("chatMsgs");
  if (!c || !box) return;
  const near = box.scrollHeight - box.scrollTop - box.clientHeight < 140;
  let day = "", h = "";
  const lastMine = [...c.messages].reverse().find((m) => m.mine);
  for (const m of c.messages) {
    const d = chatDay(m.at); if (d !== day) { h += `<div class="chat-day">${d}</div>`; day = d; }
    h += chatBubble(m);
    const rs = (c.reactions || {})[m.id];
    if (rs && rs.length) {
      const by = {}; for (const r of rs) { by[r.emoji] = by[r.emoji] || { n: 0, mine: false }; by[r.emoji].n++; if (r.mine) by[r.emoji].mine = true; }
      h += `<div class="chat-rx ${m.mine ? "me" : "them"}">${Object.entries(by).map(([e, x]) => `<span class="${x.mine ? "mine" : ""}">${e}${x.n > 1 ? " " + x.n : ""}</span>`).join("")}</div>`;
    }
    if (m === lastMine) h += `<div class="chat-meta">${chatTime(m.at)} · ${c.seen >= m.id ? "Seen" : "Sent"}</div>`;
  }
  if (!c.messages.length && !c.loading) h = `<p class="muted" style="text-align:center;margin:auto">Say hello 👋</p>`;
  box.innerHTML = h;
  if ($("chatTyping")) $("chatTyping").hidden = !c.typing;
  if (toEnd || near) box.scrollTop = box.scrollHeight;
}

function drawChatConv(toEnd) {
  const pane = $("chatConv"), c = CHAT.conv;
  if (!pane) return;
  if (!c) { pane.innerHTML = `<div class="chat-empty"><p class="muted">Pick a chat, or add a friend.<br>The same chats are on your phone app.</p></div>`; return; }
  const f = (CHAT.home && CHAT.home.friends.find((x) => x.pid === c.pid)) || c.with || {};
  pane.innerHTML = `<div class="chat-head"><span class="chat-av">${chatInitial(f.username)}</span><span style="flex:1"><b>${esc(f.username || "")}</b><br><small class="chat-typing" id="chatTyping" hidden>typing…</small></span>
      <button class="btn small primary" id="chatCall" title="Voice call">📞 Call</button><button class="btn small" id="chatRemove">Remove friend</button><button class="btn small danger" id="chatBlock">Block</button></div>
    <div class="chat-msgs" id="chatMsgs"></div>
    <div class="chat-compose"><button class="btn small" id="chatPhoto" title="Send a photo">📷</button><button class="btn small" id="chatVoice" title="Record a voice note">🎤</button>
      <textarea id="chatText" rows="1" maxlength="4000" placeholder="Message (Enter to send, Shift+Enter for a new line)"></textarea><button class="btn primary" id="chatSend">Send</button>
      <input type="file" id="chatPhotoPick" accept="image/*" hidden></div>`;
  drawChatMsgs(true);
  const ta = $("chatText");
  const send = async () => {
    const text = ta.value.trim(); if (!text) return;
    ta.value = "";
    try { await chatApi("send", { pid: c.pid, text }); await chatPoll(true); } catch (e) { ta.value = text; toast(e.message, true); }
  };
  $("chatSend").onclick = send;
  ta.onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };
  ta.oninput = () => { if (ta.value.trim() && Date.now() - CHAT.typedAt > 3000) { CHAT.typedAt = Date.now(); chatApi("typing", { pid: c.pid }).catch(() => {}); } };
  ta.focus();
  $("chatPhoto").onclick = () => $("chatPhotoPick").click();
  $("chatPhotoPick").onchange = async (e) => {
    const file = e.target.files && e.target.files[0]; e.target.value = "";
    if (!file) return;
    toast("Sending photo…");
    try { await chatApi("send", { pid: c.pid, photo: await chatShrink(file) }); await chatPoll(true); } catch (x) { toast(x.message, true); }
  };
  $("chatVoice").onclick = () => chatRecord(c);
  const act = (what, label) => async () => {
    if (!(await ehConfirm(`${label} ${f.username}?`, { title: label, ok: label, danger: what === "block" }))) return;
    try { await chatApi(what, { pid: c.pid }); CHAT.conv = null; await chatLoadHome(); drawChatList(); drawChatConv(); toast(what === "block" ? "Blocked" : "Removed"); } catch (e) { toast(e.message, true); }
  };
  $("chatRemove").onclick = act("unfriend", "Remove");
  $("chatCall").onclick = () => window.EHCall && EHCall.start(c.pid, f.username);
  $("chatBlock").onclick = act("block", "Block");
}

async function chatShrink(file) {
  const img = await createImageBitmap(file);
  const k = Math.min(1, 1600 / Math.max(img.width, img.height));
  const cv = document.createElement("canvas"); cv.width = Math.round(img.width * k); cv.height = Math.round(img.height * k);
  cv.getContext("2d").drawImage(img, 0, 0, cv.width, cv.height);
  let q = 0.82, url = cv.toDataURL("image/jpeg", q);
  while (url.length > 1900000 && q > 0.4) { q -= 0.12; url = cv.toDataURL("image/jpeg", q); }
  return url;
}

async function chatRecord(c) {
  const btn = $("chatVoice");
  if (CHAT.rec) { CHAT.rec.stop(); return; }
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); } catch (e) { return toast("Allow the microphone to send voice notes", true); }
  const type = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg"].find((x) => MediaRecorder.isTypeSupported(x)) || "";
  const rec = new MediaRecorder(stream, type ? { mimeType: type } : undefined), parts = [], started = Date.now();
  CHAT.rec = rec;
  rec.ondataavailable = (e) => { if (e.data && e.data.size) parts.push(e.data); };
  const tick = setInterval(() => { const s = Math.floor((Date.now() - started) / 1000); btn.textContent = `■ ${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; if (s >= 180) rec.stop(); }, 250);
  rec.onstop = async () => {
    clearInterval(tick); CHAT.rec = null; btn.textContent = "🎤"; stream.getTracks().forEach((x) => x.stop());
    if (!parts.length) return;
    const blob = new Blob(parts, { type: rec.mimeType || type || "audio/webm" });
    const url = await new Promise((ok) => { const fr = new FileReader(); fr.onload = () => ok(fr.result); fr.readAsDataURL(blob); });
    try { await chatApi("send", { pid: c.pid, voice: url, secs: Math.round((Date.now() - started) / 1000) }); await chatPoll(true); } catch (x) { toast(x.message, true); }
  };
  rec.start(1000);
  toast("Recording: press ■ to send");
}

async function chatReact(id) {
  const c = CHAT.conv; if (!c) return;
  const mine = ((c.reactions || {})[id] || []).find((r) => r.mine);
  const old = document.querySelector(".chat-picker"); if (old) old.remove();
  const at = document.querySelector(`[data-cmsg="${id}"]`); if (!at) return;
  const p = document.createElement("div");
  p.className = "chat-picker";
  p.innerHTML = CHAT_EMOJI.map((e) => `<button class="${mine && mine.emoji === e ? "on" : ""}" data-cemo="${e}">${e}</button>`).join("") + (mine ? `<button data-cemo="" title="Remove">✕</button>` : "");
  at.after(p);
  p.onclick = async (e) => {
    const b = e.target.closest("[data-cemo]"); if (!b) return;
    p.remove();
    try { await chatApi("react", { pid: c.pid, id, emoji: b.dataset.cemo }); c.reactFrom = 0; await chatPoll(true); } catch (x) { toast(x.message, true); }
  };
}

document.addEventListener("click", (e) => {
  if (!$("tab-chat") || $("tab-chat").hidden) return;
  const t = e.target;
  const conv = t.closest("[data-cconv]");
  if (conv && !t.closest("button")) return chatOpen(conv.dataset.cconv);
  const pick = (attr, op, extra = {}) => { const b = t.closest(`[${attr}]`); if (!b) return false; chatApi(op, { pid: b.getAttribute(attr), ...extra }).then(async (r) => { if (op === "answer" && r.friends) toast("Friends now: say hello"); await chatLoadHome(); drawChatList(); }).catch((x) => toast(x.message, true)); return true; };
  if (pick("data-cacc", "answer", { accept: true }) || pick("data-cdec", "answer", { accept: false }) || pick("data-ccan", "cancel") || pick("data-cunb", "unblock")) return;
  const msg = t.closest("[data-cmsg]");
  if (msg && !t.closest("audio") && !t.closest("a")) chatReact(+msg.dataset.cmsg);
  else if (!t.closest(".chat-picker")) { const old = document.querySelector(".chat-picker"); if (old) old.remove(); }
});

// calls: the owner can ring and be rung here too, while Home is open and showing (looked for every 8 seconds)
setTimeout(() => { if (S.state?.me?.role === "owner" && window.EHCall) EHCall.setup({ api: chatApi, every: 8000, onEnd: () => { if (CHAT.conv) chatPoll(true); } }); }, 2500);

// the tab's count, now and then, while Home is open (the owner only)
setTimeout(() => { if (S.state?.me?.role === "owner") chatLoadHome(); }, 3000);
setInterval(() => { if (S.state?.me?.role === "owner" && !document.hidden && S.tab !== "chat") chatLoadHome(); }, 60000);
