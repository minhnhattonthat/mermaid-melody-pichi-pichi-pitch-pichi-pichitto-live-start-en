"""Full QA tour: every scene warp (tools/debug/regen.py) plus story episodes 1-39 with A-mash, one contact-sheet
folder per run, and msglog TEXT lines for textcover.py.

    python -X utf8 tools/tour.py [ROM] [--out work/qa/tour] [--eps 1-39] [--ep-frames 9000] [--jobs 6] [--no-scenes]

Out: <out>/runs/<name>/ (frames, log.txt), <out>/sheets/<name>/sheet*.png (changed frames only).
Original ROM: --out work/qa/tour_jp --states work/qa/tour_jp/states (keeps work/states English).
Then: qa_gate.py init work/qa/manifest.tsv work/qa/tour/sheets --build ROM --glob "sheet*.png".
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

EMU = str(Path(SKILL) / "scripts/emu.py")
SHEET = str(Path(SKILL) / "scripts/sheet.py")


def sheet(run_dir, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-X", "utf8", SHEET, str(run_dir), "--changed", "0.02", "--max", "16",
                    "--out", str(out_dir / "sheet.png")], capture_output=True)


def episode(rom, ep, a):
    run = Path(a.out) / "runs" / f"ep{ep:02d}"
    p = subprocess.run([sys.executable, "-X", "utf8", EMU, str(rom), "--sav", a.sav, "--out", str(run),
                        "--script", str(ROOT / "tools/debug/warp.lua"), "--script", str(ROOT / "tools/lua/scenelog.lua"),
                        "--script", str(ROOT / "tools/lua/msglog.lua"), "--var", "SCENE='story'", "--var", f"EP={ep}",
                        "--frames", str(a.ep_frames), "--shot-every", "60", "--mash", "30", "--timeout", "900"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    sheet(run, Path(a.out) / "sheets" / f"ep{ep:02d}")
    return f"ep{ep:02d}", p.returncode == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build/mermaid_en.gba"))
    ap.add_argument("--out", default=str(ROOT / "work/qa/tour"))
    ap.add_argument("--states", default=str(ROOT / "work/states"))
    ap.add_argument("--sav", default=str(ROOT / "work/saves/default.sav"))
    ap.add_argument("--eps", default="1-39")
    ap.add_argument("--ep-frames", type=int, default=9000)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--no-scenes", action="store_true")
    a = ap.parse_args()
    rom = Path(a.rom).resolve()
    bad = []
    if not a.no_scenes:
        runs = Path(a.out) / "runs"
        r = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "tools/debug/regen.py"), str(rom), "--out", str(runs),
                            "--states", a.states, "--sav", a.sav, "--jobs", str(a.jobs)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-500:])
        bad += [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
        for d in sorted(runs.iterdir()):
            if d.is_dir() and d.name != "sheet" and not d.name.startswith("ep"):
                sheet(d, Path(a.out) / "sheets" / d.name)
    lo, hi = (int(x) for x in a.eps.split("-"))
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda e: episode(rom, e, a), range(lo, hi + 1)))
    bad += [n for n, ok in res if not ok]
    print(f"episodes {sum(ok for _, ok in res)}/{len(res)} ok; failures: {bad or 'none'}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
