-- Log resource-record lookups (0x08000E6C pointer of record i, 0x08000E94 attribute byte of record i): r0 table,
-- r1 index, lr caller. Finds which code asks for a record (compression.md: 5-byte records). 0x080012D4 = load
-- record (r0 dst, r1 table, r2 index, r3 ?): its lr is the scene code asking.
--   emu.py X.gba ... --script tools/lua/reslog.lua [--var FROM=600 --var TO=900]
local from, to = FROM or 0, TO or math.huge
local function r(s, n) return s["cpu.r" .. n] or -1 end
for _, a in ipairs({0x08000E6C, 0x08000E94, 0x080012D4}) do
  L.on_exec(a, a, function()
    if L.frame < from or L.frame > to then return end
    local s = emu.getState()
    L.log(string.format("f%d RES %08X r0=%08X r1=%X r2=%X lr=%08X", L.frame, a, r(s, 0), r(s, 1), r(s, 2), r(s, 14)))
  end)
end
