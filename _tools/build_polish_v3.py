"""첫 장 광택 영상(v3)을 이어 붙여요.

  A  front_polish 0~47번   : 정면에서 다가가며 보닛 잔흠집이 보임
  B  48번 프레임 디지털 확대 : 1.0 → 2.4배, 보닛 가운데로(장면 C의 시작 그림과 같은 자리)
  C  close_pad_sweep 전체   : 확대된 보닛에서 패드가 지나간 자리부터 깨끗해짐
  D  겹쳐 넘김              : C의 마지막 → 깨끗한 정면 사진(Codex)의 같은 2.4배 자리
  E  디지털 줌아웃           : 2.4 → 1.0배, 깨끗해진 차 전체 + 잠깐 멈춤

    PYTHONPATH=_tools/pylib python -I _tools/build_polish_v3.py
결과: _src/newtake/polish_v3.mp4  (그다음 extract_frames.py로 assets/polish/에 프레임)
"""
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_tools" / "pylib"))
import imageio_ffmpeg  # noqa: E402

NT = ROOT / "_src" / "newtake"
SHOT1 = NT / "front_polish_hailuo23.mp4"
CLOSE = NT / "close_pad_sweep_hailuo23.mp4"
CLEAN = ROOT / "_src" / "codex3" / "gen" / "clean_wide.png"
OUT = NT / "polish_v3.mp4"
CUT = 48                 # 패드가 나오기 전 마지막 프레임(장면 2를 만든 프레임)
ZOOM, CX, CY = 2.4, 0.5, 0.47   # _src/codex3/crop_box.txt 와 같은 값
N_ZOOM_IN, N_XFADE, N_ZOOM_OUT, N_HOLD = 30, 10, 48, 8
ff = imageio_ffmpeg.get_ffmpeg_exe()


def decode(video, d):
    d.mkdir(parents=True)
    subprocess.run([ff, "-v", "error", "-i", str(video), "-fps_mode", "passthrough", str(d / "f_%04d.png")], check=True)
    return sorted(d.glob("f_*.png"))


def ease(k):  # 천천히 시작해 천천히 멈춤
    return 0.5 - 0.5 * math.cos(math.pi * k)


def zoom(im, s):
    W, H = im.size
    cw, ch = W / s, H / s
    x0 = min(max(CX * W - cw / 2, 0), W - cw)
    y0 = min(max(CY * H - ch / 2, 0), H - ch)
    return im.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.LANCZOS)


tmp = Path(tempfile.mkdtemp(prefix="v3-"))
try:
    s1 = decode(SHOT1, tmp / "s1")
    cl = decode(CLOSE, tmp / "cl")
    W, H = Image.open(s1[0]).size
    load = lambda p: Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)  # noqa: E731
    clean = Image.open(CLEAN).convert("RGB").resize((W, H), Image.LANCZOS)
    od = tmp / "o"
    od.mkdir()
    n = 0
    marks = {}

    def put(im):
        global n
        im.save(od / f"o_{n:04d}.png")
        n += 1

    marks["A"] = n
    for p in s1[:CUT]:
        put(load(p))
    marks["B"] = n
    base = load(s1[CUT])
    for i in range(1, N_ZOOM_IN + 1):
        put(zoom(base, 1 + (ZOOM - 1) * ease(i / N_ZOOM_IN)))
    marks["C"] = n
    for p in cl:
        put(load(p))
    marks["D"] = n
    last = load(cl[-1])
    clean_close = zoom(clean, ZOOM)
    for i in range(1, N_XFADE + 1):
        put(Image.blend(last, clean_close, ease(i / (N_XFADE + 1))))
    marks["E"] = n
    for i in range(N_ZOOM_OUT + 1):
        put(zoom(clean, ZOOM - (ZOOM - 1) * ease(i / N_ZOOM_OUT)))
    for _ in range(N_HOLD):
        put(clean)
    marks["end"] = n
    subprocess.run([ff, "-v", "error", "-y", "-framerate", "24", "-i", str(od / "o_%04d.png"),
                    "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", str(OUT)], check=True)
    print({"frames": n, "marks": {k: round(v / n, 3) for k, v in marks.items()}, "out": str(OUT)})
finally:
    shutil.rmtree(tmp, ignore_errors=True)
