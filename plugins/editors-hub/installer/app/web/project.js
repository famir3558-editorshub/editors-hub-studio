const $ = (id) => document.getElementById(id);
const projectId = decodeURIComponent(location.pathname.split("/")[2] || "");
const P = { page: null, tab: location.hash.slice(1) || "overview", editing: null };
const pmedia = (rel) => `/project-media/${enc(projectId)}/${rel.split("/").map(enc).join("/")}`;

async function load() {
  try {
    P.page = await api("GET", `/api/projects/${enc(projectId)}`);
  } catch (e) {
    $("pane").innerHTML = `<div class="empty-pane">${esc(e.message)}<br><a href="/#projects">Back to projects</a></div>`;
    return;
  }
  renderHero();
  renderTabs();
  renderPane();
}

function renderHero() {
  const p = P.page;
  document.title = `${p.name} · Editors.Hub`;
  $("pName").textContent = p.name;
  $("pSub").textContent = `/${p.id}` + (p.contact ? ` · ${p.contact}` : "");
  const stills = p.videos.filter((v) => v.thumb).slice(0, 4);
  $("stills").dataset.count = stills.length;
  $("stills").innerHTML = stills.length
    ? stills.map((v) => `<a class="still" href="/review/${enc(v.id)}" title="${esc(v.name)}"><img src="/media/${enc(v.id)}/thumb.jpg?${enc(v.updated)}" alt=""></a>`).join("")
    : `<div class="empty-still">${esc(p.name.replace(/[^\p{L}\p{N}\s]/gu, "").split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join("").toUpperCase())}</div>`;
  $("chips").innerHTML = [
    ["videos", `${p.videos.length} video${p.videos.length === 1 ? "" : "s"}`],
    ["rules", `${p.rules.length} client rule${p.rules.length === 1 ? "" : "s"}`],
    ...p.sections.map((x) => [x.id, `${p.counts[x.id]} ${x.label.toLowerCase()}`]),
  ].map(([tab, label]) => `<span class="chip-s" data-tab="${tab}">${esc(label)}</span>`).join("") +
    `<span class="chip-s accent" data-tab="brand">Brand guidelines</span>`;
  $("pAbout").textContent = p.about || "No details about this client yet.";
  $("editBtn").hidden = $("deleteBtn").hidden = !p.can_edit;
  $("downloadBtn").href = `/api/projects/${enc(projectId)}/download`;
}

function renderTabs() {
  const p = P.page;
  const tabs = [["overview", "Overview"], ["videos", "Videos", p.videos.length], ["brand", "Brand guidelines"],
    ["rules", "Client rules", p.rules.length], ...p.sections.map((x) => [x.id, x.label, p.counts[x.id]]), ["details", "Details"]];
  $("tabs").innerHTML = tabs.map(([id, label, n]) => `<button data-tab="${id}" class="${P.tab === id ? "on" : ""}">${esc(label)}${n !== undefined ? `<span>${n}</span>` : ""}</button>`).join("");
}

function setTab(tab) {
  P.tab = tab;
  P.editing = null;
  history.replaceState(null, "", "#" + tab);
  renderTabs();
  renderPane();
}

function videoCard(v) {
  return `<a class="vcard" href="/review/${enc(v.id)}"><div class="th">${v.thumb ? `<img src="/media/${enc(v.id)}/thumb.jpg?${enc(v.updated)}" alt="" loading="lazy">` : ""}<span class="pill ${statusClass(v.status)}">${esc(v.status)}</span></div><div class="t" title="${esc(v.name)}">${esc(v.name)}</div><div class="faint small-print">${esc(v.style_name)}</div></a>`;
}

function ruleList(rules) {
  return `<ol class="rules">${rules.map((r) => `<li>${esc(r)}</li>`).join("")}</ol>`;
}

function detailRow(label, value) {
  const link = /^https?:\/\//i.test(value || "") ? `<a href="${esc(value)}" target="_blank" rel="noopener">${esc(value)}</a>` : esc(value || "-");
  return `<p><b>${esc(label)}</b><br>${link}</p>`;
}

async function renderPane() {
  const p = P.page, pane = $("pane"), tab = P.tab;
  if (tab === "overview") {
    pane.innerHTML = `
      <div class="pane-head"><h2>Videos for this client</h2><div class="spacer"></div><button class="btn small" data-tab="videos">${p.videos.length} video${p.videos.length === 1 ? "" : "s"}</button></div>
      ${p.videos.length ? `<div class="strip">${p.videos.map(videoCard).join("")}</div>` : `<div class="empty-pane">No videos yet. Click <b>+ Video</b> and pick a style.</div>`}
      <div class="pane-head" style="margin-top:22px"><h2>Client rules</h2><div class="spacer"></div><button class="btn small" data-tab="rules">All ${p.rules.length}</button></div>
      ${p.rules.length ? ruleList(p.rules.slice(0, 4)) : `<div class="empty-pane">No client rules yet. They're added when Claude saves a note about this client.</div>`}
      ${p.can_edit ? `<h2 style="margin-top:22px">Add brand files</h2><div class="drop-hint" data-pick>Drop the brandbook, logos, fonts or other client files anywhere on this page, or <b>click to choose</b>. Each one is sorted by its type.</div>` : ""}`;
    return;
  }
  if (tab === "videos") {
    pane.innerHTML = p.videos.length ? `<div class="vgrid">${p.videos.map(videoCard).join("")}</div>` : `<div class="empty-pane">No videos yet.</div>`;
    return;
  }
  if (tab === "brand") {
    if (P.editing === "brand") {
      pane.innerHTML = `<div class="editor"><textarea id="edText" spellcheck="false">${esc(p.brand)}</textarea>
        <div class="row"><button class="btn ghost" data-cancel>Cancel</button><div class="spacer"></div><button class="btn primary" data-save-brand>Save the guidelines</button></div></div>`;
      return;
    }
    pane.innerHTML = `<div class="pane-head"><h2>Brand guidelines</h2><div class="spacer"></div>${p.can_edit ? `<button class="btn small" data-edit="brand">Edit</button>` : ""}</div>
      ${p.brand ? `<div class="doc">${md(p.brand)}</div>` : `<div class="empty-pane">No guidelines yet.</div>`}`;
    return;
  }
  if (tab === "rules") {
    pane.innerHTML = `<div class="pane-head"><h2>Client rules</h2><span class="faint small-print">Claude follows these on every video for this client, whichever style it uses. They're kept in the guidelines' "Lessons from reviews".</span></div>
      ${p.rules.length ? ruleList(p.rules) : `<div class="empty-pane">No client rules yet.</div>`}`;
    return;
  }
  if (tab === "details") {
    if (P.editing === "details") {
      pane.innerHTML = `<div class="editor"><div class="fields">
          <label class="field">Client name<input id="edName" value="${esc(p.name)}"></label>
          <label class="field">Contact<input id="edContact" value="${esc(p.contact || "")}"></label>
          <label class="field">Website or socials<input id="edWebsite" value="${esc(p.website || "")}"></label></div>
        <label class="field">About the client<textarea id="edAbout" rows="6">${esc(p.about || "")}</textarea></label>
        <div class="row"><button class="btn ghost" data-cancel>Cancel</button><div class="spacer"></div><button class="btn primary" data-save-details>Save the details</button></div></div>`;
      return;
    }
    pane.innerHTML = `<div class="pane-head"><h2>Details</h2><div class="spacer"></div>${p.can_edit ? `<button class="btn small" data-edit="details">Edit</button>` : ""}</div>
      <div class="doc">${detailRow("Client name", p.name)}${detailRow("Contact", p.contact)}${detailRow("Website or socials", p.website)}${detailRow("About the client", p.about)}</div>`;
    return;
  }
  // a brand file section
  const label = p.sections.find((x) => x.id === tab)?.label;
  if (!label) return setTab("overview");
  pane.innerHTML = `<div class="pane-head"><h2>${esc(label)}</h2><span class="faint small-print" id="secCount"></span></div>${p.can_edit ? `<div class="drop-hint" data-pick>Drop files anywhere on this page, or <b>click to choose</b>: they go into ${esc(label)}.</div>` : ""}<div class="media" id="media"><div class="empty-pane">Loading…</div></div>`;
  try {
    const { items } = await api("GET", `/api/projects/${enc(projectId)}/section/${enc(tab)}`);
    if (P.tab !== tab) return;
    $("secCount").textContent = `${items.length} item${items.length === 1 ? "" : "s"}`;
    $("media").innerHTML = items.length ? items.map(tile).join("") : `<div class="empty-pane" style="grid-column:1/-1">Nothing in ${esc(label)} yet.</div>`;
  } catch (e) {
    $("media").innerHTML = `<div class="empty-pane">${esc(e.message)}</div>`;
  }
}

function tile(it) {
  const url = pmedia(it.file);
  const box = it.kind === "image" ? `<img src="${url}" alt="" loading="lazy">` : `<span class="icon">📄</span>`;
  return `<a class="tile" href="${url}" target="_blank" rel="noopener" title="${esc(it.file)}"><div class="box">${box}${it.kind !== "image" ? `<span class="badge-k">${esc(it.name.split(".").pop())}</span>` : ""}</div>
    <div class="cap"><b>${esc(it.name)}</b><span>${fmtSize(it.size)}</span></div></a>`;
}

async function save(body) {
  try {
    P.page = await api("POST", `/api/projects/${enc(projectId)}`, body);
    P.editing = null;
    renderHero(); renderTabs(); renderPane();
    toast("Saved");
  } catch (ex) { toast(ex.message, true); }
}

document.addEventListener("click", (e) => {
  const t = e.target.closest("[data-tab],[data-edit],[data-cancel],[data-save-brand],[data-save-details],[data-pick]");
  if (!t) return;
  if (t.dataset.tab) return setTab(t.dataset.tab);
  if (t.dataset.edit) { P.editing = t.dataset.edit; return renderPane(); }
  if ("cancel" in t.dataset) { P.editing = null; return renderPane(); }
  if ("saveBrand" in t.dataset) return save({ brand: $("edText").value });
  if ("saveDetails" in t.dataset) return save({ name: $("edName").value, contact: $("edContact").value, website: $("edWebsite").value, about: $("edAbout").value });
  if ("pick" in t.dataset) return $("fileInput").click();
});

$("pAbout").onclick = () => $("pAbout").classList.toggle("open");
$("videoBtn").onclick = () => (location.href = `/#new-video-project:${enc(projectId)}`);
$("editBtn").onclick = () => { setTab("details"); P.editing = "details"; renderPane(); };
$("folderBtn").onclick = () => api("POST", "/api/reveal", { project: projectId }).catch((e) => toast(e.message, true));
$("promptBtn").onclick = async () => {
  try {
    await navigator.clipboard.writeText(P.page.claude_prompt);
    toast("Copied: paste it into a Claude session");
  } catch (e) {
    await ehPrompt("Copy this and paste it into a Claude session:", P.page.claude_prompt, { title: "Prompt for Claude", ok: "Done", cancel: "Close" });
  }
};
$("deleteBtn").onclick = async () => {
  const n = P.page.videos.length;
  if (!(await ehConfirm(`"${P.page.name}", with their brand files${n ? ` and ${n} video${n === 1 ? "" : "s"}` : ""}, move to Recently deleted, where you can restore them.`, { title: "Delete this project?", ok: "Delete", danger: true }))) return;
  try {
    await api("DELETE", `/api/projects/${enc(projectId)}`);
    location.href = "/#deleted";
  } catch (e) { toast(e.message, true); }
};

// ---------------------------------------------------------------- saving the client to a drive

const gb = (n) => (n >= 1e9 ? `${(n / 1e9).toFixed(1)} GB` : `${Math.max(1, Math.round(n / 1e6))} MB`);

function usedStyles() {
  return [...new Set(P.page.videos.map((v) => v.style_name))];
}

$("saveBtn").onclick = async () => {
  const f = $("saveForm"), styles = usedStyles(), n = P.page.videos.length;
  f.querySelector(".error").textContent = "";
  f.querySelector(".progress").hidden = true;
  $("saveGo").disabled = false;
  $("saveStyles").hidden = !styles.length;
  $("saveStyles").innerHTML = styles.length ? `Styles are saved separately. To edit these videos on another computer, save ${styles.length === 1 ? "this style" : "these styles"} too: <b>${styles.map(esc).join(", ")}</b>.` : "";
  $("saveSize").textContent = `${n} video${n === 1 ? "" : "s"}. Big projects take a few minutes; you can keep working.`;
  $("saveDlg").showModal();
  try {
    const t = await api("GET", "/api/transfer?type=project");
    $("places").innerHTML = t.places.map((p, i) => `<label><input type="radio" name="place" value="${esc(p.path)}"${i === 0 ? " checked" : ""}> <b>${esc(p.label)}</b> <span class="faint">${esc(p.path)} · ${gb(p.free)} free</span></label>`).join("") || `<p class="faint">No drives found: type a folder below.</p>`;
  } catch (e) {
    $("places").textContent = e.message;
  }
};

$("saveForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target, err = f.querySelector(".error"), bar = f.querySelector(".progress");
  const dest = f.elements.dest.value.trim() || f.querySelector("input[name=place]:checked")?.value;
  if (!dest) return (err.textContent = "Pick a drive or type a folder.");
  $("saveGo").disabled = true;
  err.textContent = "";
  try {
    let job = await api("POST", `/api/projects/${enc(projectId)}/export`, { dest });
    window.dispatchEvent(new Event("editorshub:jobs"));
    bar.hidden = false;
    while (job.state === "running") {
      bar.firstElementChild.style.width = job.total_bytes ? `${(job.done_bytes / job.total_bytes) * 100}%` : "3%";
      await new Promise((r) => setTimeout(r, 700));
      job = await api("GET", `/api/jobs/${job.id}`);
    }
    if (job.state !== "done") throw new Error(job.message);
    bar.firstElementChild.style.width = "100%";
    toast(`Saved to ${job.result.path}`);
    $("saveSize").innerHTML = `Saved <b>${gb(job.result.bytes)}</b> to <b>${esc(job.result.path)}</b>.`;
  } catch (ex) {
    err.textContent = ex.message;
    $("saveGo").disabled = false;
  }
});

// ---------------------------------------------------------------- adding files

async function addFiles(files) {
  if (!P.page?.can_edit || !files.length) return;
  const section = P.page.sections.some((x) => x.id === P.tab) ? P.tab : "auto";
  $("uploading").hidden = false;
  const landed = {};
  try {
    for (const [i, file] of files.entries()) {
      $("upText").textContent = `Adding ${file.name} (${i + 1} of ${files.length})…`;
      const r = await upload(`/api/projects/${enc(projectId)}/upload?section=${section}&name=${enc(file.name)}`, file, (p) => ($("upBar").style.width = p * 100 + "%"));
      landed[r.label] = (landed[r.label] || 0) + 1;
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
load();
