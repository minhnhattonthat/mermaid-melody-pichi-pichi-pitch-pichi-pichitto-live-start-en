#!/bin/sh
# Warp to raw scene ids from a cold boot, one run each, for mapping scene ids: tools/debug/warp_ids.sh OUTDIR ID...
# Each run: OUTDIR/s<id>/ shots every 100 frames, sheet, log (WARP/ARRIVED/SCENE lines).
cd "$(dirname "$0")/../.." || exit 1
S="$(python tools/skill.py)"
ROM="${ROM:-rom/Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba}"
SAV="${SAV:-work/saves/default.sav}"
out="$1"; shift
for id in "$@"; do
  echo "$id"
done | xargs -P "${JOBS:-6}" -I{} python -X utf8 "$S/scripts/emu.py" "$ROM" --sav "$SAV" --out "$out/s{}" \
  --script tools/debug/warp.lua --script tools/lua/scenelog.lua --var SCENE_ID={} --frames "${FRAMES:-700}" \
  --shot-every 100 --sheet --timeout 200 > /dev/null 2>&1
for id in "$@"; do printf '%s: ' "$id"; grep -E "ARRIVED|Lua error|fail" "$out/s$id/log.txt" | head -1; echo; done
