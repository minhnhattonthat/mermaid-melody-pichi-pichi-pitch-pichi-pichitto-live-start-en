"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500]   work/tl/bNNN.tsv and build/terms_bNNN.txt for untranslated JP
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English (for check.py)
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/

Copied from the skill's assets/batches.py. Fit the ADAPTER section to this game's text format; the rest is shared.
Batch TSV: id, speaker, form, limit, JP. Output: work/tl/bNNN.out.tsv, id<TAB>English, every id once, same order.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
# Codes as tools/msgcodec.py writes them ({FA:06}, {call:@2A5B}, {end}, [XX]). In a TSV cell a newline is the two
# characters \n. Furigana runs {FD:01}（よみ）{FD:00} are dropped in English (the VWF only draws at spacing 12).
TOKEN = re.compile(r"\{[^}\n]*\}|\[[0-9A-F]{2}\]")
FREE = {"{FA:06}", "{wait}"}  # page breaks: the English may add or drop them to fit the box
FURIGANA = re.compile(r"\{FD:01\}（[^）{}]*）\{FD:00\}")
VARIABLE = r"\{F[6B]:[0-9A-F]*\}"  # a name or number the game draws: "1st" comes out as "1th"
# honorifics kept (D1); checked only after a called name, since さん/ちゃん hide inside kana words. さま is left to the
# reviewer (on a title it becomes "Princess"/"Lady"), as are calls that draw a title, not a name.
HONORIFICS = {"さん": "-san", "ちゃん": "-chan", "くん": "-kun"}
TITLE_CALLS = {"2B27", "2B32"}  # Mermaid Princess, Mermaid


def docs():
    """(path, doc, entries) per script file; entries hold id, jp, en, and optionally speaker, box, max, dup."""
    for path in sorted(SCRIPT.rglob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        yield path, doc, doc["entries"] if isinstance(doc, dict) else doc


def needs_english(entry):
    """Used units with something to draw besides codes, spaces and digits; status keep-jp = drawn by a font the
    English build leaves Japanese (the leftover debug menu), so the jp text is what draws right."""
    return entry.get("used", True) and not entry.get("en") and entry.get("status") != "keep-jp" and bool(
        re.sub(r"[\s　0-9０-９]", "", TOKEN.sub("", entry.get("jp", ""))))


def group_of(entry):
    """Entries with the same value stay in one batch: fragments of one sentence, split around a drawn number."""
    return entry.get("dup") or entry["id"]


_CTX = {}


def _ctx():
    """Font widths, units and box budgets (tools/boxes.py), loaded once."""
    if not _CTX:
        sys.path.insert(0, str(ROOT / "tools"))
        import boxes
        import enfont
        units = index()
        roms = sorted((ROOT / "rom").glob("*.gba"))
        bub = boxes.bubbles(roms[0].read_bytes()) if roms else {}
        _CTX.update(boxes=boxes, units=units, budgets=boxes.unit_budgets(list(units.values()), bub),
                    widths={ch: enfont.width(rows) for ch, rows in enfont.load()})
    return _CTX


def box_limit(entry):
    """-> (kind, px, lines) the English must fit: measured boxes as boxes.py; a guessed box grows to what the JP uses."""
    c = _ctx()
    b = c["budgets"].get(entry["id"])
    if not b or b[1] is None:
        return None
    kind, px, lines, guess = b
    if guess:
        pg = c["boxes"].pages(entry["jp"], "jp", c["units"], c["widths"])
        px, lines = max(px, c["boxes"].need_px(pg)), max(lines, c["boxes"].lines_needed(pg))
    return kind + ("?" if guess else ""), px, lines


def limit_label(entry):
    b = box_limit(entry)
    return f"{b[0]} {b[1]}px x{b[2]}" if b else ""


def wrap(entry, en):
    """Greedy word wrap of `en` to the entry's box: a break goes before the word that would overflow. Breaks the
    translator wrote stay."""
    b = box_limit(entry)
    if not b:
        return en
    c = _ctx()
    out = ""
    # a chunk also ends after a page code, so "first!{FA:06}Next" measures the line before the code
    for word in re.split(r"(?<= )(?=[^ ])|(?<=\{FA:06\})|(?<=\{wait\})", en):
        cand = out + word
        meas = re.sub(r"(\{FA:06\}|\{wait\})$", "", cand)
        last = c["boxes"].pages(meas, "en", c["units"], c["widths"])[-1][-1]
        if last[0] - last[1] > b[1] and out and not re.search(r"(\n|\{FA:06\}|\{wait\})$", out):
            out = out.rstrip(" ") + "\n" + word
        else:
            out = cand
    return out


def width_problems(entry, en):
    """Pixel width per line and lines per page, from the VWF font and the box (docs/re/vwf.md §Width gate)."""
    b = box_limit(entry)
    if not b:
        return []
    c = _ctx()
    pg = c["boxes"].pages(en, "en", c["units"], c["widths"])
    out = []
    if (need := c["boxes"].need_px(pg)) > b[1]:
        out.append(f"line needs {need} px, {b[0]} limit {b[1]}")
    jp_lines = c["boxes"].lines_needed(c["boxes"].pages(entry["jp"], "jp", c["units"], c["widths"]))
    if (n := c["boxes"].lines_needed(pg)) > max(b[2], jp_lines):
        out.append(f"{n} lines on a page, box {b[2]}: add a {{FA:06}} page break or shorten")
    return out


def speaker(entry):
    """The name in the unit's first name tag ({call:@2B8C}{call:@NAME}...), as English if translated."""
    m = re.search(r"\{call:@2B8C\}(.*?)\{call:@2B9[29]\}", entry["jp"])
    if not m:
        return ""
    units = _ctx()["units"]
    name = m[1]
    for _ in range(4):  # names call names (七海 + るちあ)
        name = re.sub(r"\{call:@(\w+)\}", lambda c: units[c[1]].get("en") or units[c[1]]["jp"], name)
    return FURIGANA.sub("", name).replace("{end}", "")


_ENC = set()


def encodable(char):
    if not _ENC:
        for line in (ROOT / "tbl/en.tbl").read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                _ENC.add(line.split("=", 1)[1].replace("\\s", " "))
    return char in _ENC
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split("/")], [x.strip() for x in cells[1].split("/")], avoid))
    return rows


def problems(entry, en, terms):
    """Every rule, on one line of English (real newlines)."""
    jp = FURIGANA.sub("", entry["jp"])
    if not en.strip():
        return ["empty English"]
    out = []
    plain = TOKEN.sub("", en)
    if bad := sorted({c for c in plain if not encodable(c) and c != "\n"}):
        out.append(f"unencodable characters {bad}")
    if re.search(r"\\u[0-9a-fA-F]{4}", en) or "\t" in en:
        out.append("escape sequence or tab in the English")
    flat = re.sub(r"\s+", " ", en).lower()  # a term the wrap split over two lines is still the term
    units = _ctx()["units"]

    def call_en(t):
        u = units.get(t[7:-1]) if t.startswith("{call:@") else None
        return TOKEN.sub("", u.get("en") or "").lower() if u else ""

    want = Counter(t for t in TOKEN.findall(jp) if t not in FREE)
    have = Counter(t for t in TOKEN.findall(en) if t not in FREE)
    # a called name may be written out ("Mermaid Princesses" for a plural): the call only inserts that text
    want -= Counter({t: n for t, n in (want - have).items() if call_en(t) and call_en(t) in flat})
    if want != have:
        out.append(f"control codes differ: JP {dict(want)} EN {dict(have)}")
    for m in re.finditer(r"\{call:@[0-9A-F]+\}s\b", en):
        if call_en(m[0][:-1]).endswith("s"):
            out.append(f"{m[0]} draws '{call_en(m[0][:-1])}s': write the plural out or reword")
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", en):
        out.append('ordinal suffix after a variable (write "No. [var]")')
    jp_plain = TOKEN.sub("", jp)
    for jps, ens, avoid in terms:
        if any(has_term(jp_plain, j) for j in jps) and not any(e.lower() in flat for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    jp_flat = jp.replace("\n", "")
    for m in re.finditer(r"(\{call:@([0-9A-F]+)\})(さん|ちゃん|くん)", jp_flat):
        suffix = HONORIFICS[m[3]]
        if m[2] not in TITLE_CALLS and m[1] + suffix not in en and f"{call_en(m[1])}{suffix}" not in flat:
            out.append(f"honorific {m[1]}{m[3]} needs {m[1]}{suffix}")
    return out + width_problems(entry, en)


def index():
    return {e["id"]: e for _, _, entries in docs() for e in entries}


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work."""
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    groups = {}
    for _, _, entries in docs():
        for e in entries:
            if needs_english(e) and e["id"] not in taken:
                groups.setdefault(group_of(e), []).append(e)
    batches, cur, chars = [], [], 0
    for group in groups.values():
        c = sum(len(TOKEN.sub("", e["jp"])) for e in group)
        if cur and (chars + c > size or len(cur) + len(group) > MAX_ENTRIES):
            batches.append(cur)
            cur, chars = [], 0
        cur += group
        chars += c
    if cur:
        batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{e['id']}\t{speaker(e)}\t\t{limit_label(e)}\t{e['jp']}".replace("\n", "\\n") for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(TOKEN.sub("", e["jp"]) for e in batch)
        used = [(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
        (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                                      or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def check_batch(batch, entries, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    rows = [(r[0], "\t".join(r[1:]).replace("\\n", "\n")) for r in read_tsv(TL / f"{batch}.out.tsv")]
    rows = [(i, wrap(entries[i], en) if i in entries else en) for i, en in rows]
    bad = []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    for eid, en in rows:
        if eid in entries:
            bad += [f"{eid}: {p}: {en!r}" for p in problems(entries[eid], en, terms)]
    return bad, dict(rows)


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written."""
    if not overwrite:
        for _, _, entries in docs():
            for e in entries:
                if e["id"] in new and e.get("en") and e["en"] != new[e["id"]] and e.get("status") != "keep-jp":
                    sys.exit(f"{e['id']} would lose {e['en']!r}: pass --overwrite if that is meant")
    changed = 0
    for path, doc, entries in docs():
        touched = False
        for e in entries:
            if e["id"] in new and e.get("en") != new[e["id"]] and e.get("status") != "keep-jp":
                e["en"], e["status"] = new[e["id"]], "done"
                touched = True
                changed += 1
        if touched:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged: {changed} entries changed")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        return split(int(args[args.index("--size") + 1]) if "--size" in args else 3500)
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    entries, terms = index(), glossary()
    if cmd == "check" and not names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in entries.items() if e.get("en") for p in problems(e, e["en"], terms)]
        print(f"{len(entries)} entries, {len(bad)} problems")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    new, failed = {}, 0
    for batch in names:
        bad, rows = check_batch(batch, entries, terms)
        new.update(rows)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
    if failed:
        return 1
    if cmd == "merge":
        merge(new, overwrite)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))  # tests: tests/test_batches.py
