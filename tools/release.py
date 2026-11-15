"""release.py: phase-9 release gate and package (skill references/pipeline.md §Release). Stops at the first failure.

    python -X utf8 tools/release.py [--version 1.0] [--force] [--skip-build]

build -> tests -> smoke -> Japanese left (script units with no English, `tools/gfx_left.py` graphics rows) -> qa_gate
check on every work/qa/**/manifest.tsv that a `verdicts` dir sits next to -> text coverage (`tools/cover.py`: this
game's text is read through message ids, logged as TEXT <id> by tools/lua/msglog.lua) -> no unticked line in
docs/polish.md -> no template placeholder in README.md -> no debug/marker writes -> BPS patch (re-applied and
compared) -> zip (patch + README.txt), re-read and verified. Writes release/v<version>/; refuses to overwrite an
existing version without --force. The playable ROM stays in build/mermaid_en.gba.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import bps  # noqa: E402
from skill import SKILL  # noqa: E402

ORIG = ROOT / "rom/Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba"
BUILT = ROOT / "build/mermaid_en.gba"
PY = [sys.executable, "-X", "utf8"]
COVER = ["work/qa/tour5/runs", "work/qa/cover"]  # the last full tour + the msgview sweep (docs/status.md)
KANA = re.compile(r"[぀-ヿ㐀-鿿]")


def step(name, cmd, **kw):
    print(f"== {name}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, **kw)
    if r.returncode:
        sys.exit(f"release stopped: {name} failed (exit {r.returncode})")


def hashes(b):
    return {"size": len(b), "crc": f"{zlib.crc32(b):08X}", "md5": hashlib.md5(b).hexdigest(),
            "sha1": hashlib.sha1(b).hexdigest()}


def untranslated():
    """Used script units whose Japanese has kana/kanji but whose English is missing or still holds some."""
    out = []
    for f in sorted((ROOT / "script").glob("msg_*.json")):
        for u in json.loads(f.read_text(encoding="utf-8")):
            if u.get("used") and u.get("status") != "keep-jp" and KANA.search(u["jp"]) \
                    and (not u.get("en") or KANA.search(u["en"])):
                out.append(u["id"])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite release/v<version>/")
    ap.add_argument("--skip-build", action="store_true", help="gate the existing build/ output (tests still run)")
    a = ap.parse_args()
    out = ROOT / f"release/v{a.version}"
    if out.exists() and any(out.iterdir()) and not a.force:
        sys.exit(f"{out} exists: pass --force to overwrite it")

    if not a.skip_build:  # plain build: no --marker / --qa overrides
        step("build", PY + ["build.py"])
    step("tests", PY + ["tools/check.py"])
    step("smoke", PY + [f"{SKILL}/scripts/emu.py", str(BUILT), "--out", "work/qa/release_smoke", "--route",
                        "tools/routes/boot.txt", "--smoke"])
    print("== Japanese left", flush=True)
    left = untranslated()
    if left:
        sys.exit(f"release stopped: {len(left)} used units with Japanese left: {left[:8]}")
    step("gfx_left", PY + ["tools/gfx_left.py"])
    for m in sorted(ROOT.glob("work/qa/**/manifest.tsv")):
        if (m.parent / "verdicts").is_dir():
            step(f"qa_gate {m.relative_to(ROOT).as_posix()}",
                 PY + [f"{SKILL}/scripts/qa_gate.py", "check", str(m), str(m.parent / "verdicts")])
    step("text coverage", PY + ["tools/cover.py", *COVER, "--waive", "docs/text_unshown.tsv"])
    print("== polish, README, debug", flush=True)
    open_minors = re.findall(r"^- \[ \].*", (ROOT / "docs/polish.md").read_text(encoding="utf-8"), re.M)
    if open_minors:
        sys.exit(f"release stopped: {len(open_minors)} unticked lines in docs/polish.md, first: {open_minors[0][:100]}")
    holes = re.findall(r"<(?!https?:)[A-Za-z][^>\n]*>", (ROOT / "README.md").read_text(encoding="utf-8"))
    if holes:
        sys.exit(f"release stopped: template placeholders in README.md: {holes[:3]}")
    # the warp/debug tool is emulator Lua (tools/debug), never built in; --marker / --qa builds name their stage
    if re.search(r"warp|debug|marker|qa:", (ROOT / "build/mermaid_en.gba.writes.log").read_text(encoding="utf-8"), re.I):
        sys.exit("release stopped: the write log mentions debug/marker/qa writes")

    src, tgt = ORIG.read_bytes(), BUILT.read_bytes()
    print("== patch", flush=True)
    patch = bps.make(src, tgt)
    if bps.apply(src, patch) != tgt:
        sys.exit("release stopped: patch re-apply does not give the build")
    out.mkdir(parents=True, exist_ok=True)
    name = f"Mermaid_Melody_Pichi_Pichitto_Live_Start_EN_v{a.version}"
    (out / f"{name}.bps").write_bytes(patch)
    h, o = hashes(src), hashes(tgt)
    readme = (ROOT / "docs/release-readme.txt").read_text(encoding="utf-8").format(
        version=a.version, rom_name=ORIG.name, rom_size=h["size"], rom_crc=h["crc"], rom_md5=h["md5"],
        rom_sha1=h["sha1"], patch_name=f"{name}.bps", out_size=o["size"], out_crc=o["crc"], out_sha1=o["sha1"])
    (out / "README.txt").write_text(readme, encoding="utf-8", newline="\r\n")
    with zipfile.ZipFile(out / f"{name}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(out / f"{name}.bps", f"{name}.bps")
        z.write(out / "README.txt", "README.txt")
    with zipfile.ZipFile(out / f"{name}.zip") as z:  # verify the zip's own patch, not the file next to it
        assert sorted(z.namelist()) == sorted([f"{name}.bps", "README.txt"])
        assert bps.apply(src, z.read(f"{name}.bps")) == tgt
    print(f"release ok: {out / name}.zip ({len(patch)} byte patch), patched sha1 {o['sha1']} crc32 {o['crc']}")


if __name__ == "__main__":
    main()
