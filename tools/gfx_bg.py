"""gfx_bg.py: edit text drawn on a tiled BG layer (map + 4bpp tiles from one block), from a scene's PPU dump.

    python -X utf8 tools/gfx_bg.py show SCENE BG [OUT.png]       the layer's whole map in real colours, 8 px grid
                                                                  every 4 cells labelled (cell x, y)
In a generator:  bg = Layer(SCENE, BG); img = bg.compose(rect); ...edit indices...; bg.write(block_img, data, rect, img)
rect = (cell x, cell y, cells w, cells h) in map space. The block's tiles are found by matching the VRAM tile bytes
in the decoded block (most common VRAM-tile minus block-tile delta), so flips and shared tiles are handled: a tile
written twice with different pixels, or also used by a map cell outside the rect, raises.
"""
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

DIMS = {0: (32, 32), 1: (64, 32), 2: (32, 64), 3: (64, 64)}


def tile_px(data, at):
    """32 bytes of 4bpp at `at` -> 8 rows of 8 indices."""
    return [[data[at + y * 4 + x // 2] >> (4 * (x & 1)) & 15 for x in range(8)] for y in range(8)]


class Layer:
    def __init__(self, scene, bg):
        d = sorted((gfx.ROOT / "work/qa/ppu" / scene).glob("ppu_*.vram.bin"))[-1]
        self.vram = d.read_bytes()
        self.pal = d.with_name(d.name.replace("vram", "pal")).read_bytes()
        io = d.with_name(d.name.replace("vram", "io")).read_bytes()
        cnt = struct.unpack_from("<H", io, 8 + 2 * bg)[0]
        self.cb, self.sb = (cnt >> 2 & 3) * 0x4000, (cnt >> 8 & 31) * 0x800
        self.w, self.h = DIMS[cnt >> 14]

    def entry(self, cx, cy):
        """map entry of cell (cx, cy): (tile, hflip, vflip, pal)."""
        blk = (cx // 32) + (cy // 32) * (self.w // 32)
        e = struct.unpack_from("<H", self.vram, self.sb + blk * 0x800 + 2 * (cy % 32 * 32 + cx % 32))[0]
        return e & 1023, e >> 10 & 1, e >> 11 & 1, e >> 12

    def cell_px(self, cx, cy):
        t, hf, vf, _ = self.entry(cx, cy)
        px = tile_px(self.vram, self.cb + t * 32)
        if hf:
            px = [r[::-1] for r in px]
        if vf:
            px = px[::-1]
        return px

    def compose(self, rect):
        """indices of the rect's cells -> rows (8 * w x 8 * h)."""
        x0, y0, w, h = rect
        img = [[0] * (8 * w) for _ in range(8 * h)]
        for j in range(h):
            for i in range(w):
                for y, row in enumerate(self.cell_px(x0 + i, y0 + j)):
                    img[8 * j + y][8 * i:8 * i + 8] = row
        return img

    def colours(self, p):
        return [gfx.rgb(c) for c in struct.unpack_from("<16H", self.pal, p * 32)]

    def block_tiles(self, data):
        """VRAM tile number -> block tile index, by the most common delta among unique byte matches."""
        where = {}
        for k in range(len(data) // 32):
            where.setdefault(bytes(data[32 * k:32 * k + 32]), []).append(k)
        deltas = Counter()
        for t in range(1024):
            ks = where.get(self.vram[self.cb + 32 * t:self.cb + 32 * t + 32], [])
            if len(ks) == 1:
                deltas[t - ks[0]] += 1
        delta = deltas.most_common(1)[0][0]
        return lambda t: t - delta if 0 <= t - delta < len(data) // 32 else None

    def write(self, block_img, data, rect, img, layout="tiles16"):
        """Put the rect's edited indices back into the block image's tiles (flips undone); check for conflicts."""
        tw = gfx.parse_layout(layout)[0]
        src = self.block_tiles(data)
        x0, y0, w, h = rect
        inside = {(x0 + i, y0 + j) for i in range(w) for j in range(h)}
        done = {}
        for cx, cy in sorted(inside):
            t, hf, vf, _ = self.entry(cx, cy)
            px = [row[8 * (cx - x0):8 * (cx - x0) + 8] for row in img[8 * (cy - y0):8 * (cy - y0) + 8]]
            if vf:
                px = px[::-1]
            if hf:
                px = [r[::-1] for r in px]
            if px == tile_px(self.vram, self.cb + t * 32):
                continue
            k = src(t)
            if k is None:
                raise SystemExit(f"cell {cx},{cy}: tile {t} is not from this block")
            if done.setdefault(k, px) != px:
                raise SystemExit(f"cell {cx},{cy}: tile {t} is shared inside the rect with other pixels")
            for ox in range(self.w):
                for oy in range(self.h):
                    if (ox, oy) not in inside and self.entry(ox, oy)[0] == t:
                        raise SystemExit(f"cell {cx},{cy}: tile {t} is also used at {ox},{oy}")
            bx, by = k % tw * 8, k // tw * 8
            for y in range(8):
                block_img[by + y][bx:bx + 8] = px[y]
        return len(done)


def show(scene, bg, out=None):
    from PIL import Image, ImageDraw
    L = Layer(scene, bg)
    im = Image.new("RGB", (8 * L.w * 2, 8 * L.h * 2))
    for cy in range(L.h):
        for cx in range(L.w):
            cols = L.colours(L.entry(cx, cy)[3])
            for y, row in enumerate(L.cell_px(cx, cy)):
                for x, v in enumerate(row):
                    im.putpixel((2 * (8 * cx + x), 2 * (8 * cy + y)), cols[v])
    px = im.load()
    for y in range(0, im.height, 2):
        for x in range(0, im.width, 2):
            c = px[x, y]
            px[x + 1, y] = px[x, y + 1] = px[x + 1, y + 1] = c
    d = ImageDraw.Draw(im)
    for c in range(0, max(L.w, L.h) + 1):
        col = (255, 0, 0) if c % 4 == 0 else (90, 90, 90)
        d.line([(16 * c, 0), (16 * c, im.height)], fill=col)
        d.line([(0, 16 * c), (im.width, 16 * c)], fill=col)
    for cy in range(0, L.h, 4):
        for cx in range(0, L.w, 4):
            d.text((16 * cx + 2, 16 * cy + 1), f"{cx},{cy}", fill=(255, 255, 0))
    out = out or str(gfx.ROOT / f"work/gfx/bg_{scene}_{bg}.png")
    im.save(out)
    print(out, f"map {L.w}x{L.h} cells, char base {L.cb:X}, screen base {L.sb:X}")


if __name__ == "__main__":
    if sys.argv[1] == "show":
        show(sys.argv[2], int(sys.argv[3]), *sys.argv[4:5])
