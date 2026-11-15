"""gfx_obj.py: edit text drawn by OAM sprites, from a scene's PPU dump (the OBJ twin of gfx_bg.Layer).

In a generator:  s = Sprites(SCENE, [oam indices]); img = s.compose(); ...edit indices (screen space, origin at
the sprites' top-left)...; s.write(block_img, data, img, layout)
2D OBJ mapping (32 tiles a VRAM row), non-affine sprites, flips undone. VRAM tiles map to block tiles by unique
byte match, so the block may be loaded at any tile number; a tile used twice with different pixels raises.
"""
import struct
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402
from gfx_bg import tile_px  # noqa: E402
from gfx_where import SHAPES  # noqa: E402


class Sprites:
    def __init__(self, scene, ids):
        d = sorted((gfx.ROOT / "work/qa/ppu" / scene).glob("ppu_*.vram.bin"))[-1]
        self.vram = d.read_bytes()
        oam = d.with_name(d.name.replace("vram", "oam")).read_bytes()
        self.cells = []  # (screen x, screen y, vram tile, hflip, vflip)
        for i in ids:
            a0, a1, a2, _ = struct.unpack_from("<4H", oam, i * 8)
            assert not a0 & 0x100, f"OBJ {i} is affine"
            w, h = SHAPES[(a0 >> 14, a1 >> 14)]
            hf, vf = a1 >> 12 & 1, a1 >> 13 & 1
            for r in range(h // 8):
                for c in range(w // 8):
                    sc, sr = (w // 8 - 1 - c if hf else c), (h // 8 - 1 - r if vf else r)
                    self.cells.append(((a1 & 511) + 8 * sc, (a0 & 255) + 8 * sr, (a2 & 1023) + r * 32 + c, hf, vf))
        self.x0 = min(c[0] for c in self.cells)
        self.y0 = min(c[1] for c in self.cells)
        self.w = max(c[0] for c in self.cells) + 8 - self.x0
        self.h = max(c[1] for c in self.cells) + 8 - self.y0

    def _px(self, t, hf, vf):
        px = tile_px(self.vram, 0x10000 + 32 * t)
        if hf:
            px = [r[::-1] for r in px]
        return px[::-1] if vf else px

    def compose(self):
        img = [[0] * self.w for _ in range(self.h)]
        for x, y, t, hf, vf in self.cells:
            for j, row in enumerate(self._px(t, hf, vf)):
                img[y - self.y0 + j][x - self.x0:x - self.x0 + 8] = row
        return img

    def write(self, block_img, data, img, layout="tiles16"):
        tw = gfx.parse_layout(layout)[0]
        where = {}
        for k in range(len(data) // 32):
            where.setdefault(bytes(data[32 * k:32 * k + 32]), []).append(k)
        def matches(t):
            return where.get(bytes(self.vram[0x10000 + 32 * t:0x10000 + 32 * t + 32]), [])
        # each stream of the block sits at one VRAM base: a tile with byte twins (e.g. the same kana twice) takes the
        # twin whose VRAM - block delta the unique matches use most
        deltas = Counter(t - ks[0] for t in {c[2] for c in self.cells} for ks in [matches(t)] if len(ks) == 1)
        done = {}
        for x, y, t, hf, vf in self.cells:
            px = [row[x - self.x0:x - self.x0 + 8] for row in img[y - self.y0:y - self.y0 + 8]]
            if vf:
                px = px[::-1]
            if hf:
                px = [r[::-1] for r in px]
            if px == tile_px(self.vram, 0x10000 + 32 * t):
                continue
            ks = matches(t)
            if len(ks) > 1 and deltas:
                best = max(ks, key=lambda k: deltas[t - k])
                if deltas[t - best]:
                    ks = [best]
            if len(ks) != 1:
                raise SystemExit(f"OBJ tile {t} at {x},{y}: {len(ks)} matches in the block")
            if done.setdefault(ks[0], px) != px:
                raise SystemExit(f"OBJ tile {t} at {x},{y}: shared with other pixels")
            bx, by = ks[0] % tw * 8, ks[0] // tw * 8
            for j in range(8):
                block_img[by + j][bx:bx + 8] = px[j]
        return len(done)
