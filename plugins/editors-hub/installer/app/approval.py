"""Whether this computer has been let in by the studio's owner.

A person asks from the /approve page, the online service emails a code to the owner only, and the code earns a signed
pass for this computer, which lasts 30 days and is renewed quietly unless the owner has removed them. The pass is checked
here with the service's public key, so the studio works offline until it runs out. With no approval-service.json next to
this file, approval is off (the source folder, and the tests).
"""
import hashlib
import json
import secrets
import time
import urllib.error
import urllib.request
from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "approval-service.json"
GRACE_DAYS = 14  # a studio already in use when this arrived has this long to get approved


class ApprovalError(Exception):
    status = 400


# ---------------------------------------------------------------- Ed25519 checking (RFC 8032), since this uses no packages

_P = 2 ** 255 - 19
_L = 2 ** 252 + 27742317777372353535851937790883648493
_D = (-121665 * pow(121666, _P - 2, _P)) % _P
_I = pow(2, (_P - 1) // 4, _P)


def _point_add(a, b):
    A, B = (a[1] - a[0]) * (b[1] - b[0]) % _P, (a[1] + a[0]) * (b[1] + b[0]) % _P
    C, D = 2 * a[3] * b[3] * _D % _P, 2 * a[2] * b[2] % _P
    E, F, G, H = B - A, D - C, D + C, B + A
    return (E * F % _P, G * H % _P, F * G % _P, E * H % _P)


def _point_mul(s, point):
    q = (0, 1, 1, 0)
    while s > 0:
        if s & 1:
            q = _point_add(q, point)
        point = _point_add(point, point)
        s >>= 1
    return q


def _recover_x(y, sign):
    if y >= _P:
        return None
    x2 = (y * y - 1) * pow(_D * y * y + 1, _P - 2, _P) % _P
    if x2 == 0:
        return None if sign else 0
    x = pow(x2, (_P + 3) // 8, _P)
    if (x * x - x2) % _P != 0:
        x = x * _I % _P
    if (x * x - x2) % _P != 0:
        return None
    if (x & 1) != sign:
        x = _P - x
    return x


_BY = 4 * pow(5, _P - 2, _P) % _P
_BX = _recover_x(_BY, 0)
_BASE = (_BX, _BY, 1, _BX * _BY % _P)


def _decompress(data):
    y = int.from_bytes(data, "little")
    sign = y >> 255
    y &= (1 << 255) - 1
    x = _recover_x(y, sign)
    return None if x is None else (x, y, 1, x * y % _P)


def _same_point(a, b):
    return (a[0] * b[2] - b[0] * a[2]) % _P == 0 and (a[1] * b[2] - b[1] * a[2]) % _P == 0


def ed25519_verify(public, message, signature):
    if len(public) != 32 or len(signature) != 64:
        return False
    A, R = _decompress(public), _decompress(signature[:32])
    s = int.from_bytes(signature[32:], "little")
    if A is None or R is None or s >= _L:
        return False
    h = int.from_bytes(hashlib.sha512(signature[:32] + public + message).digest(), "little") % _L
    return _same_point(_point_mul(s, _BASE), _point_add(R, _point_mul(h, A)))


# ---------------------------------------------------------------- the pass on this computer

_checked = {}  # a pass already checked needn't be worked out again on every page load


def config():
    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
        return data if data.get("url") and data.get("public_key") else None
    except (OSError, ValueError):
        return None


def _read(data_dir):
    try:
        return json.loads((Path(data_dir) / "approval.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write(data_dir, record):
    path = Path(data_dir) / "approval.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"approval.{secrets.token_hex(3)}.tmp")
    tmp.write_text(json.dumps(record), encoding="utf-8")
    tmp.replace(path)


def computer_id(data_dir):
    record = _read(data_dir)
    if not record.get("computer"):
        record["computer"] = secrets.token_hex(16)
        _write(data_dir, record)
    return record["computer"]


def _b64(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def read_pass(token, computer, key_hex):
    """What a pass says, if it's genuine, for this computer, and still in date."""
    cached = _checked.get(token)
    if cached is None:
        try:
            body, sig = str(token).split(".")
            if not ed25519_verify(bytes.fromhex(key_hex), body.encode(), _b64(sig)):
                return None
            cached = json.loads(_b64(body))
        except (ValueError, TypeError):
            return None
        _checked[token] = cached
    if cached.get("computer") != computer or cached.get("exp", 0) < time.time():
        return None
    return cached


def status(data_dir):
    """required: this computer can't be used until it's approved. grace_until: it can for now, but it needs approving."""
    cfg = config()
    if not cfg:
        return {"required": False, "on": False}
    record = _read(data_dir)
    passed = read_pass(record.get("token"), record.get("computer"), cfg["public_key"]) if record.get("token") else None
    if passed:
        return {"required": False, "on": True, "email": passed.get("email"), "until": passed.get("exp")}
    if record.get("removed"):
        return {"required": True, "on": True, "removed": True}
    try:
        accounts = json.loads((Path(data_dir) / "users.json").read_text(encoding="utf-8"))
        in_use = bool(accounts.get("users", accounts))
    except (OSError, ValueError, AttributeError):
        in_use = False
    if not in_use:
        return {"required": True, "on": True}
    if not record.get("grace_until"):
        record["grace_until"] = time.time() + GRACE_DAYS * 86400
        _write(data_dir, record)
    if record["grace_until"] > time.time():
        return {"required": False, "on": True, "grace_until": record["grace_until"]}
    return {"required": True, "on": True}


def open_to_others(data_dir):
    """Other people can only use the studio of the owner, who let them in by choosing to. Everyone else's is theirs alone."""
    cfg = config()
    if not cfg:
        return True
    email = (status(data_dir).get("email") or "").strip().lower()
    return bool(email) and hashlib.sha256(email.encode()).hexdigest() == cfg.get("owner_sha256")


def _signed_call(data_dir, path, body):
    token = _read(data_dir).get("token")
    if not token:
        raise ApprovalError("This computer needs the owner's approval first.")
    status_code, data = _call(path, {**body, "token": token})
    if status_code != 200:
        raise ApprovalError(data.get("error") or "The owner's service couldn't take that. Try again in a while.")
    return data


def send_report(data_dir, **report):
    """To the owner. Someone on the owner's own team is named in it, since the pass on this computer is the owner's."""
    return _signed_call(data_dir, "/report", report)["report"]


def my_reports(data_dir, from_email=""):
    return [r for r in _signed_call(data_dir, "/my-reports", {})["reports"] if (r.get("from_email") or "") == from_email]


def approved_people(data_dir):
    """For the owner's Team tab; the service only answers the owner's own pass."""
    return _signed_call(data_dir, "/owner/list", {})["people"]


def set_approved(data_dir, email, removed):
    return _signed_call(data_dir, "/owner/set", {"email": email, "removed": bool(removed)})["people"]


def shared_call(data_dir, path, **body):
    """The Shared section's listing, sharing and removing, which the service checks against this computer's pass."""
    return _signed_call(data_dir, path, body)


def open_shared_style(data_dir, key, start=0):
    """The start of a shared style's download; `start` picks up from there after a dropped connection."""
    token = _read(data_dir).get("token")
    if not token or not config():
        raise ApprovalError("This computer needs the owner's approval first.")
    headers = {"Content-Type": "application/json", "User-Agent": "Editors.Hub"}
    if start:
        headers["Range"] = f"bytes={start}-"
    req = urllib.request.Request(config()["url"].rstrip("/") + "/styles/download", method="POST", headers=headers,
                                 data=json.dumps({"token": token, "key": key}).encode())
    try:
        return urllib.request.urlopen(req, timeout=300)
    except urllib.error.HTTPError as e:
        try:
            message = json.loads(e.read() or b"{}").get("error")
        except ValueError:
            message = None
        raise ApprovalError(message or "The style couldn't be downloaded. Try again in a while.")


def _call(path, body):
    cfg = config()
    if not cfg:
        raise ApprovalError("Approval isn't set up on this copy.")
    req = urllib.request.Request(cfg["url"].rstrip("/") + path, method="POST", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "Editors.Hub"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except ValueError:
            return e.code, {}
    except (urllib.error.URLError, OSError, ValueError):
        raise ApprovalError("The approval service can't be reached. Check your internet and try again.")


def request_code(email, username):
    status_code, data = _call("/request", {"email": email, "username": username})
    if status_code != 200:
        raise ApprovalError(data.get("error") or "That didn't work. Try again in a while.")


def verify_code(data_dir, email, code):
    computer = computer_id(data_dir)
    status_code, data = _call("/verify", {"email": email, "code": code, "computer": computer})
    if status_code != 200 or not data.get("token"):
        raise ApprovalError(data.get("error") or "That didn't work. Try again in a while.")
    passed = read_pass(data["token"], computer, config()["public_key"])
    if not passed:  # a service that signs with the wrong key isn't the owner's
        raise ApprovalError("The approval service's answer couldn't be trusted.")
    record = _read(data_dir)
    record.update(token=data["token"], removed=False)
    _write(data_dir, record)
    return passed


def renew(data_dir):
    """Quietly each day. Being offline changes nothing; being removed by the owner takes the pass away."""
    record = _read(data_dir)
    if not config() or not record.get("token"):
        return "nothing to renew"
    try:
        status_code, data = _call("/renew", {"token": record["token"]})
    except ApprovalError:
        return "offline"
    if status_code == 200 and data.get("token") and read_pass(data["token"], record.get("computer"), config()["public_key"]):
        record["token"] = data["token"]
        _write(data_dir, record)
        return "renewed"
    if status_code == 403 and data.get("removed"):
        record.update(token=None, removed=True)
        _write(data_dir, record)
        return "removed"
    return "no change"
