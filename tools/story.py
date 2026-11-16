"""story.py [TOURDIR]: story-pass chapter files, one per episode, in the order the tour run showed the messages.

Reads TOURDIR/runs/epNN/log.txt (TEXT <hex id> lines from msglog.lua; default work/qa/tour5) and script/msg_*.json,
writes work/qa/story/chapters/epNN.txt as `>> id | speaker | JP` / `EN` (calls resolved, codes dropped, page breaks
shown as " / "). Repeats within an episode (song lyrics loop) are kept once. Prints the per-episode line counts.
"""
import glob, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "work/qa/story/chapters"
NAME_OPEN, NAME_CLOSE = {"2B8C"}, {"2B92", "2B99"}  # 【 name 】 wrappers around a speaker name


def load():
    units, by_msg = {}, {}
    for f in sorted(glob.glob(str(ROOT / "script/msg_*.json"))):
        for u in json.loads(Path(f).read_text(encoding="utf-8")):
            units[u["id"]] = u
            for i in u["ids"]:
                by_msg[i] = u
    return units, by_msg


def render(text, units, depth=0):
    def call(m):
        k = m.group(1)
        if k in NAME_OPEN:
            return "【"
        if k in NAME_CLOSE:
            return "】 "
        u = units.get(k)
        return render(u["en"] if render.lang == "en" and u["en"] else u["jp"], units, depth + 1) if u and depth < 8 else ""
    text = re.sub(r"\{FD:01\}.*?\{FD:00\}", "", text)  # furigana
    text = re.sub(r"\{call:@([0-9A-F]+)\}", call, text)
    if depth:
        return text
    text = re.sub(r"\{(FA:06|wait)\}", " / ", text)
    text = re.sub(r"\{[^}]*\}", "", text).replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip(" /")


def line(u, units):
    render.lang = "jp"
    jp = render(u["jp"], units)
    render.lang = "en"
    en = render(u["en"], units)
    if not jp:
        return ""
    m = re.match(r"【([^】]*)】\s*", jp)
    speaker = m.group(1) if m else "-"
    if m:
        jp = jp[m.end():]
        en = re.sub(r"^【[^】]*】\s*", "", en)
    return f">> {u['id']} | {speaker} | {jp}\n{en}\n"


BUBBLES, STRAY = 0x5C8, (range(0x936, 0x93E), range(0x977, 0xA00))  # story-bubble ids; late inserts, no block


def main(argv):
    tour = ROOT / (argv[0] if argv else "work/qa/tour5")
    units, by_msg = load()
    ok = lambda i: (u := by_msg.get(i)) and u["used"] and "dummy~" not in u["en"] and line(u, units)
    order = {}  # ep -> message ids in the order the tour showed them
    for log in sorted(tour.glob("runs/ep[0-9][0-9]/log.txt")):
        ids = order.setdefault(log.parent.name, [])
        for m in re.findall(r"^TEXT ([0-9A-Fa-f]+)", log.read_text(errors="replace"), re.M):
            if ok(i := int(m, 16)) and i not in ids:
                ids.append(i)
    # Each episode's bubbles sit in one id block: [its first id, the next episode's first id). The tour stops at the
    # song (no GOD mode), so unseen ids of a block (endings, branches) go in after the nearest lower id of that block.
    starts = {}
    for ep, ids in order.items():
        b = sorted(i for i in ids if i >= BUBBLES)
        med = b[len(b) // 2]
        starts[ep] = min(i for i in b if abs(i - med) < 0x40)
    bounds = sorted((s, ep) for ep, s in starts.items()) + [(STRAY[1].start, None)]
    shown = {i for ids in order.values() for i in ids}
    placed, extras = set(), []
    for i in sorted(by_msg):
        if i < 0x501 or i in shown or not ok(i):
            continue
        ep = next((e for (s, e), (n, _) in zip(bounds, bounds[1:]) if s <= i < n), None)
        if ep is None or any(i in r for r in STRAY):
            extras.append(i)
            continue
        ids = order[ep]
        lower = [j for j in ids if starts[ep] <= j < i]
        ids.insert(ids.index(max(lower)) + 1 if lower else len(ids), i)
        placed.add(i)
    OUT.mkdir(parents=True, exist_ok=True)
    order["extras"] = extras
    for ep, ids in order.items():
        head = (f"# Episode {int(ep[2:])} (story mode). Order: the tour run ({tour.relative_to(ROOT).as_posix()}), then"
                " lines it never reached (marked `(+)`, after the song: endings, branches) by message id."
                if ep != "extras" else "# Story lines outside every episode's id block (late inserts, finale/encore?);"
                " order by message id, episode unknown.")
        out, seen = [head + "\n"], set()
        for i in ids:
            u = by_msg[i]
            if u["id"] not in seen:
                seen.add(u["id"])
                out.append(line(u, units).replace(" | ", " (+) | ", 1) if i in placed else line(u, units))
        (OUT / f"{ep}.txt").write_text("\n".join(out), encoding="utf-8")
        print(ep, len(seen))


if __name__ == "__main__":
    main(sys.argv[1:])
