"""msgparse.py: tokenise message bytecode (grammar in docs/re/text.md §Control codes).

A token is (kind, start, end, ptrs): kind 'g' glyph (00-EF, or F0-F5 + byte), 'c' control, 'end' (FF).
ptrs = positions (relative to BASE) of 24-bit text offsets inside the token, which a repack must relocate.
Parsing one string stops at FF or at an unconditional jump (F9, FA 05 FE, FA 08, FA 0D, FA 16)."""

# FA subcommand -> fixed argument bytes after the sub byte (None: special-cased below)
FA_ARGS = {0: 0, 1: 1, 2: 4, 3: 0, 4: 0, 5: None, 6: 0, 7: 1, 8: None, 9: 0, 10: 0, 11: 1, 12: 2, 13: None,
           14: 3, 15: 1, 16: 1, 17: 1, 18: 0, 19: 0, 20: 0, 21: 6, 22: None, 23: 0, 24: 0, 25: 5, 26: 0, 27: 0}
# F6 subcommand (b & 0x1f) -> extra bytes, as a function of b
F6_ARGS = {2: lambda b: 1 if b & 0x80 else 0,
           4: lambda b: 2 + (1 if b & 0x80 else 0) + (1 if (b & 0xC0) == 0xC0 else 0),
           5: lambda b: 2, 7: lambda b: 1, 12: lambda b: 3}


class ParseError(Exception):
    pass


def u24(d, p):
    return d[p] | d[p + 1] << 8 | d[p + 2] << 16


def _table(d, p, n=None):
    """24-bit jump table at p: n entries, or (n None) entries until p reaches the lowest target seen."""
    ptrs, lo = [], None
    while (len(ptrs) < n) if n is not None else (lo is None or p < lo):
        t = u24(d, p)
        if p + 3 > len(d) or t >= len(d):
            raise ParseError(f"jump table entry {t:#x} at {p:#x} outside the text")
        ptrs.append(p)
        lo = t if lo is None else min(lo, t)
        p += 3
        if n is None and len(ptrs) > 64:
            raise ParseError(f"jump table at {p:#x} never reaches its targets")
    return p, ptrs


def token(d, p):
    """-> (kind, end, ptrs, stop) for the token at p of text data d (bytes from BASE)."""
    c = d[p]
    if c < 0xF0:
        return "g", p + 1, [], False
    if c <= 0xF5:
        return "g", p + 2, [], False
    if c == 0xFF:
        return "end", p + 1, [], True
    if c == 0xFE or c == 0xF7:  # FE newline, F7 wait for a button
        return "c", p + 1, [], False
    if c == 0xFD:
        return "c", p + 2, [], False
    if c == 0xFC:  # position: one byte if either top bit is set, else two
        return "c", p + (2 if d[p + 1] & 0xC0 else 3), [], False
    if c == 0xFB:  # print number: 32-bit RAM address + format
        return "c", p + 6, [], False
    if c in (0xF8, 0xF9):  # F8 call substring, F9 goto
        return "c", p + 4, [p + 1], c == 0xF9
    if c == 0xF6:
        b = d[p + 1]
        return "c", p + 2 + F6_ARGS.get(b & 0x1F, lambda b: 0)(b), [], False
    # FA
    s = d[p + 1]
    if s == 0xFF:  # scene callback n (table set in RAM at 0x030063EC) + one byte
        # callback 4 reads 9 more bytes (EP 28 unit 5053: English text there drew streaks)
        return "c", p + (13 if d[p + 2] == 4 else 4), [], False
    if s >= 0x80:  # colour
        return "c", p + 2, [], False
    if s == 0x7F or s >= len(FA_ARGS):
        raise ParseError(f"FA {s:02X} at {p:#x}: no handler")
    n = FA_ARGS[s]
    if n is not None:
        ptrs = {14: [p + 2], 21: [p + 2, p + 5], 25: [p + 4]}.get(s, [])
        return "c", p + 2 + n, ptrs, False
    if s == 5:  # choice: FE + one jump per option, else a flags byte (+1 if bit 7)
        b = d[p + 2]
        if b == 0xFE:
            e, ptrs = _table(d, p + 3)
            return "c", e, ptrs, True
        if b == 0xFF:
            return "c", p + 3, [], False
        return "c", p + 3 + (1 if b & 0x80 else 0), [], False
    if s == 13:  # random jump: count byte + table
        e, ptrs = _table(d, p + 3, d[p + 2])
        return "c", e, ptrs, True
    e, ptrs = _table(d, p + 2)  # 8, 22: jump on a RAM index
    return "c", e, ptrs, True


def parse(d, p):
    """Tokens of the string at p, up to and including its terminator."""
    out = []
    while True:
        if p >= len(d):
            raise ParseError(f"ran off the text data at {p:#x}")
        kind, e, ptrs, stop = token(d, p)
        out.append((kind, p, e, ptrs))
        p = e
        if stop:
            return out
