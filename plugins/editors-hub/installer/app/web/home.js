const S = { state: null, tab: "videos", kind: "client", status: "all", style: "", project: "", q: "" };
const $ = (id) => document.getElementById(id);

async function load() {
  try {
    const had = S.state?.version;
    S.state = await api("GET", "/api/state");
    // the studio updated itself and restarted: pick up the new pages, unless someone's in the middle of a form
    if (had && S.state.version !== had && !document.querySelector("dialog[open]")) return location.reload();
  } catch (e) {
    return toast(e.message, true);
  }
  render();
}

function render() {
  const { videos, styles, projects, statuses, settings, me } = S.state;
  renderMe(me);
  const waiting4Render = videos.filter((v) => v.render_waiting);
  $("renderBanner").hidden = !waiting4Render.length;
  $("renderBanner").innerHTML = waiting4Render.length ? `<div><b>Claude is waiting for your render settings</b><span class="muted">${waiting4Render.map((v) => `<a href="/review/${enc(v.id)}">${esc(v.name)}</a>`).join(", ")}</span></div>` : "";
  const grace = S.state.approval?.grace_until;
  $("approvalBanner").hidden = !grace;
  $("approvalBanner").innerHTML = grace ? `<div><b>This computer needs the owner's approval</b><span class="muted"><a href="/approve">Ask for a code</a> by ${new Date(grace * 1000).toLocaleDateString()} to keep using it.</span></div>` : "";
  const waiting4Broll = videos.filter((v) => v.broll_waiting);
  $("brollBanner").hidden = !waiting4Broll.length;
  $("brollBanner").innerHTML = waiting4Broll.length ? `<div><b>Claude is waiting for your b-roll choice</b><span class="muted">${waiting4Broll.map((v) => `<a href="/review/${enc(v.id)}">${esc(v.name)}</a>`).join(", ")}</span></div>` : "";
  const clientVideos = videos.filter((v) => v.project), styleVideos = videos.filter((v) => !v.project);
  // a reviewer only sees the videos they're invited to, with no tabs to hide any behind
  const listed = me.role === "reviewer" ? videos : S.kind === "client" ? clientVideos : styleVideos;
  $("videoKinds").innerHTML = [["client", "Client videos", clientVideos.length], ["style", "Style videos", styleVideos.length]]
    .map(([k, label, n]) => `<button type="button" data-kind="${k}" class="${S.kind === k ? "on" : ""}">${label}<em>${n}</em></button>`).join("");
  $("hello").innerHTML = `Welcome back, <span class="name">${esc(me.username)}</span>`;
  const waiting = videos.filter((v) => v.status === "in review").length;
  $("summary").textContent = videos.length
    ? `${clientVideos.length} client video${clientVideos.length === 1 ? "" : "s"} and ${styleVideos.length} style video${styleVideos.length === 1 ? "" : "s"}.`
    : "Make a project for each client and a style for each look, then pick one of each for a new video.";
  if (S.project && !projects.some((p) => p.id === S.project)) S.project = "";  // that client was deleted
  const count = (s) => videos.filter((v) => v.status === s).length;
  const countListed = (s) => listed.filter((v) => v.status === s).length;
  $("stats").innerHTML = [
    ["Videos", videos.length],
    ["In review", waiting, waiting > 0],
    ["Changes", count("changes")],
    ["Approved", count("approved")],
  ].map(([label, n, hot]) => `<div class="sl${hot ? " hot" : ""}"><b>${n}</b><span>${label}</span></div>`).join("");

  $("statusChips").innerHTML = ["all", ...statuses].map((s) =>
    `<button class="chip${S.status === s ? " on" : ""}" data-status="${esc(s)}">${esc(s)}<em>${s === "all" ? listed.length : countListed(s)}</em></button>`).join("");
  $("projectFilter").innerHTML = `<option value="">All clients</option>` +
    projects.map((p) => `<option value="${esc(p.id)}"${S.project === p.id ? " selected" : ""}>${esc(p.name)}</option>`).join("");
  $("projectFilter").hidden = !projects.length || S.kind !== "client";
  $("styleFilter").innerHTML = `<option value="">All styles</option>` +
    styles.map((s) => `<option value="${esc(s.id)}"${S.style === s.id ? " selected" : ""}>${esc(s.name)}</option>`).join("");

  const q = S.q.toLowerCase();
  const shown = listed.filter((v) =>
    (S.status === "all" || v.status === S.status) && (!S.style || v.style === S.style) && (S.kind !== "client" || !S.project || v.project === S.project) &&
    (!q || (v.name + " " + v.style_name + " " + v.project_name).toLowerCase().includes(q)));
  $("videoGrid").innerHTML = shown.length ? shown.map(videoCard).join("") : emptyVideos(listed);

  $("projectGrid").innerHTML = projects.length ? projects.map(projectCard).join("") :
    `<div class="empty"><h3>No clients yet</h3><p>A project holds one client: their details, brandbook, brand guidelines and videos.</p><button class="btn primary" data-act="new-project">Add your first client</button></div>`;

  const mine = styles.filter((s) => s.mine || s.shared);
  $("styleGrid").innerHTML = mine.length ? mine.map(styleCard).join("") :
    `<div class="empty"><h3>No styles of your own yet</h3><p>A style holds one editing look you can use for any client: its rules and references. It's private to you until you share it online.</p><button class="btn primary" data-act="new-style">Make your first style</button></div>`;
  queueMicrotask(applyJobBars);

  const f = $("settingsForm");
  if (me.role === "owner" && document.activeElement?.form !== f) f.elements.library.value = settings.library;
  const py = S.state.platform === "windows" ? "py" : "python3";
  const script = S.state.platform === "windows" ? "%USERPROFILE%\\editors-hub\\studio.py" : "~/editors-hub/studio.py";
  $("cmds").textContent = [
    `${py} ${script} status`,
    `${py} ${script} new-project "<client>"`,
    `${py} ${script} new-video <style> "<name>" --project <project> --raw <file>`,
    `${py} ${script} new-video <style> "<name>" --training --raw <file>`,
    `${py} ${script} context <video>`,
    `${py} ${script} update <video> "<what you're doing>" --snapshot <file>`,
    `${py} ${script} ask-render <video>`,
    `${py} ${script} finish-render <video> <file>`,
    `${py} ${script} notes <video>`,
    `${py} ${script} open <video>`,
  ].join("\n");
}

function videoCard(v) {
  const initials = v.name.split(/\s+/).slice(0, 2).map((w) => w[0] || "").join("").toUpperCase();
  const thumb = v.thumb ? `<img src="/media/${enc(v.id)}/thumb.jpg?${enc(v.updated)}" alt="" loading="lazy">` : `<div class="ph">${esc(initials)}</div>`;
  const notes = v.open_notes ? ` · <b>${v.open_notes} open note${v.open_notes > 1 ? "s" : ""}</b>` : "";
  return `<a class="card" href="/review/${enc(v.id)}">
    <div class="thumb">${thumb}<span class="pill ${statusClass(v.status)}">${esc(v.status)}</span>${v.latest ? `<span class="ver">v${v.latest}</span>` : ""}</div>
    <div class="body"><div class="title">${esc(v.name)}</div>
      <div class="meta">${v.project_name ? esc(v.project_name) + " · " : ""}${esc(v.style_name)}${v.latest ? "" : " · no draft yet"}${notes}</div>
      <div class="meta faint">Updated ${ago(v.updated)}</div></div></a>`;
}

function emptyVideos(listed) {
  if (S.state.me.role !== "reviewer" && S.kind === "style") {
    if (!S.state.styles.length)
      return `<div class="empty"><h3>No styles yet</h3><p>Make a style, then add videos that train it.</p><button class="btn primary" data-act="new-style">Make your first style</button></div>`;
    if (!listed.length)
      return `<div class="empty"><h3>No style videos yet</h3><p>These are videos you make to train a style, for no client. They show here and on the style's page.</p><button class="btn primary" data-act="new-training-video">+ Style video</button></div>`;
    return `<div class="empty"><h3>Nothing matches</h3><p>Try another filter.</p></div>`;
  }
  if (S.state.me.role !== "reviewer" && !S.state.projects.length)
    return `<div class="empty"><h3>Welcome to Editors.Hub</h3><p>Start by adding your first client with their brand, then make a style and add their videos.</p><button class="btn primary" data-act="new-project">Add your first client</button></div>`;
  if (S.state.me.role !== "reviewer" && !S.state.styles.length)
    return `<div class="empty"><h3>Now make a style</h3><p>A style is an editing look you can use for any client.</p><button class="btn primary" data-act="new-style">Make your first style</button></div>`;
  if (!listed.length)
    return `<div class="empty"><h3>No client videos yet</h3><p>Add a video, drop in the raw footage, and upload drafts for review.</p><button class="btn primary" data-act="new-video">+ New video</button></div>`;
  return `<div class="empty"><h3>Nothing matches</h3><p>Try another filter.</p></div>`;
}

function projectCard(p) {
  const initials = p.name.replace(/[^\p{L}\p{N}\s]/gu, "").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join("").toUpperCase();
  return `<div class="card" data-project="${esc(p.id)}">
    <div class="row"><div class="badge">${esc(initials)}</div><div><h3>${esc(p.name)}</h3><div class="faint">${esc(p.contact || "Client")}</div></div></div>
    <div class="notes">${esc(p.about || "No details about this client yet.")}</div>
    <div class="row"><span class="muted">${p.videos} video${p.videos === 1 ? "" : "s"} · ${p.brand_files} brand file${p.brand_files === 1 ? "" : "s"}</span><div class="spacer"></div>
      <button class="btn small primary" data-act="new-video-for" data-id="${esc(p.id)}">+ Video</button></div></div>`;
}

function styleCard(s) {
  const initials = s.name.replace(/[^\p{L}\p{N}\s]/gu, "").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join("").toUpperCase();
  const swatches = (s.palette || []).slice(0, 6).map((c) => `<i style="background:${esc(c)}" title="${esc(c)}"></i>`).join("");
  return `<div class="card" data-style="${esc(s.id)}">
    <div class="row"><div class="badge">${esc(initials)}</div><div><h3>${esc(s.name)}</h3><div class="faint">${esc(STYLE_FORMATS[s.format] || (s.client ? "Client: " + s.client : "Editing style"))}</div></div>
      <div class="spacer"></div>${s.online ? `<span class="share-tag online" title="In the online Shared folder">Online</span>` : `<span class="share-tag private">Private</span>`}</div>
    ${swatches ? `<div class="swatches">${swatches}</div>` : ""}
    <div class="notes">${esc(s.notes || "No style notes yet. Add the rules to STYLE.md in its folder.")}</div>
    ${s.shared ? `<div class="faint small-print">Made by ${esc(s.mine ? "you" : s.maker_name || "the owner")}${s.shared_at ? " · shared " + ago(s.shared_at) : ""}</div>` : ""}
    <div class="row"><span class="muted">${s.videos} style video${s.videos === 1 ? "" : "s"}${s.client_videos ? ` · used in ${s.client_videos} client video${s.client_videos === 1 ? "" : "s"}` : ""}</span><div class="spacer"></div>
      <button class="btn small primary" data-act="new-video" data-id="${esc(s.id)}">+ Video</button>
      <button class="btn small dots" data-act="menu" data-menu data-id="${esc(s.id)}" title="More: share, rename, duplicate, download, delete" aria-label="More">⋯</button></div></div>`;
}

const SKILL_HELP = {
  installed: "installed by Editors.Hub",
  "already there": "already on this computer, left as it is",
  "set up": "set up or edited here, never overwritten",
  missing: "not installed yet",
  update: "a newer version is packed",
  "skipped here": "not installed on this computer (on purpose)",
};

function renderSkills(data) {
  const counts = {};
  data.skills.forEach((s) => (counts[s.state] = (counts[s.state] || 0) + 1));
  $("skillSum").innerHTML = `<span class="pill">${data.skills.length} packed</span>` +
    Object.entries(counts).map(([k, n]) => `<span class="pill k-${k.replace(/\s+/g, "-")}">${n} ${esc(k)}</span>`).join("");
  $("skillList").innerHTML = data.skills.map((s) => `<div class="skill" title="${esc(s.description)}">
    <b>${esc(s.name)}</b><span class="pill k-${s.state.replace(/\s+/g, "-")}" title="${esc(SKILL_HELP[s.state] || "")}">${esc(s.state)}</span>
    <small>${esc(s.description || "")}</small></div>`).join("") || `<p class="faint">No skills packed yet.</p>`;
  const p = data.profile;
  $("skillFolder").textContent = `Claude's skills folder on this computer: ${data.folder}. ` + (p
    ? `Creator profile packed: ${p.brand || "-"} (${p.creator || "-"}), ${p.fonts.length} font${p.fonts.length === 1 ? "" : "s"}. A new computer gets it and its skills come filled in.`
    : "No creator profile packed (run: studio.py profile pack).");
  $("installSkills").disabled = !data.skills.some((s) => s.state === "missing" || s.state === "update");
}

async function loadSkills() {
  try {
    renderSkills(await api("GET", "/api/skills"));
  } catch (e) {
    toast(e.message, true);
  }
}

$("installSkills").onclick = async () => {
  try {
    const r = await api("POST", "/api/skills/install");
    renderSkills(r);
    const n = r.installed.length + r.updated.length;
    toast(r.failed.length ? `Couldn't install: ${r.failed.join("; ")}` : n ? `${n} skill${n > 1 ? "s" : ""} installed` : "Nothing to install", r.failed.length > 0);
  } catch (e) {
    toast(e.message, true);
  }
};

// ---- setup: the owner gets the studio ready before anything else

let setupTimer, wasReady = null, folderPick = null, lastSteps = "";
const TICKS = { ok: "✓", failed: "!", "needs you": "!", restart: "↻", waiting: "…", missing: "", checking: "", installing: "" };

function stepAction(it) {
  if (it.state === "ok" || it.state === "checking" || it.state === "installing") return "";
  if (it.manual === "button") return `<button class="btn small primary" data-step="${it.id}">${esc(it.button || "Install")}</button>`;
  if (it.manual === "keys") return `<button class="btn small primary" data-go="keys">Add keys</button>`;
  return "";
}

function renderSetup(s) {
  const items = s.items || [];
  const done = items.filter((i) => i.state === "ok").length;
  $("setupCount").innerHTML = `<b>${done}/${items.length}</b><span>ready</span>`;
  $("setupCount").className = "stat" + (s.ready ? "" : " hot");
  const key = JSON.stringify(items);
  if (key !== lastSteps) $("stepList").innerHTML = items.map((it) => {
    const cls = it.state === "ok" ? "ok" : ["needs you", "missing"].includes(it.state) && it.manual ? "needs" :
      ["failed", "restart"].includes(it.state) ? "failed" : ["checking", "installing"].includes(it.state) ? "busy" : "";
    const detail = it.state === "installing" ? "Installing… this can take a few minutes." : it.detail;
    const folders = it.id === "workdir" && it.state !== "ok" ? `<div class="folders" id="folderPick">Loading places…</div>` : "";
    return `<div class="step ${cls}"><div class="tick">${TICKS[it.state] ?? ""}</div>
      <div><h4>${esc(it.title)}</h4><p>${esc(it.text)}</p>${detail ? `<div class="detail">${esc(detail)}</div>` : ""}</div>
      <div>${stepAction(it)}</div>${folders}</div>`;
  }).join("") || `<p class="faint">Checking this computer…</p>`;
  lastSteps = key;
  if ($("folderPick")) loadFolders();
  $("checkAgain").disabled = s.running;
  $("setupDone").hidden = !s.ready;
  $("setupTitle").textContent = s.ready ? "Editors.Hub is ready" : "Get Editors.Hub ready";

  const pill = $("readyPill");
  pill.className = "ready-pill " + (s.running ? "busy" : s.ready ? "ok" : "todo");
  $("readyText").textContent = s.running ? `Setting up ${done}/${items.length}` : s.ready ? "Ready" : `Setup ${done}/${items.length}`;

  // everyone else just sees a note while the owner finishes
  const banner = $("setupBanner");
  if (S.state?.me.role !== "owner" && s.ready === false) {
    banner.className = "setup-banner warn";
    banner.innerHTML = `<div><b>The studio is still being set up</b><span class="muted">The owner is installing what edits need on this computer. Some things may not work until it's done.</span></div>`;
    banner.hidden = false;
  } else banner.hidden = true;

  if (S.state?.me.role === "owner") {
    if (s.ready === false && S.tab !== "setup" && !s.running && wasReady === null) setTab("setup");
    if (s.ready && wasReady === false) toast("Editors.Hub is ready");
  }
  if (!s.running && s.ready !== null) wasReady = s.ready;
  clearTimeout(setupTimer);
  if (s.running || (S.tab === "setup" && !s.ready)) setupTimer = setTimeout(loadSetup, s.running ? 1500 : 5000);
}

async function loadSetup() {
  try {
    renderSetup(await api("GET", "/api/setup"));
  } catch (e) {}
}

async function loadFolders() {
  if (!folderPick) {
    try {
      folderPick = await api("GET", "/api/setup/folders");
    } catch (e) {
      return;
    }
  }
  const box = $("folderPick");
  if (!box || box.dataset.filled) return;
  box.dataset.filled = "1";
  const f = folderPick;
  box.innerHTML = f.suggestions.map((path, i) =>
    `<label><input type="radio" name="folder" value="${esc(path)}"${i === 0 ? " checked" : ""}> ${esc(path)}${path.startsWith("/Volumes/") ? ' <span class="faint">(external drive)</span>' : ""}</label>`).join("") +
    `<label><input type="radio" name="folder" value=""> Somewhere else:</label>
     <div class="row"><input id="folderOther" placeholder="${f.suggestions[0].includes("\\") ? "D:\\Editors.Hub" : "/Volumes/MyDrive/Editors.Hub"}"><button class="btn small primary" id="folderUse">Use this folder</button></div>`;
  $("folderOther").onfocus = () => (box.querySelector('input[value=""]').checked = true);
  $("folderUse").onclick = async () => {
    const picked = box.querySelector("input[name=folder]:checked").value || $("folderOther").value.trim();
    if (!picked) return toast("Type the folder", true);
    try {
      renderSetup(await api("POST", "/api/setup/workdir", { folder: picked }));
      folderPick = null;
      toast("Saved: " + picked);
    } catch (e) {
      toast(e.message, true);
    }
  };
}

$("stepList").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-step],[data-go]");
  if (!b) return;
  if (b.dataset.go === "keys") {
    setTab("settings", true);
    return setTimeout(() => $("keysPanel").scrollIntoView({ behavior: "smooth" }), 200);
  }
  try {
    renderSetup(await api("POST", "/api/setup/run", { only: b.dataset.step }));
  } catch (ex) {
    toast(ex.message, true);
  }
});
$("checkAgain").onclick = async () => {
  try {
    renderSetup(await api("POST", "/api/setup/run", {}));
  } catch (e) {
    toast(e.message, true);
  }
};
$("setupDone").onclick = () => setTab("videos");
$("readyPill").onclick = () => setTab("setup");
$("openSetup").onclick = () => setTab("setup");

// ---- API keys (owner only)

function renderKeys(data) {
  $("keyList").innerHTML = data.keys.map((k) => `<div class="keyrow">
      <div><b>${esc(k.service)}</b> <span class="faint">· ${esc(k.group)} · ${esc(k.cost)}</span><br><small>${esc(k.for)}${k.needed ? " <b>Needed for how you work.</b>" : ""}</small></div>
      <span class="pill ${k.added ? "s-approved" : k.needed ? "s-in-review" : "s-delivered"}">${k.added ? "added" : k.needed ? "needed" : "not added"}</span>
      <div class="row">
        <input type="password" autocomplete="off" spellcheck="false" data-key="${esc(k.env)}" placeholder="${k.added ? `${k.where === "Editors.Hub" ? "Saved" : "Already on this computer"}${k.ends ? " · ends …" + esc(k.ends) : ""} - paste to replace` : "Paste your " + esc(k.service) + " key"}">
        <button class="btn small" data-save="${esc(k.env)}">Save</button>
        ${k.where === "Editors.Hub" ? `<button class="btn small" data-unset="${esc(k.env)}">Remove</button>` : ""}
        <a class="small-print" href="${esc(k.url)}" target="_blank" rel="noopener">Get a key ↗</a>
      </div></div>`).join("");
  $("keyFile").textContent = `Saved in ${data.file}`;
}

async function loadKeys() {
  try {
    renderKeys(await api("GET", "/api/keys"));
  } catch (e) {}
}

$("keyList").addEventListener("click", async (e) => {
  const save = e.target.closest("[data-save]"), unset = e.target.closest("[data-unset]");
  if (!save && !unset) return;
  const env = (save || unset).dataset.save || (save || unset).dataset.unset;
  try {
    if (save) {
      const input = $("keyList").querySelector(`[data-key="${env}"]`);
      if (!input.value.trim()) return toast("Paste the key first", true);
      renderKeys(await api("POST", "/api/keys", { env, value: input.value }));
      toast("Key saved");
    } else if (await ehConfirm("Editors.Hub stops using this key on this computer.", { title: "Remove this key?", ok: "Remove", danger: true })) {
      renderKeys(await api("POST", "/api/keys", { env, remove: true }));
      toast("Key removed");
    }
    loadSetup();
  } catch (ex) {
    toast(ex.message, true);
  }
});

// ---- who is signed in

function renderMe(me) {
  const owner = me.role === "owner";
  document.body.className = "role-" + me.role;
  document.querySelectorAll("[data-owner]").forEach((el) => (el.hidden = !owner));
  document.querySelector('[data-tab="team"]').hidden = !owner || S.state?.alone !== false;
  const report = S.state?.report;
  $("reportTab").hidden = !report;
  $("reportLabel").textContent = report?.inbox ? "Reports" : "Report to owner";
  const title = owner && S.state?.alone !== false ? "member" : me.role;  // someone else's copy: it's theirs to run, but the studio's owner is the owner
  $("me").innerHTML = `<div class="who">${esc(me.username)}<small>${esc(title)}</small></div><div class="avatar">${esc(me.username[0])}</div>`;
  $("meBadge").textContent = me.username[0].toUpperCase();
  $("meName").textContent = me.username;
  $("meInfo").textContent = `${me.email} · ${title}${title === "owner" ? " (admin)" : ""}`;
}

async function signOut() {
  await api("POST", "/api/auth/signout").catch(() => {});
  location.href = "/signin";
}
$("signOutBtn").onclick = signOut;
$("renameMeBtn").onclick = async () => {
  const name = await ehPrompt("Letters, numbers, dots, dashes or underscores.", S.state.me.username, { title: "Your new username" });
  if (!name || name.trim() === S.state.me.username) return;
  try {
    await api("POST", "/api/me/username", { username: name.trim() });
    await load();
    toast(`You're now ${name.trim()}`);
  } catch (e) {
    toast(e.message, true);
  }
};
$("me").onclick = () => setTab("settings");

// ---- team (owner only)

let teamTimer;
function renderTeam(t) {
  $("pendingList").innerHTML = t.pending.length ? t.pending.map((c) => `<div class="member">
      <span class="code-big">${esc(c.code)}</span>
      <div><b>${esc(c.username)}</b> wants to ${c.purpose === "signup" ? "join" : "sign in"}<small>${esc(c.email)} · ${Math.ceil(c.expires_in / 60)} min left</small></div>
      <span></span>
      <button class="btn small" data-cancel="${esc(c.email)}">Don't let in</button></div>`).join("")
    : `<p class="faint" style="padding:8px 10px;margin:0">No one is waiting. When someone signs up or in, their code shows here${t.mail.ready ? " and in your email" : ""}.</p>`;
  $("memberList").innerHTML = t.members.map((m) => `<div class="member">
      <div class="avatar">${esc(m.username[0])}</div>
      <div><b>${esc(m.username)}</b><small>${esc(m.email)} · last seen ${m.last_seen ? ago(m.last_seen) : "never"}</small></div>
      ${m.role === "owner" ? `<span class="pill s-in-review">owner</span><span></span>` :
        `<select data-role="${esc(m.email)}">${["editor", "reviewer"].map((r) => `<option${r === m.role ? " selected" : ""}>${r}</option>`).join("")}</select>
         <button class="btn small" data-remove="${esc(m.email)}">Remove</button>`}</div>`).join("");
  const mf = $("mailForm");
  $("mailState").textContent = t.mail.ready ? "on" : "off";
  $("mailState").className = "pill " + (t.mail.ready ? "s-approved" : "s-delivered");
  if (document.activeElement?.form !== mf) mf.elements.user.value = t.mail.user || t.owner_email;
  $("lanToggle").checked = t.lan;
  $("lanText").innerHTML = t.lan
    ? (t.lan_live ? `On. People on the same Wi-Fi open <b>${t.lan_urls.map(esc).join(", ") || "this computer's address"}</b> and sign in (you still give them the code).`
                  : `On from the next start: quit Editors.Hub and open it again.`)
    : "Off: only this computer can open the studio. Turn it on so editors and clients on the same Wi-Fi can sign in from their own devices.";
  clearTimeout(teamTimer);
  if (S.tab === "team") teamTimer = setTimeout(loadTeam, 4000);
}

async function loadTeam() {
  try {
    renderTeam(await api("GET", "/api/team"));
  } catch (e) {
    toast(e.message, true);
  }
}

function renderApproved(people) {
  const me = S.state?.me.email;
  $("approvedList").innerHTML = people.map((p) => `<div class="member">
      <div class="avatar">${esc(p.username[0])}</div>
      <div><b>${esc(p.username)}</b><small>${esc(p.email)} · ${p.computers} computer${p.computers === 1 ? "" : "s"}</small></div>
      ${p.email === me ? `<span class="pill s-in-review">you</span><span></span>` :
        `${p.revoked ? `<span class="pill s-delivered">removed</span>` : `<span></span>`}
         <button class="btn small" data-approved="${esc(p.email)}" data-name="${esc(p.username)}" data-removed="${p.revoked ? "" : "1"}">${p.revoked ? "Let back in" : "Remove"}</button>`}</div>`).join("")
    || `<p class="faint" style="padding:8px 10px;margin:0">Nobody yet.</p>`;
}

async function loadApproved() {
  try {
    renderApproved((await api("GET", "/api/approved")).people);
  } catch (e) {
    $("approvedList").innerHTML = `<p class="faint" style="padding:8px 10px;margin:0">${esc(e.message)}</p>`;
  }
}

$("approvedList").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-approved]");
  if (!b) return;
  const removed = !!b.dataset.removed;
  if (removed && !(await ehConfirm(`Their studio stops working within a day or so. Their files stay on their computer, and you can let them back in here.`, { title: `Remove ${b.dataset.name}?`, ok: "Remove", danger: true }))) return;
  try {
    renderApproved((await api("POST", `/api/approved/${enc(b.dataset.approved)}`, { removed })).people);
    toast(removed ? `${b.dataset.name} removed` : `${b.dataset.name} can come back: they'll need a new code from you`);
  } catch (ex) {
    toast(ex.message, true);
  }
});

async function teamAction(method, url, body, msg) {
  try {
    renderTeam(await api(method, url, body));
    if (msg) toast(msg);
  } catch (e) {
    toast(e.message, true);
  }
}

$("pendingList").addEventListener("click", (e) => {
  const b = e.target.closest("[data-cancel]");
  if (b) teamAction("POST", `/api/team/${enc(b.dataset.cancel)}`, { cancel_code: true }, "Code cancelled");
});
$("memberList").addEventListener("change", (e) => {
  const sel = e.target.closest("[data-role]");
  if (sel) teamAction("POST", `/api/team/${enc(sel.dataset.role)}`, { role: sel.value }, `Now ${sel.value}`);
});
$("memberList").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-remove]");
  if (b && await ehConfirm(`${b.dataset.remove} is signed out everywhere and can't come back without a new code from you.`, { title: "Remove this person?", ok: "Remove", danger: true }))
    teamAction("DELETE", `/api/team/${enc(b.dataset.remove)}`, null, "Removed");
});
$("mailForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target, btn = f.querySelector(".btn.primary");
  btn.disabled = true;
  btn.textContent = "Sending a test…";
  await teamAction("POST", "/api/mail", { user: f.elements.user.value, password: f.elements.password.value }, "Email works: check your inbox");
  f.elements.password.value = "";
  btn.disabled = false;
  btn.textContent = "Save and send a test";
});
$("mailClear").onclick = () => teamAction("POST", "/api/mail", { clear: true }, "Email turned off");
$("lanToggle").onchange = async (e) => {
  try {
    await api("POST", "/api/settings", { lan: e.target.checked });
    loadTeam();
  } catch (ex) {
    toast(ex.message, true);
  }
};

// ---- report to owner

function seenAnswers(value) {
  try {
    if (value !== undefined) localStorage.setItem("reportsSeen", value);
    return Number(localStorage.getItem("reportsSeen")) || 0;
  } catch (e) {
    return 0;
  }
}

function renderReports(reports) {
  const label = { open: "sent", answered: "answered", done: "done" };
  $("reportList").innerHTML = reports.slice().reverse().map((r) => `<div class="member" style="grid-template-columns:1fr auto">
      <div><b>${r.kind === "help" ? "I need help" : "A glitch or issue"}</b><small>${new Date(r.created * 1000).toLocaleString()}${r.shot ? " · with a screenshot" : ""}</small>
        <p style="white-space:pre-wrap;margin:6px 0 0">${esc(r.message)}</p>
        ${r.reply ? `<p style="white-space:pre-wrap;margin:8px 0 0;padding-left:10px;border-left:3px solid var(--red)"><b>Owner's answer:</b> ${esc(r.reply)}</p>` : ""}</div>
      <span class="pill ${r.status === "open" ? "s-in-review" : "s-approved"}">${label[r.status] || esc(r.status)}</span></div>`).join("")
    || `<p class="faint" style="padding:8px 10px;margin:0">Nothing sent yet.</p>`;
}

async function loadReports(justCount) {
  const { reports } = await api("GET", "/api/report");
  const newest = Math.max(0, ...reports.map((r) => r.replied || 0));
  if (!justCount) seenAnswers(newest);
  const fresh = reports.filter((r) => (r.replied || 0) > seenAnswers()).length;
  $("reportCount").textContent = fresh || "";
  if (!justCount) renderReports(reports);
}

function openReports() {
  const report = S.state?.report;
  $("reportSend").hidden = !report?.send;
  $("reportInbox").hidden = !report?.inbox;
  if (report?.inbox) $("reportAdmin").href = report.inbox;
  if (report?.send) loadReports().catch((e) => {
    $("reportList").innerHTML = `<p class="faint" style="padding:8px 10px;margin:0">${esc(e.message)}</p>`;
  });
}

async function shrinkScreenshot(file) {  // a request here can only be so big, and a screenshot doesn't need to be full size
  const picture = await createImageBitmap(file);
  const scale = Math.min(1, 1600 / Math.max(picture.width, picture.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(picture.width * scale);
  canvas.height = Math.round(picture.height * scale);
  canvas.getContext("2d").drawImage(picture, 0, 0, canvas.width, canvas.height);
  for (const quality of [0.8, 0.6, 0.4]) {
    const data = canvas.toDataURL("image/jpeg", quality);
    if (data.length < 700000) return data;
  }
  throw new Error("That screenshot is too big to send. Try a smaller one.");
}

$("reportForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target, send = f.querySelector("button.primary");
  send.disabled = true;
  try {
    const file = f.elements.shot.files[0];
    await api("POST", "/api/report", { kind: f.elements.kind.value, message: f.elements.message.value, shot: file ? await shrinkScreenshot(file) : undefined });
    f.reset();
    toast("Sent to the owner");
    await loadReports();
  } catch (ex) {
    toast(ex.message, true);
  } finally {
    send.disabled = false;
  }
});

// ---- Recently deleted (bottom of My styles)

async function loadTrash() {
  let items = [];
  try { items = (await api("GET", "/api/trash")).items; } catch (e) { return; }
  S.deleted = items;
  $("deletedCount").textContent = items.length || "";
  const group = (title, list) => list.length ? `<section class="deleted-group"><h3>${title}</h3>${list.map((i) => `<div class="trash-row"><div><b>${esc(i.name)}</b><small>${i.videos} video${i.videos === 1 ? "" : "s"} · deleted ${ago(i.deleted)}${i.shared ? " · was shared" : ""}</small></div>
    <div class="row"><button class="btn small" data-restore="${esc(i.trash)}">Restore</button><button class="btn small danger" data-erase="${esc(i.trash)}">Delete forever</button></div></div>`).join("")}</section>` : "";
  $("deletedList").innerHTML = group("Clients", items.filter((i) => i.kind === "project")) + group("Styles", items.filter((i) => i.kind !== "project")) ||
    `<div class="empty"><h3>Nothing here</h3><p>When you delete a client or a style, it waits here until you restore it.</p></div>`;
}
const restoreFromTrash = async (e) => {
  const b = e.target.closest("[data-restore]");
  if (!b) return;
  try {
    const r = await api("POST", `/api/trash/${enc(b.dataset.restore)}/restore`, {});
    toast(`"${r.name}" is back`);
    await load();
    loadTrash();
    setTab(r.kind === "project" ? "projects" : "styles");
  } catch (ex) { toast(ex.message, true); }
};
$("deletedList").addEventListener("click", restoreFromTrash);
$("deletedList").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-erase]");
  if (!b) return;
  const i = S.deleted.find((x) => x.trash === b.dataset.erase);
  if (!i) return;
  const client = i.kind === "project";
  const using = client ? 0 : S.state.videos.filter((v) => v.style === i.id && v.project).length;
  const what = client ? "their details and brand files" : "its guide, references and files";
  const message = `"${i.name}", with ${what}${i.videos ? `, plus ${i.videos} video${i.videos === 1 ? "" : "s"} with footage and drafts,` : ""} will be erased from this computer. This can't be undone.` +
    (using ? ` ${using} client video${using === 1 ? " still uses" : "s still use"} this style and would need another one.` : "");
  if (!(await ehConfirm(message, { title: "Delete forever?", ok: "Delete forever", danger: true }))) return;
  b.disabled = true;
  try {
    const r = await api("DELETE", `/api/trash/${enc(i.trash)}`);
    toast(`"${r.name}" is gone for good`);
  } catch (ex) {
    toast(ex.message, true);
  }
  await load();
  loadTrash();
});

function setTab(tab, allow) {
  const owner = S.state?.me.role === "owner";
  if ((tab === "team" || tab === "setup") && S.state && !owner) tab = "videos";
  if (tab === "team" && S.state?.alone) tab = "videos";
  // the owner finishes setup first; Settings stays open so keys can be added
  if (owner && wasReady === false && !["setup", "settings", "report"].includes(tab) && !allow) {
    toast("Finish setting up first");
    tab = "setup";
  }
  if (tab === "settings" && owner) { loadSkills(); loadKeys(); }
  if (tab === "team") { loadTeam(); loadApproved(); }
  if (tab === "report") openReports();
  if (tab === "deleted") loadTrash();
  if (tab === "shared") loadOnlineGrid();
  if (tab === "effects") loadEffects();
  if (tab === "setup") loadSetup();
  S.tab = tab;
  document.querySelectorAll(".tabs button").forEach((b) => b.classList.toggle("on", b.dataset.tab === tab));
  ["videos", "projects", "styles", "shared", "effects", "deleted", "team", "report", "settings", "setup"].forEach((t) => ($("tab-" + t).hidden = t !== tab));
  history.replaceState(null, "", tab === "videos" ? "/" : "/#" + tab);
}

function setVideoFor(kind) {
  const training = kind === "training", f = $("videoForm");
  S.videoFor = kind;
  document.querySelectorAll("#videoFor button").forEach((b) => b.classList.toggle("on", b.dataset.for === kind));
  $("videoProject").hidden = training;
  f.elements.project.required = !training;
  f.elements.name.placeholder = training ? "e.g. Reference reel 1" : "e.g. Podcast ep 12 - reel 1";
  $("videoStyleHint").textContent = training ? "The style this video trains." : "How it's edited.";
  $("videoBriefHint").textContent = training ? "What this video should teach the style." : "What this video needs: length, hook, notes from the client.";
}

function openVideoDlg(styleId, projectId, training) {
  if (!training && !S.state.projects.length) { toast("First add the client this video is for"); return openProjectDlg(); }
  if (!S.state.styles.length) { toast("Now make a style for the video"); return openStyleDlg(); }
  const f = $("videoForm");
  f.reset();
  f.querySelector(".error").textContent = "";
  f.querySelector(".progress").hidden = true;
  f.elements.style.innerHTML = S.state.styles.map((s) => `<option value="${esc(s.id)}">${esc(s.name)}${s.format ? " · " + STYLE_FORMATS[s.format] : ""}</option>`).join("");
  f.elements.style.value = styleId || S.style || S.state.styles[0].id;
  f.elements.project.innerHTML = S.state.projects.map((p) => `<option value="${esc(p.id)}">${esc(p.name)}</option>`).join("");
  if (S.state.projects.length) f.elements.project.value = projectId || S.project || S.state.projects[0].id;
  setVideoFor(training ? "training" : "client");
  $("videoDlg").showModal();
  f.elements.name.focus();
}

function openProjectDlg() {
  const f = $("projectForm");
  f.reset();
  f.querySelector(".error").textContent = "";
  f.querySelector(".progress").hidden = true;
  $("projectDlg").showModal();
  f.elements.name.focus();
}

function openStyleDlg() {
  const f = $("styleForm"), btn = f.querySelector(".btn.primary");
  f.reset();
  f.querySelector(".error").textContent = "";
  f.querySelector(".progress").hidden = true;
  btn.disabled = false;
  btn.textContent = "Make style";
  $("styleDlg").showModal();
}

$("videoForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target, err = f.querySelector(".error"), bar = f.querySelector(".progress");
  const btn = f.querySelector(".btn.primary");
  btn.disabled = true;
  err.textContent = "";
  try {
    const { id } = await api("POST", "/api/videos", { name: f.elements.name.value, style: f.elements.style.value, brief: f.elements.brief.value,
      ...(S.videoFor === "training" ? { training: true } : { project: f.elements.project.value }) });
    const files = [...f.elements.raw.files];
    if (files.length) {
      bar.hidden = false;
      const total = files.reduce((n, x) => n + x.size, 0);
      let done = 0;
      for (const file of files) {
        btn.textContent = `Copying ${file.name}…`;
        await upload(`/api/videos/${enc(id)}/upload?kind=raw&name=${enc(file.name)}`, file,
          (p) => (bar.firstElementChild.style.width = `${((done + p * file.size) / total) * 100}%`));
        done += file.size;
      }
    }
    await api("POST", `/api/videos/${enc(id)}/start`, {});  // every file is in: a Claude session can start the edit
    location.href = `/review/${enc(id)}`;
  } catch (ex) {
    err.textContent = ex.message;
    btn.disabled = false;
    btn.textContent = "Make video";
  }
});

// a new client or style gets its own parent session: the page can't create one, so this is the one paste it takes
async function askForParentSession(url, name) {
  try {
    const page = await api("GET", url);
    let copied = true;
    try { await navigator.clipboard.writeText(page.claude_prompt); } catch (e) { copied = false; }  // it's in the box to copy by hand
    await ehPrompt(`Start a new session in Claude and paste this${copied ? " (it's already copied)" : ""}. It becomes ${name}'s parent session, and each of their videos then starts by itself in its own subsession.`, page.claude_prompt, { title: `Give ${name} a Claude session`, ok: "Done", cancel: "Later" });
  } catch (e) { /* the page has it too: Copy a prompt for Claude */ }
}

$("projectForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target, err = f.querySelector(".error"), bar = f.querySelector(".progress"), btn = f.querySelector(".btn.primary");
  btn.disabled = true;
  err.textContent = "";
  try {
    const el = f.elements;
    const p = await api("POST", "/api/projects", { name: el.name.value, contact: el.contact.value, website: el.website.value, about: el.about.value, brand: el.brand.value });
    const files = [...el.files.files];
    if (files.length) {
      bar.hidden = false;
      const total = files.reduce((n, x) => n + x.size, 0);
      let done = 0;
      for (const file of files) {
        btn.textContent = `Adding ${file.name}…`;
        await upload(`/api/projects/${enc(p.id)}/upload?section=auto&name=${enc(file.name)}`, file,
          (x) => (bar.firstElementChild.style.width = `${((done + x * file.size) / total) * 100}%`));
        done += file.size;
      }
    }
    $("projectDlg").close();
    await askForParentSession(`/api/projects/${enc(p.id)}`, el.name.value.trim());
    location.href = `/project/${enc(p.id)}`;
  } catch (ex) {
    err.textContent = ex.message;
    btn.disabled = false;
    btn.textContent = "Make project";
  }
});

$("styleForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target, el = f.elements, err = f.querySelector(".error"), bar = f.querySelector(".progress"), btn = f.querySelector(".btn.primary");
  btn.disabled = true;
  err.textContent = "";
  let s;
  try {
    s = await api("POST", "/api/styles", { name: el.name.value, notes: el.notes.value, format: el.format.value, links: el.links.value.split("\n") });
  } catch (ex) {
    err.textContent = ex.message;
    btn.disabled = false;
    return;
  }
  // the files go in after the style exists, so one that fails doesn't lose the rest
  const files = [...[...el.references.files].map((file) => ["references", file]), ...[...el.projects.files].map((file) => ["projects", file])];
  const total = files.reduce((n, [, file]) => n + file.size, 0), failed = [];
  let done = 0;
  bar.hidden = !files.length;
  for (const [section, file] of files) {
    btn.textContent = `Adding ${file.name}…`;
    try {
      await upload(`/api/styles/${enc(s.id)}/upload?section=${section}&name=${enc(file.name)}`, file,
        (p) => (bar.firstElementChild.style.width = `${((done + p * file.size) / total) * 100}%`));
    } catch (ex) {
      failed.push(file.name);
    }
    done += file.size;
  }
  if (failed.length) {
    err.textContent = `The style is made, but these couldn't be added: ${failed.join(", ")}. You can add them on its page.`;
    btn.textContent = "Make style";
    await load();
    return;
  }
  $("styleDlg").close();
  await askForParentSession(`/api/styles/${enc(s.id)}`, s.name);
  location.href = `/style/${enc(s.id)}`;
});

$("settingsForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  try {
    S.state = await api("POST", "/api/settings", { library: f.elements.library.value });
    render();
    toast("Saved");
  } catch (ex) {
    toast(ex.message, true);
  }
});

document.addEventListener("click", async (e) => {
  const t = e.target.closest("[data-tab],[data-status],[data-kind],[data-act],[data-style],[data-project]");
  if (!t) return;
  if (t.dataset.tab) return setTab(t.dataset.tab);
  if (t.dataset.status) { S.status = t.dataset.status; return render(); }
  if (t.dataset.kind) { S.kind = t.dataset.kind; S.status = "all"; return render(); }
  const act = t.dataset.act;
  if (act === "new-style") return openStyleDlg();
  if (act === "new-project") return openProjectDlg();
  if (act === "new-video-for") { e.stopPropagation(); return openVideoDlg(null, t.dataset.id); }
  if (act === "new-video") { e.stopPropagation(); return openVideoDlg(t.dataset.id, null, true); }  // from a style: it trains that style
  if (act === "new-training-video") return openVideoDlg(S.style, null, true);
  if (act === "menu") {
    e.stopPropagation();
    const st = S.state.styles.find((x) => x.id === t.dataset.id);
    return openStyleMenu(t, st, async (where) => {
      await load();
      if (where === "deleted") setTab("deleted");
      else if (where) setTab(where);
    });
  }
  if (act === "reveal-style") {
    e.stopPropagation();
    return api("POST", "/api/reveal", { style: t.dataset.id }).catch((ex) => toast(ex.message, true));
  }
  if (t.dataset.project) location.href = `/project/${enc(t.dataset.project)}`;
  if (t.dataset.style) location.href = `/style/${enc(t.dataset.style)}`;
});

// ---- Import a project: a client saved to a drive or a .zip

$("importProjectBtn").onclick = async () => {
  const f = $("projectImportForm");
  f.reset();
  f.querySelector(".error").textContent = "";
  f.querySelector(".progress").hidden = true;
  $("projectImportNote").textContent = "";
  $("projectImportGo").disabled = false;
  $("projectImportDlg").showModal();
  try {
    const t = await api("GET", "/api/transfer?type=project");
    $("foundProjects").innerHTML = t.exports.length
      ? t.exports.map((x, i) => `<label><input type="radio" name="found" value="${esc(x.path)}"${i === 0 ? " checked" : ""}> <b>${esc(x.name)}</b> <span class="faint">${esc(x.where)} · ${gb(x.bytes)}${x.kind === "zip" ? " · .zip" : ""}</span></label>`).join("")
      : `<p class="faint" style="margin:0">No saved clients found on your drives, Desktop, Downloads or cloud folders. Type the folder's place below.</p>`;
    $("projectImportNote").textContent = `Space in your library: ${gb(t.library_free)}.`;
  } catch (e) {
    $("foundProjects").textContent = e.message;
  }
};

$("projectImportForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target, err = f.querySelector(".error"), bar = f.querySelector(".progress");
  const zip = f.elements.zip.files[0];
  const path = f.elements.path.value.trim() || f.querySelector("input[name=found]:checked")?.value;
  if (!zip && !path) return (err.textContent = "Pick a saved client, type the folder's place, or choose a .zip.");
  $("projectImportGo").disabled = true;
  err.textContent = "";
  bar.hidden = false;
  try {
    let job;
    if (zip) {
      $("projectImportNote").textContent = `Uploading ${zip.name}…`;
      job = await upload(`/api/import-project/upload?name=${enc(zip.name)}`, zip, (p) => (bar.firstElementChild.style.width = `${p * 50}%`));
    } else {
      job = await api("POST", "/api/import-project", { path });
    }
    window.dispatchEvent(new Event("editorshub:jobs"));
    $("projectImportNote").textContent = job.title + "…";
    while (job.state === "running") {
      const part = job.total_bytes ? job.done_bytes / job.total_bytes : 0.05;
      bar.firstElementChild.style.width = `${zip ? 50 + part * 50 : part * 100}%`;
      await new Promise((r) => setTimeout(r, 700));
      job = await api("GET", `/api/jobs/${job.id}`);
    }
    if (job.state !== "done") throw new Error(job.message);
    bar.firstElementChild.style.width = "100%";
    const r = job.result;
    await load();
    setTab("projects");
    if (r.missing_styles.length) {
      $("projectImportNote").innerHTML = `<b>${esc(r.name)}</b> is in Projects with ${r.videos} video${r.videos === 1 ? "" : "s"}. Bring in ${r.missing_styles.length === 1 ? "this style" : "these styles"} from My styles too, or pick another on each video: <b>${r.missing_styles.map(esc).join(", ")}</b>.`;
    } else {
      $("projectImportDlg").close();
      toast(`${r.name} is in Projects (${r.videos} video${r.videos === 1 ? "" : "s"})`);
    }
  } catch (ex) {
    err.textContent = ex.message;
    $("projectImportGo").disabled = false;
  }
});

// ---- Add a style: from a folder, or from the online Shared folder

const gb = (n) => (n >= 1e9 ? `${(n / 1e9).toFixed(1)} GB` : `${Math.max(1, Math.round(n / 1e6))} MB`);
let addSource = "folder", onlineCache = null;

function setSource(src) {
  addSource = src;
  document.querySelectorAll("#srcTabs button").forEach((b) => b.classList.toggle("on", b.dataset.src === src));
  $("srcFolder").hidden = src !== "folder";
  $("srcOnline").hidden = src !== "online";
  $("importGo").textContent = src === "online" ? "Download" : "Add";
  if (src === "online") loadOnlineList();
}
$("srcTabs").onclick = (e) => { const b = e.target.closest("button"); if (b) setSource(b.dataset.src); };

async function fetchOnline(force) {
  if (!onlineCache || force) onlineCache = await api("GET", "/api/online");
  return onlineCache;
}

function onlineLine(x) {
  return `${gb(x.size)} · ${x.videos ?? 0} video${x.videos === 1 ? "" : "s"} · by ${esc(x.uploaded_by || x.maker_name || "?")} · ${x.uploaded ? ago(x.uploaded) : ""}${x.complete ? "" : " · upload not finished"}`;
}

async function loadOnlineList(pick) {
  $("onlineList").textContent = "Looking online…";
  try {
    const o = await fetchOnline(true);
    if (!o.ready) return ($("onlineList").innerHTML = `<p class="faint" style="margin:0">${esc(o.message)}</p>`);
    $("onlineList").innerHTML = o.styles.length
      ? o.styles.map((x, i) => `<label><input type="radio" name="online" value="${esc(x.tag)}"${(pick ? x.tag === pick : i === 0) ? " checked" : ""}${x.complete ? "" : " disabled"}> <b>${esc(x.name)}</b> <span class="faint">${onlineLine(x)}</span></label>`).join("")
      : `<p class="faint" style="margin:0">Nothing in the online Shared folder yet. Upload a style from its ⋯ menu.</p>`;
  } catch (e) {
    $("onlineList").textContent = e.message;
  }
}

async function openAddStyle(src = "folder", pick) {
  const f = $("importForm");
  f.reset();
  f.querySelector(".error").textContent = "";
  f.querySelector(".progress").hidden = true;
  $("importNote").textContent = "";
  $("importGo").disabled = false;
  setSource(src);
  if (src === "online") loadOnlineList(pick);
  $("importDlg").showModal();
  try {
    const t = await api("GET", "/api/transfer");
    $("foundExports").innerHTML = t.exports.length
      ? t.exports.map((x, i) => `<label><input type="radio" name="found" value="${esc(x.path)}"${i === 0 ? " checked" : ""}> <b>${esc(x.name)}</b> <span class="faint">${esc(x.where)} · ${gb(x.bytes)}${x.kind === "zip" ? " · .zip" : ""}</span></label>`).join("")
      : `<p class="faint" style="margin:0">No saved styles found on your drives, Desktop, Downloads or cloud folders. Type the folder's place below.</p>`;
    $("importNote").textContent = `Space in your library: ${gb(t.library_free)}.`;
  } catch (e) {
    $("foundExports").textContent = e.message;
  }
}
$("importBtn").onclick = () => openAddStyle("folder");

$("importForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target, err = f.querySelector(".error"), bar = f.querySelector(".progress");
  const zip = addSource === "folder" ? f.elements.zip.files[0] : null;
  const path = addSource === "folder" ? (f.elements.path.value.trim() || f.querySelector("input[name=found]:checked")?.value) : null;
  const tag = addSource === "online" ? f.querySelector("input[name=online]:checked")?.value : null;
  if (addSource === "online" && !tag) return (err.textContent = "Pick a style from the online Shared folder.");
  if (addSource === "folder" && !zip && !path) return (err.textContent = "Pick a saved style, type the folder's place, or choose a .zip.");
  $("importGo").disabled = true;
  err.textContent = "";
  bar.hidden = false;
  try {
    let job;
    if (tag) {
      job = await api("POST", `/api/online/${enc(tag)}/download`, {});
      window.dispatchEvent(new Event("editorshub:jobs"));
    } else if (zip) {
      $("importNote").textContent = `Uploading ${zip.name}…`;
      job = await upload(`/api/import/upload?name=${enc(zip.name)}`, zip, (p) => (bar.firstElementChild.style.width = `${p * 50}%`));
    } else {
      job = await api("POST", "/api/import", { path });
    }
    $("importNote").textContent = job.title + "…";
    while (job.state === "running") {
      const part = job.total_bytes ? job.done_bytes / job.total_bytes : 0.05;
      bar.firstElementChild.style.width = `${(zip ? 50 + part * 50 : part * 100)}%`;
      await new Promise((r) => setTimeout(r, 700));
      job = await api("GET", `/api/jobs/${job.id}`);
    }
    if (job.state !== "done") throw new Error(job.message);
    bar.firstElementChild.style.width = "100%";
    const r = job.result;
    $("importDlg").close();
    const sorted = r.sorted ? " · " + Object.entries(r.sorted).map(([k, n]) => `${n} in ${k}`).join(", ") : "";
    toast(`${r.name} is in My styles (${r.videos} videos${sorted})`);
    await load();
    setTab("styles");
  } catch (ex) {
    err.textContent = ex.message;
    $("importGo").disabled = false;
  }
});

// ---- the Effects tab: the owner's mix of every style's effects
let effects = null, effectsTimer = null;
const effectUrl = (source, file) => `/effects-media/${enc(source)}/${file.split("/").map(enc).join("/")}`;
async function loadEffects() {
  clearTimeout(effectsTimer);
  try {
    effects = await api("GET", "/api/effects");
  } catch (e) {
    $("effectsOnline").innerHTML = `<p class="error">${esc(e.message)}</p>`;
    return;
  }
  const keep = $("effectsStyle").value;
  $("effectsStyle").innerHTML = `<option value="">All styles</option>` + effects.styles.map((s) => `<option value="${esc(s.key)}">${esc(s.name)}${s.online ? " · online" : ""}</option>`).join("");
  $("effectsStyle").value = effects.styles.some((s) => s.key === keep) ? keep : "";
  const n = effects.pending.length, gb = effects.pending.reduce((t, p) => t + (p.size || 0), 0) / 1e9;
  $("effectsOnline").innerHTML = effects.collecting ? `<div class="effects-online"><b>Collecting effects from the online folder…</b><span class="muted">See the progress at the bottom right.</span></div>`
    : n ? `<div class="effects-online"><div><b>${n} online style${n === 1 ? "" : "s"} not in the library yet</b><br><span class="muted">${esc(effects.pending.map((p) => p.name).join(", "))}. Downloads about ${gb.toFixed(1)} GB; only the effects and guide are kept.</span></div><button class="btn primary small" id="effectsCollect">Collect them</button></div>`
    : effects.problem ? `<p class="faint small-print">${esc(effects.problem)}</p>` : "";
  if (effects.can_remove && effects.removed) $("effectsOnline").insertAdjacentHTML("beforeend", `<div class="effects-online"><span class="muted">${effects.removed} removed by you, for everyone.</span><button class="btn small" id="effectsBack">Bring them all back</button></div>`);
  if ($("effectsBack")) $("effectsBack").onclick = async () => {
    try {
      await api("POST", "/api/effects/remove", { ids: [], restore: true });
      toast("They're back");
      loadEffects();
    } catch (e) { toast(e.message, true); }
  };
  if ($("effectsCollect")) $("effectsCollect").onclick = async () => {
    try {
      await api("POST", "/api/effects/collect", {});
      window.dispatchEvent(new Event("editorshub:jobs"));
      loadEffects();
    } catch (e) { toast(e.message, true); }
  };
  drawEffects();
  if (effects.collecting && S.tab === "effects") effectsTimer = setTimeout(loadEffects, 4000);
}
function drawEffects() {
  if (!effects) return;
  const q = $("effectsSearch").value.trim().toLowerCase(), style = $("effectsStyle").value, kind = $("effectsKind").value;
  const fits = (x, words) => (!style || x.source === style) && (!q || words.toLowerCase().includes(q));
  const items = effects.items.filter((i) => fits(i, `${i.name} ${i.style} ${i.section}`) && (!kind || i.section === kind));
  const tech = effects.techniques.filter((t) => fits(t, `${t.text} ${t.heading} ${t.style}`));
  $("effectsCount").textContent = `Effects · ${items.length}`;
  $("techCount").textContent = `Techniques · ${tech.length}`;
  $("effectsGrid").innerHTML = items.slice(0, 300).map((i) => {
    const url = effectUrl(i.source, i.file);
    const view = i.kind === "video" ? `<video src="${esc(url)}#t=0.1" muted loop playsinline preload="metadata"${i.poster ? ` poster="${esc(effectUrl(i.source, i.poster))}"` : ""}></video>`
      : i.kind === "image" ? `<img src="${esc(url)}" alt="" loading="lazy">`
      : i.kind === "audio" ? `<audio src="${esc(url)}" controls preload="none"></audio>` : `<div class="effect-file">${esc((i.name.split(".").pop() || "").toUpperCase())}</div>`;
    return `<a class="effect" href="${esc(url)}" target="_blank" rel="noopener"><div class="effect-view">${view}</div><b title="${esc(i.name)}">${esc(i.name)}</b><small>${esc(i.style)} · ${i.section === "transitions" ? "Transition" : "Effect"}</small>${effects.can_remove ? `<button type="button" class="btn small effect-remove" data-effect-remove="${esc(i.rid)}">Remove</button>` : ""}</a>`;
  }).join("") || `<p class="faint" style="margin:0">No effects here yet. Add files to the Effects or Transitions section of any style.</p>`;
  $("techList").innerHTML = tech.slice(0, 400).map((t) => `<div class="tech"><p>${esc(t.text)}</p><small>${esc(t.style)}${t.heading ? ` · ${esc(t.heading)}` : ""}</small>${effects.can_remove ? `<button type="button" class="btn small effect-remove" data-effect-remove="${esc(t.rid)}">Remove</button>` : ""}</div>`).join("")
    || `<p class="faint" style="margin:0">Nothing here yet. Techniques come from each style's guide.</p>`;
}
$("tab-effects").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-effect-remove]");
  if (!b) return;
  e.preventDefault();
  if (!(await ehConfirm("It leaves the Effects section for everyone, and Claude stops using it. The style it came from keeps it.", { title: "Remove this effect?", ok: "Remove", danger: true }))) return;
  try {
    await api("POST", "/api/effects/remove", { ids: [b.dataset.effectRemove] });
    loadEffects();
  } catch (ex) { toast(ex.message, true); }
});
$("effectsSearch").addEventListener("input", drawEffects);
$("effectsStyle").addEventListener("change", drawEffects);
$("effectsKind").addEventListener("change", drawEffects);
$("effectsGrid").addEventListener("mouseover", (e) => e.target.closest(".effect")?.querySelector("video")?.play().catch(() => {}));
$("effectsGrid").addEventListener("mouseout", (e) => e.target.closest(".effect")?.querySelector("video")?.pause());

// the online Shared folder, listed on the Shared tab
async function loadOnlineGrid() {
  try {
    const o = await fetchOnline(true);
    if (!o.ready) {
      $("onlineGrid").innerHTML = "";
      $("onlineNote").textContent = o.message;
      return;
    }
    $("onlineNote").textContent = o.drive ? "Download one and it's added to your styles. To share your own: on any of your styles, ⋯ → Share online."
      : `Styles uploaded online (${o.repo}) can be downloaded into Editors.Hub on any of your computers.`;
    $("onlineGrid").innerHTML = o.styles.map((x) => `<div class="online-card">
        <div class="row"><b>${esc(x.name)}</b><div class="spacer"></div>${(x.palette || []).length ? `<span class="swatches">${x.palette.slice(0, 5).map((c) => `<i style="background:${esc(c)}"></i>`).join("")}</span>` : ""}</div>
        <small>${onlineLine(x)}</small>
        ${x.client ? `<small>Client: ${esc(x.client)}</small>` : ""}
        ${x.notes ? `<small>${esc(x.notes)}</small>` : ""}
        <div class="row" style="flex-wrap:wrap"><div class="spacer"></div>
          ${(x.mine || x.is_owner) && o.drive ? `<button class="btn small" data-online-remove="${esc(x.tag)}" data-name="${esc(x.name)}">Remove</button>` : ""}
          ${x.complete ? `<button class="btn small primary" data-online-get="${esc(x.tag)}">Download</button>` : ""}</div>
      </div>`).join("") || `<p class="faint" style="margin:0">Nothing shared yet. On any of your styles: ⋯ → Share online.</p>`;
  } catch (e) {
    $("onlineNote").textContent = e.message;
  }
}
$("onlineGrid").addEventListener("click", async (e) => {
  const b = e.target.closest("[data-online-get]");
  if (b) return openAddStyle("online", b.dataset.onlineGet);
  const gone = e.target.closest("[data-online-remove]");
  if (!gone) return;
  try {
    if (!(await ehConfirm(`It's deleted from the online Shared folder. Copies people have already downloaded stay with them.`, { title: `Remove "${gone.dataset.name}"?`, ok: "Remove", danger: true }))) return;
    await api("DELETE", `/api/online/${enc(gone.dataset.onlineRemove)}`);
    toast("Removed from the online Shared folder");
    loadOnlineGrid();
  } catch (ex) {
    toast(ex.message, true);
  }
});

$("newVideoBtn").onclick = () => openVideoDlg(null, null, S.tab === "videos" && S.kind === "style");
$("videoFor").onclick = (e) => {
  const b = e.target.closest("[data-for]");
  if (!b) return;
  if (b.dataset.for === "client" && !S.state.projects.length) {
    $("videoDlg").close();
    toast("First add the client this video is for");
    return openProjectDlg();
  }
  setVideoFor(b.dataset.for);
};

// ---- live bars: on a style's card while it uploads, downloads or copies, and "Uploading now" in the online section
S.jobs = [];
function applyJobBars() {
  const running = S.jobs.filter((j) => j.state === "running");
  document.querySelectorAll("#styleGrid .card[data-style]").forEach((card) => {
    const job = running.find((j) => j.style === card.dataset.style);
    let box = card.querySelector(".card-job");
    if (!job) return box && box.remove();
    if (!box) {
      box = document.createElement("div");
      box.className = "card-job";
      card.insertBefore(box, card.querySelector(".row:last-child"));
    }
    box.innerHTML = progressBar(job);
  });
  const uploads = running.filter((j) => j.kind === "online-upload");
  $("onlineUploading").innerHTML = uploads.map((j) => `<div class="online-card is-uploading"><div class="row"><b>${esc(j.title.replace(/^Uploading /, ""))}</b><div class="spacer"></div><span class="share-tag online">Uploading now</span></div>${progressBar(j)}</div>`).join("");
}
window.addEventListener("editorshub:jobs-updated", (e) => {
  S.jobs = e.detail || [];
  applyJobBars();
});
// when an upload, download or copy finishes, show its result here
window.addEventListener("editorshub:job-done", async (e) => {
  await load();
  if (S.tab === "shared") loadOnlineGrid();
  loadTrash();
});
$("newProjectBtn").onclick = () => openProjectDlg();
$("newStyleBtn").onclick = () => openStyleDlg();
$("revealLib").onclick = () => api("POST", "/api/reveal", {}).catch((ex) => toast(ex.message, true));
$("styleFilter").onchange = (e) => { S.style = e.target.value; render(); };
$("projectFilter").onchange = (e) => { S.project = e.target.value; render(); };
$("search").oninput = (e) => { S.q = e.target.value; render(); };

async function tellIfUpdated() {
  const version = S.state?.updated;
  if (!version || document.querySelector("dialog[open]")) return;
  await api("POST", "/api/update-seen", {}).catch(() => {});  // first, so a reload while it's showing doesn't tell them twice
  ehConfirm(`Your studio updated itself to version ${version}. Your videos, clients and styles are all still here.`, { title: "You're on the newest version", ok: "Got it", cancel: "" });
}

load().then(() => {
  if (["projects", "styles", "shared", "effects", "deleted", "team", "report", "settings", "setup"].includes(location.hash.slice(1))) setTab(location.hash.slice(1), true);
  if (S.state?.report?.send) loadReports(true).catch(() => {});  // for the count of new answers
  const wanted = location.hash.match(/^#new-video:(.+)$/);  // "+ Video" on a style page
  if (wanted) {
    history.replaceState(null, "", "/");
    S.kind = "style";
    render();
    openVideoDlg(decodeURIComponent(wanted[1]), null, true);
  }
  const forClient = location.hash.match(/^#new-video-project:(.+)$/);  // "+ Video" on a project page
  if (forClient) {
    history.replaceState(null, "", "/");
    openVideoDlg(null, decodeURIComponent(forClient[1]));
  }
  loadSetup();
  if (S.state?.me.role !== "reviewer") loadTrash();
  tellIfUpdated();
});
setInterval(() => document.visibilityState === "visible" && !document.querySelector("dialog[open]") && load(), 5000);
