"""restables.py: find the game's 5-byte resource tables (u32 pointer + u8 attribute) and list every block they point at.

    python -X utf8 tools/restables.py ROM [--min 6] [--out work/restables.tsv]

A table is a run of >= --min records whose pointers land in ROM data (0x08000000-0x09FFFFFF, below the data end).
Writes one line per table (offset, records, code refs to it) and, to --out, one line per distinct pointer:
offset, attribute bytes seen, the tables that use it.
"""
import argparse
import struct
from collections import defaultdict

DATA_END = 0x1FDF760


def valid(rom, i):
    if i + 5 > len(rom):
        return False
    v = struct.unpack_from("<I", rom, i)[0]
    return 0x08000000 <= v < 0x08000000 + DATA_END and (v & 0x1FFFFFF) >= 0x10000


def find_tables(rom, minrec):
    tables, i, n = [], 0x10000, len(rom) - 5
    covered = bytearray(len(rom))
    while i < n:
        if not covered[i] and valid(rom, i):
            j = i
            while valid(rom, j + 5):
                j += 5
            count = (j - i) // 5 + 1
            if count >= minrec:
                tables.append((i, count))
                for k in range(i, j + 5):
                    covered[k] = 1
                i = j + 5
                continue
        i += 1
    return tables


def code_refs(rom, off):
    out = []
    for base in (0x08000000,):
        lit = struct.pack("<I", base + off)
        k = rom.find(lit, 0, 0x200000)
        while k >= 0:
            out.append(k)
            k = rom.find(lit, k + 1, 0x200000)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("--min", type=int, default=6)
    ap.add_argument("--out", default="work/restables.tsv")
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    tables = find_tables(rom, a.min)
    ptrs = defaultdict(lambda: [set(), set()])
    reffed = 0
    for off, count in tables:
        refs = code_refs(rom, off)
        reffed += bool(refs)
        for r in range(count):
            v = struct.unpack_from("<I", rom, off + 5 * r)[0] & 0x1FFFFFF
            ptrs[v][0].add(rom[off + 5 * r + 4])
            ptrs[v][1].add(off)
        print(f"{off:07X}\t{count}\t{','.join(f'{x:X}' for x in refs)}")
    with open(a.out, "w", encoding="utf-8") as f:
        for v in sorted(ptrs):
            f.write(f"{v:07X}\t{','.join(map(str, sorted(ptrs[v][0])))}\t{','.join(f'{t:X}' for t in sorted(ptrs[v][1]))}\n")
    print(f"# {len(tables)} tables ({reffed} with a code literal), {len(ptrs)} distinct pointers -> {a.out}")


if __name__ == "__main__":
    main()
