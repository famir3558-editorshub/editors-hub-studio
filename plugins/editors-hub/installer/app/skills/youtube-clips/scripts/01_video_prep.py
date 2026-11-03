#!/usr/bin/env python3
"""Step 1 - prepare a YouTube video.   01_video_prep.py "<video file or YouTube URL>" <slug> ["<output dir>"]
A local file (the raw or the export of one of the creator's videos) is used where it is. A YouTube URL is downloaded first with
yt-dlp at the best quality on offer, into "<download dir>/<title>.mp4"; its title, channel, chapters and "most
replayed" graph are saved to yt.json and printed, as hints for the map (never a substitute for reading the transcript).
Then: probe, mono audio for transcription, and two contact sheets of the whole video so the framing (where the speaker
sits, whether they look at the camera, where the empty space is, any screen share / B-roll / burned-in graphics) can be read
before planning.
Work dir: <work root>/<slug> (small files only). Output dir: "<video folder>/<video name> - Clips" unless given.
Downloads go to the output dir's parent when an output dir is given, otherwise to the downloads folder chosen at setup.
Needs yt-dlp for links (brew install yt-dlp)."""
import json, os, re, subprocess, sys
from ytcommon import work, probe, save, run, grab, mmss
DOWNLOADS = os.path.expanduser("@@DOWNLOADS_DIR@@")     # setup answer: where downloaded videos are kept
arg = sys.argv[1]; W = work(sys.argv[2])
out = os.path.expanduser(sys.argv[3]) if len(sys.argv) > 3 else None
if re.match(r"https?://", arg):
    import shutil
    shutil.which("yt-dlp") or sys.exit("yt-dlp is not installed: brew install yt-dlp (or give a local file instead of a link)")
    info = json.loads(subprocess.check_output(["yt-dlp", "--no-playlist", "-J", arg]))
    title = re.sub(r'[\\/:*?"<>|]+', " ", info["title"]).strip()[:120]
    if out:
        dl = os.path.dirname(out.rstrip("/"))
    elif os.path.isabs(DOWNLOADS) and os.path.isdir(os.path.dirname(DOWNLOADS.rstrip("/")) or "/"):
        dl = DOWNLOADS
    else:
        dl = os.path.expanduser("~/Movies/YouTube Downloads")
        print(f"WARNING the downloads folder from setup ({DOWNLOADS}) is not available (drive not connected?): downloading to {dl} instead. Move it afterwards if space is short.")
    os.makedirs(dl, exist_ok=True)
    src = f"{dl}/{title}.mp4"
    if not os.path.exists(src):
        subprocess.run(["yt-dlp", "--no-playlist", "-f", "bv*+ba/b", "-S", "res,fps,vcodec:h264,acodec:m4a",
                        "--merge-output-format", "mp4", "-o", src, arg], check=True)
    else:
        print(f"(already downloaded: {src})")
    heat = sorted(info.get("heatmap") or [], key=lambda h: -h["value"])[:8]
    save(W, "yt.json", {"url": arg, "id": info.get("id"), "title": info["title"], "channel": info.get("channel"),
                        "uploaded": info.get("upload_date"), "views": info.get("view_count"),
                        "chapters": info.get("chapters") or [], "heatmap": info.get("heatmap") or []})
    print(f"\"{info['title']}\" by {info.get('channel')} ({info.get('upload_date')}, {info.get('view_count')} views)")
    for c in info.get("chapters") or []:
        print(f"  chapter {mmss(c['start_time'])}  {c['title']}")
    if heat:
        print("  most replayed (a hint, not a ranking): " + "  ".join(f"{mmss(h['start_time'])}" for h in sorted(heat, key=lambda h: h["start_time"])))
else:
    src = os.path.abspath(os.path.expanduser(arg))
os.path.exists(src) or sys.exit(f"not found: {src}")
P = probe(src); P["audio"] or sys.exit("the video has no audio track")
stem = os.path.splitext(os.path.basename(src))[0]
out = out or f"{os.path.dirname(src)}/{stem} - Clips"
os.makedirs(out, exist_ok=True)
run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vn", "-ac", "1", "-ar", "16000", f"{W}/a16.flac"])
save(W, "meta.json", {"src": src, "stem": stem, "out": out, **P})

# 48 frames spread over the video, 24 per sheet, each labelled by its position in the file name list printed below
N, per = 48, 24
os.makedirs(f"{W}/sheet", exist_ok=True)
times = [P["dur"] * (i + 0.5) / N for i in range(N)]
for i, t in enumerate(times):
    grab(src, t, f"{W}/sheet/f{i:02d}.jpg", box=(640, 360))
for s in range(N // per):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-start_number", str(s * per), "-i", f"{W}/sheet/f%02d.jpg",
                    "-frames:v", "1", "-vf", f"scale=640:360:force_original_aspect_ratio=decrease,pad=640:360:(ow-iw)/2:(oh-ih)/2,tile=6x4",
                    "-q:v", "4", f"{W}/video-sheet-{s + 1}.jpg"], check=True)
print(f"{stem}: {P['w']}x{P['h']} {P['fps']} fps, {mmss(P['dur'])} ({P['dur'] / 60:.0f} min) -> work {W} | out {out}")
print(f"contact sheets: {W}/video-sheet-1.jpg, video-sheet-2.jpg (6x4, left to right, top to bottom). Tile times:")
print("  " + "  ".join(f"{i + 1}:{mmss(t)}" for i, t in enumerate(times)))
if P["w"] < P["h"]:
    print("NOTE the video is vertical. The 16:9 version needs a horizontal source: ask the creator before planning one.")
if P["h"] < 1080:
    print(f"NOTE only {P['h']}p: the 9:16 full-screen crop will be soft. Ask the creator for the original file.")
if P["fps"] != P["avg_fps"]:
    print(f"WARNING variable frame rate ({P['avg_fps']} avg vs {P['fps']}): common for screen recordings. Make a constant-rate copy first:\n"
          f'  ffmpeg -i "<video>" -fps_mode cfr -r 30 -c:v hevc_videotoolbox -b:v 40M -tag:v hvc1 -c:a copy "<cfr copy>"  and run this on that.')
if "arib" in P["transfer"] or "smpte2084" in P["transfer"]:
    print("NOTE the video is HDR; screenshots and graphics are SDR. Tell the creator before rendering.")
