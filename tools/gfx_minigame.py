"""gfx_minigame.py: minigame title panels (room -> a game object -> title page; left/right cycles four games).
gfx/minipanel.tsv 1C00CFF (pages 1 and 2) / 1C00403 (page 3) / 1C01554 (page 4): BG1 pal 10 panel. Line 1 (two rows
of white 1 ringed E on a checker) says what you win; line 2 (white 1 ringed purple A, after the coin icon) says it
costs 100 coins. The checker under the erased text is rebuilt per row by majority vote over each x mod 8 phase.
The BG1 map of each page is a run-stream record (gfx_eptitle.decode_map format; found with tools/lua/execlog.lua at
0x03000BF0, r12) that dedups plain checker tiles, so the text rect is re-tiled: rect cells get tiles by content
(each its own tile from the slots no outside cell uses), and the record is rewritten (gfx/minipanel.maps, build
stage "maps").
    python -X utf8 tools/gfx_minigame.py
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_eptitle import decode_map, encode_map, tile  # noqa: E402

# block -> (map record, line 1)
PANELS = {0x1C00CFF: (0x1D250BA, ["You can win", "Pitch Coins!"]),
          0x1C00403: (0x1D2502C, ["You can win", "posters and cards!"]),
          0x1C01554: (0x1D25156, ["You can win", "mascots!"])}
COST = "Uses 100 coins!"
RECT = (2, 1, 19, 6)
BG = {2, 3, 4, 5, 9}  # checker colours
COIN_END = 30  # line 2 keeps the coin icon left of this column
SPLIT = 26  # first row of line 2
MAPS = gfx.GFX / "minipanel.maps"


def checker(im, rows, cols):
    """rebuild the 4+4 px checker of each row from the background pixels the text left."""
    for y in rows:
        votes = [Counter() for _ in range(8)]
        for x in cols:
            if im[y][x] in BG:
                votes[x % 8][im[y][x]] += 1
        yield y, [v.most_common(1)[0][0] for v in votes]


def orient(px, v):
    px = [r[::-1] for r in px] if v & 0x400 else px
    return px[::-1] if v & 0x800 else px


def compose(img, cells):
    x0, y0, w, h = RECT
    im = [[0] * (8 * w) for _ in range(8 * h)]
    for j in range(h):
        for i in range(w):
            v = cells[(y0 + j) * 32 + x0 + i]
            for r, row in enumerate(orient(tile(img, v & 0x3FF), v)):
                im[8 * j + r][8 * i:8 * i + 8] = row
    return im


def letter(im, lines):
    rows = [y for y in range(len(im)) if im[y][6] == 9 and im[y][8] in BG]
    x1 = 8
    while im[rows[0]][x1] in BG - {9}:  # 9 is also the border's middle line
        x1 += 1
    y0, y1, x0 = rows[0], rows[-1] + 1, 8
    pat = dict(checker(im, range(y0, y1), [x for x in range(x0, x1) if x >= COIN_END]))
    for y in range(y0, y1):
        for x in range(x0 if y < SPLIT else COIN_END, x1):
            im[y][x] = pat[y][x % 8]
    gfx.typeset(im, lines, (x0, y0, x1, SPLIT), 1, [14])
    gfx.typeset(im, [COST], (COIN_END, SPLIT, x1, y1), 1, [10], bold=False)


def retile(img, cells, im):
    """every rect cell gets its own tile (in reading order, from the slots no cell outside the rect uses: content
    dedup broke the map's increment runs and outgrew the record) -> new map cells (img edited)."""
    x0, y0, w, h = RECT
    inside = {(y0 + j) * 32 + x0 + i for j in range(h) for i in range(w)}
    keep = {cells[n] & 0x3FF for n in range(1024) if n not in inside}
    free = [k for k in range(len(img) // 8 * 16) if k not in keep]
    if len(free) < w * h:
        raise SystemExit(f"minigame panel: {w * h} rect cells, {len(free)} free tiles")
    new = list(cells)
    for j in range(h):
        for i in range(w):
            k = free.pop(0)
            for r in range(8):
                img[k // 16 * 8 + r][k % 16 * 8:k % 16 * 8 + 8] = im[8 * j + r][8 * i:8 * i + 8]
            new[(y0 + j) * 32 + x0 + i] = k
    for k in free:  # unused slots blank (smaller stream)
        for r in range(8):
            img[k // 16 * 8 + r][k % 16 * 8:k % 16 * 8 + 8] = [0] * 8
    return new


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    maps = ["# map record (file offset)\tnew run stream (hex): written in place by gfx_eptitle.apply (stage maps)"]
    for _, off, size, layout, png in gfx.rows("minipanel"):
        rec, lines = PANELS[off]
        img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
        cells, end = decode_map(rom, rec)
        im = compose(img, cells)
        letter(im, lines)
        new = retile(img, cells, im)
        assert compose(img, new) == im
        stream = encode_map(new)
        if len(stream) > end - rec:
            raise SystemExit(f"{rec:X}: new map {len(stream)} bytes > old {end - rec}")
        maps.append(f"{rec:07X}\t{stream.hex()}")
        gfx.save_png(img, gfx.load_pal("minipanel"), gfx.ROOT / png)
        print(png, f"map {len(stream)}/{end - rec} bytes")
    MAPS.write_text("\n".join(maps) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
