"""gfx_cards.py: room and card-game graphics text (room, card_game, minigame_1/2).
gfx/cardbtn.tsv 1D031F4 (128x64): four 64x32 buttons あそぶ する / やめる しない -> Play Yes / Quit No, white on the
  pink fill (index 1), text area x 9-54 y 9-22 of each button.
gfx/roombub.tsv 1D09C87 (128x128): five 96x24 bubbles, 24 px apart, white text on fill 6 (x 5-85, y 5-18).
gfx/hint.tsv 1D01FD9 (chain, OBJ tiles shared by every scene that shows it): Aきめる / Bやめる -> A OK / B Quit; the
  button letter (x 0-10 of the 48x16 pair) stays, the word is redrawn pink (12) with a dark ring (4) and shadow (1).
  Edited through the room's sprites (OAM 4,3 and 2,1: tools/gfx_obj.py).
gfx/prompt.tsv 1C07510 (BG1 of card_game, map cells 2-13 x 2-6): ゲームする? -> Play a game?, white (7), shadow 5.
    python -X utf8 tools/gfx_cards.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_bg import Layer  # noqa: E402
from gfx_gameover import mask  # noqa: E402
from gfx_obj import Sprites  # noqa: E402

BUTTONS = [("Play", 0, 0), ("Yes", 64, 0), ("Quit", 0, 32), ("No", 64, 32)]
BUBBLES = ["Put up a poster?", "Play a game?", "Place a mascot?", "Listen to a song?", "View cards?"]
HINTS = [("OK", [4, 3]), ("Quit", [2, 1])]
PROMPT = ("Play a game?", (2, 2, 12, 5))


def fit(img, text, box, fill, outline, shadow=None):
    """bold if it fits, else plain."""
    for bold in (True, False):
        try:
            return gfx.typeset(img, [text], box, fill, outline, bold=bold, shadow=shadow)
        except ValueError:
            if not bold:
                raise


def buttons(img, data, layout):
    for word, x0, y0 in BUTTONS:
        for y in range(y0 + 9, y0 + 23):
            for x in range(x0 + 9, x0 + 55):
                img[y][x] = 1
        fit(img, word, (x0 + 9, y0 + 8, x0 + 55, y0 + 24), 15, [])


def bubbles(img, data, layout):
    for k, text in enumerate(BUBBLES):
        y0 = 24 * k
        for y in range(y0 + 5, y0 + 19):
            for x in range(5, 86):
                img[y][x] = 6
        gfx.typeset(img, [text], (5, y0 + 4, 86, y0 + 20), 15, [], bold=False)  # bold only fits some: keep one weight


def hints(img, data, layout):
    for word, ids in HINTS:
        s = Sprites("room", ids)
        im = s.compose()
        for row in im:
            row[11:] = [0] * (len(row) - 11)
        w = mask(word, 1, 1)[1]
        gfx.typeset(im, [word], (13, 0, 15 + w, 13), 12, [4], shadow=(1, 1, 1))  # 1 px gap after the letter
        s.write(img, data, im, layout)


def prompt(img, data, layout):
    text, rect = PROMPT
    L = Layer("card_game", 1)
    im = L.compose(rect)
    for y in range(9, 22):
        for x in range(8, 89):
            im[y][x] = 1
    gfx.typeset(im, [text], (8, 8, 88, 22), 7, [], shadow=(5, 1, 1))
    L.write(img, data, rect, im, layout)


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    for group, fn in (("cardbtn", buttons), ("roombub", bubbles), ("hint", hints), ("prompt", prompt)):
        (_, off, size, layout, png), = gfx.rows(group)
        data = gfx.decode(rom, off, size)[0]
        img = gfx.to_image(data, layout)
        fn(img, data, layout)
        gfx.save_png(img, gfx.load_pal(group), gfx.ROOT / png)
        print(png)


if __name__ == "__main__":
    main()
