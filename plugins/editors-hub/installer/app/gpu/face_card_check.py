"""Card-placement check for a finished draft: no card, picture or text on the speaker.

The rules:
  * no card / picture / text on the speaker's face or over their body;
  * cards go BEHIND the speaker (their cut-out over the card), not in front beside their head;
  * cards must not run down into the bottom edge of the frame.

Flags, per sampled frame:
  ON HIM    - a card in front of the speaker cuts their silhouette with a long straight edge
              (a person's outline is curved; a card edge is straight and flat on the far side).
  NEAR HEAD - a solid card sits in front of the speaker within ~1 face width of their head.
              A card BEHIND them is overlapped by them with a curved outline and is not flagged.
  TOO LOW   - on full-screen graphics, a card's bottom edge runs into the bottom of the frame.

Only the speaker counts: their face is learned automatically (the face seen most often in the
video, OpenCV SFace), so B-roll people and photos of people inside cards are ignored.
Silhouette = u2net_human_seg (same model as the cut-outs), face = OpenCV YuNet. Runs on the NVIDIA
graphics card when PyTorch can use one, else on the processor (slower). Needs opencv-python, onnx,
onnx2torch and torch (Editors.Hub's Graphics card setup step installs them).

Usage:
  python face_card_check.py DRAFT.mp4 [--start S --end E] [--step 3] [--margin 1.0] [--sheet spots.jpg]
Prints ranges like "4:48.5-4:50.6  ON HIM (head)" and FACE-CHECK CLEAN / N spots.
Exit code 1 when anything is flagged. Look at every flagged spot; NEAR HEAD may be a judgement call.
It samples every 3rd frame, so a 1-2 frame overlap can slip through: --step 1 for a final pass.
The face models are OpenCV Zoo's YuNet (MIT) and SFace (Apache-2.0).
"""
import argparse, os, subprocess, sys
import numpy as np, cv2, torch, torch.nn.functional as F
import onnx
from onnx2torch import convert

HERE = os.path.dirname(os.path.abspath(__file__))
U2 = os.path.join(os.path.expanduser("~"), ".cache", "hyperframes", "background-removal", "models", "u2net_human_seg.onnx")
YUNET = os.path.join(HERE, "face_detection_yunet_2023mar.onnx")
SFACE = os.path.join(HERE, "face_recognition_sface_2021dec.onnx")
W, H = 960, 540
MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
SAME = 0.36           # SFace cosine threshold for "same person"

def fmt(t): return f"{int(t // 60)}:{t % 60:04.1f}"

def frames(path, step, start, end):
    cmd = ["ffmpeg", "-nostdin", "-v", "error"] + (["-ss", str(start)] if start else []) + ["-i", path]
    if end: cmd += ["-t", str(end - start)]
    cmd += ["-vf", f"select='not(mod(n\\,{step}))',scale={W}:{H}", "-fps_mode", "passthrough",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    fb = W * H * 3
    try:
        while True:
            b = p.stdout.read(fb)
            if len(b) < fb: break
            yield np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
    finally:
        p.kill()

class Checker:
    def __init__(self, margin=1.0):
        self.dev = "cuda" if torch.cuda.is_available() else "cpu"
        self.net = convert(onnx.load(U2)).to(self.dev).eval()
        self.mean, self.std = MEAN.to(self.dev), STD.to(self.dev)
        self.det = cv2.FaceDetectorYN.create(YUNET, "", (W, H), 0.6, 0.3, 5000)
        self.rec = cv2.FaceRecognizerSF.create(SFACE, "")
        self.margin = margin
        self.ref = None

    def embed(self, f, face):
        return self.rec.feature(self.rec.alignCrop(cv2.cvtColor(f, cv2.COLOR_RGB2BGR), face))

    def is_speaker(self, f, face):
        if not self.ref: return True
        e = self.embed(f, face)
        return max(float(self.rec.match(e, r, cv2.FaceRecognizerSF_FR_COSINE)) for r in self.ref) > SAME

    def learn_speaker(self, path, dur):
        embs = []
        for t in np.linspace(dur * 0.02, dur * 0.95, 36):
            f = next(frames(path, 1, float(t), float(t) + 0.2), None)
            if f is None: continue
            _, faces = self.det.detect(cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
            if faces is None: continue
            big = max(faces, key=lambda r: r[2])
            if big[2] >= 40: embs.append(self.embed(f, big))
        if not embs: return
        sim = lambda a, b: float(self.rec.match(a, b, cv2.FaceRecognizerSF_FR_COSINE))
        votes = [sum(sim(a, b) > SAME for b in embs) for a in embs]
        best = embs[int(np.argmax(votes))]
        self.ref = [e for e in embs if sim(best, e) > SAME]

    def person(self, f):
        x = torch.from_numpy(f).to(self.dev).permute(2, 0, 1)[None].float()
        x = F.interpolate(x, size=(320, 320), mode="bicubic", antialias=True, align_corners=False).clamp(0, 255)
        x = (x / x.amax().clamp(min=1) - self.mean) / self.std
        with torch.no_grad():
            d = self.net(x); d = d[0] if isinstance(d, (list, tuple)) else d
        m = (d - d.min()) / (d.max() - d.min()).clamp(min=1e-6)
        return F.interpolate(m, size=(H, W), mode="bilinear", align_corners=False)[0, 0].cpu().numpy() > 0.5

    def check(self, f):
        probs = []
        g = cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32)
        mu = cv2.blur(g, (9, 9)); sd = np.sqrt(np.maximum(cv2.blur(g * g, (9, 9)) - mu * mu, 0))
        # TOO LOW (full-screen graphics only: mostly flat designed frames, not B-roll)
        if (sd < 2.0).mean() > 0.5:
            gy = np.abs(np.diff(cv2.GaussianBlur(g, (5, 5), 0), axis=0))
            rows = np.where((gy > 8).mean(axis=1) > 0.3)[0]          # crisp card edges only, not soft blur
            if len(rows) and rows.max() > H * 0.945:
                y = int(rows.max()); probs.append(("TOO LOW", "card", (0, y - 4, W - 1, y + 4)))
        _, faces = self.det.detect(cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
        if faces is None: return probs
        m = self.person(f)
        best = None
        for fc in faces:
            x0, y0, w, h = [float(v) for v in fc[:4]]
            if w < 40: continue
            cx, cy = int(min(W - 1, x0 + w / 2)), int(min(H - 1, y0 + h / 2))
            if not m[cy, cx] or m.mean() < 0.06: continue
            if not self.is_speaker(f, fc): continue
            if best is None or w > best[2]: best = (x0, y0, w, h)
        if best is None: return probs
        x0, y0, w, h = best
        m8 = m.astype(np.uint8)
        # ON HIM
        edge = ((m8 - cv2.erode(m8, np.ones((3, 3), np.uint8))) * 255).astype(np.uint8)
        zones = {"head": (x0 - 0.8 * w, y0 - 0.5 * h, x0 + 1.8 * w, y0 + 1.3 * h),
                 "body": (x0 - 2.2 * w, y0 + 1.3 * h, x0 + 3.2 * w, H - 6)}
        for name, (a0, b0, a1, b1) in zones.items():
            a0, b0, a1, b1 = int(max(0, a0)), int(max(0, b0)), int(min(W, a1)), int(min(H, b1))
            if a1 - a0 < 10 or b1 - b0 < 10: continue
            z = np.zeros_like(edge); z[b0:b1, a0:a1] = edge[b0:b1, a0:a1]
            L = cv2.HoughLinesP(z, 1, np.pi / 180, 30, minLineLength=int(0.35 * h), maxLineGap=3)
            if L is None: continue
            for a, b, c, d in L.reshape(-1, 4).tolist():
                ang = abs(np.degrees(np.arctan2(d - b, c - a))) % 180
                vert = abs(ang - 90) < 4
                if not (vert or ang < 4 or ang > 176): continue
                n = max(abs(c - a), abs(d - b), 2)
                xs = np.linspace(a, c, n).astype(int); ys = np.linspace(b, d, n).astype(int)
                for s in (-8, 8):
                    px = np.clip(xs + (s if vert else 0), 0, W - 1); py = np.clip(ys + (0 if vert else s), 0, H - 1)
                    if m[py, px].mean() < 0.2 and sd[py, px].mean() < 4 and g[py, px].std() < 12:
                        probs.append(("ON HIM", name, (a, b, c, d))); break
        # NEAR HEAD: solid card in front, not overlapped by the speaker, within margin of their head
        flat = ((sd < 2.5) & ~cv2.dilate(m8, np.ones((9, 9), np.uint8)).astype(bool)).astype(np.uint8)
        flat = cv2.morphologyEx(flat, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(flat, 8)
        head = np.zeros((H, W), np.uint8)
        hx0, hy0, hx1, hy1 = int(max(0, x0 - 0.25 * w)), int(max(0, y0 - 0.45 * h)), int(min(W, x0 + 1.25 * w)), int(min(H, y0 + 1.05 * h))
        head[hy0:hy1, hx0:hx1] = m8[hy0:hy1, hx0:hx1]
        k = max(3, int(2 * self.margin * w)) | 1          # kernel is a diameter: 2 x margin
        near = cv2.dilate(head, np.ones((k, k), np.uint8)).astype(bool)
        for i in range(1, n):
            bx, by, bw, bh, area = st[i]
            if area < 0.35 * w * h or bh > 0.75 * H or bw > 0.9 * W: continue
            if area / float(bw * bh) < 0.55: continue
            if g[lab == i].mean() < 60: continue                       # dark wall panels / shadows are not cards
            if (near & (lab == i)).any():
                probs.append(("NEAR HEAD", "card in front", (bx, by, bx + bw, by + bh)))
        return probs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--start", type=float, default=0); ap.add_argument("--end", type=float, default=0)
    ap.add_argument("--step", type=int, default=3); ap.add_argument("--fps", type=float, default=0, help="default: read from the file")
    ap.add_argument("--margin", type=float, default=1.0, help="clear space around the speaker's head, in face widths")
    ap.add_argument("--sheet", default="")
    a = ap.parse_args()
    if not a.fps:
        rate = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=avg_frame_rate",
                               "-of", "csv=p=0", a.draft], capture_output=True, text=True).stdout.strip() or "30000/1001"
        n, _, d = rate.partition("/")
        a.fps = float(n) / float(d or 1) if float(d or 1) else 30000 / 1001
    ck = Checker(a.margin)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.draft],
                               capture_output=True, text=True).stdout.strip() or 0)
    ck.learn_speaker(a.draft, dur)
    print(f"speaker learned from {len(ck.ref or [])} sample faces", flush=True)
    hits, ex, i = [], {}, 0
    for f in frames(a.draft, a.step, a.start, a.end):
        t = a.start + i * a.step / a.fps; i += 1
        for kind, where, box in ck.check(f):
            hits.append((t, kind, where))
            key = (kind, int(t))
            if key not in ex and len(ex) < 120: ex[key] = (cv2.resize(f, (480, 270)), [v / 2 for v in box])
    ranges = []
    for t, k, wh in sorted(hits, key=lambda r: (r[1], r[0])):
        if ranges and ranges[-1][2] == k and t - ranges[-1][1] < 0.7:
            ranges[-1][1] = t; ranges[-1][3].add(wh)
        else: ranges.append([t, t, k, {wh}])
    ranges = sorted([r for r in ranges if r[1] - r[0] >= 0.3], key=lambda r: r[0])
    for s, e, k, wh in ranges:
        print(f"{fmt(s)}-{fmt(e)}  {k} ({'/'.join(sorted(wh))})")
    print(f"FACE-CHECK {'CLEAN' if not ranges else str(len(ranges)) + ' spots'} ({i} frames checked on {ck.dev.upper()})")
    if a.sheet and ranges:
        tiles = []
        for s, e, k, wh in ranges[:40]:
            cand = [v for kk, v in ex.items() if kk[0] == k and s - 1 <= kk[1] <= e + 1]
            if not cand: continue
            img, box = cand[0]; img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.rectangle(img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), 2)
            cv2.putText(img, f"{fmt(s)} {k}", (8, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            tiles.append(img)
        while len(tiles) % 4: tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(a.sheet, np.vstack([np.hstack(tiles[r:r + 4]) for r in range(0, len(tiles), 4)]))
    sys.exit(1 if ranges else 0)

if __name__ == "__main__":
    main()
