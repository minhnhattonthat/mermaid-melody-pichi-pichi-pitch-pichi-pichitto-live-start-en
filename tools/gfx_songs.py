"""gfx_songs.py: song titles (song list scene 32, song select) -> romaji (credits spelling) / English.

The 19 titles (7 English already) are one chain 17403F7 800x19: the song list decodes it whole, so a shorter title
stream written in place garbles every title after it; one row takes the chain (each chunk keeps its own pointer,
moved by gfx.plan). Each title is one 0x800 stream (128x32 = 64 tiles, `tiles16`: OBJ VRAM 16 tiles to a 32-tile row) drawn by a sprite
list in sprite bank 0x1EFA714 (bank table 0x1D36F90 entry 0; frame entries u8 + u16 bank offset at 0x1EFEF2E..):
    u8 count, u8 flag, count x (u16 y<<6 | shape<<2, u16 x<<6 | size, u16 tile)   (reader 0x08008A74)
Every title has two lists (flag 0 and flag 1). The English is one 16 px line cut into 32x16 pieces: piece k = strip
x 32k.. -> block region (k%4*32, k//4*16), tile k//4*64 + k%4*4. Lists are rewritten in place (count may only
shrink; the tail is never read) via gfx/songs.objs (build stage `objs`).
Hippo songs (17434B2..1743F0B, no warp shows them yet): their lists are not identified (3760/3788/37A8/37C2/37D6
are the candidates; every candidate shows block x 0-95 of rows 0-15), so those stay and the English is drawn there.
    python -X utf8 tools/gfx_songs.py
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

BANK = 0x1EFA714
OBJS = gfx.GFX / "songs.objs"
TITLES = {  # block -> (list offsets in the bank, flag 0 and 1; English)
    0x17403F7: ((0x3350, 0x3558), "Taiyou no Rakuen ~Promised Land~"),
    0x1741079: ((0x33C8, 0x35D0), "Daiji na Takarabako"),
    0x1741389: ((0x33E8, 0x35F0), "Koi wa Nan Darou"),
    0x17420A3: ((0x3464, 0x366C), "Sekai de Ichiban Hayaku Asa ga Kuru Basho"),
    0x17426D4: ((0x34BA, 0x36C2), "Yume no Sono Saki e"),
    0x1742B72: ((0x34F4, 0x36FC), "Kuro no Kyousoukyoku ~concerto~"),
    0x17430DC: ((0x352C, 0x3734), "Aurora no Kaze ni Notte"),
    0x17434B2: ((), "Hippo & the Alps"),        # ヒッポとアルプス
    0x1743766: ((), "Hippo & the Watermelon"),  # ヒッポとすいか
    0x17439CC: ((), "Hippo & the Musician"),    # ヒッポとおんがくか
    0x1743CBB: ((), "Hippo & the Frog"),        # ヒッポとカエル
    0x1743F0B: ((), "Nothing here!"),           # なにもないヨ!
}
Y = -7  # line top relative to the object, as the English titles' lists (Legend of Mermaid..)
NUDGE = {"Nothing here!": -7}  # px left inside the 96 px strip: centred on screen (live_list, tour3 margins 68/54)


def strip(text, width):
    """English on a width x 16 strip (pink fill 11, white ring 15, green shadow 8), the first (bold, gap) that fits."""
    for bold, gap in ((True, 1), (True, 0), (False, 0)):
        img = [[0] * width for _ in range(16)]
        try:
            # box leaves x 0 for the left ring and the last column for the right ring's shadow
            return gfx.typeset(img, [text], (1, 0, width - 2, 16), fill=11, outline=15, bold=bold, gap=gap,
                               shadow=(8, 1, 1))
        except ValueError:
            continue
    raise SystemExit(f"{text!r} does not fit {width} px")


def ink_width(img):
    xs = [x for row in img for x, v in enumerate(row) if v]
    return max(xs) - min(xs) + 1


def pieces(n):
    """n 32x16 pieces centred on the object -> list body (shape 1 size 2 = 32x16)."""
    out = b""
    for k in range(n):
        x = -16 * n + 32 * k
        out += struct.pack("<HHH", (Y & 0x3FF) << 6 | 1 << 2, (x & 0x3FF) << 6 | 2, k // 4 * 64 + k % 4 * 4)
    return out


def draw(text, lists):
    """-> (128x32 block image, piece count or None for the hippo blocks)."""
    block = [[0] * 128 for _ in range(32)]
    if not lists:
        s = strip(text, 96)
        dx = NUDGE.get(text, 0)
        for y in range(16):
            block[y][:96] = (s[y][-dx:] + [0] * -dx) if dx < 0 else s[y]
        return block, None
    wide = strip(text, 256)
    xs = [x for row in wide for x, v in enumerate(row) if v]
    n = -(-(max(xs) - min(xs) + 1) // 32)
    s = strip(text, 32 * n)
    for k in range(n):
        for y in range(16):
            block[k // 4 * 16 + y][k % 4 * 32:k % 4 * 32 + 32] = s[y][32 * k:32 * k + 32]
    return block, n


def main():
    rom = next((gfx.ROOT / "rom").glob("*.gba")).read_bytes()
    pal = gfx.load_pal("songs")
    objs = ["# sprite list (file offset)\tnew bytes (count, flag, pieces): written in place by gfx_songs.apply (stage objs)"]
    (_, off, size, layout, png), = gfx.rows("songs")
    img = gfx.to_image(gfx.decode(rom, off, size)[0], layout)
    for k, start in enumerate(gfx.chunk_starts(rom, off, size)):
        if start not in TITLES:
            continue  # English already (Legend of Mermaid, Super Love Songs!, ..)
        lists, text = TITLES[start]
        block, n = draw(text, lists)
        img[32 * k:32 * k + 32] = block
        print(f"{start:X} {text!r}: {n} pieces")
        for lo in lists:
            p = BANK + lo
            if n > rom[p]:
                raise SystemExit(f"{text!r}: {n} pieces > list {p:X} count {rom[p]}")
            objs.append(f"{p:X}\t{bytes([n, rom[p + 1]]).hex()}{pieces(n).hex()}")
    gfx.save_png(img, pal, gfx.ROOT / png)
    OBJS.write_text("\n".join(objs) + "\n", encoding="utf-8")


def rows():
    lines = OBJS.read_text(encoding="utf-8").splitlines() if OBJS.exists() else []
    return [(int(a, 16), bytes.fromhex(b)) for a, b in (ln.split("\t") for ln in lines if ln and ln[0] != "#")]


def apply(rom):
    """Build stage objs: each list in place, never longer than the original."""
    for p, new in rows():
        if len(new) > 2 + 6 * rom[p] or new[1] != rom[p + 1]:
            raise SystemExit(f"sprite list {p:X}: {len(new)} bytes > old {2 + 6 * rom[p]} or flag changed")
        rom[p:p + len(new)] = new


def zones(rom):
    return [(p, p + len(new)) for p, new in rows()]


if __name__ == "__main__":
    main()
