const $ = (id) => document.getElementById(id);
const vidId = decodeURIComponent(location.pathname.split("/")[2] || "");
const FPS = 30;
const SPEEDS = [1, 1.5, 2, 0.5];
const R = { v: null, raw: "", version: null, frozen: null, hl: null, mode: "render", view: "watch", side: "notes",
            pending: [], role: "editor", cmpA: null, cmpB: null };
const maker = () => R.role !== "reviewer";
const firstEdit = () => maker() && !R.v.drafts.length;  // nothing to watch or note yet: the page is only the Live tab

// the video the controls drive: the single player, or the left one when comparing
const main = () => (R.view === "compare" ? $("vidA") : $("vid"));
const mediaUrl = (file) => `/media/${enc(vidId)}/${file.split("/").map(enc).join("/")}`;

async function load(first) {
  let v;
  try {
    v = await api("GET", `/api/videos/${enc(vidId)}`);
  } catch (e) {
    if (first) document.querySelector(".stage").innerHTML = `<div class="drop" style="position:static;height:60vh"><h3>${esc(e.message)}</h3><p class="muted"><a href="/">Back to Home</a></p></div>`;
    return;
  }
  const raw = JSON.stringify(v);
  if (raw === R.raw) return;
  const prevLatest = R.v?.latest;
  if (R.v && !R.v.drafts.length && v.drafts.length) R.side = "notes";  // the first draft is here: on to watching it
  R.raw = raw;
  R.v = v;
  const hash = parseInt((location.hash.match(/v(\d+)/) || [])[1]);
  if (first && !v.drafts.length && v.updates?.length) R.side = "live";  // nothing to watch yet: show how it's going
  if (first) R.version = v.drafts.some((d) => d.version === hash) ? hash : v.latest;
  else if (!R.version || (R.version === prevLatest && v.latest !== prevLatest)) {
    R.version = v.latest;
    if (prevLatest) toast(`v${v.latest} is here`);
  }
  render();
}

const draft = () => R.v.drafts.find((d) => d.version === R.version);

function noteState(n) {
  const b = (R.v.feedback || []).find((x) => x.id === n.batch);
  if (n.done) return ["fixed", "Fixed"];
  if (b && b.picked_up) return ["with", "With Claude"];
  if (b) return ["sent", "Sent to Claude"];
  return ["new", "New"];
}

function fmtWorked(s) {
  if (!s) return "";
  const m = Math.floor(s / 60), h = Math.floor(m / 60);
  return h ? `Worked for ${h}h ${m % 60}m` : `Worked for ${m}m ${s % 60}s`;
}

// ---------------------------------------------------------------- render

function render() {
  const v = R.v, d = draft();
  document.title = `${v.name} · Editors.Hub`;
  document.body.classList.toggle("first-edit", firstEdit());
  $("vName").textContent = v.name;
  $("vClient").innerHTML = v.project_name ? `${maker() ? `<a href="/project/${enc(v.project)}">${esc(v.project_name)}</a>` : esc(v.project_name)}<span> / </span>` : "";
  const listening = v.claude?.listening;
  $("claudeState").textContent = listening ? "Claude is listening" : "Claude is not listening. Notes still save.";
  $("claudeState").className = "claude-state" + (listening ? " on" : "");
  $("liveDot").className = "live-dot" + (listening ? " on" : "");
  $("statusSel").innerHTML = v.statuses.map((s) => `<option${s === v.status ? " selected" : ""}>${esc(s)}</option>`).join("");
  $("statusSel").className = "pill " + statusClass(v.status);
  const approvedThis = d && v.approved?.version === d.version;
  $("approveBtn").textContent = approvedThis ? `✓ v${d.version} approved` : "Approve the edit";
  $("approveBtn").disabled = !d || approvedThis;
  $("changesBtn").disabled = !d || v.status === "changes";
  $("approvedBar").hidden = !v.approved;
  if (v.approved) $("approvedBar").textContent = `✓ v${v.approved.version} approved ${ago(v.approved.at)}`;
  if (d && location.hash !== `#v${d.version}`) history.replaceState(null, "", `#v${d.version}`);

  renderStage();
  renderSide();
  renderInfo();
  askForRender();
  askForBroll();
}

// ---------------------------------------------------------------- the b-roll: who picks, what's picked, is it good

const brollClip = (o) => (o.kind === "image" || o.poster
  ? `<img src="${esc(mediaUrl(o.poster || o.file))}" alt="" loading="lazy"${o.kind === "video" ? ` data-clip="${esc(mediaUrl(o.file))}"` : ""}>`
  : `<video src="${esc(mediaUrl(o.file))}#t=0.1" muted loop playsinline preload="metadata"></video>`);
const brollWhen = (p) => `${fmtTime(p.start)} to ${fmtTime(p.end)}`;
const brollPicked = (p) => p.options.find((o) => o.id === p.picked);

function askForBroll() {
  const b = R.v.broll, dlg = $("brollDlg"), asking = b && ["mode", "picking", "review"].includes(b.stage);
  $("brollNew").hidden = !asking || R.side === "broll";
  if (!maker() || !asking) {
    if (dlg.open) dlg.close();
    return;
  }
  const key = `${b.stage}-${b.ask}`;
  if (R.brollLater === key || $("renderDlg").open || (dlg.open && R.brollShown === key)) return;
  openBrollDlg();
}

function openBrollDlg() {
  const b = R.v.broll, dlg = $("brollDlg");
  const key = `${b.stage}-${b.ask}`;
  if (R.brollShown !== key || !R.brollPicks) {  // coming back from Later keeps what was chosen
    R.brollPicks = {};
    R.brollChange = new Set();
  }
  R.brollShown = key;
  $("brollForm").querySelector(".error").textContent = "";
  $("brollCount").textContent = "";
  $("brollActions").innerHTML = "";
  if (b.stage === "mode" && R.brollOwn) {
    drawBrollOwn();
  } else if (b.stage === "mode") {
    $("brollTitle").textContent = "How should the b-roll be chosen?";
    $("brollIntro").textContent = `For ${R.v.name}. Claude is about to start editing.`;
    $("brollBody").innerHTML = `<div class="broll-modes">
      <button type="button" class="broll-mode" data-mode="manual"><b>Pick manually</b><span>Claude watches the whole video and finds every place b-roll can go. You see 3 or 4 options for each one and choose.</span></button>
      <button type="button" class="broll-mode" data-mode="auto"><b>Claude picks automatically</b><span>Claude chooses the b-roll itself and carries on with the edit. You can still change any of it on the next draft.</span></button>
      <button type="button" class="broll-mode" id="brollAddOwn"><b>Add your b-roll</b><span>Give Claude your own clips: a folder from this computer, or links to online folders like Google Drive or Dropbox.</span></button></div>`;
  } else if (b.stage === "picking") {
    drawBrollPicker();
  } else {
    drawBrollReview();
  }
  if (!dlg.open) dlg.showModal();
}

const BROLL_FILE = /\.(mp4|mov|m4v|webm|mkv|png|jpe?g|gif|webp)$/i;

function drawBrollOwn() {
  $("brollTitle").textContent = "Add your b-roll";
  $("brollIntro").textContent = "Claude uses your clips first. Add a folder, paste links, or both.";
  $("brollBody").innerHTML = `<div class="broll-own">
    <label class="btn" id="brollFolderBtn">Choose a folder from this computer<input type="file" id="brollFolder" webkitdirectory multiple hidden></label>
    <p class="faint small-print" id="brollOwnFiles"></p>
    <div class="progress" id="brollOwnBar" hidden><div></div></div>
    <label class="field">Or paste links to online folders <small>One on each line. Google Drive, Dropbox, or any page Claude can open.</small><textarea id="brollLinks" rows="3" placeholder="https://drive.google.com/drive/folders/…"></textarea></label>
    </div>`;
  $("brollActions").innerHTML = `<button type="button" class="btn" id="brollOwnBack">Back</button><button type="button" class="btn" data-own="manual">I'll pick from them</button><button type="button" class="btn primary" data-own="auto">Claude picks from them</button>`;
  const say = () => { const n = R.v.broll_yours; $("brollOwnFiles").textContent = n ? `${n} file${n === 1 ? "" : "s"} added.` : "Copies its videos and images into this video. Other files are skipped."; };
  say();
  $("brollOwnBack").onclick = () => { R.brollOwn = false; openBrollDlg(); };
  $("brollFolder").onchange = async (e) => {
    const err = $("brollForm").querySelector(".error"), bar = $("brollOwnBar"), buttons = $("brollActions").querySelectorAll("button");
    const files = [...e.target.files].filter((f) => BROLL_FILE.test(f.name));
    err.textContent = "";
    if (!files.length) return (err.textContent = "That folder has no videos or images.");
    const total = files.reduce((n, f) => n + f.size, 0);
    let done = 0;
    bar.hidden = false;
    buttons.forEach((b) => (b.disabled = true));
    try {
      for (const [i, file] of files.entries()) {
        $("brollOwnFiles").textContent = `Copying ${i + 1} of ${files.length}: ${file.name}`;
        await upload(`/api/videos/${enc(vidId)}/upload?kind=broll&name=${enc(file.name)}`, file, (p) => (bar.firstElementChild.style.width = `${((done + p * file.size) / total) * 100}%`));
        done += file.size;
        R.v.broll_yours = (R.v.broll_yours || 0) + 1;
      }
    } catch (ex) {
      err.textContent = ex.message;
    }
    bar.hidden = true;
    buttons.forEach((b) => (b.disabled = false));
    e.target.value = "";
    say();
  };
}

function drawBrollPicker() {
  const parts = R.v.broll.parts.filter((p) => p.needs_pick);
  $("brollTitle").textContent = "Pick the b-roll";
  $("brollIntro").textContent = "Choose one for each part, then submit. Hover over a clip to play it.";
  $("brollBody").innerHTML = parts.map((p) => `<section class="broll-part" data-part="${p.id}">
    <div class="broll-head">${p.frame ? `<img src="${esc(mediaUrl(p.frame))}" alt="">` : ""}<div${p.frame ? "" : ' style="grid-column:1/-1"'}><div class="when">${esc(brollWhen(p))}</div>${p.says ? `<q>${esc(p.says)}</q>` : ""}<small>${esc(p.why)}</small></div></div>
    <div class="broll-options">${p.options.map((o) => `<button type="button" class="broll-opt" data-opt="${o.id}">${brollClip(o)}<b>${esc(o.label)}</b>${o.why ? `<small>${esc(o.why)}</small>` : ""}${o.source ? `<small class="faint">${esc(o.source)}</small>` : ""}</button>`).join("")}</div>
    <button type="button" class="broll-none" data-opt="none">No b-roll here</button></section>`).join("");
  $("brollActions").innerHTML = `<button type="button" class="btn primary" id="brollSubmit" disabled>Submit my picks</button>`;
  for (const [part, value] of Object.entries(R.brollPicks)) {
    const box = $("brollBody").querySelector(`[data-part="${part}"]`);
    box?.querySelector(`[data-opt="${value}"]`)?.classList.add("on");
    box?.classList.add("done");
  }
  updateBrollCount();
}

function updateBrollCount() {
  const parts = R.v.broll.parts.filter((p) => p.needs_pick);
  const done = parts.filter((p) => R.brollPicks[p.id] !== undefined).length;
  $("brollCount").textContent = `${done} of ${parts.length} picked`;
  if ($("brollSubmit")) $("brollSubmit").disabled = done < parts.length;
}

function drawBrollReview() {
  const parts = R.v.broll.parts.filter((p) => p.picked);
  $("brollTitle").textContent = `How's the b-roll in draft ${R.v.latest || 1}?`;
  $("brollIntro").textContent = "Claude is about to start the next draft. Tick any you want changed and you'll get new options for those, or say it's all good.";
  $("brollBody").innerHTML = parts.map((p) => {
    const o = brollPicked(p);
    return `<label class="broll-review" data-change="${p.id}">${o ? brollClip(o) : "<span></span>"}<div><div class="when"><b>${esc(brollWhen(p))}</b></div>${p.says ? `<q>${esc(p.says)}</q>` : ""}<div class="faint small-print">${esc(o ? o.label : "No b-roll here")}</div></div><input type="checkbox" value="${p.id}"></label>`;
  }).join("");
  $("brollActions").innerHTML = `<button type="button" class="btn" id="brollChange" disabled>Change these</button><button type="button" class="btn primary" id="brollGood">All b-roll is good</button>`;
}

function renderBrollSide() {
  const b = R.v.broll;
  const asking = b && ["mode", "picking", "review"].includes(b.stage);
  const parts = b ? b.parts : [];
  $("brollSide").innerHTML = (asking ? `<div class="render-card"><b>Claude is waiting for you.</b><br><button class="btn small primary" id="brollOpen" type="button">Answer now</button></div>` : "") +
    (b?.settled ? `<div class="live-empty" style="padding:10px">You said the b-roll is good. To change any, mention b-roll in a note.</div>` : "") +
    (parts.length ? parts.map((p) => {
      const o = brollPicked(p);
      return `<div class="broll-side"><b>${esc(brollWhen(p))}</b> · ${esc(p.needs_pick ? "waiting for your pick" : o ? o.label : "no b-roll here")}${p.says ? `<div class="faint small-print">${esc(p.says)}</div>` : ""}${o ? (o.poster || o.kind === "image" ? `<img src="${esc(mediaUrl(o.poster || o.file))}" alt="" loading="lazy">` : "") : ""}</div>`;
    }).join("") : (asking ? "" : `<div class="live-empty">When Claude adds b-roll to this video, each part and its clip shows here.</div>`));
  if ($("brollOpen")) $("brollOpen").onclick = () => { R.brollLater = null; openBrollDlg(); };
}

async function answerBroll(body, msg) {
  const err = $("brollForm").querySelector(".error");
  err.textContent = "";
  try {
    R.v = await api("POST", `/api/videos/${enc(vidId)}/broll`, body);
    R.raw = JSON.stringify(R.v);
    $("brollDlg").close();
    R.side = "live";
    render();
    toast(msg);
  } catch (ex) {
    err.textContent = ex.message;
  }
}

$("brollForm").addEventListener("click", (e) => {
  if (e.target.closest("#brollAddOwn")) { R.brollOwn = true; return openBrollDlg(); }
  const own = e.target.closest("[data-own]");
  if (own) return answerBroll({ own: { mode: own.dataset.own, links: $("brollLinks").value.split(/\s+/).filter(Boolean) } }, "Claude will use your b-roll first");
  const mode = e.target.closest("[data-mode]");
  if (mode) return answerBroll({ mode: mode.dataset.mode }, mode.dataset.mode === "manual" ? "Claude is finding where b-roll can go" : "Claude will choose the b-roll");
  const opt = e.target.closest("[data-opt]");
  if (opt) {
    const part = opt.closest("[data-part]"), value = opt.dataset.opt === "none" ? "none" : +opt.dataset.opt;
    R.brollPicks[part.dataset.part] = value;
    part.querySelectorAll("[data-opt]").forEach((x) => x.classList.toggle("on", x === opt));
    part.classList.add("done");
    return updateBrollCount();
  }
  if (e.target.id === "brollSubmit") return answerBroll({ picks: R.brollPicks }, "Picks sent: Claude will carry on with the edit");
  if (e.target.id === "brollGood") return answerBroll({ change: [] }, "Got it: no more b-roll questions unless a note brings it up");
  if (e.target.id === "brollChange") return answerBroll({ change: [...R.brollChange] }, "Claude is finding new options for those");
});
$("brollForm").addEventListener("change", (e) => {
  if (e.target.type !== "checkbox") return;
  const id = +e.target.value;
  e.target.checked ? R.brollChange.add(id) : R.brollChange.delete(id);
  e.target.closest("[data-change]").classList.toggle("on", e.target.checked);
  $("brollChange").disabled = !R.brollChange.size;
  $("brollGood").disabled = R.brollChange.size > 0;
});
// a clip plays while the pointer is on its option
$("brollForm").addEventListener("mouseover", (e) => {
  const box = e.target.closest(".broll-opt, .broll-review");
  if (!box) return;
  const img = box.querySelector("img[data-clip]");
  if (img) {
    const v = document.createElement("video");
    Object.assign(v, { src: img.dataset.clip, muted: true, autoplay: true, loop: true, playsInline: true, poster: img.src });
    img.replaceWith(v);
  } else box.querySelector("video")?.play().catch(() => {});
});
$("brollForm").addEventListener("mouseout", (e) => {
  const box = e.target.closest(".broll-opt, .broll-review");
  if (box && !box.contains(e.relatedTarget)) box.querySelector("video")?.pause();
});
const brollPutOff = () => {
  R.brollLater = R.brollShown;
  R.side = "broll";
  renderSide();
};
$("brollLater").onclick = () => {
  brollPutOff();
  $("brollDlg").close();
  toast("You can answer any time in the B-roll tab");
};
$("brollDlg").addEventListener("cancel", brollPutOff);  // Esc is the same as Later

// ---------------------------------------------------------------- the Live tab and the render popup

// one layer: a clip for each snapshot of this draft, at its place in the edit, and the one being worked on marked
function renderTimeline(items) {
  const box = $("liveTimeline");
  const round = items.length ? items[items.length - 1].draft : null;
  const shots = items.filter((u) => u.image && u.draft === round);
  if (!shots.length) return (box.innerHTML = "");
  const now = shots[shots.length - 1];
  const total = [...items].reverse().find((u) => u.draft === round && u.total)?.total;
  const placed = shots.filter((u) => u.pos != null).sort((a, b) => a.pos - b.pos);
  const order = [...placed, ...shots.filter((u) => u.pos == null)];
  const len = (u, i) => {
    const next = order[i + 1];
    if (u.pos == null) return 1;
    const end = next?.pos ?? total ?? u.pos + 1;
    const whole = total || order[order.length - 1].pos + 1;
    return Math.max(0.05, (end - u.pos) / whole) * order.length;
  };
  const shown = shots.find((u) => u.id === R.shot) || now;
  const scroll = box.querySelector(".tl-track")?.scrollLeft;
  box.innerHTML = `<div class="tl">
    <div class="tl-head"><b>${shown === now ? "Working on now" : "Earlier"}</b>${shown.pos != null ? `<span class="faint">${fmtTime(shown.pos)}${total ? ` of ${fmtTime(total)}` : ""}</span>` : ""}</div>
    <a class="tl-big" href="${esc(mediaUrl(shown.image))}" target="_blank" rel="noopener"><img src="${esc(mediaUrl(shown.image))}" alt="Snapshot of the edit"></a>
    ${shown.text ? `<p class="tl-text">${esc(shown.text)}</p>` : ""}
    <div class="tl-track">${order.map((u, i) => `<button type="button" class="tl-clip${u === now ? " now" : ""}${u === shown ? " on" : ""}" data-shot="${u.id}" style="flex:${len(u, i).toFixed(3)} 0 74px" title="${esc(u.text || "")}"><img src="${esc(mediaUrl(u.image))}" alt="">${u.pos != null ? `<span>${fmtTime(u.pos)}</span>` : ""}</button>`).join("")}</div>
  </div>`;
  const track = box.querySelector(".tl-track");
  if (R.shot == null) box.querySelector(".tl-clip.now")?.scrollIntoView({ block: "nearest", inline: "center" });
  else if (scroll != null) track.scrollLeft = scroll;
}
$("liveTimeline").addEventListener("click", (e) => {
  const clip = e.target.closest("[data-shot]");
  if (!clip) return;
  const id = +clip.dataset.shot, shots = (R.v.updates || []).filter((u) => u.image);
  R.shot = shots[shots.length - 1]?.id === id ? null : id;  // the newest one goes back to following along
  renderTimeline(R.v.updates || []);
});

function renderLive() {
  const v = R.v, items = v.updates || [];
  if (R.side === "live") R.seen = items.length;
  $("liveNew").hidden = R.side === "live" || !(items.length > (R.seen ?? 0));
  $("liveNew").textContent = items.length - (R.seen ?? 0);
  const req = v.render_request, b = v.broll, start = v.start;
  const brollCard = firstEdit() && b && ["mode", "picking", "review"].includes(b.stage)  // "Later" on the popup: the way back to it
    ? `<div class="render-card"><b>Claude is waiting for your b-roll choice.</b><br><button class="btn small primary" id="brollAgain" type="button">Answer now</button></div>` : "";
  const startCard = start?.state === "starting" ? `<div class="render-card"><b>The parent session is starting this edit.</b> Its first update shows here in a moment.</div>`
    : start?.state === "waiting" && start.listening ? `<div class="render-card"><b>Starting the edit…</b> ${esc(start.parent)}'s session is picking this up.</div>`
    : start?.state === "waiting" ? `<div class="render-card"><b>Waiting for ${esc(start.parent)}'s Claude session.</b> The edit starts by itself as soon as that session is listening. If it isn't open, open it. If it doesn't exist yet, paste this into a new session:<div class="start-prompt">${esc(start.prompt)}</div><button class="btn small" id="copyListen" type="button">Copy</button></div>` : "";
  $("renderCard").innerHTML = startCard + brollCard + (req?.status === "waiting"
    ? `<div class="render-card"><b>Claude is waiting for your render settings.</b><br><button class="btn small primary" id="renderOpen" type="button">Choose the render settings</button></div>`
    : req?.status === "chosen" ? `<div class="render-card"><b>Render settings chosen.</b> ${v.claude?.listening ? "Claude is starting the render." : "The render starts when Claude picks them up."}</div>` : "");
  if ($("renderOpen")) $("renderOpen").onclick = () => openRenderDlg();
  if ($("brollAgain")) $("brollAgain").onclick = () => { R.brollLater = null; openBrollDlg(); };
  if ($("copyListen")) $("copyListen").onclick = async () => {
    try { await navigator.clipboard.writeText(start.prompt); toast("Copied: paste it into a Claude session"); }
    catch (e) { await ehPrompt("Copy this and paste it into a Claude session:", start.prompt, { title: "Prompt for Claude", ok: "Done", cancel: "Close" }); }
  };
  renderTimeline(items);
  let round = null;
  $("liveFeed").innerHTML = items.slice().reverse().map((u, i) => {
    const head = u.draft !== round ? `<div class="live-round">Working on draft ${u.draft}</div>` : "";
    round = u.draft;
    return `${head}<div class="live-item${i === 0 ? " now" : ""}">${u.text ? `<p>${esc(u.text)}</p>` : ""}${u.image ? `<a href="${esc(mediaUrl(u.image))}" target="_blank" rel="noopener"><img src="${esc(mediaUrl(u.image))}" alt="Snapshot of the edit" loading="lazy"></a>` : ""}<small>${ago(u.at)}</small></div>`;
  }).join("") || `<div class="live-empty">When Claude works on this video, what it's doing shows here in plain words, with snapshots.</div>`;
}

// the same sums as render_size and render_mbps in studio.py
function renderPlan(c, src) {
  const size = () => {
    if (!src?.width) return null;
    if (c.resolution === "same") return [src.width - src.width % 2, src.height - src.height % 2];
    const scale = +c.resolution / Math.min(src.width, src.height);
    return [Math.round((src.width * scale) / 2) * 2, Math.round((src.height * scale) / 2) * 2];
  };
  const wh = size(), fps = c.fps === "same" ? src?.fps : +c.fps;
  const parts = [wh ? `${wh[0]} × ${wh[1]}` : c.resolution === "same" ? "Same size as the edit" : `${c.resolution}p`, fps ? `${+(+fps).toFixed(2)} fps` : "same frame rate"];
  if (c.format === "prores") return parts.concat("ProRes, very large file").join(" · ");
  if (wh && fps) {
    const base = { low: 4, medium: 8, high: 16, higher: 30 }[c.bitrate];
    const mbps = Math.max(0.5, Math.round(base * ((wh[0] * wh[1] * fps) / (1920 * 1080 * 30)) ** 0.75 * (c.format === "h265" ? 0.7 : 1) * 10) / 10);
    parts.push(`about ${mbps} Mbps`);
    if (src.duration) parts.push(`about ${Math.max(1, Math.round((mbps * src.duration) / 8 + (+c.audio * src.duration) / 8000))} MB`);
  }
  return parts.join(" · ");
}

function openRenderDlg() {
  const req = R.v.render_request, f = $("renderForm");
  if (!req || $("renderDlg").open) return;
  for (const [key, options] of Object.entries(R.v.render_options)) {
    f.elements[key].innerHTML = options.map(([value, label]) => `<option value="${esc(value)}">${esc(label)}</option>`).join("");
    f.elements[key].value = req.defaults?.[key] ?? options[0][0];
  }
  $("renderTitle").textContent = `Choose the render settings for draft ${(R.v.latest || 0) + 1}`;
  $("renderNote").textContent = req.note || "Claude has finished this round of the edit and will render it with what you choose.";
  f.querySelector(".error").textContent = "";
  $("renderGo").disabled = false;
  showRenderPlan();
  $("renderDlg").showModal();
}

function showRenderPlan() {
  const f = $("renderForm"), c = Object.fromEntries(Object.keys(R.v.render_options).map((k) => [k, f.elements[k].value]));
  $("renderPlan").textContent = renderPlan(c, R.v.render_request?.source);
}

function askForRender() {
  const req = R.v.render_request;
  if (!maker() || req?.status !== "waiting") {
    if ($("renderDlg").open) $("renderDlg").close();
    return;
  }
  if (R.renderLater !== req.id) openRenderDlg();
}

function renderStage() {
  const v = R.v, d = draft(), live = v.live;
  document.querySelectorAll("#modeSeg button").forEach((b) => b.classList.toggle("on", b.dataset.mode === R.mode));
  document.querySelectorAll("#viewSeg button").forEach((b) => b.classList.toggle("on", b.dataset.view === R.view));
  $("renderBar").hidden = R.mode !== "render";
  $("comparePick").hidden = R.view !== "compare";
  $("renderName").textContent = R.mode === "live" ? (live ? `Live: ${live.project}` : "") : d ? `The render: v${d.version} · ${d.original || d.file}` : "";
  $("studioBtn").hidden = !(live && live.running);
  if (live) $("studioBtn").href = live.url;

  const showVideo = R.mode === "render" && R.view === "watch" && d;
  const showCompare = R.mode === "render" && R.view === "compare" && v.drafts.length > 0;
  const showLive = R.mode === "live" && live && live.running;
  $("vid").hidden = !showVideo;
  $("compareBox").hidden = !showCompare;
  $("liveFrame").hidden = !showLive;
  $("controls").style.visibility = R.mode === "render" && (showVideo || showCompare) ? "" : "hidden";
  $("timeline").style.visibility = $("controls").style.visibility;

  const empty = !(showVideo || showCompare || showLive);
  $("emptyDrop").hidden = !empty;
  $("startLive").hidden = !(R.mode === "live" && maker());
  if (R.mode === "live") {
    $("emptyTitle").textContent = live ? "Live preview is starting…" : "No live preview";
    $("emptyText").innerHTML = "While Claude works on the edit, its HyperFrames preview shows here (<code>studio.py live</code>). It only works on the studio's own computer.";
  } else {
    $("emptyTitle").textContent = "No draft yet";
    $("emptyText").innerHTML = "Drop a rendered video here, click <b>+ Upload draft</b>, or wait for Claude to ask for your render settings.";
  }

  const noPlay = showVideo && (d.render?.format === "prores" || R.playFail === d.version);
  $("playNote").hidden = !noPlay;
  if (noPlay) $("playNote").innerHTML = `This draft's format can't play in this browser. <a href="${esc(mediaUrl(d.file))}" download>Save the file</a> to watch it, or choose MP4 H.264 for the next render.`;
  if (showVideo) setSrc($("vid"), mediaUrl(d.file));
  if (!showVideo) $("vid").pause();
  if (showCompare) renderCompare();
  else { $("vidA").pause(); $("vidB").pause(); }
  if (showLive && $("liveFrame").dataset.src !== live.url) {
    $("liveFrame").dataset.src = live.url;
    $("liveFrame").src = live.url;
  }
  drawTimeline();
}

function setSrc(el, src) {
  if (el.dataset.src === src) return;
  const t = el.currentTime;
  el.dataset.src = src;
  el.src = src;
  el.addEventListener("loadedmetadata", () => { if (t && t < el.duration) el.currentTime = t; }, { once: true });
}

function renderCompare() {
  const vs = R.v.drafts.map((d) => d.version);
  if (!vs.includes(R.cmpB)) R.cmpB = R.version || vs[vs.length - 1];
  if (!vs.includes(R.cmpA)) R.cmpA = vs[Math.max(0, vs.indexOf(R.cmpB) - 1)];
  const opts = (sel) => vs.map((x) => `<option value="${x}"${x === sel ? " selected" : ""}>v${x}</option>`).join("");
  $("cmpA").innerHTML = opts(R.cmpA);
  $("cmpB").innerHTML = opts(R.cmpB);
  const byV = (x) => R.v.drafts.find((d) => d.version === x);
  setSrc($("vidA"), mediaUrl(byV(R.cmpA).file));
  setSrc($("vidB"), mediaUrl(byV(R.cmpB).file));
  $("capA").textContent = `v${R.cmpA}`;
  $("capB").textContent = `v${R.cmpB}`;
}

function drawTimeline() {
  const el = main(), dur = el.duration;
  const notes = (R.v?.notes || []).filter((n) => n.version === R.version).sort((a, b) => a.t - b.t);
  if (!dur || !isFinite(dur)) {
    $("markers").innerHTML = $("bubbles").innerHTML = $("ticks").innerHTML = "";
    return;
  }
  const pos = (t) => Math.min(100, (t / dur) * 100);
  $("markers").innerHTML = notes.map((n) => `<div class="mark${n.done ? " done" : ""}" style="left:${pos(n.t)}%"></div>`).join("");
  $("bubbles").innerHTML = notes.map((n, i) => `<div class="bubble${n.done ? " done" : ""}${R.hl === n.id ? " hl" : ""}" style="left:${pos(n.t)}%" data-id="${n.id}" title="${esc(fmtTime(n.t) + "  " + n.text)}">${i + 1}</div>`).join("");
  $("ticks").innerHTML = [0, 0.25, 0.5, 0.75, 1].map((f) => `<span>${fmtTime(dur * f).replace(/\.\d$/, "")}</span>`).join("");
}

function noteCard(n, num) {
  const [cls, label] = noteState(n);
  const atts = (n.attachments || []).map((a) => a.kind === "link"
    ? `<a class="att" href="${esc(a.url)}" target="_blank" rel="noopener">🔗 <span>${esc(a.url)}</span></a>`
    : `<a class="att" href="${esc(mediaUrl(a.file))}" target="_blank" rel="noopener">${a.image ? `<img src="${esc(mediaUrl(a.file))}" alt="">` : "📄"}<span>${esc(a.name)}</span></a>`).join("");
  const mine = maker() || n.author_email === R.email;
  return `<li class="card ${cls === "fixed" ? "fixed" : ""}${R.hl === n.id ? " cur" : ""}" data-id="${n.id}">
    <div class="head-row">
      ${cls === "fixed" ? '<span class="state fixed">✓</span>' : num ? `<b>${num}</b>` : ""}
      <button class="time" data-t="${n.t}" data-ver="${n.version}">${fmtTime(n.t)}</button>
      <span class="state ${cls}">${label}</span>
      ${$("allVers").checked ? `<span>v${n.version}</span>` : ""}
      <span>${esc(n.author || "")}</span>
      ${mine ? `<span class="tools"><button data-act="toggle" title="${n.done ? "Not fixed yet" : "Mark fixed"}">${n.done ? "↺" : "✓"}</button><button data-act="del" title="Delete">✕</button></span>` : ""}
    </div>
    ${n.text ? `<div class="text">${esc(n.text)}</div>` : ""}
    ${atts ? `<div class="atts">${atts}</div>` : ""}
    ${n.reply ? `<div class="reply"><b>Claude:</b> ${esc(n.reply.text)}</div>` : ""}
    ${n.saved_to ? `<div class="saved">✓ Saved to ${esc(n.saved_to)}</div>` : ""}
  </li>`;
}

function renderSide() {
  const v = R.v, d = draft();
  if (firstEdit()) R.side = "live";
  document.querySelectorAll("#sideSeg button").forEach((b) => b.classList.toggle("on", b.dataset.side === R.side));
  $("notesPane").hidden = R.side !== "notes";
  $("draftsPane").hidden = R.side !== "drafts";
  $("livePane").hidden = R.side !== "live";
  $("brollPane").hidden = R.side !== "broll";
  $("composer").style.display = R.side === "live" || R.side === "broll" ? "none" : "";
  renderLive();
  renderBrollSide();
  const doneCount = v.notes.filter((n) => n.done && n.version === R.version).length;
  $("doneCount").textContent = doneCount ? `${doneCount} done` : "";
  $("draftInfo").textContent = d ? `Draft ${d.version} · ${ago(d.added)}` : "No draft yet";

  // what this draft fixed, with Claude's answers
  const changed = v.notes.filter((n) => n.fixed_in === R.version);
  $("changedBox").hidden = !changed.length;
  $("workedFor").textContent = fmtWorked(d?.worked_for);
  $("changedList").innerHTML = changed.map((n) => noteCard(n)).join("");

  const all = $("allVers").checked;
  const list = v.notes.filter((n) => (all || n.version === R.version) && n.fixed_in !== R.version)
    .sort((a, b) => a.version - b.version || a.t - b.t);
  const order = v.notes.filter((n) => n.version === R.version).sort((a, b) => a.t - b.t).map((n) => n.id);
  const open = v.notes.filter((n) => n.version === R.version && !n.done).length;
  $("noteCount").textContent = R.version ? `${open} open on v${R.version}` : "Notes";
  $("noteList").innerHTML = list.length ? list.map((n) => noteCard(n, order.indexOf(n.id) + 1 || "")).join("")
    : `<li class="notes-empty">${R.version ? (changed.length ? "Nothing else on this draft." : "No notes yet. Pause on a moment and type what should change.") : "Notes appear here once there's a draft."}</li>`;

  $("draftList").innerHTML = v.drafts.slice().reverse().map((x) => {
    const notes = v.notes.filter((n) => n.version === x.version);
    const fixed = v.notes.filter((n) => n.fixed_in === x.version).length;
    return `<div class="draft-card${x.version === R.version ? " cur" : ""}">
      <div class="row"><b>v${x.version}</b><span class="faint">${ago(x.added)}</span>${v.approved?.version === x.version ? '<span class="state fixed">✓ approved</span>' : ""}<div class="spacer"></div>
        <button class="btn small" data-watch="${x.version}">Watch</button>${x.version !== R.version ? `<button class="btn small" data-cmp="${x.version}">Compare</button>` : ""}</div>
      <p>${esc(x.note || x.original || "")}</p>
      ${x.render ? `<div class="faint small-print">${x.render.width} × ${x.render.height} · ${+(+x.render.fps).toFixed(2)} fps · ${x.render.format === "prores" ? "ProRes" : `${esc(x.render.bitrate)} bitrate`} · ${x.render.size_mb} MB</div>` : ""}
      <div class="faint small-print">${notes.length} note${notes.length === 1 ? "" : "s"}${fixed ? ` · fixed ${fixed}` : ""}${x.worked_for ? " · " + fmtWorked(x.worked_for).toLowerCase() : ""}</div>
    </div>`;
  }).join("") || `<p class="notes-empty">No drafts yet.</p>`;

  // composer
  const fresh = v.notes.filter((n) => !n.batch && !n.done).length;
  $("submitBtn").disabled = !fresh;
  $("submitBtn").textContent = fresh ? `Submit feedback to Claude (${fresh})` : "Submit feedback to Claude";
  $("submitHint").textContent = !maker() ? "Your notes go to the editor." :
    fresh && !v.claude?.listening ? "No Claude session is listening right now: the notes wait until one runs studio.py wait." : "";
  $("noteText").placeholder = d ? `Feedback on draft ${d.version} at ${fmtTime(R.frozen ?? main().currentTime)}…` : "Notes need a draft first";
  $("noteText").disabled = !d;
  $("addBtn").disabled = !d;
  renderPending();
}

function renderPending() {
  $("pendingAtt").innerHTML = R.pending.map((a, i) => `<span class="att">${a.kind === "link" ? "🔗" : a.image ? `<img src="${esc(mediaUrl(a.file))}" alt="">` : "📄"}<span>${esc(a.kind === "link" ? a.url : a.name)}</span><button data-i="${i}" title="Remove">✕</button></span>`).join("");
}

function renderMadeWith() {
  const v = R.v, styles = R.styles || [];
  const client = v.project ? `<div><span class="faint">Client:</span> <a href="/project/${enc(v.project)}">${esc(v.project_name)}</a></div>` : `<div class="faint">To train a style, for no client.</div>`;
  const known = styles.some((s) => s.id === v.style);
  const options = (known ? "" : `<option value="${esc(v.style)}" selected>${esc(v.style_name)}</option>`) +
    styles.map((s) => `<option value="${esc(s.id)}"${s.id === v.style ? " selected" : ""}>${esc(s.name)}</option>`).join("");
  $("madeWith").innerHTML = client + (v.project
    ? `<label class="field"><span><span class="faint">Style</span> <a href="/style/${enc(v.style)}">open</a></span><select id="styleSel">${options}</select></label>`
    : `<div><span class="faint">Style:</span> <a href="/style/${enc(v.style)}">${esc(v.style_name)}</a></div>`);
  if ($("styleSel")) $("styleSel").onchange = changeStyle;
}

async function changeStyle(e) {
  const name = e.target.selectedOptions[0].textContent;
  if (!(await ehConfirm(`The next draft will follow "${name}". Earlier drafts stay as they are.`, { title: "Change the style?", ok: "Change style" }))) return renderMadeWith();
  try {
    R.v = await api("POST", `/api/videos/${enc(vidId)}/style`, { style: e.target.value });
    R.raw = JSON.stringify(R.v);
    render();
    toast(`The style is now ${name}`);
  } catch (ex) {
    toast(ex.message, true);
    renderMadeWith();
  }
}

function renderInfo() {
  const v = R.v;
  if (maker() && document.activeElement?.id !== "styleSel") renderMadeWith();
  $("reviewers").innerHTML = (v.reviewers || []).map((e) => `<span class="att">👤 <span>${esc(e)}</span><button data-rev="${esc(e)}" title="Remove">✕</button></span>`).join("") ||
    `<span class="faint small-print">No clients invited yet.</span>`;
  $("brief").innerHTML = v.brief ? esc(v.brief) : `<span class="faint">No brief. Write one in VIDEO.md in the video's folder.</span>`;
  const group = (title, list) => list.length ? `<div class="file-group">${title}</div>` + list.map((f) =>
    `<div class="file"><span title="${esc(f.name)}">${esc(f.name)}</span><span class="faint">${f.size == null ? esc(f.side) : fmtSize(f.size)}</span></div>`).join("") : "";
  const drafts = v.drafts.map((x) => ({ name: `v${x.version} · ${x.original || x.file}`, side: ago(x.added) }));
  $("files").innerHTML = group("Raw", v.raw) + group("Drafts", drafts) + group("Exports", v.exports) ||
    `<span class="faint">No files yet. Raw footage goes in the raw folder.</span>`;
}

// ---------------------------------------------------------------- the player

function tick() {
  const el = main(), dur = el.duration || 0, t = el.currentTime || 0;
  const pct = dur ? (t / dur) * 100 : 0;
  $("played").style.width = pct + "%";
  $("head").style.left = pct + "%";
  $("tNow").textContent = fmtTime(t);
  $("tDur").textContent = fmtTime(dur);
  $("playBtn").textContent = el.paused ? "▶" : "❚❚";
  if (R.frozen === null) $("atBtn").textContent = "◷ " + fmtTime(t);
  if (R.view === "compare") {  // keep the right-hand draft in step
    const b = $("vidB");
    if (Math.abs(b.currentTime - t) > 0.15) b.currentTime = Math.min(t, b.duration || t);
  }
  const near = R.v?.notes.find((n) => n.version === R.version && Math.abs(n.t - t) < 0.6);
  const id = near ? near.id : null;
  if (id !== R.hl) {
    R.hl = id;
    if (R.v) { renderSide(); drawTimeline(); }
  }
}

function seek(t, version) {
  if (version && version !== R.version) {
    R.version = version;
    R.mode = "render";
    R.view = "watch";
    render();
    $("vid").addEventListener("loadedmetadata", () => ($("vid").currentTime = t), { once: true });
    return;
  }
  const el = main();
  el.currentTime = Math.max(0, Math.min(t, el.duration || t));
}

function play(toggle = true) {
  const el = main();
  if (el.paused) {
    el.play();
    if (R.view === "compare") $("vidB").play();
  } else if (toggle) {
    el.pause();
    $("vidB").pause();
  }
}

["vid", "vidA", "vidB"].forEach((id) => {
  $(id).addEventListener("timeupdate", tick);
  $(id).addEventListener("seeked", tick);
  $(id).addEventListener("loadedmetadata", () => { tick(); drawTimeline(); });
  $(id).addEventListener("click", () => play());
});
$("vidA").addEventListener("pause", () => $("vidB").pause());
(function loop() { if (!main().paused) tick(); requestAnimationFrame(loop); })();

$("playBtn").onclick = () => play();
$("back5").onclick = () => seek(main().currentTime - 5);
$("fwd5").onclick = () => seek(main().currentTime + 5);
$("speedBtn").onclick = () => {
  const next = SPEEDS[(SPEEDS.indexOf(main().playbackRate) + 1) % SPEEDS.length] || 1;
  ["vid", "vidA", "vidB"].forEach((id) => ($(id).playbackRate = next));
  $("speedBtn").textContent = `${next}x`;
};
$("soundBtn").onclick = () => {
  const muted = !$("vid").muted;
  $("vid").muted = muted;
  $("vidA").muted = muted;  // in Compare only the left draft plays sound
  $("soundBtn").classList.toggle("on", muted);
  $("soundBtn").textContent = muted ? "Muted" : "Sound";
};
$("vidA").muted = false;
$("fullBtn").onclick = () => (document.fullscreenElement ? document.exitFullscreen() : $("player").requestFullscreen());

$("timeline").addEventListener("pointerdown", (e) => {
  const bubble = e.target.closest(".bubble");
  if (bubble) {
    const n = R.v.notes.find((x) => x.id === +bubble.dataset.id);
    return n && seek(n.t);
  }
  const track = $("timeline").querySelector(".track");
  const move = (ev) => {
    const r = track.getBoundingClientRect(), el = main();
    if (el.duration) seek(Math.max(0, Math.min(1, (ev.clientX - r.left) / r.width)) * el.duration);
  };
  move(e);
  const up = () => { removeEventListener("pointermove", move); removeEventListener("pointerup", up); };
  addEventListener("pointermove", move);
  addEventListener("pointerup", up);
});

$("modeSeg").onclick = (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  R.mode = b.dataset.mode;
  renderStage();
};
$("viewSeg").onclick = (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  R.view = b.dataset.view;
  renderStage();
  tick();
};
$("cmpA").onchange = (e) => { R.cmpA = +e.target.value; renderCompare(); };
$("cmpB").onchange = (e) => { R.cmpB = +e.target.value; renderCompare(); };
$("startLive").onclick = async () => {
  $("startLive").disabled = true;
  $("emptyTitle").textContent = "Starting the live preview…";
  try {
    R.v = await api("POST", `/api/videos/${enc(vidId)}/live`, {});
    R.raw = "";
    await load();
  } catch (e) {
    toast(e.message, true);
  }
  $("startLive").disabled = false;
};

// ---------------------------------------------------------------- notes, attachments, feedback

function freeze() {
  if (R.frozen === null) R.frozen = main().currentTime || 0;
  main().pause();
  $("atBtn").textContent = "◷ " + fmtTime(R.frozen);
  $("atBtn").classList.add("frozen");
}

function unfreeze() {
  R.frozen = null;
  $("atBtn").classList.remove("frozen");
}

async function addNote() {
  const text = $("noteText").value.trim();
  if ((!text && !R.pending.length) || !draft()) return;
  const t = R.frozen ?? main().currentTime ?? 0;
  try {
    await api("POST", `/api/videos/${enc(vidId)}/notes`, { version: R.version, t, text, attachments: R.pending });
    $("noteText").value = "";
    R.pending = [];
    unfreeze();
    await load();
    toast(`Note added at ${fmtTime(t)}`);
  } catch (e) {
    toast(e.message, true);
  }
}

async function attach(files) {
  for (const file of files) {
    try {
      const a = await upload(`/api/videos/${enc(vidId)}/upload?kind=attach&name=${enc(file.name)}`, file);
      R.pending.push(a);
      renderPending();
    } catch (e) {
      toast(e.message, true);
    }
  }
  $("noteText").focus();
}

$("noteText").addEventListener("focus", freeze);
$("noteText").addEventListener("blur", () => { if (!$("noteText").value.trim() && !R.pending.length) unfreeze(); });
$("noteText").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); addNote(); }
  if (e.key === "Escape") { $("noteText").blur(); unfreeze(); }
});
$("noteForm").addEventListener("submit", (e) => { e.preventDefault(); addNote(); });
$("atBtn").onclick = () => {
  R.frozen = main().currentTime || 0;
  $("atBtn").textContent = "◷ " + fmtTime(R.frozen);
  $("atBtn").classList.add("frozen");
  $("noteText").focus();
};
$("addMoreBtn").onclick = () => ($("addMenu").hidden = !$("addMenu").hidden);
$("attFile").onchange = (e) => { attach([...e.target.files]); e.target.value = ""; };
$("attFile2").onchange = (e) => { attach([...e.target.files]); e.target.value = ""; };
$("addLink").onclick = () => {
  const url = $("linkInput").value.trim();
  if (!/^https?:\/\/\S+$/.test(url)) return toast("Links start with http:// or https://", true);
  R.pending.push({ kind: "link", url });
  $("linkInput").value = "";
  renderPending();
};
$("linkInput").addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); $("addLink").click(); } });
$("pendingAtt").onclick = (e) => {
  const b = e.target.closest("button[data-i]");
  if (b) { R.pending.splice(+b.dataset.i, 1); renderPending(); }
};

$("submitBtn").onclick = async () => {
  try {
    R.v = await api("POST", `/api/videos/${enc(vidId)}/feedback`, {});
    R.raw = "";
    await load();
    toast(R.v.claude?.listening ? "Sent: Claude is on it" : "Sent: Claude picks it up when a session listens");
  } catch (e) {
    toast(e.message, true);
  }
};

async function noteAction(e, list) {
  const card = e.target.closest(".card");
  if (!card) return;
  const time = e.target.closest(".time");
  if (time) return seek(+time.dataset.t, +time.dataset.ver);
  const act = e.target.closest("[data-act]")?.dataset.act;
  if (!act) return;
  const id = card.dataset.id, n = R.v.notes.find((x) => x.id === +id);
  try {
    if (act === "toggle") await api("PATCH", `/api/videos/${enc(vidId)}/notes/${id}`, { done: !n.done });
    if (act === "del") {
      if (!(await ehConfirm("The note and its attachments go.", { title: "Delete this note?", ok: "Delete", danger: true }))) return;
      await api("DELETE", `/api/videos/${enc(vidId)}/notes/${id}`);
    }
    await load();
  } catch (ex) {
    toast(ex.message, true);
  }
}
$("noteList").addEventListener("click", noteAction);
$("changedList").addEventListener("click", noteAction);
$("allVers").onchange = renderSide;

$("sideSeg").onclick = (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  R.side = b.dataset.side;
  renderSide();
};
$("draftList").onclick = (e) => {
  const w = e.target.closest("[data-watch]"), c = e.target.closest("[data-cmp]");
  if (w) { R.version = +w.dataset.watch; R.mode = "render"; R.view = "watch"; R.side = "notes"; render(); }
  if (c) { R.cmpA = +c.dataset.cmp; R.cmpB = R.version; R.mode = "render"; R.view = "compare"; render(); }
};

async function reviewer(email, remove) {
  try {
    R.v = await api("POST", `/api/videos/${enc(vidId)}/reviewers`, { email, remove });
    R.raw = "";
    await load();
    toast(remove ? "Removed" : `${email} can review this video`);
  } catch (e) {
    toast(e.message, true);
  }
}
$("addRev").onclick = () => { const e = $("revEmail").value.trim(); if (e) { reviewer(e, false); $("revEmail").value = ""; } };
$("revEmail").addEventListener("keydown", (e) => { if (e.key === "Enter") $("addRev").click(); });
$("reviewers").onclick = async (e) => { const b = e.target.closest("[data-rev]"); if (b && await ehConfirm(`${b.dataset.rev} won't see this video any more.`, { title: "Stop them reviewing?", ok: "Stop", danger: true })) reviewer(b.dataset.rev, true); };

// ---------------------------------------------------------------- header actions, drafts, keys

async function post(body, msg) {
  try {
    await api("POST", `/api/videos/${enc(vidId)}`, body);
    await load();
    if (msg) toast(msg);
  } catch (e) {
    toast(e.message, true);
  }
}
$("statusSel").onchange = (e) => post({ status: e.target.value }, `Status: ${e.target.value}`);
$("approveBtn").onclick = () => post({ approve: R.version }, `v${R.version} approved`);
$("changesBtn").onclick = () => post({ status: "changes" }, "Changes asked for");
$("folderBtn").onclick = () => api("POST", "/api/reveal", { video: vidId }).catch((e) => toast(e.message, true));

async function uploadDraft(file) {
  if (!file || !maker()) return;
  if (!/^video\//.test(file.type) && !/\.(mp4|mov|m4v|webm|mkv)$/i.test(file.name)) return toast("That isn't a video file", true);
  $("uploading").hidden = false;
  $("upText").textContent = `Uploading ${file.name}…`;
  try {
    const r = await upload(`/api/videos/${enc(vidId)}/upload?kind=draft&name=${enc(file.name)}`, file, (p) => ($("upBar").style.width = p * 100 + "%"));
    await load();
    R.version = r.version;
    render();
    toast(`v${r.version} added`);
  } catch (e) {
    toast(e.message, true);
  } finally {
    $("uploading").hidden = true;
    $("upBar").style.width = "0";
  }
}
$("draftInput").onchange = (e) => { uploadDraft(e.target.files[0]); e.target.value = ""; };

document.addEventListener("keydown", (e) => {
  if (e.target.closest("input, textarea, select") || e.metaKey || e.ctrlKey || e.altKey) return;
  const step = e.shiftKey ? 5 : 1, el = main();
  if (e.key === " ") { e.preventDefault(); play(); }
  else if (e.key === "ArrowLeft") { e.preventDefault(); seek(el.currentTime - step); }
  else if (e.key === "ArrowRight") { e.preventDefault(); seek(el.currentTime + step); }
  else if (e.key === ",") { el.pause(); seek(el.currentTime - 1 / FPS); }
  else if (e.key === ".") { el.pause(); seek(el.currentTime + 1 / FPS); }
  else if (e.key === "n" || e.key === "N") { e.preventDefault(); $("noteText").focus(); }
});

// a video file dropped on the page becomes a draft; anything else dropped on the notes becomes an attachment
let dragDepth = 0;
addEventListener("dragenter", (e) => { if (e.dataTransfer.types.includes("Files") && maker()) { dragDepth++; $("dropVeil").classList.add("on"); } });
addEventListener("dragleave", () => { if (--dragDepth <= 0) { dragDepth = 0; $("dropVeil").classList.remove("on"); } });
addEventListener("dragover", (e) => e.preventDefault());
addEventListener("drop", (e) => {
  e.preventDefault();
  dragDepth = 0;
  $("dropVeil").classList.remove("on");
  const files = [...e.dataTransfer.files];
  if (e.target.closest(".side")) return attach(files);
  const video = files.find((f) => /^video\//.test(f.type) || /\.(mp4|mov|m4v|webm|mkv)$/i.test(f.name));
  if (video) uploadDraft(video);
  else if (files.length) attach(files);
});
$("composer").addEventListener("paste", (e) => {  // paste a screenshot straight into a note
  const files = [...(e.clipboardData?.files || [])];
  if (files.length) { e.preventDefault(); attach(files); }
});

api("GET", "/api/auth/me").then((me) => {
  if (!me.user) return;
  R.role = me.user.role;
  R.email = me.user.email;
  document.body.className = "role-" + me.user.role;
  if (R.v) renderSide();
}).catch(() => {});
load(true);
$("vid").addEventListener("error", () => { R.playFail = R.version; renderStage(); });
$("vid").addEventListener("loadedmetadata", () => {
  if ($("vid").videoWidth === 0) { R.playFail = R.version; renderStage(); }
});
if (maker()) api("GET", "/api/state").then((s) => { R.styles = s.styles; if (R.v) renderMadeWith(); }).catch(() => {});
$("renderForm").addEventListener("change", showRenderPlan);
$("renderLater").onclick = () => {
  R.renderLater = R.v.render_request?.id;
  $("renderDlg").close();
  R.side = "live";
  renderSide();
  $("livePane").scrollIntoView({ behavior: "smooth", block: "nearest" });
  toast("You can choose them any time in the Live tab");
};
$("renderForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target, choice = Object.fromEntries(Object.keys(R.v.render_options).map((k) => [k, f.elements[k].value]));
  $("renderGo").disabled = true;
  try {
    R.v = await api("POST", `/api/videos/${enc(vidId)}/render-choice`, choice);
    R.raw = JSON.stringify(R.v);
    $("renderDlg").close();
    R.side = "live";
    render();
    $("livePane").scrollIntoView({ behavior: "smooth", block: "nearest" });
    toast("Saved: Claude will render with these settings");
  } catch (ex) {
    f.querySelector(".error").textContent = ex.message;
    $("renderGo").disabled = false;
  }
});
setInterval(() => document.visibilityState === "visible" && load(), 3000);
