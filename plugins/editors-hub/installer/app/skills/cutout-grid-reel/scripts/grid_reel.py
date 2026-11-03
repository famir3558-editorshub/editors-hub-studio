#!/usr/bin/env python3
"""Cut-out grid reel: the speaker cut out of their footage, medium size, fixed in the centre of a 2x2 grid of four
full images (two on top, two below, no gaps). All four images change together when the subject changes (every 5-10 s).
Captions sit on the chest. Same hook and caption style as the cut-out backdrop reel.
Brand values (fonts, light rim colour) are read from ~/.claude/creator-profile/profile.json; sizes come from the
skill answers filled in at setup and can be overridden per video in plan.json.

  grid_reel.py matte   --video V --work W                                          background removal -> W/matte.webm (once per clip)
  grid_reel.py sheet   --plan plan.json --words words.json --work W [--video V]      one tile per image set -> W/sheet.jpg
  grid_reel.py preview --plan plan.json --words words.json --work W [--video V] --out O   720p review preview
  grid_reel.py final   --plan plan.json --words words.json --work W  --video V  --out O   1080x1920 final (after approval)
No --video = grey silhouette placeholder. --audio A = use this sound instead of the clip's.
A missing or unreadable font is reported as a WARNING and falls back to a system font: tell the creator, do not ship it.

plan.json (paths relative to the plan):
 {"duration": 21.55,
  "hook": {"lines": ["First line of the hook", "second line"], "sub": "(a smaller line under it)", "end": 4.2, "y": 330},   # optional; "bg" / "fg" override the label colours
  "captions": ["Three to six words", "per caption", ...],                       # every spoken word once, in order, 3-6 words each
  "sets": [{"t": 0, "images": [{"file": "images/a.jpg", "fx": 0.5, "fy": 0.5}, x4]}, ...],   # order: top-left, top-right, bottom-left, bottom-right
  "cutout": {"top": 230, "left": 0, "width": 1080, "height": 1180, "w": 540, "rim": 0.5},   # source crop (top = just above the head) and width on screen
  "caption": {"size": 46, "lead": 0.08, "up": 140, "track": -0.045}, "zoom": 0.05}   # the numbers shown are the defaults    # caption centre sits "up" px above the bottom of the cut-out
words.json = [[start, end, "word"], ...] or [{"w","s","e"}, ...]."""
import json, subprocess, os, sys, re, argparse, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ap = argparse.ArgumentParser(); ap.add_argument('mode', choices=['matte', 'sheet', 'preview', 'final']); ap.add_argument('--work', required=True)
for a in ('plan', 'words', 'video', 'audio', 'out'): ap.add_argument('--' + a)
A = ap.parse_args(); MODE = A.mode; WK = os.path.abspath(A.work); os.makedirs(WK, exist_ok=True); W, H = 1080, 1920
MATTE = WK + '/matte.webm'
def probe(f, e, s='v:0'): return subprocess.run(['ffprobe', '-v', 'error', '-select_streams', s, '-show_entries', e, '-of', 'csv=p=0', f], capture_output=True, text=True).stdout.strip().split('\n')[0].rstrip(',')
if MODE == 'matte':
    if not A.video: raise SystemExit('matte needs --video')
    r = subprocess.run(['npx', 'hyperframes', 'remove-background', os.path.abspath(A.video), '-o', MATTE, '--quality', 'best'], cwd=WK, stdout=subprocess.DEVNULL)
    if r.returncode or not os.path.exists(MATTE): raise SystemExit('background removal failed')
    print(MATTE, '- now look at a few frames on a bright colour before building (see SKILL.md, "Check the matte")'); sys.exit()
for a in ('plan', 'words'):
    if not getattr(A, a): raise SystemExit(f'{MODE} needs --{a}')
P = json.load(open(A.plan)); BASE = os.path.dirname(os.path.abspath(A.plan))
if A.video:
    VW, VH = [int(v) for v in probe(A.video, 'stream=width,height').split(',')[:2]]
    if (VW, VH) != (W, H): raise SystemExit(f'video is {VW}x{VH}: give the edited 1080x1920 clip')
    num, den = probe(A.video, 'stream=r_frame_rate').split('/'); FPS = float(num) / float(den); RATE = f'{num}/{den}'
    VD = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', A.video], capture_output=True, text=True).stdout.strip())
    if not os.path.exists(MATTE): raise SystemExit('no matte yet: run "grid_reel.py matte --video V --work W" first')
else: FPS = 30.0; RATE = '30/1'; VD = None
def norm(w): return re.sub(r"[^\w']", '', w.lower())
raw = json.load(open(A.words)); raw = raw.get('words', raw) if isinstance(raw, dict) else raw; words = []
for x in raw:
    if isinstance(x, dict):
        if x.get('type', 'word') != 'word': continue
        w, s, e = x.get('w', x.get('word', x.get('text'))), x.get('s', x.get('start')), x.get('e', x.get('end'))
    else: s, e, w = x[0], x[1], x[2]
    if norm(str(w)): words.append([float(s), float(e), str(w)])
DUR = float(P.get('duration') or VD or words[-1][1] + 0.3); DUR = min(DUR, VD) if VD else DUR
words = [w for w in words if w[0] < DUR - 0.01]
CAPS = P['captions']; HOOK = P.get('hook') or {}; BG = sorted(P['sets'], key=lambda b: b['t']); CUT = dict(top=230, left=0, width=1080, height=1180, w=int('@@CUTOUT_WIDTH@@'), rim=0.5); CUT.update(P.get('cutout', {}))
CAP = dict(size=int('@@CAPTION_SIZE@@'), lead=0.08, up=140, track=float('@@CAPTION_TRACKING@@')); CAP.update(P.get('caption', {})); ZOOM = P.get('zoom', 0.05)
CW = CUT['w']; CH = round(CUT['height'] * CW / CUT['width']); CX, CY = (W - CW) // 2, (H - CH) // 2; CAP['y'] = CY + CH - CAP['up']   # cut-out centred where the four images meet
# ---- checks ----
problems = []; a_ = [norm(w) for c in CAPS for w in c.split()]; b_ = [norm(w[2]) for w in words]
if a_ != b_:
    i = next((i for i, (x, y) in enumerate(zip(a_, b_)) if x != y), min(len(a_), len(b_)))
    raise SystemExit(f'captions do not match the transcript at word {i}: plan {a_[i:i+4]} vs transcript {b_[i:i+4]} ({len(a_)} vs {len(b_)} words up to {DUR:.1f}s)')
n = 0; cap_t = []
for i, c in enumerate(CAPS):
    cap_t.append(max(0.0, words[n][0] - CAP['lead'])); k = len(c.split()); n += k
    if not 3 <= k <= 6: problems.append(f'caption {i} has {k} words (wants 3-6): {c!r}')
    if '\n' in c: problems.append(f'caption {i} has a line break (captions are one line)')
if BG[0]['t'] > 0.001: problems.append('first backdrop must start at 0')
for i, b in enumerate(BG):
    nxt = BG[i + 1]['t'] if i + 1 < len(BG) else DUR
    if len(b['images']) != 4: raise SystemExit(f"set {i}: needs exactly 4 images")
    if nxt - b['t'] > 10.5: problems.append(f"set {i} stays {nxt - b['t']:.1f}s (wants a change every 5-10s or on a new subject)")
for p in problems: print('CHECK:', p)
# ---- drawing ----
# ---- fonts: the creator's own, from the profile (never a font that ships with this skill) ----
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDIR = os.path.expanduser(os.environ.get('CREATOR_PROFILE_DIR', '~/.claude/creator-profile'))
try: PROF = json.load(open(PDIR + '/profile.json'))
except Exception: PROF = {}
FONT_DIRS = [os.path.expanduser(d) for d in ('~/Library/Fonts', '/Library/Fonts', '/System/Library/Fonts', '/System/Library/Fonts/Supplemental')]
ADOBE = os.path.expanduser('~/Library/Application Support/Adobe/CoreSync/plugins/livetype')
FALLBACK = ['/System/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/HelveticaNeue.ttc', '/Library/Fonts/Arial.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf']
def font_files():
    for d in FONT_DIRS + [ADOBE]:
        for r, _, fs in os.walk(d):
            for f in fs:
                if f.lower().endswith(('.otf', '.ttf', '.ttc')): yield os.path.join(r, f)
def norm_name(x): return re.sub(r'[^a-z0-9]', '', str(x).lower())
def resolve_font(key, *alts):
    """profile key -> font file path. {"file": "X.ttf"} is looked for in assets/fonts (skill, then profile); {"local": [names]}
    is matched against installed fonts by file name or PostScript / full name (fontTools if installed)."""
    for k in (key,) + alts:
        spec = PROF.get(k)
        if not spec: continue
        spec = {'file': spec} if isinstance(spec, str) else spec
        if spec.get('file'):
            for d in (SKILL + '/assets/fonts', PDIR + '/assets/fonts'):
                if os.path.exists(d + '/' + os.path.basename(spec['file'])): return d + '/' + os.path.basename(spec['file'])
        names = [norm_name(n) for n in spec.get('local', [])]
        if names:
            try: from fontTools.ttLib import TTFont
            except ImportError: TTFont = None
            for p in font_files():
                if norm_name(os.path.splitext(os.path.basename(p))[0]) in names: return p
                if TTFont and p.lower().endswith(('.otf', '.ttf')):
                    try:
                        nm = TTFont(p, lazy=True)['name']
                        if {norm_name(nm.getDebugName(4) or ''), norm_name(nm.getDebugName(6) or '')} & set(names): return p
                    except Exception: pass
    return None
def load_font(role, size, key, *alts):
    p = resolve_font(key, *alts)
    if p:
        try: return ImageFont.truetype(p, size)
        except OSError: pass
    for q in FALLBACK:
        if os.path.exists(q):
            print(f'WARNING: {role} font from the profile ({key}) was not found: using {os.path.basename(q)}. Tell the creator, do not ship this.'); return ImageFont.truetype(q, size)
    print(f'WARNING: no usable font for {role}'); return ImageFont.load_default()
F_CAP = load_font('caption', CAP['size'], 'font_caption', 'font_main_bold')       # captions: the caption font (the main bold when none is set)
F_HOOK = load_font('hook', 68, 'font_main_bold'); F_SUB = load_font('hook sub-line', 46, 'font_caption', 'font_main_bold')
def path(f): return f if os.path.isabs(f) else os.path.join(BASE, f)
def cover(im, w, h, fx=.5, fy=.5):
    im = im.convert('RGB'); s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s) + 1, round(im.height * s) + 1), Image.LANCZOS)
    x = round((im.width - w) * fx); y = round((im.height - h) * fy); return im.crop((x, y, x + w, y + h))
def trim(im, p=0.015): return im.crop((round(im.width * p), round(im.height * p), round(im.width * (1 - p)), round(im.height * (1 - p))))
M = 1 + ZOOM + 0.01; QW, QH = W // 2, H // 2; PREP = []     # each quarter is prepared a little oversize so the push-in never upscales
for b in BG: PREP.append([cover(trim(Image.open(path(q['file']))), round(QW * M), round(QH * M), q.get('fx', .5), q.get('fy', .5)) for q in b['images']])
def backdrop(i, t):
    t0 = BG[i]['t']; t1 = BG[i + 1]['t'] if i + 1 < len(BG) else DUR; p = (t - t0) / max(0.01, t1 - t0); z = 1 + ZOOM * p; out = Image.new('RGB', (W, H))
    for n, im in enumerate(PREP[i]):
        cw, ch = im.width / z, im.height / z; x, y = (im.width - cw) / 2, (im.height - ch) / 2
        out.paste(im.resize((QW, QH), Image.BILINEAR, box=(x, y, x + cw, y + ch)), ((n % 2) * QW, (n // 2) * QH))
    return out
def silhouette(w, h):
    S = 3; im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); g = (138, 138, 138, 255); u = w * S
    rx, ry = .17 * u, .215 * u; cx = u / 2; top = .03 * u; sh_y = top + 2 * ry + .05 * u
    d.ellipse((cx - rx, top, cx + rx, top + 2 * ry), fill=g); d.rectangle((cx - .075 * u, top + 1.7 * ry, cx + .075 * u, sh_y + .08 * u), fill=g)
    d.rounded_rectangle((.03 * u, sh_y, .97 * u, h * S + .3 * u), radius=.2 * u, fill=g); im = im.resize((w, h), Image.LANCZOS)
    d = ImageDraw.Draw(im); f = load_font('placeholder label', max(20, w // 16), 'font_caption', 'font_main_bold'); tx = 'YOU (cut-out)'
    d.text(((w - d.textlength(tx, font=f)) / 2, h - f.size * 1.9), tx, font=f, fill=(92, 92, 92, 255)); return im
SIL = silhouette(CW, CH)
def cutout(rgb, alpha):
    """Source frame + matte -> head-to-chest cut-out, chest cropped flat. The matte is used AS IS: anything that will not
    separate cleanly (e.g. the black chair behind him) stays in on every frame rather than flickering in and out."""
    w, h = CW, CH; im = rgb.copy(); im.putalpha(alpha)
    box = (CUT['left'], CUT['top'], CUT['left'] + CUT['width'], CUT['top'] + CUT['height']); im = im.crop(box).resize((w, h), Image.LANCZOS)
    if not CUT['rim']: return im
    al = im.getchannel('A'); rim = al.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2.5)).point(lambda v: int(v * CUT['rim']))
    out = Image.new('RGBA', (w, h), RIM + (0,)); out.putalpha(rim); out.alpha_composite(im); return out   # light rim: dark clothes vs dark backdrops
def hex_rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
try: RIM = hex_rgb(PROF.get('paper') or '#F2F0EC')    # the light off-white from the profile
except Exception: RIM = (242, 240, 236)
def layer(fn): L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fn(ImageDraw.Draw(L), L); return L
def tracked(d, x, y, tx, **kw):     # letter by letter so the tracking applies; positions come from the kerned run
    tr = CAP['track'] * F_CAP.size
    for n, ch in enumerate(tx): d.text((x + F_CAP.getlength(tx[:n]) + n * tr, y), ch, font=F_CAP, **kw)
def cap_layer(tx):
    def draw(d, L):
        tw = F_CAP.getlength(tx) + (len(tx) - 1) * CAP['track'] * F_CAP.size; x = (W - tw) / 2; y = CAP['y'] - F_CAP.size * .62
        if tw > 980: print('CHECK: caption too wide:', tx)
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); tracked(ImageDraw.Draw(sh), x, y + 2, tx, fill=(0, 0, 0, 170), stroke_width=4, stroke_fill=(0, 0, 0, 170))
        L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
        tracked(d, x, y, tx, fill=(0, 0, 0, 235), stroke_width=2, stroke_fill=(0, 0, 0, 235)); tracked(d, x, y, tx, fill='white')   # outline pass first so strokes never cover a neighbour
    return layer(draw)
def hook_layer():
    def draw(d, L):
        y = HOOK.get('y', 330); lh = 96; padx = 34; lines = HOOK.get('lines', [])
        for i, ln in enumerate(lines):
            tw = d.textlength(ln, font=F_HOOK); d.rounded_rectangle(((W - tw) / 2 - padx, y + i * lh - 12, (W + tw) / 2 + padx, y + (i + 1) * lh + 8), radius=26, fill=HOOK.get('bg', 'white'))
            if tw + 2 * padx > 1000: print('CHECK: hook line too wide:', ln)
        for i, ln in enumerate(lines): d.text(((W - d.textlength(ln, font=F_HOOK)) / 2, y + i * lh + 2), ln, font=F_HOOK, fill=HOOK.get('fg', '#0b0b0b'))
        if HOOK.get('sub'): d.text(((W - d.textlength(HOOK['sub'], font=F_SUB)) / 2, y + len(lines) * lh + 36), HOOK['sub'], font=F_SUB, fill='white', stroke_width=2, stroke_fill=(0, 0, 0, 200))
    return layer(draw)
CAPL = [cap_layer(c) for c in CAPS]; HOOKL = hook_layer(); HOOK_END = HOOK.get('end', 0) if HOOK.get('lines') else 0
def frame(t, rgb=None, alpha=None):
    bi = max(i for i, b in enumerate(BG) if b['t'] <= t + 1e-6); ci = max([i for i, ct in enumerate(cap_t) if ct <= t + 1e-6], default=None)
    im = backdrop(bi, t).convert('RGBA'); im.alpha_composite(cutout(rgb, alpha) if rgb else SIL, (CX, CY))
    if t < HOOK_END: im.alpha_composite(HOOKL)
    if ci is not None: im.alpha_composite(CAPL[ci])
    return im.convert('RGB')
def grab(t):    # one source frame + its matte (sheet mode)
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', A.video, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    a = subprocess.run(['ffmpeg', '-v', 'error', '-c:v', 'libvpx-vp9', '-ss', f'{t:.3f}', '-i', MATTE, '-frames:v', '1', '-vf', 'alphaextract', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    return Image.frombytes('RGB', (W, H), r), Image.frombytes('L', (W, H), a)
if MODE == 'sheet':
    ts = [min(b['t'] + 1.0, DUR - 0.1) for b in BG]; tiles = [frame(t, *(grab(t) if A.video else (None, None))).resize((270, 480), Image.LANCZOS) for t in ts]
    cols = 4; sh = Image.new('RGB', (270 * cols, 480 * ((len(tiles) + cols - 1) // cols)), 'black')
    for i, tl in enumerate(tiles): sh.paste(tl, ((i % cols) * 270, (i // cols) * 480))
    sh.save(WK + '/sheet.jpg', quality=88); print(WK + '/sheet.jpg'); sys.exit()
if not A.out: raise SystemExit(f'{MODE} needs --out')
if MODE == 'final' and not A.video: raise SystemExit('final needs --video')
ends = [b['t'] for b in BG[1:]] + [DUR]; nm = lambda b: os.path.splitext(os.path.basename(b['file']))[0]
ev = ([dict(id='hook', type='headline', t0=0, t1=HOOK_END, text=' '.join(HOOK.get('lines', [])) + ' ' + HOOK.get('sub', ''))] if HOOK_END else [])
ev += [dict(id=f'set{i:02d}_{n}_{nm(q)}', type='image', t0=b['t'], t1=ends[i], text=f"{('top-left', 'top-right', 'bottom-left', 'bottom-right')[n]}: {nm(q)}") for i, b in enumerate(BG) for n, q in enumerate(b['images'])]
ev += [dict(id=f'cap{i:02d}', type='caption', t0=round(t, 3), t1=round((cap_t + [DUR])[i + 1], 3), text=CAPS[i]) for i, t in enumerate(cap_t)]
json.dump(ev, open(WK + '/review_events.json', 'w'), indent=1); json.dump([dict(w=w[2], s=w[0], e=w[1]) for w in words], open(WK + '/words_used.json', 'w'))
snd = A.audio or A.video; enc = (['-vf', 'scale=720:1280:flags=lanczos', '-b:v', '3M', '-preset', 'veryfast'] if MODE == 'preview' else ['-crf', '16', '-preset', 'medium'])
cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', RATE, '-i', '-'] + (['-t', str(DUR), '-i', snd, '-map', '0:v', '-map', '1:a?', '-c:a', 'aac', '-b:a', '128k' if MODE == 'preview' else '256k'] if snd else [])
ff = subprocess.Popen(cmd + ['-c:v', 'libx264'] + enc + ['-pix_fmt', 'yuv420p', '-shortest', A.out], stdin=subprocess.PIPE)
if A.video:
    v = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', A.video, '-t', str(DUR), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    m = subprocess.Popen(['ffmpeg', '-v', 'error', '-c:v', 'libvpx-vp9', '-i', MATTE, '-t', str(DUR), '-vf', 'alphaextract', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
N = round(DUR * FPS); done = 0
for i in range(N):
    if A.video:
        rb = v.stdout.read(W * H * 3); ab = m.stdout.read(W * H)
        if len(rb) < W * H * 3 or len(ab) < W * H: break
        ff.stdin.write(frame(i / FPS, Image.frombytes('RGB', (W, H), rb), Image.frombytes('L', (W, H), ab)).tobytes())
    else: ff.stdin.write(frame(i / FPS).tobytes())
    done += 1
ff.stdin.close(); ff.wait(); print('done', A.out, f'{done}/{N} frames', '- events:', WK + '/review_events.json')
