"""msgcodec.py: message text <-> bytes, and the script dump (docs/re/text.md §Script, §Control codes).

    python -X utf8 tools/msgcodec.py dump [--force]     # script/msg_NN.json from the pinned dump (never clobbers en)

A unit is the bytes from one entry point to the next: entry points are the message-table offsets, every 24-bit text
pointer inside the bytecode (F8 call, F9 goto, FA jump tables) and, for bytes nothing reaches, the first such byte
(`used: false`). Units are stored and repacked in address order, so a unit with no terminator still falls through to
the next one as in the original. Unit id = 4-hex offset from BASE in the original ROM.

Text form: glyphs through the table, FE = newline, F7 = {wait}, FF = {end}, F8 = {call:@id}, F9 = {goto:@id};
other controls as {OP:hexargs} with any text pointer written as @id inside the hex (e.g. {FA:08@1A2B@1A40}).
Unmapped bytes are [XX]."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from msgparse import ParseError, parse, token, u24  # noqa: E402
from msgtable import BASE, END, N, TAB, offsets  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "script"
PER_FILE = 100
NAMED = {0xF7: "wait", 0xFF: "end"}
PTR_NAMED = {0xF8: "call", 0xF9: "goto"}
TOKEN = re.compile(r"\{(\w+)(?::([0-9A-Fa-f@]*))?\}|\[([0-9A-Fa-f]{2})\]|\n|.", re.S)


def text_data(rom):
    return bytes(rom[BASE:END]).rstrip(b"\0")


def scan(d, table_offs):
    """-> (sorted entry points, set of entry points reachable from the table)."""
    role, seen, used = {}, set(), set()

    def walk(todo, mark):
        while todo:
            s = todo.pop()
            if s in seen:
                continue
            seen.add(s)
            if mark:
                used.add(s)
            for kind, a, b, ptrs in parse(d, s):
                for i in range(a, b):
                    r = "op" if i == a else "arg"
                    if role.setdefault(i, r) != r:
                        raise ParseError(f"byte {i:#x} is both an opcode and an argument")
                todo += [u24(d, q) for q in ptrs]

    walk(sorted(set(table_offs)), True)
    while len(role) < len(d):  # bytes nothing reaches: dump them as unused units so they roundtrip
        walk([next(i for i in range(len(d)) if i not in role)], False)
    return sorted(seen), used


def units(rom):
    """-> list of dicts {id, ids, used, bytes, tokens} in address order, covering the text data exactly."""
    d = text_data(rom)
    offs = offsets(rom)
    starts, used = scan(d, offs)
    ids = {}
    for i, o in enumerate(offs):
        ids.setdefault(o, []).append(i)
    out = []
    for a, b in zip(starts, starts[1:] + [len(d)]):
        toks, p = [], a
        while p < b:
            kind, e, ptrs, _ = token(d, p)
            assert e <= b, f"token at {p:#x} crosses the unit boundary {b:#x}"
            toks.append((p, e, ptrs))
            p = e
        out.append({"id": f"{a:04X}", "ids": ids.get(a, []), "used": a in used, "bytes": d[a:b],
                    "tokens": [(d[s:e], [q - s for q in ptrs]) for s, e, ptrs in toks],
                    "targets": [[f"{u24(d, q):04X}" for q in ptrs] for s, e, ptrs in toks]})
    return out


def decode_unit(u, table):
    out = []
    for (raw, ptrs), tgts in zip(u["tokens"], u["targets"]):
        c = raw[0]
        if c < 0xF6 and raw in table.dec:
            out.append(table.dec[raw])
        elif c < 0xF6:
            out.append("".join(f"[{x:02X}]" for x in raw))
        elif c == 0xFE:
            out.append("\n")
        elif c in NAMED:
            out.append("{%s}" % NAMED[c])
        elif c in PTR_NAMED:
            out.append("{%s:@%s}" % (PTR_NAMED[c], tgts[0]))
        else:
            h, k = [], 1
            for q, t in sorted(zip(ptrs, tgts)):
                h.append(raw[k:q].hex().upper() + "@" + t)
                k = q + 3
            h.append(raw[k:].hex().upper())
            out.append("{%02X:%s}" % (c, "".join(h)))
    return "".join(out)


def encode(text, table):
    """-> (bytes, [(byte position, target id)]). Raises ValueError on a character the table lacks."""
    out, fix = bytearray(), []
    rev = {v: k for k, v in NAMED.items()} | {v: k for k, v in PTR_NAMED.items()}
    for m in TOKEN.finditer(text):
        name, args, raw = m[1], m[2], m[3]
        if raw:
            out.append(int(raw, 16))
        elif m[0] == "\n":
            out.append(0xFE)
        elif name:
            if name in rev:
                out.append(rev[name])
            elif re.fullmatch(r"F[6ABCD]", name):
                out.append(int(name, 16))
            else:
                raise ValueError(f"unknown control {m[0]!r}")
            for part in re.split(r"(@[0-9A-F]{4})", args or ""):
                if part.startswith("@"):
                    fix.append((len(out), part[1:]))
                    out += b"\0\0\0"
                elif part:
                    out += bytes.fromhex(part)
        else:
            code = table.enc.get(m[0])
            if code is None:
                raise ValueError(f"no glyph for {m[0]!r} in {text[:40]!r}")
            out += code
    return bytes(out), fix


TERMINATED = re.compile(r"(\{end\}|\{goto:@\w+\})$")


def pack(rom, entries, table, lang="jp", regions=((BASE, END),), fallback=None):
    """Write entries (address order: id, ids, text in `lang` encoded with `table`, else jp with `fallback`) into
    `regions` (file offsets >= BASE, filled in order) and rebuild the message table and every text pointer inside
    the bytecode. A unit with no terminator falls through to the next one, so such runs stay in one region.
    The first region is zero-filled after its text (as in the original); later regions keep their other bytes."""
    fallback = fallback or table
    chains, cur = [], []
    for e in entries:
        text = e.get(lang)
        b, fix = encode(text, table) if text else encode(e["jp"], fallback)
        cur.append((e["id"], b, fix))
        if TERMINATED.search(text or e["jp"]):
            chains.append(cur)
            cur = []
    if cur:
        chains.append(cur)
    pos, used, ri = {}, [0] * len(regions), 0
    for ch in chains:
        size = sum(len(b) for _, b, _ in ch)
        while regions[ri][0] + used[ri] + size > regions[ri][1]:
            ri += 1
            if ri == len(regions):
                raise ValueError(f"text overflows its regions ({size} bytes left to place)")
        for uid, b, _ in ch:
            pos[uid] = regions[ri][0] + used[ri] - BASE
            used[ri] += len(b)
    lo, hi = regions[0]
    rom[lo + used[0]:hi] = bytes(hi - lo - used[0])
    for ch in chains:
        for uid, b, fix in ch:
            b = bytearray(b)
            for q, t in fix:
                b[q:q + 3] = pos[t].to_bytes(3, "little")
            rom[BASE + pos[uid]:BASE + pos[uid] + len(b)] = b
    offs = [None] * N
    for e in entries:
        for i in e["ids"]:
            offs[i] = pos[e["id"]]
    missing = [i for i, o in enumerate(offs) if o is None]
    if missing:
        raise ValueError(f"message ids with no unit: {missing[:10]}")
    rom[TAB:TAB + 3 * N] = b"".join(o.to_bytes(3, "little") for o in offs)


def load_script():
    entries = []
    for f in sorted(SCRIPT.glob("msg_*.json")):
        entries += json.loads(f.read_text(encoding="utf-8"))
    return entries


def dump(rom, table, force=False):
    us = units(rom)
    SCRIPT.mkdir(exist_ok=True)
    old = {e["id"]: e for e in load_script()}
    if old and not force:
        sys.exit("script/ already has files: refusing to overwrite (use --force, which keeps every en/status/notes)")
    for k in range(0, len(us), PER_FILE):
        rows = []
        for u in us[k:k + PER_FILE]:
            o = old.get(u["id"], {})
            rows.append({"id": u["id"], "ids": u["ids"], "used": u["used"], "jp": decode_unit(u, table),
                         "en": o.get("en", ""), "status": o.get("status", ""), "notes": o.get("notes", "")})
        path = SCRIPT / f"msg_{k // PER_FILE:02d}.json"
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(us)} units in {(len(us) + PER_FILE - 1) // PER_FILE} files under script/")


def main():
    import argparse
    import check_rom
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["dump"])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    check_rom.check()
    rom = (ROOT / "rom").glob("*.gba").__next__().read_bytes()
    dump(rom, Table.load(ROOT / "tbl" / "jp.tbl"), a.force)


if __name__ == "__main__":
    main()
