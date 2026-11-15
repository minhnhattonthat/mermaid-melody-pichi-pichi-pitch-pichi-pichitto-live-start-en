-- Log each message the text engine starts (0x08007454 setup; id = u16 at text object +0x18, table ROM 0x09860CE0).
-- Lines: "MSG <frame> <id> obj=<addr> lr flags sp W H" (flags bit 0 = 8 px mode, W cells, H tile rows) and "TEXT <hex id>" (textcover.py format, ids in build/strings.tsv).
L.on_exec(0x08007488, 0x08007488, function()
  local s = emu.getState()
  local o = s["cpu.r5"]
  local id = emu.read16(o + 0x18, emu.memType.gbaMemory, false)
  local m = emu.memType.gbaMemory
  L.log(string.format("MSG %d %d obj=%08X lr=%08X flags=%08X sp=%d W=%d H=%d", L.frame, id, o, s["cpu.r14"],
    emu.read32(o + 0x10, m), emu.read(o + 0x2C, m), emu.read(o + 0x22, m), emu.read(o + 0x23, m)))
  L.log(string.format("TEXT %X", id))
end)
