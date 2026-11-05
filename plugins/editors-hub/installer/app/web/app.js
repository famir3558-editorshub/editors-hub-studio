// Shared helpers for the Home and review pages.

async function api(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && data.signin) toSignIn();
  if (res.status === 401 && data.approve) location.href = "/approve";
  if (!res.ok) throw new Error(data.error || res.statusText);
  return data;
}

function upload(url, file, onProgress) {
  return new Promise((resolve, reject) => {
    const x = new XMLHttpRequest();
    x.open("PUT", url);
    x.upload.onprogress = (e) => e.lengthComputable && onProgress && onProgress(e.loaded / e.total);
    x.onload = () => {
      let data = {};
      try { data = JSON.parse(x.responseText || "{}"); } catch (e) {}
      if (x.status === 401 && data.signin) toSignIn();
      if (x.status === 401 && data.approve) location.href = "/approve";
      x.status < 300 ? resolve(data) : reject(new Error(data.error || x.statusText));
    };
    x.onerror = () => reject(new Error("upload failed"));
    x.send(file);
  });
}

function toSignIn() {
  location.href = "/signin?next=" + encodeURIComponent(location.pathname + location.hash);
}

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const enc = encodeURIComponent;
const previewAttr = (v) => v.preview ? ` data-preview="/media/${enc(v.id)}/${v.preview.split("/").map(enc).join("/")}"` : "";
const statusClass = (s) => "s-" + String(s).replace(/\s+/g, "-");

function fmtTime(t) {
  t = Math.max(0, t || 0);
  const m = Math.floor(t / 60), s = t - m * 60;
  return `${m}:${s.toFixed(1).padStart(4, "0")}`;
}

function fmtSize(n) {
  const u = ["B", "KB", "MB", "GB"];
  let i = 0;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(i ? 1 : 0)} ${u[i]}`;
}

function ago(iso) {
  if (!iso) return "";
  const s = (Date.now() - new Date(iso).getTime()) / 1000;
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.floor(s / 60)} min ago`;
  if (s < 86400) return `${Math.floor(s / 3600)} h ago`;
  if (s < 86400 * 7) return `${Math.floor(s / 86400)} d ago`;
  return new Date(iso).toLocaleDateString();
}

let toastTimer;
function toast(msg, bad) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = "show" + (bad ? " bad" : "");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (el.className = ""), bad ? 5000 : 2600);
}

const LOGO = `<span class="logo-mark"><svg viewBox="0 0 16 16" fill="#fff"><path d="M4 2.5v11l9-5.5z"/></svg></span><span>Editors<span class="dot">.</span><span class="hub">Hub</span></span>`;
document.querySelectorAll(".logo").forEach((el) => (el.innerHTML = LOGO));

// ---- Editors.Hub's own questions: the browser built into the Claude app answers confirm() with "Cancel" at once and
// has no prompt(), so asking happens in a pop-up of the page's own

function ehAsk({ title = "", message = "", ok = "OK", cancel = "Cancel", danger = false, input = null }) {
  return new Promise((resolve) => {
    const dlg = document.createElement("dialog");
    dlg.className = "ask";
    dlg.innerHTML = `<form method="dialog"><h2></h2><p class="muted ask-text"></p>${input !== null ? '<input class="ask-input" autocomplete="off">' : ""}
      <div class="actions"><button type="button" class="btn ghost" data-no></button><button class="btn ${danger ? "danger" : "primary"}" data-yes></button></div></form>`;
    dlg.querySelector("h2").textContent = title;
    dlg.querySelector("h2").hidden = !title;
    dlg.querySelector(".ask-text").textContent = message;
    dlg.querySelector("[data-no]").textContent = cancel;
    dlg.querySelector("[data-no]").hidden = !cancel;
    dlg.querySelector("[data-yes]").textContent = ok;
    const field = dlg.querySelector(".ask-input");
    if (field) field.value = input;
    let answered = false;
    const finish = (value) => {
      if (answered) return;
      answered = true;
      dlg.close();
      dlg.remove();
      resolve(value);
    };
    dlg.querySelector("form").addEventListener("submit", (e) => { e.preventDefault(); finish(field ? field.value : true); });
    dlg.querySelector("[data-no]").addEventListener("click", () => finish(field ? null : false));
    dlg.addEventListener("cancel", (e) => { e.preventDefault(); finish(field ? null : false); });
    document.body.appendChild(dlg);
    dlg.showModal();
    (field || dlg.querySelector("[data-yes]")).focus();
    if (field) field.select();
  });
}
const ehConfirm = (message, opts = {}) => ehAsk({ message, ...opts });
const ehPrompt = (message, value = "", opts = {}) => ehAsk({ message, input: value, ok: "Save", ...opts });

// ---- the ⋯ menu for a style (cards on Home and the style page share it)

function closeMenus() {
  document.querySelectorAll(".menu").forEach((m) => m.remove());
}
addEventListener("click", (e) => { if (!e.target.closest(".menu, [data-menu]")) closeMenus(); });
addEventListener("keydown", (e) => { if (e.key === "Escape") closeMenus(); });
addEventListener("scroll", closeMenus, { passive: true });

async function waitForJob(job) {
  while (job.state === "running") {
    await new Promise((r) => setTimeout(r, 600));
    job = await api("GET", `/api/jobs/${job.id}`);
  }
  if (job.state !== "done") throw new Error(job.message);
  return job.result;
}

// a small markdown renderer for the guide and brief (headings, lists, bold, code); everything is escaped first
function md(text) {
  const inline = (s) => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>").replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
    .replace(/(^|[\s(])\*([^*\s][^*]*)\*/g, "$1<i>$2</i>");
  const out = [];
  let list = false, code = false, para = [];
  const flush = () => { if (para.length) { out.push(`<p>${inline(para.join(" "))}</p>`); para = []; } };
  for (const raw of String(text || "").replace(/^---\n[\s\S]*?\n---\n/, "").split("\n")) {
    const line = raw.replace(/\s+$/, "");
    if (line.startsWith("```")) { flush(); if (list) { out.push("</ul>"); list = false; } out.push(code ? "</pre>" : "<pre>"); code = !code; continue; }
    if (code) { out.push(esc(line) + "\n"); continue; }
    const h = line.match(/^(#{1,4})\s+(.*)$/);
    const li = line.match(/^\s*[-*]\s+(.*)$/) || line.match(/^\s*\d+\.\s+(.*)$/);
    if (h || li || !line) flush();
    if (!li && list) { out.push("</ul>"); list = false; }
    if (h) out.push(`<h${Math.min(h[1].length, 3)}>${inline(h[2])}</h${Math.min(h[1].length, 3)}>`);
    else if (li) { if (!list) { out.push("<ul>"); list = true; } out.push(`<li>${inline(li[1])}</li>`); }
    else if (line) para.push(line);
  }
  flush();
  if (list) out.push("</ul>");
  return out.join("");
}

const STYLE_FORMATS = { short: "Short-form", long: "Long-form" };

function openStyleMenu(btn, s, done) {
  closeMenus();
  const onPage = location.pathname.startsWith("/style/");
  const act = async (fn) => { closeMenus(); try { await fn(); } catch (e) { toast(e.message, true); } };
  const items = [
    !onPage && ["Open", () => (location.href = `/style/${enc(s.id)}`)],
    s.can_manage && ["Rename", () => act(async () => {
      const name = await ehPrompt("The style's new name:", s.name, { title: "Rename the style" });
      if (!name || name.trim() === s.name) return;
      await api("POST", `/api/styles/${enc(s.id)}/rename`, { name });
      toast("Renamed"); done();
    })],
    ["Duplicate", () => act(async () => {
      await api("POST", `/api/styles/${enc(s.id)}/duplicate`, {});
      window.dispatchEvent(new Event("editorshub:jobs"));
      toast("Duplicating: see the progress at the bottom right");
    })],
    s.can_manage && [s.online ? "Update the online copy" : "Share online", () => act(async () => {
      if (!(await ehConfirm(`"${s.name}" goes online as a lighter copy, and everyone using Editors.Hub can download it from their Shared tab right away. Large videos are made smaller, and its style videos and finished edits aren't included. Your own style doesn't change. The limit is 3 GB, or 7 GB for a long-form style. Share only what you have the right to share: no client files, and nobody else's work. The progress shows at the bottom right, and you can keep working.`, { title: s.online ? "Update the online copy?" : "Share this style online?", ok: s.online ? "Update" : "Share" }))) return;
      await api("POST", `/api/styles/${enc(s.id)}/online`, {});
      window.dispatchEvent(new Event("editorshub:jobs"));
      toast("Sharing: see the progress at the bottom right");
    })],
    s.can_manage && s.online && ["Remove from the online Shared folder", () => act(async () => {
      if (!(await ehConfirm(`"${s.name}" stays in this studio; only the online copy goes.`, { title: "Remove from the online Shared folder?", ok: "Remove", danger: true }))) return;
      await api("DELETE", `/api/online/${enc(s.online.tag)}`);
      toast("Removed from the online Shared folder"); done();
    })],
    "-",
    ["Download (.zip)", () => { closeMenus(); location.href = `/api/styles/${enc(s.id)}/download`; }],
    ["Save to a drive", () => (location.href = `/style/${enc(s.id)}#save`)],
    ["Open folder", () => act(() => api("POST", "/api/reveal", { style: s.id }))],
    s.can_manage && "-",
    s.can_manage && ["Delete", () => act(async () => {
      const n = s.videos?.length ?? s.videos ?? 0, c = s.client_videos || 0;
      if (!(await ehConfirm(`"${s.name}"${n ? ` and its ${n} style video${n === 1 ? "" : "s"}` : ""} move to Recently deleted, where you can restore them.${c ? ` ${c} client video${c === 1 ? " uses" : "s use"} this style: they stay in their projects, but can't follow its rules until it's restored.` : ""}`, { title: "Delete this style?", ok: "Delete", danger: true }))) return;
      await api("DELETE", `/api/styles/${enc(s.id)}`);
      toast(`"${s.name}" moved to Recently deleted`); done("deleted");
    }), "danger"],
  ].filter(Boolean);
  const menu = document.createElement("div");
  menu.className = "menu";
  menu.setAttribute("role", "menu");
  items.forEach((it) => {
    if (it === "-") return menu.appendChild(document.createElement("hr"));
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = it[0];
    if (it[2]) b.className = it[2];
    b.onclick = (e) => { e.stopPropagation(); it[1](); };
    menu.appendChild(b);
  });
  document.body.appendChild(menu);
  const r = btn.getBoundingClientRect();
  const left = Math.min(r.right - menu.offsetWidth, innerWidth - menu.offsetWidth - 8);
  const top = r.bottom + 6 + menu.offsetHeight > innerHeight ? r.top - menu.offsetHeight - 6 : r.bottom + 6;
  menu.style.left = `${Math.max(8, left)}px`;
  menu.style.top = `${Math.max(8, top)}px`;
}

// ---- the activity panel: uploads, downloads, copies, with a live bar (bottom-right on every page)

const Activity = { seen: {}, timer: null, dismissed: new Set(), watching: new Set() };
try { JSON.parse(sessionStorage.getItem("eh-dismissed") || "[]").forEach((id) => Activity.dismissed.add(id)); } catch (e) {}

const STOP_WHAT = {
  "online-upload": "The part already online is removed, so nobody downloads half a style. The style itself stays as it is.",
  "online-download": "Nothing is added to your styles; what was downloaded so far is removed.",
  export: "The unfinished copy on the drive is removed.",
  duplicate: "The unfinished copy is removed; the original stays as it is.",
  import: "Nothing is added to your styles; what was copied so far is removed.",
};
async function stopJob(j) {
  const ok = await ehConfirm(STOP_WHAT[j.kind] || "What was done so far is removed.", { title: `Stop ${j.title.replace(/^./, (c) => c.toLowerCase())}?`, ok: "Stop", cancel: "Keep going", danger: true });
  if (!ok) return;
  try {
    await api("POST", `/api/jobs/${enc(j.id)}/stop`, {});
    toast("Stopping…");
    refreshActivity();
  } catch (e) {
    toast(e.message, true);
  }
}
// any Stop button (panel, cards, pages) carries its job's id
document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-stop-job]");
  if (!b) return;
  e.preventDefault();
  e.stopPropagation();
  const job = (Activity.last || []).find((j) => j.id === b.dataset.stopJob);
  if (job) stopJob(job);
}, true);

function fmtBytes(n) {
  return n >= 1e9 ? `${(n / 1e9).toFixed(2)} GB` : n >= 1e6 ? `${(n / 1e6).toFixed(0)} MB` : `${Math.max(0, Math.round(n / 1e3))} KB`;
}
function fmtLeft(sec) {
  if (!isFinite(sec) || sec <= 0) return "";
  if (sec < 60) return `${Math.ceil(sec)} s left`;
  if (sec < 3600) return `${Math.ceil(sec / 60)} min left`;
  return `${Math.floor(sec / 3600)} h ${Math.ceil((sec % 3600) / 60)} min left`;
}

function activityBox() {
  let box = document.getElementById("activity");
  if (!box) {
    box = document.createElement("div");
    box.id = "activity";
    box.setAttribute("aria-live", "polite");
    document.body.appendChild(box);
    box.addEventListener("click", (e) => {
      const b = e.target.closest("[data-dismiss]");
      if (!b) return;
      Activity.dismissed.add(b.dataset.dismiss);
      try { sessionStorage.setItem("eh-dismissed", JSON.stringify([...Activity.dismissed])); } catch (err) {}
      refreshActivity();
    });
  }
  return box;
}

function doneText(j) {
  if (j.state === "stopped") return j.message || "Stopped";
  const r = j.result || {};
  if (j.kind === "online-upload") return "Done: it's in the online Shared folder" + (r.original_bytes ? `. Lighter copy: ${(r.bytes / 1e9).toFixed(2)} GB, down from ${(r.original_bytes / 1e9).toFixed(2)} GB` : "");
  if (j.kind === "export") return `Done: saved to ${r.path || "the drive"}`;
  if (j.kind === "effects") return `Done: ${r.collected || 0} collected into Effects` + (r.failed?.length ? `. Not collected: ${r.failed.join("; ")}` : "");
  if (j.kind === "project-import") return `Done: "${r.name || "the client"}" is in Projects`;
  if (j.kind === "duplicate") return `Done: "${r.name || "the copy"}" is in My styles`;
  if (j.kind === "import" || j.kind === "online-download") return `Done: "${r.name || "the style"}" is in My styles`;
  return "Done";
}

async function refreshActivity() {
  clearTimeout(Activity.timer);
  let jobs = [];
  try {
    const res = await fetch("/api/jobs");
    if (!res.ok) return;
    jobs = (await res.json()).jobs || [];
  } catch (e) {
    Activity.timer = setTimeout(refreshActivity, 5000);
    return;
  }
  const now = Date.now() / 1000;
  Activity.last = jobs;
  window.dispatchEvent(new CustomEvent("editorshub:jobs-updated", { detail: jobs }));  // for bars on cards and pages
  const shown = jobs.filter((j) => !Activity.dismissed.has(j.id) && (j.state === "running" || now - (j.finished_ts || 0) < (j.state === "failed" ? 3600 : j.state === "stopped" ? 20 : 12)));
  activityBox().innerHTML = shown.map((j) => {
    const pct = j.total_bytes ? Math.min(100, (j.done_bytes / j.total_bytes) * 100) : 0;
    // speed and time left, from how far it moved since the last look
    const prev = Activity.seen[j.id];
    let speed = prev && prev.bytes <= j.done_bytes ? (j.done_bytes - prev.bytes) / Math.max(0.5, now - prev.t) : null;
    if (prev && prev.speed && speed !== null) speed = prev.speed * 0.7 + speed * 0.3;
    Activity.seen[j.id] = { bytes: j.done_bytes, t: now, speed: speed ?? prev?.speed };
    const left = speed ? fmtLeft((j.total_bytes - j.done_bytes) / speed) : "";
    const state = j.state === "done" ? "done" : j.state === "failed" ? "failed" : j.state === "stopped" ? "stopped" : "running";
    const detail = state === "running"
      ? `${esc(j.stage || "Working")}${j.total_bytes ? ` · ${fmtBytes(j.done_bytes)} of ${fmtBytes(j.total_bytes)}` : ""}${speed ? ` · ${fmtBytes(speed)}/s` : ""}${left ? ` · ${left}` : ""}`
      : state === "done" ? esc(doneText(j)) : esc(j.message || "It stopped");
    const stopping = state === "running" && /^Stopping|^Removing the unfinished/.test(j.stage || "");
    return `<div class="act ${state}">
      <div class="act-top"><span class="act-icon">${state === "done" ? "✓" : state === "failed" ? "!" : state === "stopped" ? "■" : ""}</span><b>${esc(j.title)}</b>
        <span class="act-pct">${state === "running" ? `${Math.floor(pct)}%` : ""}</span>
        ${state === "running" && !stopping ? `<button class="act-stop" data-stop-job="${esc(j.id)}" title="Stop">Stop</button>` : ""}
        ${state !== "running" ? `<button class="act-x" data-dismiss="${esc(j.id)}" title="Close">✕</button>` : ""}</div>
      <div class="act-bar"><div style="width:${state === "done" ? 100 : pct}%"></div></div>
      <div class="act-detail">${detail}</div></div>`;
  }).join("");
  for (const j of jobs) {  // tell the page when something it was showing has finished, so it can refresh
    if (j.state === "running") Activity.watching.add(j.id);
    else if (Activity.watching.delete(j.id)) window.dispatchEvent(new CustomEvent("editorshub:job-done", { detail: j }));
  }
  Activity.timer = setTimeout(refreshActivity, jobs.some((j) => j.state === "running") ? 1000 : 6000);
}
window.addEventListener("editorshub:jobs", () => refreshActivity());
if (!location.pathname.startsWith("/signin")) refreshActivity();


// a job's words and numbers, for bars shown on a style card or page
const JOB_VERB = { "online-upload": "Uploading online", "online-download": "Downloading", export: "Saving to a drive",
                   duplicate: "Duplicating", import: "Bringing in", "project-import": "Bringing in" };
function jobLine(j) {
  const pct = j.total_bytes ? Math.min(100, (j.done_bytes / j.total_bytes) * 100) : 0;
  const seen = Activity.seen[j.id];
  const speed = seen && seen.speed;
  const left = speed ? fmtLeft((j.total_bytes - j.done_bytes) / speed) : "";
  const verb = /^Packing/.test(j.stage || "") ? "Packing" : /^Unpacking|^Putting/.test(j.stage || "") ? "Unpacking" : (JOB_VERB[j.kind] || j.title);
  return { pct, text: `${verb} · ${Math.floor(pct)}%${j.total_bytes ? ` · ${fmtBytes(j.done_bytes)} of ${fmtBytes(j.total_bytes)}` : ""}${left ? ` · ${left}` : ""}`, stage: j.stage || "" };
}
function progressBar(j) {
  const l = jobLine(j);
  const stopping = /^Stopping|^Removing the unfinished/.test(j.stage || "");
  return `<div class="job-bar" data-job="${esc(j.id)}"><div class="job-track"><div style="width:${l.pct}%"></div></div>
    <div class="job-text"><span>${esc(l.text)}</span>${stopping ? "" : `<button class="job-stop" data-stop-job="${esc(j.id)}">Stop</button>`}</div>
    <div class="job-text"><span class="faint">${esc(l.stage)}</span></div></div>`;
}

/* ---- video cards: hover one to play it silently; a sideways video fits inside its tall card ---- */
const Hover = { card: null, timer: null, video: null };

function hoverStop() {
  clearTimeout(Hover.timer);
  if (Hover.video) {
    Hover.video.pause();
    Hover.video.removeAttribute("src");
    Hover.video.load();  // lets go of the connection to the file
    Hover.video.remove();
  }
  Hover.card = Hover.video = null;
}

function hoverStart(card) {
  const box = card.querySelector(".thumb, .th");
  if (!box) return;
  const video = document.createElement("video");
  Object.assign(video, { muted: true, loop: true, playsInline: true, preload: "auto", className: "hover-video" });
  video.addEventListener("loadedmetadata", () => box.classList.toggle("wide", video.videoWidth > video.videoHeight));
  video.addEventListener("playing", () => video.classList.add("on"));
  video.addEventListener("error", () => { if (Hover.video === video) hoverStop(); });  // the still stays
  video.src = card.dataset.preview;
  (box.querySelector("img, .ph") || box.firstChild)?.after(video);
  Hover.video = video;
  video.play().catch(() => {});
}

document.addEventListener("pointerover", (e) => {
  if (e.pointerType === "touch") return;
  const card = e.target.closest?.("[data-preview]") || null;
  if (card === Hover.card) return;
  hoverStop();
  if (!card) return;
  Hover.card = card;
  Hover.timer = setTimeout(() => hoverStart(card), 180);  // not for a mouse just passing over
});
document.addEventListener("load", (e) => {
  const img = e.target;
  if (img.tagName === "IMG" && img.parentElement?.matches(".thumb, .th")) img.parentElement.classList.toggle("wide", img.naturalWidth > img.naturalHeight);
}, true);
