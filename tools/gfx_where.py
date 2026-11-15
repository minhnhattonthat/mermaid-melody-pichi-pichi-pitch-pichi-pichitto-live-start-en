"""gfx_where.py: where a scene shows one block: its VRAM tiles (vramfind), the OAM sprites / BG map cells that use
them (palette, size, position), and the block rendered in the palette most used -> work/gfx/w_<off>.png.

    python -X utf8 tools/gfx_where.py SCENE OFFSET SPEC LAYOUT     e.g. gameover 1F0D0FC 800x1 tiles16
Needs the scene's PPU dump in work/qa/ppu/<scene>/ (docs/re/graphics.md §Redraws).
"""
import re
import shutil
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from skill import SKILL  # noqa: E402

SHAPES = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
          (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}


def main():
    scene, off, spec, layout = sys.argv[1:5]
    d = sorted((gfx.ROOT / "work/qa/ppu" / scene).glob("ppu_*.vram.bin"))[-1]
    vram, oam = d.read_bytes(), d.with_name(d.name.replace("vram", "oam")).read_bytes()
    pal = d.with_name(d.name.replace("vram", "pal")).read_bytes()
    io = d.with_name(d.name.replace("vram", "io")).read_bytes()
    tmp = gfx.ROOT / "work/gfx/one"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    shutil.copy(gfx.ROOT / f"work/gfx/blocks/{off}.bin", tmp)
    out = subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/vramfind.py"), str(d), str(tmp),
                          "--fmt", "gba4"], capture_output=True, text=True).stdout
    tiles, src = set(), {}
    for m in re.finditer(r"VRAM ([0-9A-F]+)-([0-9A-F]+) .*?(\S+)\.bin ([0-9A-F]+)-", out):
        a, b = int(m.group(1), 16), int(m.group(2), 16)
        print(m.group(0))
        tiles |= set(range(a // 32, b // 32 + 1))
        for k in range((b + 1 - a) // 32):
            src[a // 32 + k] = int(m.group(4), 16) // 32 + k
    tw = gfx.parse_layout(layout)[0]
    pals = Counter()
    for i in range(128):
        a0, a1, a2, _ = struct.unpack_from("<4H", oam, i * 8)
        if a0 >> 8 & 3 == 2:
            continue
        t = a2 & 1023
        if 0x10000 // 32 + t in tiles:
            w, h = SHAPES.get((a0 >> 14, a1 >> 14), (0, 0))
            # block tiles under the sprite (2D map: 32 tiles a row) -> pixel rect in the block render
            bt = [src.get(0x800 + t + r * 32 + c) for r in range(h // 8) for c in range(w // 8)]
            xs = [b % tw * 8 for b in bt if b is not None]
            ys = [b // tw * 8 for b in bt if b is not None]
            rect = f"block x {min(xs)}-{max(xs) + 7} y {min(ys)}-{max(ys) + 7}" if xs else ""
            print(f"OBJ {i}: tile {t} pal {a2 >> 12} {w}x{h} at {a1 & 511},{a0 & 255} prio {a2 >> 10 & 3}  {rect}")
            pals[16 + (a2 >> 12)] += 1
    for bg in range(4):
        cnt = struct.unpack_from("<H", io, 8 + 2 * bg)[0]
        cb, sb = (cnt >> 2 & 3) * 0x4000, (cnt >> 8 & 31) * 0x800
        for c in range(1024):
            e = struct.unpack_from("<H", vram, sb + 2 * c)[0]
            if (cb + (e & 1023) * 32) // 32 in tiles:
                pals[e >> 12] += 1
                if pals[e >> 12] == 1:
                    print(f"BG{bg}: char base {cb:X} screen {sb:X} cell {c % 32},{c // 32} tile {e & 1023} pal {e >> 12}")
    print("palettes (BG 0-15, OBJ 16-31):", dict(pals))
    p = (pals.most_common(1) or [(16, 0)])[0][0]
    cols = struct.unpack_from("<16H", pal, p * 32)
    (gfx.ROOT / f"work/gfx/w_{off}.pal").write_bytes(pal[p * 32:p * 32 + 32])
    a, b = spec.split("x")
    data, _ = gfx.decode((gfx.ROOT / "work/orig.gba").read_bytes(), int(off, 16), (int(a, 16), int(b)))
    gfx.save_png(gfx.to_image(data, layout), [gfx.rgb(c) for c in cols], gfx.ROOT / f"work/gfx/w_{off}.png")
    print(f"work/gfx/w_{off}.png (palette {p}, saved as work/gfx/w_{off}.pal)")


if __name__ == "__main__":
    main()
