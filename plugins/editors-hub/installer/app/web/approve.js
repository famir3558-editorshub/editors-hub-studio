const $ = (id) => document.getElementById(id);
let asked = null;

async function post(path, body) {
  const res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "That didn't work. Try again in a while.");
  return data;
}

function showCodeStep() {
  $("askForm").hidden = true;
  $("codeForm").hidden = false;
  $("title").textContent = "Ask the owner for your code";
  $("lead").textContent = "It's been sent to the studio's owner, not to you. It works for 24 hours.";
  $("codeForm").elements.code.focus();
}

$("askForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const f = e.target;
  $("askBtn").disabled = true;
  $("err").textContent = "";
  try {
    asked = { email: f.elements.email.value.trim(), username: f.elements.username.value.trim() };
    await post("/api/approval/request", asked);
    showCodeStep();
  } catch (ex) {
    $("err").textContent = ex.message;
  }
  $("askBtn").disabled = false;
});

$("codeForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("codeBtn").disabled = true;
  $("err").textContent = "";
  try {
    const r = await post("/api/approval/verify", { ...asked, code: e.target.elements.code.value });
    location.href = r.next || "/";
  } catch (ex) {
    $("err").textContent = ex.message;
    $("codeBtn").disabled = false;
  }
});

$("backBtn").onclick = () => {
  $("codeForm").hidden = true;
  $("askForm").hidden = false;
  $("err").textContent = "";
  $("title").textContent = "Ask for access";
};

fetch("/api/approval/status").then((r) => r.json()).then((s) => {
  if (!s.required && !s.grace_until) location.href = "/";
  if (s.removed) $("lead").textContent = "The owner has removed your access. Ask them to let you back in, then ask for a new code.";
}).catch(() => {});
