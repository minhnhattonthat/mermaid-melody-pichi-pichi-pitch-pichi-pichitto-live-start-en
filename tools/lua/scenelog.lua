-- Log every change of the scene id (u8 at IWRAM 0x0300287C, main loop 0x0800E1C0, table ROM 0x09D37060).
-- Usage: emu.py ROM --script tools/lua/scenelog.lua   -> log.txt lines "SCENE frame id prev stack..."
local A = 0x0300287C
local last = -1
L.on_frame(function(f)
  local id = emu.read(A, emu.memType.gbaMemory)
  if id ~= last then
    local depth = emu.read(A + 4, emu.memType.gbaMemory)
    local st = {}
    for i = 0, 5 do st[#st + 1] = string.format("%d", emu.read(A + 5 + i, emu.memType.gbaMemory)) end
    L.log(string.format("SCENE %d %d prev %d depth %d stack %s", f, id, last, depth, table.concat(st, ",")))
    last = id
  end
end)
