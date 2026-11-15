"""gfx_scenes.py: which graphics-sweep rows each warped scene loads (vramfind of its PPU dump against the decoded
blocks of tools/gfx_chain.py), and which rows no scene reached.

    python -X utf8 tools/debug/regen.py --out work/qa/ppu --states work/qa/ppu/states --script $SKILL/scripts/lua/probes/ppudump.lua
    python -X utf8 tools/gfx_chain.py
    python -X utf8 tools/gfx_scenes.py [work/qa/ppu]   -> work/gfx/scenes.tsv (scene, offset, kind, tiles matched)
"""
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402


def main():
    ppu = Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "work/qa/ppu")
    kind = {}
    for line in (ROOT / "docs/re/graphics_sweep.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        f = line.split("\t")
        kind[f[0]] = f[1]
    rows, seen = [], set()
    for vram in sorted(ppu.glob("*/ppu_*.vram.bin")):
        out = subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/vramfind.py"), str(vram),
                              str(ROOT / "work/gfx/blocks"), "--fmt", "gba4"], capture_output=True, text=True).stdout
        hits = defaultdict(int)
        for m in re.finditer(r"\(\s*(\d+) tiles\) <- \S+?([0-9A-F]{7})\.bin", out):
            hits[m.group(2)] += int(m.group(1))
        for off, n in sorted(hits.items()):
            if kind.get(off) in ("jp-text", "mixed") and n >= 4:
                rows.append(f"{vram.parent.name}\t{off}\t{kind[off]}\t{n}")
                seen.add(off)
    missing = sorted(o for o, k in kind.items() if k in ("jp-text", "mixed") and o not in seen)
    (ROOT / "work/gfx/scenes.tsv").write_text("\n".join(rows) + "\n" + "".join(f"-\t{o}\t{kind[o]}\t0\n" for o in missing))
    print(f"{len(seen)} rows seen in a scene, {len(missing)} not")


if __name__ == "__main__":
    main()
