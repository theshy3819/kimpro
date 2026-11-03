"""두 장면을 한 영상으로 이어요.

  장면 1: 0 ~ (cut-1)번 프레임(정면에서 다가가며 흠집이 보임)
  장면 2: 0 ~ a_end번(패드가 들어와 흠집 위에 닿음)
          → a_end번에서 resume번으로 xfade프레임 동안 겹쳐 넘김(흠집이 걷힘)
          → resume번 ~ 끝(깨끗한 도장, 패드가 빠짐)
  장면 2의 첫 프레임은 장면 1의 cut번 프레임과 같은 그림이에요(그 프레임으로 장면 2를 뽑음).
  장면 2는 카메라를 고정해 뽑았으니, 프레임을 조금씩 잘라 들어가(디지털 확대) 다가가는 움직임을 이어 줘요.
  장면 2의 24~80번은 보닛이 하얗게 번지는 오류가 있어 a_end ~ resume 사이를 건너뛰어요.

    PYTHONPATH=_tools/pylib python -I _tools/splice_shots.py <shot1.mp4> <cut> <shot2.mp4> <out.mp4> \
        [zoom=1.3] [fx=0.45] [fy=0.45] [a_end=16] [resume=88] [xfade=14]
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_tools" / "pylib"))
import imageio_ffmpeg  # noqa: E402

args = sys.argv[1:]
shot1, cut, shot2, out = Path(args[0]), int(args[1]), Path(args[2]), Path(args[3])
opt = [float(x) for x in args[4:]]
zoom, fx, fy = (opt + [1.3, 0.45, 0.45])[:3] if len(opt) < 3 else opt[:3]
a_end, resume, xfade = (int(x) for x in (opt[3:6] if len(opt) >= 6 else [16, 88, 14]))
ff = imageio_ffmpeg.get_ffmpeg_exe()


def decode(video, d):
    d.mkdir(parents=True)
    subprocess.run([ff, "-v", "error", "-i", str(video), "-fps_mode", "passthrough", str(d / "f_%04d.png")], check=True)
    return sorted(d.glob("f_*.png"))


tmp = Path(tempfile.mkdtemp(prefix="splice-"))
try:
    a = decode(shot1, tmp / "a")[:cut]
    b = decode(shot2, tmp / "b")
    W, H = Image.open(a[0]).size
    load = lambda p: Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)  # noqa: E731

    # 장면 2 쪽 프레임 목록(그림을 만드는 함수로)
    part2 = [lambda p=p: load(p) for p in b[: a_end + 1]]
    for j in range(1, xfade + 1):
        w = j / (xfade + 1)
        w = w * w * (3 - 2 * w)  # 부드럽게
        part2.append(lambda w=w: Image.blend(load(b[a_end]), load(b[resume]), w))
    part2 += [lambda p=p: load(p) for p in b[resume:]]

    outdir = tmp / "o"
    outdir.mkdir()
    n = 0
    for p in a:
        load(p).save(outdir / f"o_{n:04d}.png"); n += 1
    m = len(part2)
    for i, make in enumerate(part2):
        k = i / max(1, m - 1)
        s = 1 + (zoom - 1) * (1 - (1 - k) ** 3)  # 처음엔 장면 1처럼 다가가다 천천히 멈춤
        im = make()
        cw, ch = W / s, H / s
        x0 = min(max(fx * W - cw / 2, 0), W - cw)
        y0 = min(max(fy * H - ch / 2, 0), H - ch)
        im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((W, H), Image.LANCZOS).save(outdir / f"o_{n:04d}.png"); n += 1
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([ff, "-v", "error", "-y", "-framerate", "24", "-i", str(outdir / "o_%04d.png"),
                    "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", str(out)], check=True)
    print({"shot1": len(a), "shot2_kept": a_end + 1 + len(b) - resume, "xfade": xfade, "total": n, "size": (W, H), "out": str(out)})
finally:
    shutil.rmtree(tmp, ignore_errors=True)
