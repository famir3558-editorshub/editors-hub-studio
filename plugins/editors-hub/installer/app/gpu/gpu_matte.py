"""Cut the speaker out of a video, on the NVIDIA graphics card when there is one.

A drop-in for `hyperframes remove-background IN -o OUT.webm --quality Q`: the same model (u2net_human_seg), the same
pre- and post-processing and the same VP9-with-alpha file, about 6x faster on the card. Without a card (or without
PyTorch with CUDA), it runs HyperFrames' own remove-background on the processor instead, so it always works.

    python gpu_matte.py INPUT.mp4 -o OUT.webm [--quality fast|balanced|best] [--batch 8] [--cpu]

Don't use HyperFrames' `--device cuda` on Windows: it silently runs on the processor.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

MODEL = Path.home() / ".cache" / "hyperframes" / "background-removal" / "models" / "u2net_human_seg.onnx"
CRF = {"fast": 30, "balanced": 18, "best": 12}


def card_ready():
    """(True, torch) when PyTorch can use an NVIDIA card and the model is on this computer."""
    if not MODEL.exists():
        return False, None
    try:
        import torch
        import onnx  # noqa: F401
        import onnx2torch  # noqa: F401
    except Exception:
        return False, None
    return (torch.cuda.is_available(), torch)


def on_processor(a):
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        sys.exit("Cutting out needs HyperFrames (Node) or an NVIDIA card with PyTorch.")
    r = subprocess.run([npx, "--yes", "hyperframes", "remove-background", os.path.abspath(a.input), "-o",
                        os.path.abspath(a.output), "--quality", a.quality])
    if r.returncode:
        sys.exit(r.returncode)
    print(f"Removed background on the PROCESSOR -> {a.output}")


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate", "-of", "json", path],
                         capture_output=True, text=True, check=True).stdout
    s = json.loads(out)["streams"][0]
    return s["width"], s["height"], s["r_frame_rate"]


def on_card(a, torch):
    import numpy as np
    import onnx
    import torch.nn.functional as F
    from onnx2torch import convert
    dev = "cuda"
    net = convert(onnx.load(str(MODEL))).to(dev).eval()
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(dev)
    std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(dev)
    w, h, rate = probe(a.input)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.input, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}",
                            "-r", rate, "-i", "-", "-vf", "scale=out_color_matrix=bt709:out_range=tv:flags=neighbor",
                            "-c:v", "libvpx-vp9", "-b:v", "0", "-crf", str(CRF[a.quality]), "-deadline", "good",
                            "-row-mt", "1", "-cpu-used", "4", "-auto-alt-ref", "0", "-pix_fmt", "yuva420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-color_range", "tv", "-metadata:s:v:0", "alpha_mode=1", "-an", a.output],
                           stdin=subprocess.PIPE)
    size, n = w * h * 3, 0
    with torch.no_grad():
        while True:
            frames = []
            for _ in range(a.batch):
                buf = dec.stdout.read(size)
                if len(buf) < size:
                    break
                frames.append(np.frombuffer(buf, np.uint8).reshape(h, w, 3))
            if not frames:
                break
            rgb = torch.from_numpy(np.stack(frames)).to(dev)
            x = rgb.permute(0, 3, 1, 2).float()
            x = F.interpolate(x, size=(320, 320), mode="bicubic", antialias=True, align_corners=False).clamp(0, 255).round()
            x = (x / x.amax(dim=(1, 2, 3), keepdim=True).clamp(min=1) - mean) / std
            out = net(x)
            d0 = out[0] if isinstance(out, (list, tuple)) else out
            lo, hi = d0.amin(dim=(1, 2, 3), keepdim=True), d0.amax(dim=(1, 2, 3), keepdim=True)
            m = ((d0 - lo) / (hi - lo).clamp(min=1e-12) * 255).round().clamp(0, 255)
            m = F.interpolate(m, size=(h, w), mode="bicubic", antialias=False, align_corners=False).clamp(0, 255).round()
            rgba = torch.cat([rgb, m.to(torch.uint8).permute(0, 2, 3, 1)], dim=3)
            enc.stdin.write(rgba.cpu().numpy().tobytes())
            n += len(frames)
    enc.stdin.close()
    enc.wait()
    dec.wait()
    if enc.returncode or n == 0:
        raise RuntimeError(f"the card made {n} frames")
    print(f"Removed background from {n} frames on the GRAPHICS CARD -> {a.output}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("input")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--quality", default="balanced", choices=CRF)
    ap.add_argument("--batch", type=int, default=8, help="frames at a time on the card (lower it if memory runs out)")
    ap.add_argument("--cpu", action="store_true", help="use HyperFrames on the processor")
    a = ap.parse_args()
    ok, torch = (False, None) if a.cpu else card_ready()
    if ok:
        try:
            return on_card(a, torch)
        except Exception as e:  # out of memory, driver trouble: the processor still gets it done
            print(f"The graphics card couldn't do it ({str(e)[:200]}); using the processor.", file=sys.stderr)
    on_processor(a)


if __name__ == "__main__":
    main()
