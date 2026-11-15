import os
import re

TSV = os.path.join(os.path.dirname(__file__), "..", "tools", "debug", "scenes.tsv")
WRITE = re.compile(r"^0x[0-9A-Fa-f]+:(0x[0-9A-Fa-f]+|\d+|\$[A-Z]+)(:[124])?(@\d+|!0x[0-9A-Fa-f]+)?$")
STEP = re.compile(r"^\d+ (-|[a-z]+(\+[a-z]+)*)$")


def test_scene_rows_parse():
    lines = open(TSV, encoding="utf-8").read().splitlines()
    assert lines[0].split("\t") == ["name", "id", "expect", "writes", "route", "note"]
    names = set()
    for ln in lines[1:]:
        f = ln.split("\t")
        assert len(f) == 6, ln
        assert f[0] not in names, f[0]
        names.add(f[0])
        assert 0 <= int(f[1]) < 43 and (f[2] == "" or 0 <= int(f[2]) < 43), ln  # scene table has 43 entries
        assert all(w == "-" or WRITE.match(w) for w in f[3].split()), ln
        assert all(STEP.match(s) for s in f[4].split(";") if f[4]), ln
