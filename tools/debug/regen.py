"""Warp to every scene in tools/debug/scenes.tsv from a cold boot; keep a shot and a savestate of each.

    python -X utf8 tools/debug/regen.py [ROM] [--only name,name] [--jobs 6] [--out work/qa/warp]
        [--states work/states] [--sav work/saves/default.sav] [--var EP=1 ...]

Per scene: <out>/<name>/ (frames, log), <out>/sheet/<name>.png (final frame), <states>/<name>.mss.
A scene passes when warp.lua logs ARRIVED (its expected scene id held 30 frames after the route). Exit 1 if any
scene fails. Regenerate after any code, font or graphics change: states keep the old VRAM and code.
"""
import argparse
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
WARP_AT = 760  # scene 9 begins ~frame 731; warp.lua fires there
DEFAULT_VARS = ["EP=1", "MSG=1028"]


def scenes():
    rows = []
    for line in (ROOT / "tools/debug/scenes.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        if line and not line.startswith("#"):
            f = line.split("\t")
            rows.append((f[0], f[4] if len(f) > 4 else ""))
    return rows


def route_frames(route):
    return sum(int(m) for m in re.findall(r"(\d+)\s+\S+", route))


def run(rom, name, route, a):
    out = Path(a.out) / name
    frames = WARP_AT + route_frames(route) + a.settle
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/emu.py"), str(rom), "--sav", a.sav, "--out", str(out),
           "--script", str(ROOT / "tools/debug/warp.lua"), "--script", str(ROOT / "tools/lua/scenelog.lua"),
           "--script", str(ROOT / "tools/lua/msglog.lua"), "--var", f"SCENE='{name}'", "--frames", str(frames),
           "--shot-every", "60", "--state-out", str(Path(a.states).resolve() / f"{name}.mss"), "--timeout", "400"]
    for v in DEFAULT_VARS + a.var:
        cmd += ["--var", v]
    for s in a.script:
        cmd += ["--script", str(Path(s).resolve())]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    ok = p.returncode == 0 and "ARRIVED" in log
    if (out / "final.png").exists():
        shutil.copy(out / "final.png", Path(a.out) / "sheet" / f"{name}.png")
    why = "" if ok else (p.stdout + p.stderr).strip().splitlines()[-1:] or ["no output"]
    return name, ok, why


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", default=str(ROM))
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--out", default=str(ROOT / "work/qa/warp"))
    ap.add_argument("--states", default=str(ROOT / "work/states"))
    ap.add_argument("--sav", default=str(ROOT / "work/saves/default.sav"))
    ap.add_argument("--settle", type=int, default=240, help="frames after the route before the shot")
    ap.add_argument("--var", action="append", default=[])
    ap.add_argument("--script", action="append", default=[], help="extra Lua probe, e.g. tools/lua/boxlog.lua")
    a = ap.parse_args()
    if not Path(a.sav).exists():
        sys.exit(f"missing save fixture {a.sav}: run tools/debug/make_save.py first")
    (Path(a.out) / "sheet").mkdir(parents=True, exist_ok=True)
    Path(a.states).mkdir(parents=True, exist_ok=True)
    rows = [r for r in scenes() if not a.only or r[0] in a.only.split(",")]
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda r: run(a.rom, r[0], r[1], a), rows))
    bad = [r for r in res if not r[1]]
    for name, ok, why in res:
        print(f"{'ok  ' if ok else 'FAIL'} {name} {why or ''}")
    print(f"{len(res) - len(bad)}/{len(res)} scenes reached")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
