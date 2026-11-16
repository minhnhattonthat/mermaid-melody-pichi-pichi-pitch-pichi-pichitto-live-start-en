"""story_verdicts.py [--minors]: work/qa/story/reports/<ch>.report.md -> work/qa/story/verdicts/<ch>.tsv
("<ch><TAB>ok|issue<TAB>note" from the report's Assessment). --minors also prints the Minor items as
`- [ ] id - note (story <ch>)` lines for docs/polish.md (paste them with the edit tool).
A chapter whose verdict file is newer than its report is skipped (a later `fixed` line stays).
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REP, VER = ROOT / "work/qa/story/reports", ROOT / "work/qa/story/verdicts"


def section(text, head):
    m = re.search(rf"^#+ *{head}[^\n]*\n(.*?)(?=^#+ |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def main(argv):
    VER.mkdir(parents=True, exist_ok=True)
    for rep in sorted(REP.glob("*.report.md")):
        ch, text = rep.name[: -len(".report.md")], rep.read_text(encoding="utf-8")
        verdict = section(text, "Assessment").replace("`", "")
        word = re.match(r"\W*(ok|issue)\b", verdict)
        out = VER / f"{ch}.tsv"
        if word and not (out.exists() and out.stat().st_mtime > rep.stat().st_mtime):
            note = re.sub(r"\s+", " ", verdict[word.end():]).strip(" -")
            out.write_text(f"{ch}\t{word.group(1)}\t{note}\n", encoding="utf-8")
        print(f"{ch}\t{word.group(1) if word else 'NO ASSESSMENT'}")
        if "--minors" in argv:
            for item in re.findall(r"^\s*[-*] +(.+)$", section(text, "Minor"), re.M):
                print(f"- [ ] {re.sub(r'[`*]', '', item.strip())} (story {ch})")


if __name__ == "__main__":
    main(sys.argv[1:])
