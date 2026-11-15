"""oamlist.py: list a scene's visible OAM sprites (tile, pal, size, pos), optionally only inside a screen rect.

    python -X utf8 tools/oamlist.py SCENE [x0,y0,x1,y1]
Finding the block behind a sprite: its VRAM bytes are at 0x10000 + 32 * tile; dump them with --dump OUT.bin and
vramfind them against work/gfx/blocks/.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_where import SHAPES  # noqa: E402


def sprites(scene):
    d = sorted((gfx.ROOT / "work/qa/ppu" / scene).glob("ppu_*.vram.bin"))[-1]
    oam = d.with_name(d.name.replace("vram", "oam")).read_bytes()
    for i in range(128):
        a0, a1, a2, _ = struct.unpack_from("<4H", oam, i * 8)
        if a0 >> 8 & 3 == 2:
            continue
        w, h = SHAPES.get((a0 >> 14, a1 >> 14), (0, 0))
        yield i, a2 & 1023, a2 >> 12, w, h, a1 & 511, a0 & 255


def main():
    scene = sys.argv[1]
    box = [int(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    for i, t, p, w, h, x, y in sprites(scene):
        if box and not (box[0] <= x < box[2] and box[1] <= y < box[3]):
            continue
        print(f"OBJ {i}: tile {t} pal {p} {w}x{h} at {x},{y}")


if __name__ == "__main__":
    main()
