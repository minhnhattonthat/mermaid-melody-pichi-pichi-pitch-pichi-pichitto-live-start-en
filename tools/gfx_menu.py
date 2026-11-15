"""gfx_menu.py: main-menu captions (gfx/menu.tsv) -> gfx/out/menu/*.png. Rerun after a wording change.

The six captions share one flower banner; their text uses only indices 12-15. The clean banner takes each pixel from a
caption where it isn't text (else from 64 px away: the banner repeats every 8 tiles), then the English is typeset on it.
    python -X utf8 tools/gfx_menu.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

TEXT = {12, 13, 14, 15}
BOX = (6, 3, 234, 29)  # banner interior on screen (x 0-239)


def clean(imgs):
    h, w = len(imgs[0]), len(imgs[0][0])
    out = [[None] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            out[y][x] = next((im[y][x] for im in imgs if im[y][x] not in TEXT), None)
    for y in range(h):
        for x in range(w):
            if out[y][x] is None:
                out[y][x] = next(out[y][xx] for xx in (x - 64, x + 64, x - 128, x + 128)
                                 if 0 <= xx < w and out[y][xx] is not None)
    return out


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("menu")
    rows = list(gfx.rows("menu"))
    texts = {}
    for line in (gfx.GFX / "menu.tsv").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            f = line.split("\t")
            texts[int(f[0], 16)] = f[4].split("|")
    imgs = [gfx.to_image(gfx.decode(rom, off, size)[0], layout) for _, off, size, layout, _ in rows]
    base = clean(imgs)
    for _, off, size, layout, png in rows:
        img = [r[:] for r in base]
        n = len(texts[off])
        gfx.typeset(img, texts[off], BOX, fill=15, top=14, outline=12, lead=11 if n > 1 else 12)
        gfx.save_png(img, pal, gfx.ROOT / png)
        print(png)


if __name__ == "__main__":
    main()
