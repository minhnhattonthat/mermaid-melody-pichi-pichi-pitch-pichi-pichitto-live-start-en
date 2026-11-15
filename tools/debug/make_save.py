"""Make the warp save fixture the game's own way: blank SRAM -> name entry (name あい) -> title -> main menu.

    python -X utf8 tools/debug/make_save.py [ROM] [--out work/saves/default.sav]

The game writes its save itself, so the format and checksum are its own. The run must reach the main menu
(scene 8); exit 1 otherwise or if the written save is still blank.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

ROM = ROOT / "rom" / "Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
ROUTE = "1100 -;6 a;30 -;6 right;20 -;6 a;30 -;6 start;150 -;6 a;150 -;6 a;150 -;6 start;300 -"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", default=str(ROM))
    ap.add_argument("--out", default=str(ROOT / "work/saves/default.sav"))
    a = ap.parse_args()
    run = ROOT / "work/qa/make_save"
    blank = run.parent / "blank_input.sav"
    run.parent.mkdir(parents=True, exist_ok=True)
    blank.write_bytes(b"\xff" * 0x8000)
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/emu.py"), a.rom, "--sav", str(blank), "--out", str(run),
           "--route-str", ROUTE, "--script", str(ROOT / "tools/lua/scenelog.lua"), "--timeout", "300"]
    if subprocess.run(cmd, capture_output=True).returncode != 0:
        sys.exit("emu.py failed")
    scenes = [ln.split()[2] for ln in (run / "log.txt").read_text().splitlines() if ln.startswith("SCENE")]
    written = run / (Path(a.rom).stem + ".sav")
    if "8" not in scenes or not written.exists() or written.read_bytes() == blank.read_bytes():
        sys.exit(f"save not made: scenes {scenes}")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(written, a.out)
    print(f"wrote {a.out} (scenes {' '.join(scenes)})")


if __name__ == "__main__":
    main()
