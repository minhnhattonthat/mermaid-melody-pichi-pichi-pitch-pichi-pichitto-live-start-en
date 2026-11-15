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


def selftest():
    # literal run, long back-ref, short copies
    rom = bytes([0x00, 0x03, 1, 2, 3, 4, 0x41, 3, 0x80, 0xC0]) + bytes(200)
    data, end = decompress(rom, 0, 10, table=bytes(127))
    assert data == bytes([1, 2, 3, 4, 1, 2, 3, 3, 3, 3]), data
    assert end == 10, end
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        rom = open(sys.argv[1], "rb").read()
        data, end = decompress(rom, int(sys.argv[2], 16), int(sys.argv[3], 16))
        open(sys.argv[4], "wb").write(data)
        print(f"{len(data):X} bytes, stream ends at {end:X}")
