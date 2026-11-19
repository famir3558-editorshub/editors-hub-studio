"""What this computer's graphics card can do for an edit, and the settings to use.

    python check.py          # plain words
    python check.py --json   # for scripts

Prints whether FFmpeg can encode on an NVIDIA card (NVENC) and whether PyTorch can use it (Whisper, cut-outs),
and the FFmpeg settings for in-between files (base footage, section parts, joins, test renders).
"""
import json
import shutil
import subprocess
import sys

NVENC_MID = ["-c:v", "h264_nvenc", "-preset", "p5", "-rc", "vbr", "-cq", "16", "-b:v", "0", "-pix_fmt", "yuv420p"]
X264_MID = ["-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p"]


def nvenc():
    ff = shutil.which("ffmpeg")
    if not ff:
        return False
    try:
        r = subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=black:s=256x256:d=0.1",
                            "-c:v", "h264_nvenc", "-f", "null", "-"], capture_output=True, timeout=30)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def cuda():
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except Exception:
        pass
    return ""


def main():
    enc, card = nvenc(), cuda()
    try:
        import whisper  # noqa: F401
        has_whisper = True
    except Exception:
        has_whisper = False
    info = {"nvenc": enc, "cuda": bool(card), "card": card, "whisper": has_whisper,
            "whisper_device": "cuda" if card and has_whisper else "cpu",
            "intermediate_args": NVENC_MID if enc else X264_MID,
            "hwaccel_args": ["-hwaccel", "cuda"] if enc else []}
    if "--json" in sys.argv:
        print(json.dumps(info))
        return
    print(f"Video encoding: {'graphics card (NVENC)' if enc else 'processor (x264)'}")
    print(f"Whisper and cut-outs: {'graphics card, ' + card if card else 'processor'}")
    print("In-between files: ffmpeg " + " ".join(info["hwaccel_args"] + ["-i", "IN"] + info["intermediate_args"]) + " OUT.mp4")


if __name__ == "__main__":
    main()
