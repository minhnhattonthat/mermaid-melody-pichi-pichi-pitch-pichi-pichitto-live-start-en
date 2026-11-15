-- Log a state machine (0x08049F70 layout: +0 u32 state table, +4 u8 state, +5 u8 next state, +8 u32 frames in
-- state) whenever its table or state changes. Default SM = 0x03003DFC (room, table 0x09F730C0).
--   emu.py ROM ... --script tools/lua/smlog.lua [--var SM=0x03003DFC]
local A = SM or 0x03003DFC
local m = emu.memType.gbaMemory
local last = ""
L.on_frame(function(f)
  local s = string.format("%08X %d %d", emu.read32(A, m), emu.read(A + 4, m), emu.read(A + 5, m))
  if s ~= last then
    L.log(string.format("SM %d %s", f, s))
    last = s
  end
end)
