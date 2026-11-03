const $ = (id) => document.getElementById(id);
const next = new URLSearchParams(location.search).get("next") || "/";
const A = { mode: "signin", ownerExists: true, pending: null, resendAt: 0 };

function go() {
  location.href = next.startsWith("/") && !next.startsWith("//") ? next : "/";
}

function setMode(mode) {
  A.mode = mode;
  document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("on", b.dataset.mode === mode));
  const signup = mode !== "signin";
  $("loginField").hidden = signup;
  $("userField").hidden = !signup;
  $("emailField").hidden = !signup;
  $("startError").textContent = "";
  if (mode === "owner") {
    $("tabs").hidden = true;
    $("title").textContent = "Set up your studio";
    $("lead").innerHTML = "You're setting up this studio, so your account becomes the <b>owner</b>. Use your own email: only the owner can do admin things.";
  } else if (signup) {
    $("title").textContent = "Create an account";
    $("lead").textContent = "Pick a username and add your email. The studio owner gets your code and lets you in.";
  } else {
    $("title").textContent = "Welcome back";
    $("lead").textContent = "Sign in with your username or email. A code is sent to the studio owner.";
  }
  (signup ? $("startForm").elements.username : $("startForm").elements.login).focus();
}

function showCode(r) {
  A.pending = r;
  A.resendAt = Date.now() + 30000;
  $("startForm").hidden = true;
  $("tabs").hidden = true;
  $("codeForm").hidden = false;
  $("codeError").textContent = "";
  $("code").value = "";
  const connect = r.owner && !r.emailed && !r.email_ready;
  $("connectBox").hidden = !connect;
  if (r.owner) {
    $("codeLead").innerHTML = r.emailed
      ? `We emailed a 6-digit code to <b>${esc(r.to)}</b>. It works for 10 minutes.`
      : connect
      ? `Your code is ready. This computer can't email it yet:`
      : `<span class="notice">Couldn't email the code just now, so it's waiting on this computer. Ask Claude for it (or run <code>studio.py codes</code>), and check the email login on the Team page once you're in.</span>`;
    $("ownerMail").textContent = r.email;
  } else {
    $("codeLead").innerHTML = `Your code was sent to the <b>studio owner</b>. Ask them for it: only they can let you in. It works for 10 minutes.`;
  }
  (connect ? $("appPassword") : $("code")).focus();
  tickResend();
}

function tickResend() {
  const left = Math.ceil((A.resendAt - Date.now()) / 1000);
  $("resendBtn").disabled = left > 0;
  $("resendBtn").textContent = left > 0 ? `Send a new code (${left})` : "Send a new code";
  if (left > 0) setTimeout(tickResend, 1000);
}

async function requestCode() {
  const f = $("startForm").elements;
  if (A.mode === "signin") return api("POST", "/api/auth/signin", { login: f.login.value });
  return api("POST", "/api/auth/signup", { username: f.username.value, email: f.email.value });
}

$("startForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("sendBtn").disabled = true;
  $("startError").textContent = "";
  try {
    showCode(await requestCode());
  } catch (ex) {
    $("startError").textContent = ex.message;
  } finally {
    $("sendBtn").disabled = false;
  }
});

$("codeForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  $("verifyBtn").disabled = true;
  $("codeError").textContent = "";
  try {
    await api("POST", "/api/auth/verify", { login: A.pending.email, code: $("code").value });
    go();
  } catch (ex) {
    $("codeError").textContent = ex.message;
    $("verifyBtn").disabled = false;
  }
});

$("connectBtn").onclick = async () => {
  $("connectBtn").disabled = true;
  $("codeError").textContent = "";
  try {
    showCode(await api("POST", "/api/auth/connect-email", { email: A.pending.email, password: $("appPassword").value }));
    $("appPassword").value = "";
    toast("Gmail connected: code sent");
  } catch (ex) {
    $("codeError").textContent = ex.message;
  } finally {
    $("connectBtn").disabled = false;
  }
};

$("code").addEventListener("input", (e) => {
  e.target.value = e.target.value.replace(/\D/g, "").slice(0, 6);
  if (e.target.value.length === 6) $("codeForm").requestSubmit();
});

$("resendBtn").onclick = async () => {
  try {
    showCode(await requestCode());
    toast("New code sent");
  } catch (ex) {
    $("codeError").textContent = ex.message;
  }
};

$("backBtn").onclick = () => {
  $("codeForm").hidden = true;
  $("startForm").hidden = false;
  $("tabs").hidden = A.mode === "owner";
  setMode(A.mode);
};

$("tabs").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (b) setMode(b.dataset.mode);
});

(async () => {
  try {
    const me = await api("GET", "/api/auth/me");
    if (me.user) return go();
    A.ownerExists = me.owner_exists;
  } catch (e) {}
  setMode(A.ownerExists ? "signin" : "owner");
})();
