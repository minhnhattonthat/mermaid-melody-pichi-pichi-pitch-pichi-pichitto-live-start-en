"""gfx_cards.py: room and card-game graphics text (room, card_game, minigame_1/2).
gfx/cardbtn.tsv 1D031F4 (128x64): four 64x32 buttons あそぶ する / やめる しない -> Play Yes / Quit No, white on the
  pink fill (index 1), text area x 9-54 y 9-22 of each button.
gfx/roombub.tsv 1D09C87 (128x128): five 96x24 bubbles, 24 px apart, white text on fill 6 (x 5-85, y 5-18).
gfx/hint.tsv 1D01FD9 (chain, OBJ tiles shared by every scene that shows it): Aきめる / Bやめる -> A OK / B Quit; the
  button letter (x 0-10 of the 48x16 pair) stays, the word is redrawn pink (12) with a dark ring (4) and shadow (1).
  Edited through the room's sprites (OAM 4,3 and 2,1: tools/gfx_obj.py).
gfx/prompt.tsv 1C07510 (BG1 of card_game, map cells 2-13 x 2-6): ゲームする? -> Play a game?, white (7), shadow 5.
gfx/bonus.tsv 1D095BE: おまけムービー! banner (96x24 at 0,0: white 4 inside x 6-86 y 5-18) -> Bonus Movie! in gold 15.
    python -X utf8 tools/gfx_cards.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_bg import Layer  # noqa: E402
from gfx_gameover import mask  # noqa: E402
from gfx_obj import Sprites  # noqa: E402
from gfx_eptitle import decode_map, encode_map  # noqa: E402
import gfx_minigame as minigame  # noqa: E402
from gfx_winlose import ring  # noqa: E402

BUTTONS = [("Play", 0, 0), ("Yes", 64, 0), ("Quit", 0, 32), ("No", 64, 32)]
# card game (くらべてピッチ, warp card_game + A presses): (text, button x1, top of each button)
HILO = (["Higher!", "Lower!"], 87, [0, 35])  # 1D02946 おおきい! / ちいさい! (96x28 buttons)
CONT = (["Keep going", "Stop here"], 71, [0, 32])  # 1D02DEB つづける / やめておく (80x28 buttons)
# BG1 prompt panels: text, map record (run stream, gfx_eptitle.decode_map; found by matching the BG1 map of the
# dumps work/qa/ppu/card_pick, card_hilo), text rect in cells (all panel fill), index of the fill. The record dedups
# blank fill tiles, so the rect is re-tiled (gfx_minigame.retile) and the record rewritten (gfx/cards.maps).
PANELS = {"pick": (["Pick any one card!"], 0x1D254B7, (2, 3, 20, 2), 1),  # 1C04DE8 どれかいちまいえらんでね。
          "hilotxt": (["Is the face-down card", "higher or lower than the left?"], 0x1D25528, (3, 3, 20, 3),
                      2),  # 1C0537C ふせてあるカードは ひだりのカードより…?
          "conttxt": (["Keep going and your coins", "will double!"], 0x1D258E7, (2, 2, 20, 4),
                      2),  # 1C078DE つづけてやると コインがばいにふえるよ! (dump work/qa/ppu/card_cont)
          "memo": (["Match the same pictures!"], 0x1D255BC, (2, 3, 20, 2), 1, 4),  # 1C05A1E おなじえをそろえてね。
          "crane": (["Hold A to move,", "let go to grab!"], 0x1D2563D, (3, 3, 18, 4), 1, 4),  # 1C05F03
          # Aボタンでいどう、はなすとつかむよ! (crane game start)
          "guess": (["Find the matching card", "among these!"], 0x1D25428, (3, 3, 18, 4), 1, 5)}  # 1C047A6
          # このなかから おなじカードをあててね! (screen not reached; record matched by the panel frame + reading order)
PANELS.update({"again": (["Keep playing?"], 0x1D256CE, (3, 2, 12, 3), 1, 7, 3),  # 1C0657A つづけてあそぶ? (after a win)
               "nocoin": (["Not enough coins!"], 0x1D25730, (3, 2, 15, 3), 1, 7, 3),  # 1C06A00 コインがたりないよ!
               "stop": (["Stop it wherever you like!"], 0x1D25791, (5, 15, 20, 2), 1, 4)})  # 1C06EBF 800x2
# すきなところでとめてね! (wide bottom panel under a card frame; record matched by tile count, screen not reached)
# again / nocoin: smaller frame, records found by rendering each block with the records after 1D2563D
# memory game start panel: dump work/qa/ppu/mem_panel (play.py state work/play/mem/0000.mss + "6 a;200 -")
MAPS = gfx.GFX / "cards.maps"
# Big result words on BG1 (map records found as for PANELS; the record must not grow: a new tile mid-run costs bytes,
# so the text sits on cells with their own tiles, retile_keep, nudged DX px). Spec: word, record, rect (cells),
# letter box (map px x0, y0, x1, y1: x0..x1 is also the erase span), DX, erase mode, rings outermost first, shadow.
# ざんねん (lost card / memory game, 1C023B4 800x4): the four kana are the ink components lying wholly in x0..x1
#   (the bubbles are other components and stay) -> Too bad!: fill 3, dark ring 1, white ring 5, outer edge 4.
# あたり (won round, 1C030D4 800x4): the kana touch the stars, so erase = ink within 7 px of the kana's fill
#   (index 3, components of 30+ px; stars hold only specks of 3) -> Right!: fill 3, rings 1 5 5 4, shadow 1 (+2,+2).
BIGWORDS = {"zannen": ("Too bad!", 0x1D252A4, (5, 0, 19, 8), (42, 16, 184, 43), 0, "components", [4, 5, 1], None),
            "atari": ("Right!", 0x1D2532D, (4, 0, 18, 8), (36, 8, 162, 56), 0, "near3", [4, 5, 5, 1], 1),
            # ゲット! (1C01D37 800x2, crane win?) and やったね (1C03D2A 800x4, memory win?): same palette roles as
            # ざんねん; records matched by tile count (last tile used = record's max index), screens not reached
            "getto": ("Got it!", 0x1D251F3, (4, 0, 18, 8), (38, 8, 174, 56), 0, "components", [4, 5, 1], None),
            "yatta": ("Hooray!", 0x1D2539F, (6, 0, 20, 8), (48, 8, 204, 58), 0, "components", [4, 5, 1], None)}


def erase_near(im, ox, span, idx=3, dist=7, minpx=30):
    """erase ink within `dist` px (Chebyshev) of fill-`idx` components of minpx+ pixels inside span (map x)."""
    seeds, seen = set(), set()
    for y in range(len(im)):
        for x in range(len(im[0])):
            if im[y][x] == idx and (x, y) not in seen and span[0] <= x + ox < span[1]:
                comp, st = {(x, y)}, [(x, y)]
                while st:
                    px, py = st.pop()
                    for q in ((px + a, py + b) for a in (-1, 0, 1) for b in (-1, 0, 1)):
                        if q not in comp and 0 <= q[0] < len(im[0]) and 0 <= q[1] < len(im) and im[q[1]][q[0]] == idx:
                            comp.add(q)
                            st.append(q)
                seen |= comp
                if len(comp) >= minpx:
                    seeds |= comp
    for x, y in {(x + a, y + b) for x, y in seeds for a in range(-dist, dist + 1) for b in range(-dist, dist + 1)}:
        if 0 <= x < len(im[0]) and 0 <= y < len(im):
            im[y][x] = 0


def bigword(group, maps):
    word, rec, rect, (x0, y0, x1, y1), dxn, mode, rings, shadow = BIGWORDS[group]

    def fn(img, data, layout):
        rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
        cells, end = decode_map(rom, rec)
        im = minigame.compose(img, cells, rect)
        ox = 8 * rect[0]
        if mode == "components":
            for y in range(len(im)):  # erase every ink component lying wholly inside the letter box's columns
                for x in range(len(im[0])):
                    if im[y][x] and x0 <= x + ox < x1:
                        component(im, x, y, ox, (x0, x1))
        else:
            erase_near(im, ox, (x0, x1))
        pad = 2 * len(rings) + (2 if shadow is not None else 0)
        for sy in (4, 3):
            ink, w, h = mask(word, 3, sy)
            if w + pad <= x1 - x0 and h + pad <= y1 - y0:
                break
        dx, dy = x0 - ox + (x1 - x0 - w) // 2 + dxn, y0 + (y1 - y0 - h) // 2
        ink = {(x + dx, y + dy) for x, y in ink}
        layers, shape = [], set(ink)
        for c in reversed(rings):  # innermost ring first
            r = ring(shape)
            layers.append((r, c))
            shape |= r
        if shadow is not None:
            for x, y in shape:
                if 0 <= y + 2 < len(im) and 0 <= x + 2 < len(im[0]):
                    im[y + 2][x + 2] = shadow
        for pts, c in layers[::-1] + [(ink, 3)]:  # outermost first
            for x, y in pts:
                im[y][x] = c
        new = minigame.retile_keep(img, cells, im, rect)
        assert minigame.compose(img, new, rect) == im
        stream = encode_map(new)  # a longer stream is moved by the maps stage (gfx_eptitle.placed)
        maps.append(f"{rec:07X}\t{stream.hex()}")
    return fn


def component(im, x, y, ox, span):
    """erase the 8-connected ink component at (x, y) if all of it lies within span (map x)."""
    pts, st = {(x, y)}, [(x, y)]
    while st:
        px, py = st.pop()
        for q in ((px + a, py + b) for a in (-1, 0, 1) for b in (-1, 0, 1)):
            if q not in pts and 0 <= q[0] < len(im[0]) and 0 <= q[1] < len(im) and im[q[1]][q[0]]:
                pts.add(q)
                st.append(q)
    if all(span[0] <= px + ox < span[1] for px, _ in pts):
        for px, py in pts:
            im[py][px] = 0
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


def wide_buttons(spec):
    """two stacked buttons: fill 6 inside x 9..x1, text rows 9-19 below each top; white (15) text."""
    words, x1, tops = spec

    def fn(img, data, layout):
        for word, y0 in zip(words, tops):
            for y in range(y0 + 9, y0 + 20):
                img[y][9:x1 + 1] = [6] * (x1 - 8)
            fit(img, word, (9, y0 + 7, x1 + 1, y0 + 22), 15, [])
    return fn


def panel(group, maps):
    lines, rec, rect, bg, *opt = PANELS[group]
    core, keep = (opt + [7, 0][len(opt):])  # index of the original lettering's white core; top pixel rows kept
    # (keep > 0: the rect's first cell row also holds the frame ornament, kept; the kana tops below it are erased)

    def fn(img, data, layout):
        rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
        cells, end = decode_map(rom, rec)
        orig = minigame.compose(img, cells, rect)
        im = [list(r) if y < keep else [bg] * len(r) for y, r in enumerate(orig)]
        for bold in (True, False):  # white core, as the original lettering
            try:
                gfx.typeset(im, lines, (2, keep, len(im[0]) - 2, len(im)), core, [], bold=bold)
                break
            except ValueError:
                if not bold:
                    raise
        new = minigame.retile(img, cells, im, rect)
        assert minigame.compose(img, new, rect) == im
        stream = encode_map(new)
        if len(stream) > end - rec:
            raise SystemExit(f"{rec:X}: new map {len(stream)} bytes > old {end - rec}")
        maps.append(f"{rec:07X}\t{stream.hex()}")
    return fn


def bonus(img, data, layout):
    for y in range(5, 19):
        img[y][6:87] = [4] * 81
    fit(img, "Bonus Movie!", (6, 4, 87, 20), 15, [])


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    maps = ["# map record (file offset)\tnew run stream (hex): written in place by gfx_eptitle.apply (stage maps)"]
    for group, fn in (("cardbtn", buttons), ("roombub", bubbles), ("hint", hints), ("prompt", prompt),
                      ("bonus", bonus), ("hilo", wide_buttons(HILO)), ("cont", wide_buttons(CONT)),
                      ("pick", panel("pick", maps)), ("hilotxt", panel("hilotxt", maps)),
                      ("conttxt", panel("conttxt", maps)), ("memo", panel("memo", maps)),
                      ("crane", panel("crane", maps)), ("guess", panel("guess", maps)),
                      ("again", panel("again", maps)), ("nocoin", panel("nocoin", maps)),
                      ("zannen", bigword("zannen", maps)), ("atari", bigword("atari", maps)),
                      ("getto", bigword("getto", maps)), ("yatta", bigword("yatta", maps)),
                      ("stop", panel("stop", maps))):
        (_, off, size, layout, png), = gfx.rows(group)
        data = gfx.decode(rom, off, size)[0]
        img = gfx.to_image(data, layout)
        fn(img, data, layout)
        gfx.save_png(img, gfx.load_pal(group), gfx.ROOT / png)
        print(png)
    MAPS.write_text("\n".join(maps) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
