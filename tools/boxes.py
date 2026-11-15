"""boxes.py: per-unit text budgets (the phase-5 width gate, docs/re/vwf.md §Boxes), the fit lint and the story-bubble
auto-grow the English build applies.

    python -X utf8 tools/boxes.py [--lang en|jp] [--warn]   # fit report; exit 1 on any error

Rule (read from the wrap code 0x08007688): the last glyph of a line must start at px <= W*8 - 12, so a line fits when
its width minus its last glyph's advance is <= `limit`. Lines per page: an error only past both the box (H/2) and what
the Japanese unit already does on its longest page (the bubbles scroll: 71 Japanese pages run 4-5 lines in H 6).
Budgets: story bubbles from the event scripts (W may grow to 28 at build, `grow`), ranges for the measured variants,
unobserved ids a guess (narration, 196 px / 3 lines: warnings only)."""
import math
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enfont  # noqa: E402
import msgboxes  # noqa: E402
from msgcodec import TOKEN  # noqa: E402

EVENTS = (0x1F5C660, 0x1F67000)  # event-script u16 stream; past ~0x1F67000 the linear walk desyncs in data (false bubbles)
MSG_BASE = 0x500  # op 10 shows message (arg & 0x7FFF) + 0x500
MAX_W = 28  # widest bubble the game uses (col + W <= 29)
NAME_PX = 60  # shortcut: F6 00/01/02/0A (player name etc.) guessed at 60 px; measure when English name entry exists
DIGIT_PX = 7  # shortcut: FB numbers guessed at (format & 0xF, at least 2) digits of 7 px


def bubbles(rom):
    """-> {message id: (file offset of the op-9 word, col, row, W, H, tail)}: the last set-bubble before each
    show-message. tail 0 = no bubble tail (framed story boxes at col 1 W 28, or text straight on the scene)."""
    a, b = EVENTS
    ws = struct.unpack_from(f"<{(b - a) // 2}H", rom, a)
    out, box, i = {}, None, 0
    while i < len(ws):
        n, op = ws[i] >> 12, ws[i] & 0xFFF
        if n == 0:  # not an op (data block inside the stream): resync on the next word
            i += 1
            continue
        if op == 9 and n == 4:
            box = (a + 2 * i, ws[i + 1] >> 8, ws[i + 1] & 0xFF, ws[i + 2] >> 8, ws[i + 2] & 0xFF, ws[i + 3] >> 8)
        elif op == 10 and n == 3 and box:
            out.setdefault((ws[i + 1] & 0x7FFF) + MSG_BASE, box)
        i += n
    return out


SONG = (0x1F5C660, 0x1F74000)  # gameplay event stream holding op 6 (in-song dialogue boxes)
SONG_COLS = (4, 26)  # a song box stays between the side gauges: col >= 4, col + W <= 26 (Japanese uses 4..24)


def song_boxes(rom):
    """-> {message id: [(file offset of the op-6 word, col, row, W, H), ...]}: op 0x7006 = t, message - 0x500,
    duration, col<<8|row, W<<8|H, 0; drawn in 8 px mode (flags bit 0) through the VWF (docs/re/vwf.md)."""
    a, b = SONG
    ws = struct.unpack_from(f"<{(b - a) // 2}H", rom, a)
    out = {}
    for i in range(len(ws) - 6):
        msg, cr, wh, z = ws[i + 2], ws[i + 4], ws[i + 5], ws[i + 6]
        if ws[i] == 0x7006 and msg < 0x800 and cr >> 8 < 30 and cr & 0xFF < 20 and 1 <= wh >> 8 <= 30 \
                and wh & 0xFF in (2, 4, 6, 8) and z == 0:
            out.setdefault(msg + MSG_BASE, []).append((a + 2 * i, cr >> 8, cr & 0xFF, wh >> 8, wh & 0xFF))
    return out


# (first id, last id, kind, last-glyph start limit px, lines per page); None limit = not lint-checked
RANGES = [
    (0, 6, "numbers/debug", None, None),
    (252, 255, "font test", None, None),  # 1ADE: debug charset line, no spaces to wrap at
    (128, 141, "profiles", 212, 9),  # 【name】 + text; box unseen: the game char-wraps (Japanese lines run to 76 kana)
    (80, 80, "credits", 220, 9), (88, 98, "credits", 220, 9),  # Japanese runs to 216: no wrap, screen edge at col 1
    (256, 305, "lyrics", 180, 1), (512, 1023, "lyrics", 180, 1),  # = longest Japanese line; UI sprites cover x > ~200
    (1024, 1030, "link messages", 212, 1),
    (1281, 1329, "narration", 196, 6),
]
GUESS = ("guess", 196, 3)
SEEN = msgboxes.load()


def fixed(box):
    """A tail-less box off col 1 is text straight on the scene (EP 13 Aqua Regina inside a drawn frame): grown to col
    1 it covers the frame, so it keeps its width (15 boxes)."""
    return box[5] == 0 and box[1] > 1


def budget(e, bub, song=None):
    """-> (kind, limit, lines, guess) for unit `e` (its tightest message id)."""
    out = []
    for mid in e["ids"]:
        if song and mid in song:  # may grow to SONG_COLS (`grow`); 8 px mode: last glyph starts <= W*8 - 8
            out.append(("song dialogue", (SONG_COLS[1] - SONG_COLS[0]) * 8 - 8, min(b[4] for b in song[mid]) // 2,
                        False))
            if mid not in bub:
                continue
        if mid in bub:  # any bubble may grow to W 28 at col 1 (`grow`; checked in EP 1, work/p5/g1.png)
            w = bub[mid][3] if fixed(bub[mid]) else MAX_W
            out.append(("bubble", w * 8 - 12, bub[mid][4] // 2, False))
            continue
        for lo, hi, kind, limit, lines in RANGES:
            if lo <= mid <= hi:
                out.append((kind, limit, lines, False))
                break
        else:
            if mid in SEEN:  # box measured in game (docs/re/msgboxes.tsv); 8 px mode: last glyph <= W*8 - 8
                w, h, flags = SEEN[mid]
                out.append(("seen", w * 8 - (8 if flags & 1 else 12), h // 2, False))
            else:
                out.append(GUESS + (True,))
    return min(out, key=lambda b: (b[3], b[1] is None, b[1] or 0, b[2] or 0))  # measured before guessed, then tightest


def unit_budgets(entries, bub, song=None):
    """-> {unit id: budget}. A unit with no message id takes the budget of a unit that jumps to it (not a call)."""
    out = {e["id"]: budget(e, bub, song) for e in entries if e["ids"]}
    for e in entries:
        for m in re.finditer(r"\{(\w+):([0-9A-F@]*)\}", e["jp"]):
            if m[1] != "call" and e["id"] in out:
                for t in re.findall(r"@([0-9A-F]{4,5})", m[2]):
                    out.setdefault(t, out[e["id"]])
    return out


def pages(text, lang, units, widths, sp=12):
    """-> list of pages, each a list of lines (px, last glyph advance), name tags on their own line left out (a tag
    closed without a newline, 2B99 in song dialogue, counts on the line it starts). `units`: id -> entry.
    sp: the box's starting spacing (8 for boxes opened in 8 px mode)."""
    pg, st = [[[0, 0, 0]]], {"sp": sp, "tag": False, "tagpx": 0, "tagadv": 0, "tagnl": False}
    # line = [px, last advance, pending space px]

    def run(t, depth):
        for m in TOKEN.finditer(t):
            name, args = m[1], m[2] or ""
            line = pg[-1][-1]
            if st["tag"] and not (name == "FA" and args == "0C0088") and name != "call":
                if m[0] == "\n":
                    st["tagnl"] = True
                elif not name and not m[3] and m[0] not in " 　":
                    st["tagadv"] = widths.get(m[0], 12) if lang != "jp" else st["sp"]
                    st["tagpx"] += st["tagadv"]
                continue
            if name == "FA" and args == "0C0088" and st["tag"] and not st["tagnl"] and st["tagpx"]:
                line[0] += line[2] + st["tagpx"]
                line[1], line[2] = st["tagadv"], 0
            if m[0] == "\n" or (name == "FA" and args.startswith("11")):  # FA 11 n: credits column move
                pg[-1].append([0, 0, 0])
            elif name == "call":
                u = units[args[1:]]
                if depth < 8 and run(u.get(lang) or u["jp"], depth + 1):
                    return True
            elif name in ("end", "goto"):
                return depth == 0 or name == "goto"
            elif name == "wait" or (name == "FA" and args == "06"):
                pg.append([[0, 0, 0]])
            elif name == "FA" and args in ("0C0008", "0C0088"):
                st["tag"] = args == "0C0008"
                st["tagpx"], st["tagnl"] = 0, False
            elif name == "FD":
                st["sp"] = 8 if int(args, 16) & 1 else 16 if int(args, 16) & 0x80 else 12
            elif name in ("F6", "FB"):
                sub = int(args[:2], 16)
                px = (NAME_PX if sub & 0x1F != 5 else 0) if name == "F6" else DIGIT_PX * max(int(args[-2:], 16) & 0xF, 2)
                if px:
                    line[0] += line[2] + px
                    line[1], line[2] = min(px, 12), 0
            elif name or m[3]:
                pass
            elif m[0] in " 　":  # trailing spaces never count (credits pad lines with them)
                line[2] += widths.get(m[0], 12) if st["sp"] in (8, 12) and lang != "jp" else st["sp"]
            else:  # the VWF draws English at spacing 12 and in 8 px mode (FD 01) alike
                adv = widths.get(m[0], 12) if st["sp"] in (8, 12) and lang != "jp" else st["sp"]
                line[0] += line[2] + adv
                line[1], line[2] = adv, 0
        return False

    run(text, 0)
    out = []
    for p in pg:
        while len(p) > 1 and p[-1][0] == 0:  # trailing blank lines (a newline before {end})
            p = p[:-1]
        out.append([(px, last) for px, last, _ in p])
    return out


def lines_needed(pgs):
    return max((len(p) for p in pgs if any(px for px, _ in p)), default=0)


def need_px(pgs):
    """Smallest last-glyph start limit the text fits."""
    return max((px - last for p in pgs for px, last in p if px), default=0)


def lint(entries, lang="en", bub=None, song=None):
    """-> [(level, unit id, message)], level 'error' or 'warn'. Only units with `lang` text (all used units for jp)."""
    widths = {ch: enfont.width(rows) for ch, rows in enfont.load()}
    units = {e["id"]: e for e in entries}
    budgets = unit_budgets(entries, bub or {}, song)
    out = []
    for e in entries:
        text = e.get(lang) if lang != "jp" else (e["jp"] if e["used"] else "")
        if not text or e["id"] not in budgets:
            continue
        kind, limit, lines, guess = budgets[e["id"]]
        if limit is None:
            continue
        sp = 8 if kind == "song dialogue" else 12
        pgs = pages(text, lang, units, widths, sp)
        jp_lines = lines_needed(pages(e["jp"], "jp", units, widths, sp))
        level = "warn" if guess else "error"
        need = need_px(pgs)
        if need > limit and not (lang == "jp" and (sp == 8 or kind in ("profiles", "seen"))):
            # ^ kana lines the engine auto-wraps at any glyph (song lines; Japanese written as one long line)
            out.append((level, e["id"], f"{kind}: line needs {need} px, limit {limit}"))
        n = lines_needed(pgs)
        if n > max(lines, jp_lines):
            out.append((level, e["id"], f"{kind}: {n} lines on a page, box {lines}, Japanese {jp_lines}"))
        elif n > lines:
            out.append(("warn", e["id"], f"{kind}: {n} lines on a page scroll a {lines}-line box"))
    return out


def grow(rom, entries, lang="en"):
    """Widen each story bubble to fit its `lang` text (W <= 28, col moved left so col + W <= 29). -> boxes changed."""
    widths = {ch: enfont.width(rows) for ch, rows in enfont.load()}
    units = {e["id"]: e for e in entries}
    need = {}
    bub = bubbles(rom)
    for e in entries:
        if not e.get(lang):
            continue
        for mid in e["ids"]:
            if mid in bub and not fixed(bub[mid]):
                w = math.ceil((need_px(pages(e[lang], lang, units, widths)) + 12) / 8)
                need[bub[mid]] = max(need.get(bub[mid], 0), w)
    changed = 0
    for (off, col, row, w, h, _), nw in need.items():
        nw = min(nw, MAX_W)
        if nw > w:
            col = min(col, MAX_W + 1 - nw)
            rom[off + 2:off + 6] = struct.pack("<HH", col << 8 | row, nw << 8 | h)
            changed += 1
    lo, hi = SONG_COLS  # song boxes: geometry words at +8/+10 of the op-6 record; 8 px mode wraps at W*8 - 8
    song = song_boxes(rom)
    for e in entries:
        for mid in e["ids"] if e.get(lang) else ():
            nw = min(math.ceil((need_px(pages(e[lang], lang, units, widths, 8)) + 8) / 8), hi - lo)
            for off, col, row, w, h in song.get(mid, ()):
                if nw > w:
                    col = max(lo, min(col, hi - nw))
                    rom[off + 8:off + 12] = struct.pack("<HH", col << 8 | row, nw << 8 | h)
                    changed += 1
    return changed


def main():
    import argparse
    import msgcodec
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en")
    ap.add_argument("--warn", action="store_true", help="also print warnings")
    a = ap.parse_args()
    rom = next((Path(__file__).resolve().parents[1] / "rom").glob("*.gba")).read_bytes()
    res = lint(msgcodec.load_script(), a.lang, bubbles(rom), song_boxes(rom))
    for level, uid, msg in res:
        if a.warn or level == "error":
            print(f"{level} {uid} {msg}")
    errors = sum(r[0] == "error" for r in res)
    print(f"{errors} errors, {len(res) - errors} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
