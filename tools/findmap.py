"""findmap.py: which resource-table block decodes to a scene's BG map (so a picture's siblings' maps can be found).
    python -X utf8 tools/findmap.py SCENE BG          -> resource pointers whose first 0x800 decoded bytes hold the map
Every pointer in work/gfx/restables.tsv (tools/restables.py) is tried as a kcomp stream.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
import kcomp  # noqa: E402


def main():
    scene, bg = sys.argv[1], int(sys.argv[2])
    d = sorted((gfx.ROOT / "work/qa/ppu" / scene).glob("ppu_*.vram.bin"))[-1]
    vram = d.read_bytes()
    io = d.with_name(d.name.replace("vram", "io")).read_bytes()
    sb = (struct.unpack_from("<H", io, 8 + 2 * bg)[0] >> 8 & 31) * 0x800
    want = vram[sb:sb + 60]  # first map row (a 30-wide source map matches too)
    rom = (gfx.ROOT / "work/orig.gba").read_bytes()
    for line in (gfx.ROOT / "work/gfx/restables.tsv").read_text().splitlines():
        off = int(line.split("\t")[0], 16)
        try:
            data, _ = kcomp.decompress(rom, off, 0x800)
        except Exception:
            continue
        if data[:len(want)] == want:
            print(f"{off:X}\t{line}")


if __name__ == "__main__":
    main()
