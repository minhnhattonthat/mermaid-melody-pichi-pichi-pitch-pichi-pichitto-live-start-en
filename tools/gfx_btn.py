"""gfx_btn.py: cloud buttons of pause / game over / continue prompts (gfx/btn.tsv) -> gfx/out/btn/<off>.png.
Each block is a 128-px-wide OBJ sheet (tiles16) of 64x32 cloud bubbles: violet kana (fill 10-13) in a light ring
(13-14) on cloud fill 3; stars/notes use 4-9, F. The kana (10-14) inside the bubble is painted back to 3, the English
goes on in 10 with rings 14, 13. A crossed-out bubble keeps its X (7-9) drawn back over the English.
1F0E3F7 rows 64-95: the prompt ほんとうにはじめからでいいですか? (one 128x16 line + 64x16 tail, transparent 0), redrawn
as one line in the first 128 px; the highlighted word uses fill 5, ring 9 like はじめから.
    python -X utf8 tools/gfx_btn.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enfont  # noqa: E402
import gfx  # noqa: E402

TEXT = {10, 11, 12, 13, 14}
# offset -> bubble words in sheet order (64x32 each, row-major in 128 px); None = no text; (word, True) = crossed out
BUBBLES = {
    0x1F0D0FC: ["Quit", "Continue"],                                  # やめる つづける
    0x1F0D56D: ["Quit", "Retry"],                                     # やめる もういちど
    0x1F0DA41: ["Continue", "New Game", ("Continue", True), "Select"],  # つづきから はじめから つづ✗から えらぶ
    0x1F0E3F7: ["Yes", "No"],                                         # はい いいえ
}
PROMPT = ("Start a ", "New Game", "?")  # ほんとうに[はじめから]でいいですか?


def bubble(img, cx, cy, word, crossed=False):
    orig = [row[:] for row in img]
    for y in range(cy + 6, cy + 25):
        for x in range(cx + 3, cx + 61):
            if img[y][x] in TEXT:
                img[y][x] = 3
    gfx.typeset(img, [word], (cx + 4, cy + 6, cx + 60, cy + 24), fill=10, outline=[14, 13])
    if crossed:
        for y in range(cy + 2, cy + 30):
            for x in range(cx + 8, cx + 56):
                if orig[y][x] in (7, 8, 9):
                    img[y][x] = orig[y][x]


def prompt(img):
    for y in range(64, 96):
        img[y][:] = [0] * len(img[y])
    font = {c: rows for c, rows in enfont.load()}
    text = "".join(PROMPT)
    gfx.typeset(img, [text], (0, 64, 128, 80), fill=10, outline=[14, 13])
    w = sum(len(font[c][0]) + 2 for c in text) - 1
    x0 = (128 - w + 1) // 2 + sum(len(font[c][0]) + 2 for c in PROMPT[0])
    x1 = x0 + sum(len(font[c][0]) + 2 for c in PROMPT[1])
    for y in range(64, 80):
        for x in range(max(x0 - 2, 0), min(x1 + 1, 128)):
            img[y][x] = {10: 5, 11: 5, 12: 5, 13: 9, 14: 9}.get(img[y][x], img[y][x])


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("btn")
    for _, off, size, layout, png in gfx.rows("btn"):
        img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
        for i, w in enumerate(BUBBLES[off]):
            word, crossed = w if isinstance(w, tuple) else (w, False)
            bubble(img, i % 2 * 64, i // 2 * 32, word, crossed)
        if off == 0x1F0E3F7:
            prompt(img)
        gfx.save_png(img, pal, gfx.ROOT / png)
        print(png)


if __name__ == "__main__":
    main()
