"""gfx_grid.py: zoom a band of a block render with an 8-px tile grid and pixel coordinates, for reading piece bounds.

    python -X utf8 tools/gfx_grid.py IN.png Y0 Y1 OUT.png [ZOOM]
"""
import sys
from PIL import Image, ImageDraw

src, y0, y1, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
z = int(sys.argv[5]) if len(sys.argv) > 5 else 5
im = Image.open(src).convert("RGB")
im = im.crop((0, y0, im.size[0], y1))
im = im.resize((im.size[0] * z, im.size[1] * z), Image.NEAREST)
d = ImageDraw.Draw(im)
for x in range(0, im.size[0], 8 * z):
    d.line([(x, 0), (x, im.size[1])], fill=(0, 0, 0))
    d.text((x + 2, im.size[1] - 10), str(x // z), fill=(0, 0, 0))
for y in range(0, im.size[1], 8 * z):
    d.line([(0, y), (im.size[0], y)], fill=(0, 0, 0))
    d.text((1, y + 1), str(y0 + y // z), fill=(0, 0, 0))
im.save(out)
