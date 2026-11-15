"""gfx_epnum.py: episode-select cursor numbers (gfx/epnum.tsv, 179BC34..179DE22, scene 25).
Each 32x32 cell = two digits + a white plate (border 15 at x 15/29, bottom y 28) with a pink 話 -> "EP" in plain caps.
The right digit's foot overlaps the plate at x 16-21 y 18-20, so rows 19-20 are cleared only from x 22.
    python -X utf8 tools/gfx_epnum.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

WHITE, PINK = 15, 8


def has_plate(img, x0, y0):
    return sum(img[y0 + 28][x0 + x] == WHITE for x in range(14, 31)) >= 12


def edit(img, x0, y0):
    """One 32x32 cell at (x0, y0) -> 1 if edited."""
    if not has_plate(img, x0, y0):
        # chunk 10 cell 1: light "40話" with no plate, 話 in 9 on transparent at x 18-29 y 19-26
        if any(img[y0 + y][x0 + x] for y in range(19, 28) for x in range(18, 31)):
            for y in range(19, 28):
                img[y0 + y][x0 + 18:x0 + 31] = [0] * 13
            gfx.typeset(img, ["EP"], (x0 + 17, y0 + 20, x0 + 31, y0 + 28), 9, [], bold=False)
            return 1
        return 0
    for y in range(19, 28):
        for x in range(16, 29):
            if 8 <= img[y0 + y][x0 + x] <= 14 and (y >= 21 or x >= 22):
                img[y0 + y][x0 + x] = WHITE
    gfx.typeset(img, ["EP"], (x0 + 16, y0 + 21, x0 + 29, y0 + 28), PINK, [], bold=False)
    return 1


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    (_, off, size, layout, png), = gfx.rows("epnum")
    img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
    n = sum(edit(img, x0, y0) for y0 in range(0, 32 * 11, 32) for x0 in range(0, 128, 32))  # chunk 11: no numbers
    print(png, n, "cells")
    gfx.save_png(img, gfx.load_pal("epnum"), gfx.ROOT / png)


if __name__ == "__main__":
    main()
