"""gfx_modes.py: main-menu mode labels (gfx/modes.tsv) -> gfx/out/modes/*.png. Rerun after a wording change.
Six 128x32 labels (OBJ pal 1): white-haloed glyph strokes over an ellipse, teal (strokes 11, ellipse 9-11) or pink
(strokes 5, ellipse 3-5). The ellipse is the same shape in all six, so the clean ellipse takes each pixel by vote
across the six labels (pink mapped to teal) where it isn't text; the English goes on with gfx.typeset.
    python -X utf8 tools/gfx_modes.py
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

PINK = {3: 9, 4: 10, 5: 11}
TEXT_ROWS = 20  # text blob and its shadow sit in rows 0-19; the ellipse body below is untouched
BOX = (12, 1, 118, 19)


def clean(imgs):
    out = [r[:] for r in imgs[0]]
    for y in range(TEXT_ROWS):
        for x in range(128):
            if y < 14:  # above the ellipse top: only text (every label ends in ッチ, so a vote keeps that)
                out[y][x] = 0
                continue
            votes = Counter(PINK.get(im[y][x], im[y][x]) for im in imgs)
            bg = [(n, v) for v, n in votes.items() if v in (0, 9, 10, 11)]
            out[y][x] = max(bg)[1] if bg else (11 if y >= 14 else 0)
    return out


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("modes")
    rows = list(gfx.rows("modes"))
    texts = {}
    for line in (gfx.GFX / "modes.tsv").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            f = line.split("\t")
            texts[int(f[0], 16)] = f[4]
    imgs = {off: gfx.to_image(gfx.decode(rom, off, size)[0], layout) for _, off, size, layout, _ in rows}
    base = clean(list(imgs.values()))
    for _, off, size, layout, png in rows:
        pink = any(v in PINK for r in imgs[off][TEXT_ROWS:] for v in r)
        back = {v: k for k, v in PINK.items()} if pink else {}
        img = [[back.get(v, v) for v in r] for r in base]
        gfx.typeset(img, [texts[off]], BOX, fill=5 if pink else 11, outline=[15, 15], shadow=(1, 1, 1), gap=2)
        # the ellipse body below the text rows stays exactly the original
        img[TEXT_ROWS:] = [r[:] for r in imgs[off][TEXT_ROWS:]]
        gfx.save_png(img, pal, gfx.ROOT / png)
        print(png)


if __name__ == "__main__":
    main()
