"""영상을 스크롤용 WebP 프레임으로 쪼개요.

    PYTHONPATH=_tools/pylib python -I _tools/extract_frames.py <video.mp4> [frames=120] [name=turntable]

결과: assets/<name>/desktop/f_000.webp ... (가로 1600)
      assets/<name>/mobile/f_000.webp  ... (가로 900)
      assets/<name>/manifest.json
ffmpeg는 imageio-ffmpeg(_tools/pylib)에 든 것을 써요.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_tools" / "pylib"))
import imageio_ffmpeg  # noqa: E402

video = Path(sys.argv[1]).resolve()
want = int(sys.argv[2]) if len(sys.argv) > 2 else 120
name_arg = sys.argv[3] if len(sys.argv) > 3 else "turntable"
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
out = ROOT / "assets" / name_arg

tmp = Path(tempfile.mkdtemp(prefix="tt-"))
try:
    subprocess.run([ffmpeg, "-v", "error", "-i", str(video), "-fps_mode", "passthrough",str(tmp / "r_%04d.png")], check=True)
    raw = sorted(tmp.glob("r_*.png"))
    if not raw:
        sys.exit("no frames decoded")
    n = min(want, len(raw))
    picks = [raw[round(i * (len(raw) - 1) / (n - 1))] for i in range(n)]

    # 4번째 인자로 화질을 낮출 수 있어요: "desktop,mobile" 예) 58,55
    dq, mq = (int(x) for x in sys.argv[4].split(",")) if len(sys.argv) > 4 else (74, 70)
    sets = {"desktop": (1600, dq), "mobile": (900, mq)}
    for name in sets:
        d = out / name
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    total = {k: 0 for k in sets}
    for i, p in enumerate(picks):
        im = Image.open(p).convert("RGB")
        for name, (w, q) in sets.items():
            fr = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) if im.width > w else im
            dst = out / name / f"f_{i:03d}.webp"
            fr.save(dst, "WEBP", quality=q, method=5)
            total[name] += dst.stat().st_size
    first = Image.open(picks[0])
    manifest = {
        "count": n,
        "pad": 3,
        "ext": "webp",
        "source": video.name,
        "sourceFrames": len(raw),
        "size": list(first.size),
        "desktop": {"dir": f"assets/{name_arg}/desktop", "prefix": "f_", "width": sets["desktop"][0]},
        "mobile": {"dir": f"assets/{name_arg}/mobile", "prefix": "f_", "width": sets["mobile"][0]},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"frames": n, "decoded": len(raw), "size": first.size,
                      "desktopMB": round(total["desktop"] / 1e6, 2), "mobileMB": round(total["mobile"] / 1e6, 2)}))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
