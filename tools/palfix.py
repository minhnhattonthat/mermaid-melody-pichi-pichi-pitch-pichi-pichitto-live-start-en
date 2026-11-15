"""Make a 16-colour GBA palette file distinct by flipping the low bit of repeats (png rendering only)."""
import struct
import sys

f = sys.argv[1]
p = list(struct.unpack("<16H", open(f, "rb").read()))
seen = set()
for i in range(16):
    while p[i] in seen:
        p[i] = (p[i] + 1) & 0x7FFF
    seen.add(p[i])
open(f, "wb").write(struct.pack("<16H", *p))
print([hex(c) for c in p])
