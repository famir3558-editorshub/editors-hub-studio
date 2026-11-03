"""Editors.Hub accounts: a username and an email, and a 6-digit code to sign up or sign in. No passwords.

Every code goes to the OWNER: their own, and everyone else's. A new person signs up, the owner gets their code (by email
and on the Team page) and hands it over only if they want that person in. So nobody gets in without the owner.
On a studio that isn't the owner's (see approval.open_to_others), nobody but its one person can sign in at all.

Only the owner can do admin things (settings, team, tools, skills, email). Everyone else is an editor or a reviewer.
Accounts, sessions and codes are kept in the studio's data folder on this computer.
"""
import hashlib
import json
import os
import re
import secrets
import smtplib
import ssl
import threading
import time
from email.message import EmailMessage
from pathlib import Path

ROLES = ("editor", "reviewer")
CODE_TTL = 10 * 60
CODE_TRIES = 5
RESEND_GAP = 30
SESSION_TTL = 30 * 86400
MAX_CODES_PER_HOUR = 30  # so nobody can flood the owner's inbox
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,23}$")  # shown as typed; matched ignoring case


class AuthError(Exception):
    status = 400


class Forbidden(AuthError):
    status = 403


def _now():
    return time.time()


def _iso(t=None):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t or _now()))


def _token_key(token):
    return hashlib.sha256(token.encode()).hexdigest()


def mask(email):
    name, _, domain = email.partition("@")
    return f"{name[:1]}{'•' * max(2, len(name) - 2)}{name[-1:] if len(name) > 1 else ''}@{domain}"


ALONE = "This studio is only for the person it was approved for. To use Editors.Hub, install it on your own computer and ask for approval there."


class Auth:
    def __init__(self, data_dir, owner_email, log=print, claim=None, open_to_others=None):
        self.claim = claim  # how a new studio's first account becomes its owner; None when the owner is settled
        self.open_to_others = open_to_others  # whether anyone but this studio's owner may use it; None means yes
        self.dir = Path(data_dir)
        self.owner_email = owner_email.strip().lower()
        self.log = log
        self.lock = threading.RLock()

    # ------------------------------------------------------------ storage

    def _load(self, name):
        try:
            return json.loads((self.dir / name).read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save(self, name, data):
        self.dir.mkdir(parents=True, exist_ok=True)
        path = self.dir / name
        tmp = path.with_name(f"{name}.{os.getpid()}.tmp")
        tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
        try:
            os.chmod(tmp, 0o600)  # only this user can read accounts, sessions and the mail login
        except OSError:
            pass
        os.replace(tmp, path)

    def users(self):
        return self._load("users.json").get("users", {})

    def _save_users(self, users):
        self._save("users.json", {"users": users})

    def owner_exists(self):
        return self.owner_email in self.users()

    def kept_out(self, email):
        return email != self.owner_email and self.open_to_others is not None and not self.open_to_others()

    def find(self, login):
        login = (login or "").strip().lower().lstrip("@")
        for email, u in self.users().items():
            if login in (email, u["username"].lower()):
                return u
        return None

    @staticmethod
    def public(u):
        return {k: u.get(k) for k in ("email", "username", "role", "created", "last_seen")} if u else None

    # ------------------------------------------------------------ codes

    def request_code(self, purpose, login, username=""):
        """Make a code for signing up or in and send it to the owner. Returns what the page should tell the person."""
        with self.lock:
            users = self.users()
            if purpose == "signup":
                email = (login or "").strip().lower()
                username = (username or "").strip().lstrip("@")
                if not EMAIL_RE.match(email):
                    raise AuthError("That email doesn't look right.")
                if not USERNAME_RE.match(username):
                    raise AuthError("Usernames are 3-24 characters: letters, numbers, dots, dashes or underscores.")
                if email in users:
                    raise AuthError("There's already an account with that email. Sign in instead.")
                if any(u["username"].lower() == username.lower() for u in users.values()):
                    raise AuthError("That username is taken.")
                if not self.owner_exists() and self.claim:  # a new studio: whoever sets it up owns it
                    self.owner_email = email
                    self.claim(email)
                if email != self.owner_email and not self.owner_exists():
                    raise AuthError("This studio isn't set up yet. The owner has to create their account first.")
                if self.kept_out(email):
                    raise Forbidden(ALONE)
            elif purpose == "signin":
                u = self.find(login)
                if not u:
                    raise AuthError("No account with that username or email. Create one instead.")
                email, username = u["email"], u["username"]
                if self.kept_out(email):
                    raise Forbidden(ALONE)
            else:
                raise AuthError("unknown request")

            codes = self._load("codes.json")
            codes = {k: c for k, c in codes.items() if c["expires"] > _now()}
            old = codes.get(email)
            if old and _now() - old["sent"] < RESEND_GAP:
                raise AuthError(f"A code was just sent. Wait {int(RESEND_GAP - (_now() - old['sent'])) + 1} seconds to ask again.")
            if sum(1 for c in codes.values() if _now() - c["sent"] < 3600) >= MAX_CODES_PER_HOUR:
                raise AuthError("Too many codes were asked for this hour. Try again later.")
            code = f"{secrets.randbelow(10 ** 6):06d}"
            codes[email] = {"purpose": purpose, "code": code, "username": username, "email": email,
                            "sent": _now(), "expires": _now() + CODE_TTL, "tries": 0}
            self._save("codes.json", codes)
        return self._send_code(codes[email])

    def resend_code(self, email):
        """Email a code that's already waiting again (once the owner has connected their email)."""
        c = self._load("codes.json").get((email or "").strip().lower())
        if not c or c["expires"] < _now():
            raise AuthError("That code has run out. Ask for a new one.")
        return self._send_code(c)

    def _send_code(self, c):
        email, username, code = c["email"], c["username"], c["code"]
        is_owner = email == self.owner_email
        what = "sign up" if c["purpose"] == "signup" else "sign in"
        if is_owner:
            subject = f"Your Editors.Hub code: {code}"
            text = f"Your code to {what} to Editors.Hub is {code}.\n\nIt works for 10 minutes. If this wasn't you, ignore it."
        else:
            subject = f"Editors.Hub: {username} wants to {what} - code {code}"
            text = (f"{username} ({email}) wants to {what} to your Editors.Hub studio.\n\n"
                    f"Their code is {code}. It works for 10 minutes.\n\n"
                    f"Give it to them only if you know them and want them in. If not, ignore this email: "
                    f"without the code they can't get in.\n")
        emailed = self.send_mail(self.owner_email, subject, text)
        return {"step": "code", "email": email, "username": username, "owner": is_owner, "emailed": emailed,
                "to": mask(self.owner_email), "email_ready": self.mail_status()["ready"]}

    def verify(self, login, code, agent=""):
        """Check a code. Returns (session token, user)."""
        code = re.sub(r"\D", "", str(code or ""))
        with self.lock:
            codes = self._load("codes.json")
            u = self.find(login)
            email = u["email"] if u else (login or "").strip().lower()
            if self.kept_out(email):
                raise Forbidden(ALONE)
            c = codes.get(email)
            if not c or c["expires"] < _now():
                raise AuthError("That code has run out. Ask for a new one.")
            if c["tries"] >= CODE_TRIES:
                raise AuthError("Too many wrong tries. Ask for a new code.")
            if not secrets.compare_digest(c["code"], code):
                c["tries"] += 1
                self._save("codes.json", codes)
                left = CODE_TRIES - c["tries"]
                raise AuthError(f"Wrong code. {left} tr{'y' if left == 1 else 'ies'} left." if left else
                                "Too many wrong tries. Ask for a new code.")
            del codes[email]
            self._save("codes.json", codes)

            users = self.users()
            if c["purpose"] == "signup":
                if email in users or any(x["username"].lower() == c["username"].lower() for x in users.values()):
                    raise AuthError("That account was made in the meantime. Sign in instead.")
                users[email] = {"email": email, "username": c["username"],
                                "role": "owner" if email == self.owner_email else "editor", "created": _iso()}
            user = users.get(email)
            if not user:
                raise AuthError("That account was removed.")
            user["last_seen"] = _iso()
            self._save_users(users)

            token = secrets.token_urlsafe(32)
            sessions = {k: s for k, s in self._load("sessions.json").items() if s["expires"] > _now()}
            sessions[_token_key(token)] = {"email": email, "created": _now(), "expires": _now() + SESSION_TTL,
                                           "agent": agent[:120]}
            self._save("sessions.json", sessions)
        self.log(f"{user['username']} signed {'up' if c['purpose'] == 'signup' else 'in'}")
        return token, user

    def adopt_owner(self, email, username, agent=""):
        """The person the online approval just let in becomes this new studio's owner, with no second code."""
        email, username = email.strip().lower(), username.strip()
        with self.lock:
            users = self.users()
            if users:
                raise AuthError("This studio already has accounts. Sign in instead.")
            self.owner_email = email
            if self.claim:
                self.claim(email)
            users[email] = {"email": email, "username": username, "role": "owner", "created": _iso(), "last_seen": _iso()}
            self._save_users(users)
        self.log(f"{username} approved, owner of this studio")
        return self.session_for_owner(agent)

    def session_for_owner(self, agent=""):
        """A session for the owner without a code: only for the private link `studio.py open` prints on this computer."""
        with self.lock:
            if not self.owner_exists():
                return None
            token = secrets.token_urlsafe(32)
            sessions = {k: s for k, s in self._load("sessions.json").items() if s["expires"] > _now()}
            sessions[_token_key(token)] = {"email": self.owner_email, "created": _now(),
                                           "expires": _now() + SESSION_TTL, "agent": ("local link " + agent)[:120]}
            self._save("sessions.json", sessions)
            return token

    def user_for(self, token):
        if not token:
            return None
        s = self._load("sessions.json").get(_token_key(token))
        if not s or s["expires"] < _now() or self.kept_out(s["email"]):
            return None
        return self.users().get(s["email"])

    def sign_out(self, token):
        with self.lock:
            sessions = self._load("sessions.json")
            sessions.pop(_token_key(token or ""), None)
            self._save("sessions.json", sessions)

    # ------------------------------------------------------------ the owner's team page

    def pending(self):
        """Codes waiting to be handed over (not the owner's own)."""
        codes = self._load("codes.json")
        return sorted(({"username": c["username"], "email": c["email"], "purpose": c["purpose"], "code": c["code"],
                        "expires_in": int(c["expires"] - _now())}
                       for c in codes.values() if c["expires"] > _now() and c["email"] != self.owner_email),
                      key=lambda c: -c["expires_in"])

    def all_codes(self):
        codes = self._load("codes.json")
        return [c for c in codes.values() if c["expires"] > _now()]

    def team(self):
        return sorted((self.public(u) for u in self.users().values()),
                      key=lambda u: (u["role"] != "owner", u["username"]))

    def rename(self, email, username):
        """Change someone's username (their email, role and sign-ins stay)."""
        username = (username or "").strip().lstrip("@")
        if not USERNAME_RE.match(username):
            raise AuthError("Usernames are 3-24 characters: letters, numbers, dots, dashes or underscores.")
        with self.lock:
            users = self.users()
            if email not in users:
                raise AuthError("no such account")
            if any(e != email and u["username"].lower() == username.lower() for e, u in users.items()):
                raise AuthError("That username is taken.")
            old = users[email]["username"]
            users[email]["username"] = username
            self._save_users(users)
        return old

    def set_role(self, email, role):
        if role not in ROLES:
            raise AuthError(f"role must be {' or '.join(ROLES)}")
        with self.lock:
            users = self.users()
            if email not in users:
                raise AuthError("no such account")
            if email == self.owner_email:
                raise Forbidden("The owner's role can't change.")
            users[email]["role"] = role
            self._save_users(users)

    def remove(self, email):
        with self.lock:
            if email == self.owner_email:
                raise Forbidden("The owner can't be removed.")
            users = self.users()
            if users.pop(email, None) is None:
                raise AuthError("no such account")
            self._save_users(users)
            sessions = {k: s for k, s in self._load("sessions.json").items() if s["email"] != email}
            self._save("sessions.json", sessions)

    def cancel_code(self, email):
        with self.lock:
            codes = self._load("codes.json")
            codes.pop(email, None)
            self._save("codes.json", codes)

    # ------------------------------------------------------------ email

    def mail_status(self):
        cfg = self._load("mail.json")
        return {"ready": bool(cfg.get("password")), "user": cfg.get("user", self.owner_email),
                "host": cfg.get("host", "smtp.gmail.com"), "port": cfg.get("port", 587), "error": cfg.get("error")}

    def set_mail(self, user, password, host="smtp.gmail.com", port=587, test_email=True):
        """Save the login codes are sent with, once it works. test_email=False only checks the login, sending nothing."""
        user = (user or "").strip()
        password = re.sub(r"\s+", "", password or "")  # Google shows app passwords in groups of four
        if not EMAIL_RE.match(user) or not password:
            raise AuthError("Add the Gmail address and its app password.")
        cfg = {"user": user, "password": password, "host": host or "smtp.gmail.com", "port": int(port or 587)}
        try:
            if test_email:
                self._smtp(cfg, self.owner_email, "Editors.Hub email works",
                           "Editors.Hub can now email you sign-up and sign-in codes.")
            else:
                self._smtp(cfg)
        except Exception as e:
            raise AuthError(f"Couldn't send with that login: {e}. For Gmail use an app password, not your normal password.")
        self._save("mail.json", cfg)

    def clear_mail(self):
        self._save("mail.json", {})

    @staticmethod
    def _smtp(cfg, to=None, subject="", text=""):
        """Log in to the mail server and send one email; with no `to`, only check the login works."""
        msg = EmailMessage()
        msg["From"] = f"Editors.Hub <{cfg['user']}>"
        msg["To"] = to or cfg["user"]
        msg["Subject"] = subject
        msg.set_content(text)
        ctx = ssl.create_default_context()
        if int(cfg["port"]) == 465:
            with smtplib.SMTP_SSL(cfg["host"], 465, timeout=20, context=ctx) as s:
                s.login(cfg["user"], cfg["password"])
                if to:
                    s.send_message(msg)
        else:
            with smtplib.SMTP(cfg["host"], int(cfg["port"]), timeout=20) as s:
                s.starttls(context=ctx)
                s.login(cfg["user"], cfg["password"])
                if to:
                    s.send_message(msg)

    def send_mail(self, to, subject, text):
        cfg = self._load("mail.json")
        if not cfg.get("password"):
            self.log("code waiting in the studio (email isn't set up): see the Team page or `studio.py codes`")
            return False
        try:
            self._smtp(cfg, to, subject, text)
            return True
        except Exception as e:
            self.log(f"couldn't email the code: {e}")
            return False
