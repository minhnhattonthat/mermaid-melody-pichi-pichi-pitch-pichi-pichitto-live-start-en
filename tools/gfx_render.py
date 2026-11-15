"""gfx_render.py: render one block of the original ROM in grey (or a .pal) for reading its layout.

    python -X utf8 tools/gfx_render.py OFFSET SIZE LAYOUT OUT.png [PAL]     e.g. 18AF223 800x2 obj8x4*4 work/gfx/a.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gfx  # noqa: E402

off, spec, layout, out = sys.argv[1:5]
rom = (gfx.ROOT / "work/orig.gba").read_bytes()
a, b = spec.split("x")
data, _ = gfx.decode(rom, int(off, 16), (int(a, 16), int(b)))
pal = [gfx.rgb(c) for c in __import__("struct").unpack("<16H", Path(sys.argv[5]).read_bytes()[:32])] \
    if len(sys.argv) > 5 else [(i * 17,) * 3 for i in range(16)]
gfx.save_png(gfx.to_image(data, layout), pal, out)
