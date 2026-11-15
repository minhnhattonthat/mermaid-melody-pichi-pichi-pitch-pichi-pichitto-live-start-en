-- Zero the mosaic register every frame: locked episodes in the episode grid show their title art mosaicked.
-- Usage: emu.py ROM ... --script tools/lua/nomosaic.lua   (QA shots of episode titles)
L.on_frame(function()
  emu.write(0x0400004C, 0, emu.memType.gbaMemory)
  emu.write(0x0400004D, 0, emu.memType.gbaMemory)
end)
