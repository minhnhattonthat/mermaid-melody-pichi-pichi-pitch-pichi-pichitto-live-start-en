"""msgtable.py: unpack and repack the message table (docs/re/text.md).

Table at TAB: N x 24-bit LE offsets from BASE; strings live in BASE..END. Only two code literals point here
(0x09860CE0 table, 0x098629DE base), so the strings can move freely as long as the table follows.

A segment is the bytes from one distinct table offset to the next (or to the end of the data), with the ids that
point at it. Segment boundaries come from the table, not from FF: FF also occurs as a control-code argument, and
some bytes are reached by no id (kept in the segment before them). Phase 4 replaces this with real string bounds."""

TAB, BASE, END, N = 0x1860CE0, 0x18629DE, 0x1872DE0, 2474  # END: expansion table at 0x1872DE0 follows the zero pad


def offsets(rom):
    return [int.from_bytes(rom[TAB + 3 * i:TAB + 3 * i + 3], "little") for i in range(N)]


def unpack(rom):
    """-> list of (ids, bytes) in address order; covers BASE..last nonzero byte exactly."""
    offs = offsets(rom)
    data_end = len(rom[BASE:END].rstrip(b"\0"))
    starts = sorted(set(offs) | {0})
    assert starts[-1] < data_end, "table points past the string data"
    ids = {}
    for i, o in enumerate(offs):
        ids.setdefault(o, []).append(i)
    bounds = starts + [data_end]
    return [(ids.get(a, []), rom[BASE + a:BASE + b]) for a, b in zip(bounds, bounds[1:])]


def pack(rom, segments):
    """Write segments back to back from BASE and the table to match; zero-fill the rest of the region."""
    data = b"".join(seg for _, seg in segments)
    if BASE + len(data) > END:
        raise ValueError(f"strings overflow the text region by {BASE + len(data) - END} bytes")
    offs = [None] * N
    pos = 0
    for ids, seg in segments:
        for i in ids:
            offs[i] = pos
        pos += len(seg)
    missing = [i for i, o in enumerate(offs) if o is None]
    if missing:
        raise ValueError(f"ids with no segment: {missing[:10]}")
    rom[TAB:TAB + 3 * N] = b"".join(o.to_bytes(3, "little") for o in offs)
    rom[BASE:END] = data + bytes(END - BASE - len(data))
