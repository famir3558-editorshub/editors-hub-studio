"""Hair-accurate cut-out: sharpens a speaker cut-out's edge round the hair, ears and face.

u2net (the cut-out model) sees the whole frame at 320 px, so on a 4K frame its outline is soft. Over a card placed behind
the speaker that shows as a coloured rim of the old wall round the hair, a blurry skin-coloured "fake ear", or lit specks
in the hair. Per frame, this:
  1. runs u2net again on a square round the head (about 3x finer) and blends it in (--no-head skips this),
  2. refines the edge on the full-size frame (guided filter, a small choke and feather), keeping the inside solid,
  3. re-decides each pixel near the outline at head height: closer to the background just outside, or to the hair or skin
     just inside? It only shrinks the cut-out, never grows it,
  4. takes the background colour out of mixed edge pixels.

    python head_matte.py VIDEO MATTE OUT.mov [--frames 10,250] [--no-head] [--cpu]

VIDEO is the speaker's clip; MATTE is its cut-out with alpha, the same length (a .webm from gpu_matte.py or HyperFrames,
or a .mov with alpha). OUT is ProRes 4444 with alpha. --frames writes only those frames, as a quick check.
Always check the result: zoomed crops (about 500 x 900 at 4K) of the hair and ears over every card that sits behind the
speaker, from the final render. There must be no coloured band, no specks, no hair or ear cut off.
Runs on the NVIDIA graphics card. On the processor it works but is very slow at 4K. Never run it while a final render is
encoding.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

MODEL = Path.home() / ".cache/hyperframes/background-removal/models/u2net_human_seg.onnx"
R, EPS, LO, HI, ERODE, DEC, CORE, BAND, GROW = 12, 1e-4, 0.30, 0.85, 1, 24, 40, 16, 6
SHRINK = 8  # at 4K; scaled to the frame


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,avg_frame_rate", "-of", "json", str(path)],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    s = json.loads(r.stdout)["streams"][0]
    return int(s["width"]), int(s["height"]), s["avg_frame_rate"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video")
    ap.add_argument("matte")
    ap.add_argument("out")
    ap.add_argument("--frames", default="", help="only these frame numbers (comma-separated), for a quick check")
    ap.add_argument("--no-head", action="store_true", help="skip the finer second look at the head")
    ap.add_argument("--cpu", action="store_true")
    a = ap.parse_args()
    try:
        import torch
        import torch.nn.functional as F
    except ImportError:
        sys.exit("The hair-accurate cut-out needs PyTorch; Editors.Hub's setup step 'Graphics card and checks' installs it.")
    dev = "cuda" if torch.cuda.is_available() and not a.cpu else "cpu"
    if dev == "cpu":
        print("No usable graphics card: running on the processor, which is very slow at 4K.", file=sys.stderr)
    W, H, rate = probe(a.video)
    S = min(W, H, max(320, round(H * 1000 / 2160)))  # the head square: 1000 px at 4K
    shrink = max(2, round(SHRINK * H / 2160))
    only = {int(x) for x in a.frames.split(",") if x.strip()} or None

    def box(x, r):
        return F.avg_pool2d(x, 2 * r + 1, stride=1, padding=r, count_include_pad=False)

    def dil(x, r):
        return F.max_pool2d(x[None], 2 * r + 1, stride=1, padding=r)[0]

    def ero(x, r):
        return -F.max_pool2d(-x[None], 2 * r + 1, stride=1, padding=r)[0]

    net = None
    if not a.no_head:
        if not MODEL.exists():
            sys.exit(f"The cut-out model isn't at {MODEL}; run one HyperFrames remove-background first, or use --no-head.")
        import onnx
        from onnx2torch import convert
        net = convert(onnx.load(str(MODEL))).to(dev).eval()
    mean = torch.tensor([0.485, 0.456, 0.406], device=dev).view(1, 3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225], device=dev).view(1, 3, 1, 1)

    @torch.no_grad()
    def u2(x):  # x (1,3,h,w) 0-255
        h, w = x.shape[2:]
        y = F.interpolate(x, size=(320, 320), mode="bicubic", antialias=True, align_corners=False).clamp(0, 255).round()
        y = (y / y.amax().clamp(min=1) - mean) / std
        o = net(y)
        d = o[0] if isinstance(o, (list, tuple)) else o
        d = (d - d.amin()) / (d.amax() - d.amin()).clamp(min=1e-12)
        return F.interpolate(d, size=(h, w), mode="bicubic", align_corners=False).clamp(0, 1)

    def head(rgb, p):
        m = p[0] > 0.5
        rows = torch.nonzero(m.any(1)).flatten()
        if len(rows) == 0:
            return p, round(H * 0.53)
        yt = int(rows[0])
        cols = torch.nonzero(m[yt:yt + S // 2].any(0)).flatten()
        xc = int((cols[0] + cols[-1]) // 2)
        x0, y0 = max(0, min(W - S, xc - S // 2)), max(0, min(H - S, yt - S // 12))
        q = u2(rgb[None, :, y0:y0 + S, x0:x0 + S] * 255)[0]
        edge = max(8, S // 8)  # fade back to the first cut-out over the square's last edge pixels
        r = torch.arange(S, device=dev).float()
        wy = ((S - 1 - r) / edge).clamp(0, 1) * (r / edge + (y0 == 0)).clamp(0, 1)
        wx = (r / edge + (x0 == 0)).clamp(0, 1) * ((S - 1 - r) / edge + (x0 == W - S)).clamp(0, 1)
        wgt = (wy[:, None] * wx[None, :])[None]
        out = p.clone()
        out[:, y0:y0 + S, x0:x0 + S] = q * wgt + p[:, y0:y0 + S, x0:x0 + S] * (1 - wgt)
        return out, y0 + S

    def refine(rgb, a):  # the edge follows the real hair; the rim takes the colour of solid hair further in
        I = (0.299 * rgb[0:1] + 0.587 * rgb[1:2] + 0.114 * rgb[2:3])[None]
        p = a[None]
        mI, mp = box(I, R), box(p, R)
        A = (box(I * p, R) - mI * mp) / (box(I * I, R) - mI * mI + EPS)
        q = (box(A, R) * I + box(mp - A * mI, R)).clamp(0, 1)
        t = ((q - LO) / (HI - LO)).clamp(0, 1)
        al = t * t * (3 - 2 * t)
        al = -F.max_pool2d(-al, 2 * ERODE + 1, stride=1, padding=ERODE)
        al = torch.maximum(al, -F.max_pool2d(-(p > 0.98).float(), 2 * CORE + 1, stride=1, padding=CORE))
        al = torch.minimum(al, F.max_pool2d((p > 0.5).float(), 2 * GROW + 1, stride=1, padding=GROW))
        al = F.avg_pool2d(al, 5, stride=1, padding=2, count_include_pad=False)
        nearo = F.max_pool2d((al < 0.5).float(), 2 * BAND + 1, stride=1, padding=BAND)
        solid = -F.max_pool2d(-(al > 0.97).float(), 2 * BAND + 1, stride=1, padding=BAND)
        n = box(solid, DEC)
        Fc = box(rgb[None] * solid, DEC) / n.clamp(min=1e-4)
        band = ((al > 0.001) & (nearo > 0) & (n > 0.02)).float()
        return (rgb[None] * (1 - band) + Fc * band)[0].clamp(0, 1), al[0]

    def fixup(rgb, p, head_bottom):
        o, al = refine(rgb, p)
        lum = 0.299 * rgb[0:1] + 0.587 * rgb[1:2] + 0.114 * rgb[2:3]

        def lmean(mask, r=32):
            n = box(mask[None], r)[0]
            return box((rgb * mask)[None], r)[0] / n.clamp(min=1e-4), n
        out = (al < 0.02).float()
        Bl, nb = lmean(out)
        solid = ero((al > 0.97).float(), 8)
        # two foreground colours: the darker half (hair) and the lighter half (skin) of the solid part
        cut = float(torch.quantile(lum[solid > 0][::97].float(), 0.5)) if bool((solid > 0).any()) else 0.27
        Fh, nh = lmean(solid * (lum < cut - 0.05).float())
        Fs, ns = lmean(solid * (lum > cut + 0.05).float())

        def d(X, n):
            return torch.where(n > 0.03, (rgb - X).norm(dim=0, keepdim=True), torch.full_like(n, 9.0))
        dB, dF = d(Bl, nb), torch.minimum(d(Fh, nh), d(Fs, ns))
        acl = ((dB / (dB + dF).clamp(min=1e-4) - 0.25) / 0.5).clamp(0, 1)  # 0 = background, 1 = the speaker
        ring = dil(out, 28) * (al > 0.001).float() * (nb > 0.03).float()
        ring[:, head_bottom:] = 0  # head height only
        a2 = torch.where(ring > 0, torch.minimum(al, acl), al)
        a2 = torch.maximum(a2, ero((al > 0.98).float(), 30))
        keep = ero((al > 0.5).float(), shrink)  # below the hairline, never cut more than SHRINK px into the speaker:
        top = torch.nonzero((p[0] > 0.5).any(1)).flatten()
        keep[:, :(int(top[0]) if len(top) else 0) + S // 4] = 0  # the hair above may still lose a lamp-lit wedge of wall
        a2 = torch.maximum(a2, keep)
        # glasses, ears and pale skin look like a pale wall, and a deeper cut leaves a notch
        a2 = F.avg_pool2d(a2[None], 3, stride=1, padding=1, count_include_pad=False)[0]
        un = ((rgb - (1 - a2) * Bl) / a2.clamp(min=0.05)).clamp(0, 1)
        w = ((a2 - 0.3) / 0.5).clamp(0, 1)
        col = un * w + torch.where(d(Fh, nh) < d(Fs, ns), Fh, Fs) * (1 - w)
        return torch.where(ring > 0, col, o).clamp(0, 1), a2

    mdec = ["-c:v", "libvpx-vp9"] if a.matte.lower().endswith(".webm") else []  # keeps the webm's alpha
    dv = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-i", a.video, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                          stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
    dm = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", *mdec, "-i", a.matte, "-vf", f"scale={W}:{H}",
                           "-f", "rawvideo", "-pix_fmt", "rgba", "-"], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
    enc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                            "-r", rate, "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
                            "-alpha_bits", "16", "-qscale:v", "4", a.out], stdin=subprocess.PIPE)
    n = k = 0
    with torch.no_grad():
        while True:
            g, m = dv.stdout.read(W * H * 3), dm.stdout.read(W * H * 4)
            if len(g) < W * H * 3 or len(m) < W * H * 4:
                break
            if only is None or n in only:
                rgb = torch.frombuffer(bytearray(g), dtype=torch.uint8).to(dev).view(H, W, 3).permute(2, 0, 1).float() / 255
                p = torch.frombuffer(bytearray(m), dtype=torch.uint8).to(dev).view(H, W, 4)[..., 3][None].float() / 255
                p, bottom = head(rgb, p) if net is not None else (p, round(H * 0.53))
                o, al = fixup(rgb, p, bottom)
                enc.stdin.write(torch.cat([o, al], 0).mul(255).round().byte().permute(1, 2, 0).contiguous().cpu().numpy().tobytes())
                k += 1
            n += 1
    enc.stdin.close()
    enc.wait()
    dv.kill()
    dm.kill()
    if not k:
        sys.exit("No frames were written: check that the video and its cut-out play and match.")
    print(f"{k} frames ({W}x{H}) on the {'GRAPHICS CARD' if dev == 'cuda' else 'PROCESSOR'} -> {a.out}")


if __name__ == "__main__":
    main()
