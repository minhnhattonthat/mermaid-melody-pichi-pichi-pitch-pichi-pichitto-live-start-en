"""objsrc.py: which decoded block (work/gfx/blocks/*.bin) holds the tiles of a scene's OBJ tile number(s).

    python -X utf8 tools/objsrc.py SCENE TILE [TILE..]
Prints per tile: block offset and tile index in the block (blank tiles skipped). 2D OBJ map: a WxH sprite at tile T
uses T + r * 32 + c.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402


def main():
    scene, tiles = sys.argv[1], [int(t) for t in sys.argv[2:]]
    d = sorted((gfx.ROOT / "work/qa/ppu" / scene).glob("ppu_*.vram.bin"))[-1]
    vram = d.read_bytes()
    blocks = {p.stem: p.read_bytes() for p in (gfx.ROOT / "work/gfx/blocks").glob("*.bin")}
    for t in tiles:
        b = vram[0x10000 + 32 * t:0x10000 + 32 * t + 32]
        if len(set(b)) == 1:
            print(f"tile {t}: blank")
            continue
        hits = [f"{n}#{k}" for n, data in blocks.items() for k in range(len(data) // 32) if data[32 * k:32 * k + 32] == b]
        print(f"tile {t}: {' '.join(hits[:6]) or '-'}")


if __name__ == "__main__":
    main()
