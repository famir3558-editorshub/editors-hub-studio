#!/usr/bin/env python3
"""Cut-out backdrop reel: the speaker cut out of their footage over full-screen image backdrops that change with each
idea. Text hook over an opening collage, the cut-out jumps to a new corner on every backdrop, captions stay in one spot.
Brand values (accent colour, fonts, caption size and position, rim) come from the creator profile filled in at setup.

  cutout_reel.py matte   --video V --work W                                          background removal -> W/matte.webm (once per clip)
  cutout_reel.py sheet   --plan plan.json --words words.json --work W [--video V]      one tile per backdrop -> W/sheet.jpg
  cutout_reel.py preview --plan plan.json --words words.json --work W [--video V] --out O   720p review preview
  cutout_reel.py final   --plan plan.json --words words.json --work W  --video V  --out O   1080x1920 final (after approval)
No --video = grey silhouette placeholder (script test). --audio A = use this sound instead of the clip's.
--video must be the edited 9:16 clip (1080x1920) that words.json was timed on.

plan.json (paths relative to the plan; x, y, w, h in px on 1080x1920):
 {"duration": 15.05,
  "hook": {"lines": ["Three ways to make people", "watch your videos longer"], "sub": "(they get more specific)", "end": 4.2},
  "captions": ["Here are three ways to", "make people watch your", ...],              # every spoken word once, in order, 3-6 words each
  "collage": [{"file": "images/cinema.jpg", "x": 0, "y": 0, "w": 430, "h": 480}, ...], # tiles of the opening mosaic
  "backdrops": [{"t": 0, "file": "collage", "pos": "BIG"},
                {"t": 4.2, "file": "images/chess.jpg", "fx": 0.5, "fy": 0.5, "pos": "TR"}, ...],   # pos: BIG TR TL BL BR; fx/fy = crop focus 0-1
  "cutout": {"top": 250, "left": 0, "width": 1080, "rim": 0.5},   # source-pixel crop: top = just above the head; rim 0 = no light edge
  "caption": {"y": 885, "size": 58, "lead": 0.08}, "zoom": 0.05}
words.json = [[start, end, "word"], ...] or [{"w","s","e"}, ...]."""
import json, subprocess, os, sys, re, argparse, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); SKILL = os.path.dirname(HERE); sys.path.insert(0, HERE)
import stt  # the creator profile is read through it (shared by every skill in the pack)
# the creator's answers for this skill (setup/SETUP.md). Change the answer and re-run setup/apply_profile.py, never this text.
ACCENT = "@@ACCENT@@"; ON_ACCENT = "@@ON_ACCENT@@"
SET = {"caption_size": "@@CAPTION_SIZE@@", "caption_y": "@@CAPTION_Y@@", "rim": "@@RIM@@", "hook_label": "@@HOOK_LABEL@@"}
if "@" * 2 in ACCENT + ON_ACCENT + "".join(SET.values()):
    sys.exit("This skill has not been set up yet. Run the setup interview (setup/SETUP.md), then python3 setup/apply_profile.py")
def setnum(key, default):
    try: return float(SET[key])
    except (ValueError, TypeError): return default
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
    if not os.path.exists(MATTE): raise SystemExit('no matte yet: run "cutout_reel.py matte --video V --work W" first')
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
CAPS = P['captions']; HOOK = P.get('hook') or {}; BG = sorted(P['backdrops'], key=lambda b: b['t']); CUT = dict(top=250, left=0, width=1080, rim=setnum('rim', 0.5)); CUT.update(P.get('cutout', {}))
CAP = dict(y=round(setnum('caption_y', 885)), size=round(setnum('caption_size', 58)), lead=0.08); CAP.update(P.get('caption', {})); ZOOM = P.get('zoom', 0.05)
POS = dict(BIG=(40, 990, 1000, 930), TR=(480, 280, 560, 480), TL=(40, 280, 560, 480), BL=(40, 1020, 560, 480), BR=(480, 1020, 560, 480))
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
    if b['pos'] not in POS: raise SystemExit(f"backdrop {i}: pos must be one of {list(POS)}")
    if b['file'] != 'collage' and nxt - b['t'] > 3.6: problems.append(f"backdrop {i} ({b['file']}) stays {nxt - b['t']:.1f}s (this style changes backdrop every 1.5-3s)")
    if i and b['pos'] == BG[i - 1]['pos'] and b['pos'] != 'BIG': problems.append(f"backdrop {i}: cut-out stays at {b['pos']} twice in a row (it should jump)")
for p in problems: print('CHECK:', p)
# ---- drawing ----
PDIR = os.path.dirname(stt.PROFILE); PROF = stt.profile(); FONT_NOTES = []
def find_font(names):
    """A font given by installed name (PostScript or full name) -> (path, collection index), or None. Needs fontTools for
    .ttc collections and Adobe Fonts; without it, falls back to matching the file name."""
    dirs = [os.path.expanduser('~/Library/Application Support/Adobe/CoreSync/plugins/livetype/.*/.*'), os.path.expanduser('~/Library/Fonts/*'),
            '/Library/Fonts/*', '/System/Library/Fonts/*', '/System/Library/Fonts/Supplemental/*', '/usr/share/fonts/**/*']
    try: from fontTools.ttLib import TTFont, TTCollection
    except ImportError: TTFont = None
    want = {n.lower() for n in names}; squash = {re.sub(r'[^a-z0-9]', '', n.lower()) for n in names}
    for d in dirs:
        for p in glob.glob(d, recursive=True):
            if not p.lower().endswith(('.otf', '.ttf', '.ttc')): continue
            if TTFont is None:
                if re.sub(r'[^a-z0-9]', '', os.path.splitext(os.path.basename(p))[0].lower()) in squash: return (p, 0)
                continue
            try:
                fonts = list(TTCollection(p, lazy=True).fonts) if p.lower().endswith('.ttc') else [TTFont(p, lazy=True)]
                for i, f in enumerate(fonts):
                    if any((f['name'].getDebugName(n) or '').lower() in want for n in (4, 6)): return (p, i)
            except Exception: pass
    return None
def load_font(roles, size):
    """First role in `roles` that the profile names and that can be loaded: a file in assets/fonts, or an installed font.
    Falls back to a system sans and says so (CHECK line): a fallback must never ship unnoticed."""
    for role in roles:
        spec = PROF.get(role)
        if not spec: continue
        spec = {'file': spec} if isinstance(spec, str) else spec
        if spec.get('file'):
            for d in (f'{SKILL}/assets/fonts', f'{PDIR}/assets/fonts'):
                fp = os.path.join(d, os.path.basename(spec['file']))
                if os.path.exists(fp):
                    FONT_NOTES.append(f"{role}: {os.path.basename(fp)}"); return ImageFont.truetype(fp, size)
        if spec.get('local'):
            hit = find_font(spec['local'])
            if hit:
                FONT_NOTES.append(f"{role}: {spec['local'][0]} ({os.path.basename(hit[0])})"); return ImageFont.truetype(hit[0], size, index=hit[1])
    for fp in ('/System/Library/Fonts/Helvetica.ttc', '/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial.ttf',
               '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        try:
            FONT_NOTES.append(f"{roles[0]}: NOT FOUND, using {os.path.basename(fp)}"); return ImageFont.truetype(fp, size)
        except Exception: pass
    FONT_NOTES.append(f"{roles[0]}: NOT FOUND, using the built-in font"); return ImageFont.load_default()
F_CAP = load_font(['font_caption', 'font_main_bold'], CAP['size']); F_HOOK = load_font(['font_main_bold'], 68)
F_SUB = load_font(['font_main_regular', 'font_main_bold'], 46)
for n in dict.fromkeys(FONT_NOTES): print('FONT:', n)
def path(f): return f if os.path.isabs(f) else os.path.join(BASE, f)
def cover(im, w, h, fx=.5, fy=.5):
    im = im.convert('RGB'); s = max(w / im.width, h / im.height); im = im.resize((round(im.width * s) + 1, round(im.height * s) + 1), Image.LANCZOS)
    x = round((im.width - w) * fx); y = round((im.height - h) * fy); return im.crop((x, y, x + w, y + h))
def trim(im, p=0.015): return im.crop((round(im.width * p), round(im.height * p), round(im.width * (1 - p)), round(im.height * (1 - p))))
def collage():
    c = Image.new('RGB', (W, H), '#111')
    for t in P.get('collage', []): c.paste(cover(trim(Image.open(path(t['file']))), t['w'], t['h'], t.get('fx', .5), t.get('fy', .5)), (t['x'], t['y']))
    return c
M = 1 + ZOOM + 0.01; PREP = []     # backdrops are prepared a little oversize so the push-in never upscales
for b in BG:
    PREP.append(collage().resize((round(W * M), round(H * M)), Image.LANCZOS) if b['file'] == 'collage'
                else cover(trim(Image.open(path(b['file']))), round(W * M), round(H * M), b.get('fx', .5), b.get('fy', .5)))
def backdrop(i, t):
    t0 = BG[i]['t']; t1 = BG[i + 1]['t'] if i + 1 < len(BG) else DUR; p = (t - t0) / max(0.01, t1 - t0)
    z = 1 + ZOOM * p * min(1.0, (t1 - t0) / 2.5); im = PREP[i]; cw, ch = im.width / z, im.height / z; x, y = (im.width - cw) / 2, (im.height - ch) / 2
    return im.resize((W, H), Image.BILINEAR, box=(x, y, x + cw, y + ch))
def silhouette(w, h):
    S = 3; im = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); g = (138, 138, 138, 255); u = w * S
    rx, ry = .17 * u, .215 * u; cx = u / 2; top = .03 * u; sh_y = top + 2 * ry + .05 * u
    d.ellipse((cx - rx, top, cx + rx, top + 2 * ry), fill=g); d.rectangle((cx - .075 * u, top + 1.7 * ry, cx + .075 * u, sh_y + .08 * u), fill=g)
    d.rounded_rectangle((.03 * u, sh_y, .97 * u, h * S + .3 * u), radius=.2 * u, fill=g); im = im.resize((w, h), Image.LANCZOS)
    d = ImageDraw.Draw(im); f = load_font(['font_main_regular', 'font_main_bold'], max(20, w // 16)); tx = 'CUT-OUT'
    d.text(((w - d.textlength(tx, font=f)) / 2, h - f.size * 1.9), tx, font=f, fill=(92, 92, 92, 255)); return im
SIL = {k: silhouette(v[2], v[3]) for k, v in POS.items()}
def cutout(rgb, alpha, k):
    """Source frame + matte -> head-to-chest cut-out, chest cropped flat. The matte is used AS IS: anything that will not
    separate cleanly (e.g. the black chair behind him) stays in on every frame rather than flickering in and out."""
    x, y, w, h = POS[k]; im = rgb.copy(); im.putalpha(alpha)
    box = (CUT['left'], CUT['top'], CUT['left'] + CUT['width'], CUT['top'] + round(CUT['width'] * h / w)); im = im.crop(box).resize((w, h), Image.LANCZOS)
    if not CUT['rim']: return im
    al = im.getchannel('A'); rim = al.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2.5)).point(lambda v: int(v * CUT['rim']))
    out = Image.new('RGBA', (w, h), (255, 244, 230, 0)); out.putalpha(rim); out.alpha_composite(im); return out   # light rim: dark clothes vs dark backdrops
def layer(fn): L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fn(ImageDraw.Draw(L), L); return L
def cap_layer(tx):
    def draw(d, L):
        tw = d.textlength(tx, font=F_CAP); x = (W - tw) / 2; y = CAP['y'] - F_CAP.size * .62
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((x, y + 2), tx, font=F_CAP, fill=(0, 0, 0, 170), stroke_width=4, stroke_fill=(0, 0, 0, 170))
        L.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5))); d.text((x, y), tx, font=F_CAP, fill='white', stroke_width=2, stroke_fill=(0, 0, 0, 235))
    return layer(draw)
LABEL, LABEL_TEXT = (ACCENT, ON_ACCENT) if SET['hook_label'].strip().lower() == 'accent' else ('white', '#0b0b0b')   # the hook label: white or the accent colour
def hook_layer():
    def draw(d, L):
        y = 400; lh = 96; padx = 34; lines = HOOK.get('lines', [])
        for i, ln in enumerate(lines):
            tw = d.textlength(ln, font=F_HOOK); d.rounded_rectangle(((W - tw) / 2 - padx, y + i * lh - 12, (W + tw) / 2 + padx, y + (i + 1) * lh + 8), radius=26, fill=LABEL)
            if tw + 2 * padx > 1000: print('CHECK: hook line too wide:', ln)
        for i, ln in enumerate(lines): d.text(((W - d.textlength(ln, font=F_HOOK)) / 2, y + i * lh + 2), ln, font=F_HOOK, fill=LABEL_TEXT)
        if HOOK.get('sub'): d.text(((W - d.textlength(HOOK['sub'], font=F_SUB)) / 2, y + len(lines) * lh + 36), HOOK['sub'], font=F_SUB, fill='white', stroke_width=2, stroke_fill=(0, 0, 0, 200))
    return layer(draw)
CAPL = [cap_layer(c) for c in CAPS]; HOOKL = hook_layer(); HOOK_END = HOOK.get('end', 0) if HOOK.get('lines') else 0
def frame(t, rgb=None, alpha=None):
    bi = max(i for i, b in enumerate(BG) if b['t'] <= t + 1e-6); ci = max([i for i, ct in enumerate(cap_t) if ct <= t + 1e-6], default=None)
    im = backdrop(bi, t).convert('RGBA'); k = BG[bi]['pos']; im.alpha_composite(cutout(rgb, alpha, k) if rgb else SIL[k], POS[k][:2])
    if t < HOOK_END: im.alpha_composite(HOOKL)
    if ci is not None: im.alpha_composite(CAPL[ci])
    return im.convert('RGB')
def grab(t):    # one source frame + its matte (sheet mode)
    r = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', A.video, '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
    a = subprocess.run(['ffmpeg', '-v', 'error', '-c:v', 'libvpx-vp9', '-ss', f'{t:.3f}', '-i', MATTE, '-frames:v', '1', '-vf', 'alphaextract', '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True).stdout
    return Image.frombytes('RGB', (W, H), r), Image.frombytes('L', (W, H), a)
if MODE == 'sheet':
    ts = [min(b['t'] + 0.5, DUR - 0.1) for b in BG]; tiles = [frame(t, *(grab(t) if A.video else (None, None))).resize((270, 480), Image.LANCZOS) for t in ts]
    cols = 6; sh = Image.new('RGB', (270 * cols, 480 * ((len(tiles) + cols - 1) // cols)), 'black')
    for i, tl in enumerate(tiles): sh.paste(tl, ((i % cols) * 270, (i // cols) * 480))
    sh.save(WK + '/sheet.jpg', quality=88); print(WK + '/sheet.jpg'); sys.exit()
if not A.out: raise SystemExit(f'{MODE} needs --out')
if MODE == 'final' and not A.video: raise SystemExit('final needs --video')
ends = [b['t'] for b in BG[1:]] + [DUR]; nm = lambda b: os.path.splitext(os.path.basename(b['file']))[0]
ev = ([dict(id='hook', type='headline', t0=0, t1=HOOK_END, text=' '.join(HOOK.get('lines', [])) + ' ' + HOOK.get('sub', ''))] if HOOK_END else [])
ev += [dict(id=f'bg{i:02d}_{nm(b)}', type='image', t0=b['t'], t1=ends[i], text=f"{nm(b)} (cut-out {b['pos']})") for i, b in enumerate(BG)]
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
