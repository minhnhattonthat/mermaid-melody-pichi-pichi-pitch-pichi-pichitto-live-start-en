"""tools/batches.py rules on real units, and every shipped English line passes them (the batch check as a gate)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import batches  # noqa: E402

U = batches.index()
BUBBLE = "102A7"  # Rina: おそらく、\n{call:@2AAC}だろう。 (story bubble, 212 px)


def test_wrap_fits_and_keeps_words():
    e = U[BUBBLE]
    en = "Probably {call:@2AAC}, but who knows, she always runs off on her own.{end}"  # box: 2 lines
    out = batches.wrap(e, en)
    assert "\n" in out and out.replace("\n", " ") == en
    assert not batches.width_problems(e, out)
    assert batches.width_problems(e, en)  # unwrapped it overflows


def test_wrap_before_page_code():
    e = U[BUBBLE]
    en = "Probably {call:@2AAC}, but who knows, she always runs off on her own!{FA:06}Next.{end}"
    out = batches.wrap(e, en)
    assert out.index("\n") < out.index("{FA:06}") and not batches.width_problems(e, out)


def test_problems():
    e = U[BUBBLE]
    assert batches.problems(e, "Probably {call:@2AAC}.{end}", []) == []
    assert any("control codes" in p for p in batches.problems(e, "Probably Rina.{end}", []))
    assert any("unencodable" in p for p in batches.problems(e, "Probably {call:@2AAC}　.{end}", []))
    # furigana runs are dropped in English; page breaks are free
    assert batches.problems(U["2AF8"], "{call:@2AEA} Domoto{end}", []) == []
    assert batches.problems(e, "Probably...{FA:06}{call:@2AAC}.{end}", []) == []
    # a called name written out is fine; a plural "s" glued to a name ending in s is not
    karen = batches.TOKEN.sub("", batches._ctx()["units"]["2AAC"].get("en"))
    assert batches.problems(e, f"Probably {karen}.{{end}}", []) == []
    p = U["F486"]
    assert any("draws" in x for x in batches.problems(p, p["jp"].replace("が\nなぜここに！？", "s?!"), []))


def test_shipped_english_passes():
    terms = batches.glossary()
    bad = [(i, p) for i, e in U.items() if e.get("en") for p in batches.problems(e, e["en"], terms)]
    assert not bad, bad[:20]
