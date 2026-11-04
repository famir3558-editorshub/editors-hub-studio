const $ = (id) => document.getElementById(id);
const styleId = decodeURIComponent(location.pathname.split("/")[2] || "");
const openSave = location.hash === "#save";  // "Save to a drive" from a style card's ⋯ menu
const P = { page: null, tab: openSave ? "overview" : (location.hash.slice(1) || "overview"), editing: null, browse: "" };
const smedia = (rel) => `/style-media/${enc(styleId)}/${rel.split("/").map(enc).join("/")}`;
const fixed = ["overview", "videos", "brief", "guide", "rules", "files"];

async function load() {
  try {
    P.page = await api("GET", `/api/styles/${enc(styleId)}`);
  } catch (e) {
    $("pane").innerHTML = `<div class="empty-pane">${esc(e.message)}<br><a href="/#styles">Back to styles</a></div>`;
    return;
  }
  renderHero();
  renderTabs();
  renderPane();
}

function renderHero() {
  const s = P.page;
  document.title = `${s.name} · Editors.Hub`;
  $("sName").textContent = s.name;
  const last = s.last_finished;
  $("sSub").textContent = `/${s.id}` + (last ? ` · last finished: ${last.name}, ${(last.at || last.updated).slice(0, 10)}` : "");
  $("shareTag").textContent = s.online ? "Online" : "Private";
  $("shareTag").className = "share-tag " + (s.online ? "online" : "private");
  const stills = s.videos.filter((v) => v.thumb).slice(0, 4);
  $("stills").dataset.count = stills.length;
  $("stills").innerHTML = stills.length
    ? stills.map((v) => `<a class="still" href="/review/${enc(v.id)}" title="${esc(v.name)}"><img src="/media/${enc(v.id)}/thumb.jpg?${enc(v.updated)}" alt=""></a>`).join("")
    : `<div class="empty-still">${esc(s.name.replace(/[^\p{L}\p{N}\s]/gu, "").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join("").toUpperCase())}</div>`;
  const c = s.counts;
  $("chips").innerHTML = [
    ["videos", `${s.videos.length} style video${s.videos.length === 1 ? "" : "s"}`],
    ["rules", `${s.rules.length} learned rule${s.rules.length === 1 ? "" : "s"}`],
    ["broll", `${c.broll} B-roll`], ["graphics", `${c.graphics} graphics`], ["references", `${c.references} references`],
  ].map(([tab, label]) => `<span class="chip-s" data-tab="${tab}">${label}</span>`).join("") +
    (s.format ? `<span class="chip-s accent" data-tab="brief">${STYLE_FORMATS[s.format]}</span>` : "") +
    (s.client_videos ? `<span class="chip-s">Used in ${s.client_videos} client video${s.client_videos === 1 ? "" : "s"}</span>` : "") +
    (s.guide ? `<span class="chip-s accent" data-tab="guide">Guide</span>` : "");
  $("swatches").innerHTML = (s.palette || []).slice(0, 8).map((h) => `<i style="background:${esc(h)}" title="${esc(h)}"></i>`).join("");
  $("sDesc").textContent = s.notes || "No description yet. Add one in the About tab.";
  $("sClient").textContent = s.client ? `Client: ${s.client}` : "";
  $("briefBtn").hidden = !s.can_edit;
  $("downloadBtn").href = `/api/styles/${enc(styleId)}/download`;
}

function renderTabs() {
  const s = P.page;
  const tabs = [["overview", "Overview"], ["videos", "Style videos", s.videos.length], ["brief", "About"],
    ["references", "References", s.counts.references], ["guide", "Guide"], ["rules", "Learned rules", s.rules.length],
    ...s.sections.filter((x) => x.id !== "references").map((x) => [x.id, x.label, s.counts[x.id]]), ["files", "Files"]];
  $("tabs").innerHTML = tabs.map(([id, label, n]) => `<button data-tab="${id}" class="${P.tab === id ? "on" : ""}">${esc(label)}${n !== undefined ? `<span>${n}</span>` : ""}</button>`).join("");
}

function setTab(tab) {
  P.tab = tab;
  P.editing = null;
  history.replaceState(null, "", "#" + tab);
  renderTabs();
  renderPane();
  window.scrollTo({ top: Math.min(window.scrollY, $("tabs").offsetTop - 70), behavior: "smooth" });
}

function videoCard(v) {
  return `<a class="vcard" href="/review/${enc(v.id)}"><div class="th">${v.thumb ? `<img src="/media/${enc(v.id)}/thumb.jpg?${enc(v.updated)}" alt="" loading="lazy">` : ""}<span class="pill ${statusClass(v.status)}">${esc(v.status)}</span></div><div class="t" title="${esc(v.name)}">${esc(v.name)}</div>${v.project_name ? `<div class="faint small-print">${esc(v.project_name)}</div>` : ""}</a>`;
}

function dropHint(label) {
  return P.page.can_edit ? `<div class="drop-hint" data-pick>Drop files anywhere on this page, or <b>click to choose</b>: they go into ${esc(label)}.</div>` : "";
}

async function renderPane() {
  const s = P.page, pane = $("pane"), tab = P.tab;
  if (tab === "overview") {
    pane.innerHTML = `
      <div class="pane-head"><h2>Videos that train this style</h2><div class="spacer"></div><button class="btn small" data-tab="videos">${s.videos.length} video${s.videos.length === 1 ? "" : "s"}</button></div>
      ${s.videos.length ? `<div class="strip">${s.videos.map(videoCard).join("")}</div>` : `<div class="empty-pane">No training videos yet. Click <b>+ Video</b> to make one. Videos for a client show in their project.</div>`}
      <div class="pane-head" style="margin-top:22px"><h2>Learned rules</h2><div class="spacer"></div><button class="btn small" data-tab="rules">All ${s.rules.length}</button></div>
      ${s.rules.length ? `<ol class="rules">${s.rules.slice(0, 4).map((r) => `<li>${ruleHtml(r)}</li>`).join("")}</ol>` : `<div class="empty-pane">No learned rules yet. They're added when Claude saves a note to this style.</div>`}
      ${s.can_edit ? `<h2 style="margin-top:22px">Add to this style</h2><div class="drop-hint" data-pick>Drop references, B-roll, graphics, LUTs, music, sound effects, fonts or project files (XML, Premiere, After Effects, Final Cut, DaVinci, CapCut) anywhere on this page, or <b>click to choose</b>. Each one is sorted into the right section by its type.</div>` : ""}`;
    return;
  }
  if (tab === "videos") {
    pane.innerHTML = s.videos.length ? `<div class="vgrid">${s.videos.map(videoCard).join("")}</div>` : `<div class="empty-pane">No training videos yet. Videos for a client show in their project.</div>`;
    return;
  }
  if (tab === "brief" || tab === "guide") {
    const text = tab === "brief" ? s.brief : s.guide;
    const label = tab === "brief" ? "description" : "guide (STYLE.md)";
    if (P.editing === tab) {
      pane.innerHTML = `<div class="editor">
        ${tab === "brief" ? `<div class="fields"><label class="field">Format<select id="edFormat"><option value="">Not set</option>${Object.entries(STYLE_FORMATS).map(([k, label]) => `<option value="${k}"${s.format === k ? " selected" : ""}>${label}</option>`).join("")}</select></label><label class="field">Description<input id="edNotes" value="${esc(s.notes || "")}"></label></div>` : ""}
        <textarea id="edText" spellcheck="false">${esc(text)}</textarea>
        <div class="row"><button class="btn ghost" data-cancel>Cancel</button><div class="spacer"></div><button class="btn primary" data-save="${tab}">Save the ${esc(label)}</button></div></div>`;
      return;
    }
    pane.innerHTML = `<div class="pane-head"><h2>${tab === "brief" ? "About this style" : "Guide"}</h2><div class="spacer"></div>${s.can_edit ? `<button class="btn small" data-edit="${tab}">Edit</button>` : ""}</div>
      ${text ? `<div class="doc">${md(text)}</div>` : `<div class="empty-pane">No ${esc(label)} yet.${s.can_edit ? " Click Edit to write one." : ""}</div>`}`;
    return;
  }
  if (tab === "rules") {
    pane.innerHTML = `<div class="pane-head"><h2>Learned rules</h2><span class="faint small-print">Claude reads these before every edit in this style. They're added from review notes ("Saved to ${esc(s.name)}"), and kept in the guide's "Lessons from reviews".</span></div>
      ${s.rules.length ? `<ol class="rules">${s.rules.map((r) => `<li>${ruleHtml(r)}</li>`).join("")}</ol>` : `<div class="empty-pane">No learned rules yet.</div>`}`;
    return;
  }
  if (tab === "files") {
    pane.innerHTML = `<div class="files"><div class="crumb">Loading…</div></div>`;
    try {
      const b = await api("GET", `/api/styles/${enc(styleId)}/browse?path=${enc(P.browse)}`);
      const parts = b.path ? b.path.split("/") : [];
      const crumb = [`<a data-path="">${esc(s.name)}</a>`, ...parts.map((p, i) => `<a data-path="${esc(parts.slice(0, i + 1).join("/"))}">${esc(p)}</a>`)].join(" / ");
      const icon = { folder: "📁", video: "🎬", image: "🖼", audio: "🎵", file: "📄" };
      pane.innerHTML = `<div class="pane-head"><h2>Files</h2><div class="spacer"></div><button class="btn small" id="openHere">Open in ${navigator.platform.startsWith("Win") ? "Explorer" : "Finder"}</button></div>
        <div class="files"><div class="crumb">${crumb}</div>${b.entries.map((e) => `<div class="frow" data-${e.dir ? "path" : "file"}="${esc(e.path)}"><span>${icon[e.kind] || "📄"}</span><span>${esc(e.name)}</span><span class="faint">${e.dir ? "" : fmtSize(e.size)}</span><span class="faint">${new Date(e.modified * 1000).toLocaleDateString()}</span></div>`).join("") || `<div class="frow"><span></span><span class="faint">Empty folder</span></div>`}</div>`;
      $("openHere").onclick = () => api("POST", "/api/reveal", { style: styleId }).catch((e) => toast(e.message, true));
    } catch (e) {
      pane.innerHTML = `<div class="empty-pane">${esc(e.message)}</div>`;
    }
    return;
  }
  // a media section
  const label = s.sections.find((x) => x.id === tab)?.label || tab;
  pane.innerHTML = `<div class="pane-head"><h2>${esc(label)}</h2><span class="faint small-print" id="secCount"></span></div>${dropHint(label)}<div class="media" id="media"><div class="empty-pane">Loading…</div></div>`;
  try {
    const { items } = await api("GET", `/api/styles/${enc(styleId)}/section/${enc(tab)}`);
    if (P.tab !== tab) return;
    $("secCount").textContent = `${items.length} item${items.length === 1 ? "" : "s"}`;
    $("media").innerHTML = items.length ? items.map(tile).join("") : `<div class="empty-pane" style="grid-column:1/-1">Nothing in ${esc(label)} yet.</div>`;
    lazyVideos();
  } catch (e) {
    $("media").innerHTML = `<div class="empty-pane">${esc(e.message)}</div>`;
  }
}

function ruleHtml(rule) {
  const [main, why] = rule.split(/\sWhy:\s/);
  return esc(main) + (why ? ` <em>Why: ${esc(why)}</em>` : "");
}

function tile(it) {
  const url = smedia(it.file);
  let box;
  if (it.kind === "image") box = `<img src="${url}" alt="" loading="lazy">`;
  else if (it.kind === "video") box = it.poster ? `<img src="${smedia(it.poster)}" alt="" loading="lazy" data-video="${url}">` : `<video muted playsinline preload="none" data-src="${url}#t=0.5"></video>`;
  else if (it.kind === "audio") box = `<audio controls preload="none" src="${url}"></audio>`;
  else box = `<span class="icon">📄</span>`;
  return `<a class="tile" href="${url}" target="_blank" rel="noopener" title="${esc(it.file)}"><div class="box">${box}${it.kind !== "image" ? `<span class="badge-k">${esc(it.name.split(".").pop())}</span>` : ""}</div>
    <div class="cap"><b>${esc(it.name)}</b><span>${fmtSize(it.size)}${it.folder.split("/").length > 2 ? " · " + esc(it.folder.split("/").slice(2).join("/")) : ""}</span></div></a>`;
}

// videos without a still only load when they scroll into view; clips with a still play on hover
function lazyVideos() {
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (e.isIntersecting && e.target.dataset.src) { e.target.src = e.target.dataset.src; delete e.target.dataset.src; io.unobserve(e.target); }
  }), { rootMargin: "200px" });
  document.querySelectorAll("video[data-src]").forEach((v) => io.observe(v));
}
document.addEventListener("mouseover", (e) => {
  const img = e.target.closest("img[data-video]");
  if (!img) return;
  const v = document.createElement("video");
  Object.assign(v, { src: img.dataset.video, muted: true, autoplay: true, loop: true, playsInline: true });
  v.poster = img.src;
  img.replaceWith(v);
  v.closest(".tile").addEventListener("mouseleave", () => v.pause(), { once: true });
});

// ---------------------------------------------------------------- actions

document.addEventListener("click", async (e) => {
  const t = e.target.closest("[data-tab],[data-edit],[data-cancel],[data-save],[data-path],[data-file],[data-pick]");
  if (!t) return;
  if (t.dataset.tab) return setTab(t.dataset.tab);
  if (t.dataset.edit) { P.editing = t.dataset.edit; return renderPane(); }
  if ("cancel" in t.dataset) { P.editing = null; return renderPane(); }
  if (t.dataset.save) {
    const body = { [t.dataset.save]: $("edText").value };
    if (t.dataset.save === "brief") { body.notes = $("edNotes").value; body.format = $("edFormat").value; }
    try {
      P.page = await api("POST", `/api/styles/${enc(styleId)}`, body);
      P.editing = null;
      renderHero(); renderTabs(); renderPane();
      toast("Saved");
    } catch (ex) { toast(ex.message, true); }
    return;
  }
  if (t.dataset.path !== undefined && t.classList.contains("frow") || t.tagName === "A" && t.dataset.path !== undefined) {
    P.browse = t.dataset.path;
    return renderPane();
  }
  if (t.dataset.file) return window.open(smedia(t.dataset.file), "_blank", "noopener");
  if ("pick" in t.dataset) return $("fileInput").click();
});

$("sDesc").onclick = () => $("sDesc").classList.toggle("open");
window.addEventListener("editorshub:job-done", () => load());
// this style's upload, download or copy, as a bar under its buttons
window.addEventListener("editorshub:jobs-updated", (e) => {
  const job = (e.detail || []).find((j) => j.state === "running" && j.style === styleId);
  $("pageJob").hidden = !job;
  if (job) $("pageJob").innerHTML = progressBar(job);
});
$("menuBtn").onclick = (e) => {
  e.stopPropagation();
  const s = P.page;
  openStyleMenu(e.currentTarget, { ...s, can_manage: s.can_edit }, (where) => {
    if (where === "deleted") location.href = "/#deleted";
    else if (where === "styles" && !s.shared) location.href = "/#styles";  // a duplicate lands in My styles
    else load();
  });
};
$("promptBtn").onclick = async () => {
  try {
    await navigator.clipboard.writeText(P.page.claude_prompt);
    toast("Copied: paste it into a Claude session");
  } catch (e) {
    await ehPrompt("Copy this and paste it into a Claude session:", P.page.claude_prompt, { title: "Prompt for Claude", ok: "Done", cancel: "Close" });
  }
};
$("briefBtn").onclick = () => { setTab("brief"); P.editing = "brief"; renderPane(); };
$("folderBtn").onclick = () => api("POST", "/api/reveal", { style: styleId }).catch((e) => toast(e.message, true));
$("videoBtn").onclick = () => (location.href = `/#new-video:${enc(styleId)}`);

// ---------------------------------------------------------------- saving the style to a drive

const gb = (n) => (n >= 1e9 ? `${(n / 1e9).toFixed(1)} GB` : `${Math.max(1, Math.round(n / 1e6))} MB`);
async function followJob(job, bar, onDone, onFail) {
  bar.hidden = false;
  while (job.state === "running") {
    bar.firstElementChild.style.width = job.total_bytes ? `${(job.done_bytes / job.total_bytes) * 100}%` : "3%";
    await new Promise((r) => setTimeout(r, 700));
    try { job = await api("GET", `/api/jobs/${job.id}`); } catch (e) { return onFail(e.message); }
  }
  bar.firstElementChild.style.width = "100%";
  job.state === "done" ? onDone(job.result) : onFail(job.message);
}

$("saveBtn").onclick = async () => {
  const f = $("saveForm");
  f.querySelector(".error").textContent = "";
  f.querySelector(".progress").hidden = true;
  $("saveGo").disabled = false;
  $("saveDlg").showModal();
  try {
    const t = await api("GET", "/api/transfer");
    $("places").innerHTML = t.places.map((p, i) => `<label><input type="radio" name="place" value="${esc(p.path)}"${i === 0 ? " checked" : ""}> <b>${esc(p.label)}</b> <span class="faint">${esc(p.path)} · ${gb(p.free)} free</span></label>`).join("") || `<p class="faint">No drives found: type a folder below.</p>`;
  } catch (e) {
    $("places").textContent = e.message;
  }
  const total = Object.values(P.page.counts).reduce((a, b) => a + b, 0);
  const nv = P.page.videos.length;
  $("saveSize").textContent = `${nv} video${nv === 1 ? "" : "s"} and ${total} section item${total === 1 ? "" : "s"}. Big styles take a few minutes; you can keep working.`;
};
$("saveForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target, err = f.querySelector(".error");
  const dest = f.elements.dest.value.trim() || f.querySelector("input[name=place]:checked")?.value;
  if (!dest) return (err.textContent = "Pick a drive or type a folder.");
  $("saveGo").disabled = true;
  err.textContent = "";
  try {
    const job = await api("POST", `/api/styles/${enc(styleId)}/export`, { dest });
    followJob(job, f.querySelector(".progress"),
      (r) => { err.textContent = ""; toast(`Saved to ${r.path}`); $("saveSize").innerHTML = `Saved <b>${gb(r.bytes)}</b> to <b>${esc(r.path)}</b>. On the other computer: My styles → Import a style.`; },
      (m) => { err.textContent = m; $("saveGo").disabled = false; });
  } catch (ex) {
    err.textContent = ex.message;
    $("saveGo").disabled = false;
  }
});

// ---------------------------------------------------------------- adding files

async function addFiles(files) {
  if (!P.page?.can_edit || !files.length) return;
  const section = [...P.page.sections.map((x) => x.id)].includes(P.tab) ? P.tab : "auto";
  $("uploading").hidden = false;
  const landed = {};
  try {
    for (const [i, file] of files.entries()) {
      $("upText").textContent = `Adding ${file.name} (${i + 1} of ${files.length})…`;
      const r = await upload(`/api/styles/${enc(styleId)}/upload?section=${section}&name=${enc(file.name)}`, file, (p) => ($("upBar").style.width = p * 100 + "%"));
      landed[r.label || "Files"] = (landed[r.label || "Files"] || 0) + 1;
    }
    toast("Added: " + Object.entries(landed).map(([k, n]) => `${n} to ${k}`).join(", "));
  } catch (e) {
    toast(e.message, true);
  } finally {
    $("uploading").hidden = true;
    $("upBar").style.width = "0";
    await load();
  }
}
$("fileInput").onchange = (e) => { addFiles([...e.target.files]); e.target.value = ""; };
let depth = 0;
addEventListener("dragenter", (e) => {
  if (!e.dataTransfer.types.includes("Files") || !P.page?.can_edit) return;
  depth++;
  const label = P.page.sections.find((x) => x.id === P.tab)?.label;
  $("dropText").textContent = label ? `Drop to add to ${label}` : "Drop to add: each file goes to the right section";
  $("dropVeil").classList.add("on");
});
addEventListener("dragleave", () => { if (--depth <= 0) { depth = 0; $("dropVeil").classList.remove("on"); } });
addEventListener("dragover", (e) => e.preventDefault());
addEventListener("drop", (e) => { e.preventDefault(); depth = 0; $("dropVeil").classList.remove("on"); addFiles([...e.dataTransfer.files]); });

api("GET", "/api/auth/me").then((me) => me.user && (document.body.className = "role-" + me.user.role)).catch(() => {});
load().then(() => { if (openSave && P.page) { history.replaceState(null, "", "#overview"); $("saveBtn").click(); } });
