"""vwf.py: variable-width English text in the 12x12 font (docs/re/vwf.md).

    from vwf import apply; apply(rom)      # patches code, glyph cells, width table, attribute bits

drawchar (0x080056CC) advances a fixed [obj+0x2C] px (12) and its blitter (0x08004E68) draws a glyph only at
x & ~3, overwriting the whole 12 px window. The English path (glyph with a width; mode 0 with spacing 12, or mode 1 =
flags bit 0, the 8 px kana font of in-song dialogue and credits, except message ids < 7: debug menu 4) instead:
  - composes the cell in RAM: the previous glyph's pixels still inside the new window (same text object, same row,
    x moving right) OR the glyph shifted by x & 3, so neighbours are not erased;
  - moves a glyph to the next 4 px boundary when the colour changes, so no earlier pixel is redrawn in the new colour;
  - calls the blitter with the RAM cell (its font-address computation reads an override pointer) and advances by
    the glyph's width.
Everything else falls through to the original drawchar. Code and tables live in free space; the two detours
(drawchar's prologue, the blitter's font-address computation) return with absolute `bx`, since BL cannot reach
0x09FDxxxx from 0x0800xxxx.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enfont  # noqa: E402

FONT = 0x098745E0  # glyph cells, 36 bytes each
ATTR = 0x187E2B8  # u16 per glyph code: bit 15 = other path in drawchar, bit 14 = alternate cell in the blitter
CODE = 0x1FDF800  # file offsets in the free space (docs/re/compression.md: zero-filled 0x1FDF760..)
WIDTHS = 0x1FDFC00  # u8 advance per glyph code, 0 = not an English glyph
NWIDTH = 0x600  # codes 0x000-0x5FF (F0-F5 prefix)
FREE_END = 0x1FE0200  # first byte after the VWF code and tables
RAM = 0x02033700  # 64 bytes: +0 cell override, +4 obj, +8 row, +12 last x, +16 colour, +24 cell (36)
DRAWCHAR = 0x080056CC
BLIT = 0x08004E68
BLIT_SITE = 0x4F46  # lsls r0,r7,#3 .. adds r2,r0,r1 (10 bytes); its pool word 0x4F94 (= FONT) has no other user
BLIT_POOL = 0x4F94


def rom_addr(off):
    return 0x08000000 + off


ASM = """
    b detour
    b blit_font
detour:
    ldr r2, =WIDTHS
    ldrb r2, [r2, r1]
    cmp r2, #0
    beq orig
    ldr r3, [r0, #0x10]
    movs r2, #0x12
    tst r3, r2
    bne orig
    lsls r3, r3, #31
    beq mode0
    ldrh r3, [r0, #0x18]
    cmp r3, #7
    blt orig
    b english
mode0:
    mov r2, r0
    adds r2, #0x2c
    ldrb r2, [r2]
    cmp r2, #12
    beq english
orig:
    push {r4-r7, lr}
    mov r7, r8
    push {r7}
    sub sp, #8
    ldr r2, =DRAWCHAR_BODY
    bx r2

english:
    push {r4-r7, lr}
    sub sp, #16
    mov r4, r0
    mov r6, r1
    ldr r3, [r4, #0x10]
    movs r2, #4
    orrs r3, r2
    str r3, [r4, #0x10]
    mov r0, r4
    adds r0, #0x30
    ldrb r1, [r0]
    str r1, [sp]
    subs r0, #2
    ldrb r1, [r0]
    str r1, [sp, #4]
    subs r0, #1
    ldrb r1, [r0]
    str r1, [sp, #12]
    mov r0, r4
    adds r0, #0x21
    ldrb r2, [r0]
    adds r0, #4
    movs r1, #0
    ldrsb r1, [r0, r1]
    adds r2, r2, r1
    str r2, [sp, #8]
    mov r0, r4
    adds r0, #0x20
    ldrb r5, [r0]
    lsls r5, r5, #3
    adds r0, #0x0b
    ldrb r1, [r0]
    adds r5, r5, r1
    ldr r7, =RAM
    ldr r0, [r7, #4]
    cmp r0, r4
    bne fresh
    ldr r0, [r7, #8]
    cmp r0, r2
    bne fresh
    ldr r0, [r7, #12]
    cmp r5, r0
    ble fresh
    ldr r1, [r7, #16]
    ldr r2, [sp, #12]
    cmp r1, r2
    beq cont
    movs r1, #3
    tst r5, r1
    beq cont
    adds r1, r5, #3
    movs r2, #3
    bics r1, r2
    subs r2, r1, r5
    mov r5, r1
    mov r1, r4
    adds r1, #0x2b
    ldrb r3, [r1]
    adds r3, r3, r2
    strb r3, [r1]
cont:
    movs r1, #3
    bics r0, r1
    lsrs r2, r0, #3
    adds r2, #1
    str r2, [r7, #20]
    mov r2, r5
    bics r2, r1
    subs r3, r2, r0
    cmp r3, #12
    bge fresh
    lsls r3, r3, #1
    b compose
fresh:
    movs r3, #32
    movs r2, #0
    mvns r2, r2
    str r2, [r7, #20]
compose:
    str r4, [r7, #4]
    ldr r0, [sp, #8]
    str r0, [r7, #8]
    str r5, [r7, #12]
    ldr r0, [sp, #12]
    str r0, [r7, #16]
    str r6, [sp, #8]
    movs r0, #3
    ands r0, r5
    lsls r0, r0, #1
    movs r1, #36
    muls r1, r6
    ldr r6, =FONT
    adds r6, r6, r1
    mov r2, r7
    adds r2, #24
    str r2, [r7, #0]
    movs r5, #12
row:
    ldrb r1, [r2, #0]
    ldrb r4, [r2, #1]
    lsls r4, r4, #8
    orrs r1, r4
    ldrb r4, [r2, #2]
    lsls r4, r4, #16
    orrs r1, r4
    lsrs r1, r3
    ldrb r4, [r6, #0]
    ldrb r7, [r6, #1]
    lsls r7, r7, #8
    orrs r4, r7
    ldrb r7, [r6, #2]
    lsls r7, r7, #16
    orrs r4, r7
    lsls r4, r0
    orrs r1, r4
    strb r1, [r2, #0]
    lsrs r1, r1, #8
    strb r1, [r2, #1]
    lsrs r1, r1, #8
    strb r1, [r2, #2]
    adds r2, #3
    adds r6, #3
    subs r5, #1
    bne row
    ldr r7, =RAM
    ldr r0, [sp]
    cmp r0, #1
    bgt map_ptr
    movs r1, #0xA0
    lsls r1, r1, #3
    muls r0, r1
    ldr r1, =0x03002DB0
    adds r6, r0, r1
    b map_ok
map_ptr:
    ldr r1, =0x03002A20
    ldr r6, [r1, #0xc]
map_ok:
    ldr r0, [r7, #8]
    lsls r0, r0, #5
    ldr r1, [r7, #12]
    lsrs r2, r1, #3
    adds r0, r0, r2
    lsls r0, r0, #1
    adds r6, r6, r0
    ldr r5, [sp, #4]
    adds r5, #1
    ldr r4, =0x03002A42
    ldr r3, [r7, #20]
    movs r0, #4
    tst r1, r0
    bne right_only
    cmp r2, r3
    bgt right_only
    mov r0, r6
    bl free_col
right_only:
    adds r2, #1
    cmp r2, r3
    bgt freed
    adds r0, r6, #2
    bl free_col
freed:
    ldr r0, [sp, #8]
    ldr r1, [r7, #12]
    negs r1, r1
    ldr r2, [r7, #8]
    ldr r3, [r7, #16]
    ldr r4, =BLIT_THUMB
    bl call_r4
    ldr r7, =RAM
    ldr r4, [r7, #4]
    ldr r0, [sp, #8]
    ldr r1, =WIDTHS
    ldrb r1, [r1, r0]
    mov r0, r4
    adds r0, #0x2b
    ldrb r2, [r0]
    adds r2, r2, r1
    strb r2, [r0]
    lsls r2, r2, #24
    lsrs r2, r2, #27
    subs r0, #7
    strb r2, [r0]
    add sp, #16
    pop {r4-r7}
    pop {r0}
    bx r0
call_r4:
    bx r4

free_col:
    ldrh r0, [r0]
    ldr r1, =0x3FF
    ands r0, r1
    cmp r0, #0x3F
    ble fc_done
    subs r0, #0x40
    adds r0, r4, r0
    ldrb r1, [r0]
    cmp r1, r5
    bne fc_done
    movs r1, #0
    strb r1, [r0]
    push {r2, r3}
    subs r2, r0, r4
    mov r3, r4
    subs r3, #10
    ldrh r1, [r3]
    cmp r2, r1
    bge fc_cur
    strh r2, [r3]
fc_cur:
    pop {r2, r3}
    ldrb r1, [r0, #1]
    cmp r1, r5
    bne fc_done
    movs r1, #0
    strb r1, [r0, #1]
fc_done:
    bx lr

blit_font:
    ldr r1, =RAM
    ldr r2, [r1, #0]
    cmp r2, #0
    beq rom_cell
    movs r0, #0
    str r0, [r1, #0]
    b blit_back
rom_cell:
    lsls r0, r7, #3
    adds r0, r0, r7
    lsls r0, r0, #2
    ldr r1, =FONT
    adds r2, r0, r1
blit_back:
    ldr r0, =BLIT_BACK
    bx r0
.ltorg
"""


def assemble():
    """-> (code bytes at CODE, {label: address})."""
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    src = ASM
    for k, v in {"DRAWCHAR_BODY": DRAWCHAR + 8 + 1, "BLIT_THUMB": BLIT + 1, "BLIT_BACK": rom_addr(BLIT_SITE + 10) + 1,
                 "WIDTHS": rom_addr(WIDTHS), "FONT": FONT, "RAM": RAM}.items():
        src = src.replace("=" + k, f"=0x{v:08X}")
    ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)
    base = rom_addr(CODE)
    enc, _ = ks.asm(src, base)
    code = bytes(enc)
    labels = {"detour": base, "blit_font": base + 2}  # the two entry branches at the top of ASM
    if CODE + len(code) > WIDTHS:
        raise ValueError("VWF code overflows into the width table")
    return code, labels


def apply(rom):
    """Patch an English build in place: VWF code, detours, glyph cells, widths, attribute bits."""
    code, lab = assemble()
    if any(rom[CODE:FREE_END]):
        raise ValueError("VWF free space is not free")
    rom[CODE:CODE + len(code)] = code
    # drawchar prologue (push {r4-r7,lr}; mov r7,r8; push {r7}; sub sp,#8) -> ldr r2,[pc,#0]; bx r2; .word detour
    site = DRAWCHAR - 0x08000000
    assert rom[site:site + 8] == bytes.fromhex("f0b5474680b482b0"), "drawchar prologue changed"
    rom[site:site + 8] = bytes.fromhex("004a1047") + struct.pack("<I", lab["detour"] | 1)
    # blitter font address -> ldr r1,[pc,#0x4C] (pool 0x4F94); bx r1; never-run tail stays as is
    assert rom[BLIT_SITE:BLIT_SITE + 10] == bytes.fromhex("f800c019800011494218"), "blitter site changed"
    assert struct.unpack_from("<I", rom, BLIT_POOL)[0] == FONT
    rom[BLIT_SITE:BLIT_SITE + 4] = bytes.fromhex("13490847")
    struct.pack_into("<I", rom, BLIT_POOL, lab["blit_font"] | 1)
    glyphs = enfont.load()
    slots = enfont.slots(glyphs)
    widths = bytearray(NWIDTH)
    for ch, rows in glyphs:
        c = slots[ch]
        off = FONT - 0x08000000 + 36 * c
        rom[off:off + 36] = enfont.cell(rows)
        widths[c] = enfont.width(rows)
        a = struct.unpack_from("<H", rom, ATTR + 2 * c)[0]
        struct.pack_into("<H", rom, ATTR + 2 * c, a & 0x3FFF)
    rom[WIDTHS:WIDTHS + NWIDTH] = widths
    return rom
