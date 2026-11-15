#!/bin/sh
# Run one warp per value of a --var, in parallel: tools/debug/warp_many.sh SCENE VAR OUTDIR VALUE...
#   e.g. tools/debug/warp_many.sh anime EP work/qa/eps 0 1 2     -> work/qa/eps/<value>/ (log with SCENE/SHOW/TEXT lines)
#   coverage sweep: ROM=build/mermaid_en.gba FRAMES=1300 tools/debug/warp_many.sh msgview MSG work/qa/cover <ids>
#   then tools/cover.py work/qa/tour3/runs work/qa/cover
# Env: FRAMES (default 1500), EVERY (shot interval, default 100), MASH (default 0), JOBS (default 6), SAV, ROM.
cd "$(dirname "$0")/../.." || exit 1
S="$(python tools/skill.py)"
ROM="${ROM:-rom/Mermaid Melody - Pichi Pichi Pitch - Pichi Pichitto Live Start! (Japan).gba}"
SAV="${SAV:-work/saves/default.sav}"
scene="$1"; var="$2"; out="$3"; shift 3
for v in "$@"; do echo "$v"; done | xargs -P "${JOBS:-6}" -I{} python -X utf8 "$S/scripts/emu.py" "$ROM" --sav "$SAV" \
  --out "$out/{}" --script tools/debug/warp.lua --script tools/lua/scenelog.lua --script tools/lua/showmsg.lua \
  --script tools/lua/msglog.lua --var "SCENE='$scene'" --var "$var={}" --frames "${FRAMES:-1500}" --shot-every "${EVERY:-100}" \
  --mash "${MASH:-0}" --timeout 400 > /dev/null 2>&1
for v in "$@"; do
  printf '%s: %s\n' "$v" "$(grep -E 'SCENE|SHOW|ARRIVED|rror' "$out/$v/log.txt" | tail -n +3 | awk '{printf "%s %s %s | ", $1, $2, $3$4}' | cut -c1-200)"
done
