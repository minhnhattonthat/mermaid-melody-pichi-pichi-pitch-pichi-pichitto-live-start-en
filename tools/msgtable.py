"""msgtable.py: message table constants (docs/re/text.md §Script).

Table at TAB: N x 24-bit LE offsets from BASE; strings live in BASE..END. Only two code literals point here
(0x09860CE0 table, 0x098629DE base), so the strings can move freely as long as the table and the text pointers inside
the bytecode follow (tools/msgcodec.py packs them)."""

TAB, BASE, END, N = 0x1860CE0, 0x18629DE, 0x1872DE0, 2474  # END: expansion table at 0x1872DE0 follows the zero pad


def offsets(rom):
    return [int.from_bytes(rom[TAB + 3 * i:TAB + 3 * i + 3], "little") for i in range(N)]
