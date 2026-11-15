"""gbaio.py: print the GBA display setup from an emu.py ppu dump (.io.bin) and the tile under a screen point per BG.

    python -X utf8 tools/gbaio.py work/qa/x/ppu_001290 [--at X,Y]

Reads PREFIX.io.bin (IO regs from 0x04000000) and PREFIX.vram.bin. Text BGs only (modes 0/1).
"""
import argparse
import struct


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prefix")
    ap.add_argument("--at", help="screen x,y: print each BG's map entry there")
    a = ap.parse_args()
    io = open(a.prefix + ".io.bin", "rb").read()
    vram = open(a.prefix + ".vram.bin", "rb").read()
    disp = struct.unpack_from("<H", io, 0)[0]
    print(f"DISPCNT {disp:04X} mode {disp & 7} obj1d {bool(disp & 0x40)} bg-on {[(disp >> (8 + i)) & 1 for i in range(4)]} obj-on {(disp >> 12) & 1}")
    for i in range(4):
        cnt = struct.unpack_from("<H", io, 8 + 2 * i)[0]
        hofs, vofs = struct.unpack_from("<HH", io, 0x10 + 4 * i)
        cbb, sbb, bpp8, size = (cnt >> 2) & 3, (cnt >> 8) & 31, (cnt >> 7) & 1, cnt >> 14
        print(f"BG{i} cnt {cnt:04X} prio {cnt & 3} tiles@{cbb * 0x4000:05X} map@{sbb * 0x800:05X} {'8bpp' if bpp8 else '4bpp'} size {size} scroll {hofs & 511},{vofs & 511}")
        if a.at and (disp >> (8 + i)) & 1:
            x, y = map(int, a.at.split(","))
            tx, ty = ((x + hofs) & 511) // 8, ((y + vofs) & 511) // 8
            w = 64 if size in (1, 3) else 32
            blk = (tx // 32) + (ty // 32) * (w // 32)
            e = struct.unpack_from("<H", vram, sbb * 0x800 + blk * 0x800 + ((ty % 32) * 32 + tx % 32) * 2)[0]
            t = e & 0x3FF
            print(f"   at {x},{y}: entry {e:04X} tile {t} (vram {cbb * 0x4000 + t * (64 if bpp8 else 32):05X}) pal {e >> 12} hflip {(e >> 10) & 1} vflip {(e >> 11) & 1}")


if __name__ == "__main__":
    main()
