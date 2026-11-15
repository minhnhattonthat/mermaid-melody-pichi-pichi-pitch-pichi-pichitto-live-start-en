"""kcomp.py: the game's graphics compression (decoder at ROM 0x08009328, ARM, run from IWRAM 0x03000BA4).

Called as decompress(dst, src, size, r3) from Thumb 0x08000D20. Stream (r3 < 0x10000 mode, the only one seen):
  byte 0      flags; bit 0 set = unscramble every 64-byte block afterwards with the 62-byte swap table at
              IWRAM 0x03000B25 + (flags >> 1) (an IWRAM image copied from ROM 0x1D36E21, 127 bytes)
  then ops until `size` bytes are out; op byte c, n = (c & 0x3F) + 1:
    c>>6 == 0  n literal bytes follow
    c>>6 == 1  next byte d: copy n+1 bytes from out[-d-1]
    c>>6 == 2  copy 2 bytes from out[-n]
    c>>6 == 3  copy 1 byte  from out[-n]
The decoder returns the source pointer after the stream; blocks are byte-aligned and often back to back.

    python -X utf8 tools/kcomp.py ROM OFFSET SIZE OUT.bin     # decode one block
    python -X utf8 tools/kcomp.py --selftest
"""
import sys

TABLE_OFF = 0x1D36E21  # ROM copy of the IWRAM swap table (verified equal to IWRAM 0x03000B25..0x03000BA3)


def decompress(rom, off, size, table=None):
    """Return (data, end_offset). Raises ValueError on a stream that reads before the output start."""
    if table is None:
        table = rom[TABLE_OFF:TABLE_OFF + 127]
    flags = rom[off]
    p = off + 1
    out = bytearray()
    while len(out) < size:
        c = rom[p]
        p += 1
        n = (c & 0x3F) + 1
        t = c >> 6
        if t == 0:
            out += rom[p:p + n]
            p += n
        elif t == 1:
            d = rom[p] + 1
            p += 1
            if d > len(out):
                raise ValueError(f"back-reference before start at {p - 2:X}")
            for _ in range(n + 1):
                out.append(out[-d])
        else:
            if n > len(out):
                raise ValueError(f"back-reference before start at {p - 1:X}")
            for _ in range(2 if t == 2 else 1):
                out.append(out[-n])
    # The ARM loop may overrun `size` by a byte or a run; the caller's buffer only uses `size`.
    out = out[:size]
    if flags & 1:
        tab = table[flags >> 1:(flags >> 1) + 62]
        for b in range(0, size - size % 64, 64):
            for k in range(1, 63):
                j = b + tab[k - 1]
                out[b + k], out[j] = out[j], out[b + k]
    return bytes(out), p


def compress(data):
    """Optimal-parse encoder (flags 0, no scramble); decompress(compress(d), 0, len(d)) == d."""
    n = len(data)
    pos = {}  # 2-byte key -> positions, newest last
    best = [(0, 0)] * n  # (longest match length, its distance) at i, window 256
    near1 = [False] * n  # some d <= 64 matches 1 byte
    near2 = [False] * n  # some d <= 64 matches 2 bytes
    for i in range(n):
        lo = max(0, i - 64)
        near1[i] = data.rfind(data[i:i + 1], lo, i) >= 0
        if i + 1 < n:
            key = data[i:i + 2]
            cands = pos.setdefault(key, [])
            while cands and cands[0] < i - 256:
                cands.pop(0)
            bl, bd = 0, 0
            for j in reversed(cands):
                m = 2
                while m < 65 and i + m < n and data[j + m] == data[i + m]:
                    m += 1
                if i - j <= 64:
                    near2[i] = True
                if m > bl:
                    bl, bd = m, i - j
                    if m == 65:
                        break
            best[i] = (bl, bd)
            cands.append(i)
    INF = 1 << 30
    cost = [INF] * (n + 1)
    step = [None] * (n + 1)
    cost[n] = 0
    for i in range(n - 1, -1, -1):
        for k in range(1, min(64, n - i) + 1):
            c = k + 1 + cost[i + k]
            if c < cost[i]:
                cost[i], step[i] = c, ("lit", k, 0)
        if near1[i] and 1 + cost[i + 1] < cost[i]:
            cost[i], step[i] = 1 + cost[i + 1], ("c1", 1, 0)
        if near2[i] and 1 + cost[i + 2] < cost[i]:
            cost[i], step[i] = 1 + cost[i + 2], ("c2", 2, 0)
        bl, bd = best[i]
        for m in range(3, bl + 1):
            if 2 + cost[i + m] < cost[i]:
                cost[i], step[i] = 2 + cost[i + m], ("cl", m, bd)
    out = bytearray([0])
    i = 0
    while i < n:
        kind, m, d = step[i]
        if kind == "lit":
            out.append(m - 1)
            out += data[i:i + m]
        elif kind == "cl":
            out += bytes([0x40 | (m - 2), d - 1])
        else:
            dist = next(dd for dd in range(1, 65) if data[i - dd:i - dd + m] == data[i:i + m] if i - dd >= 0)
            out.append((0x80 if kind == "c2" else 0xC0) | (dist - 1))
        i += m
    return bytes(out)


def selftest():
    # literal run, long back-ref, short copies
    rom = bytes([0x00, 0x03, 1, 2, 3, 4, 0x41, 3, 0x80, 0xC0]) + bytes(200)
    data, end = decompress(rom, 0, 10, table=bytes(127))
    assert data == bytes([1, 2, 3, 4, 1, 2, 3, 3, 3, 3]), data
    assert end == 10, end
    import random
    rnd = random.Random(1)
    for size in (1, 2, 3, 70, 700, 3000):
        d = bytes(rnd.choice(b"\x00\x00\x11\x12\x21\xff") for _ in range(size))
        c = compress(d)
        assert decompress(c, 0, len(d), table=bytes(127)) == (d, len(c)), size
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        rom = open(sys.argv[1], "rb").read()
        data, end = decompress(rom, int(sys.argv[2], 16), int(sys.argv[3], 16))
        open(sys.argv[4], "wb").write(data)
        print(f"{len(data):X} bytes, stream ends at {end:X}")
