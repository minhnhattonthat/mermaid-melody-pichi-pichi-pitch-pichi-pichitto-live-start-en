#!/bin/sh
# codex_tl_review.sh NAME..: independent read-only codex review of work/qa/review/NAME.txt per docs/reviewer-brief.md;
# the final message lands in work/qa/review/NAME.report.md (the saved reviewer record). Runs all NAMEs in parallel.
cd "$(dirname "$0")/.." || exit 1
for n in "$@"; do
  ( timeout 1800 codex exec --sandbox read-only --skip-git-repo-check -o "work/qa/review/$n.report.md" \
      "You are the translation reviewer. Read docs/reviewer-brief.md and follow it exactly. Inputs: pairs file \
work/qa/review/$n.txt (read ALL of it), glossary.md, docs/style-reference.md, docs/translator-brief.md. \
Read-only: change no files. Your final message is the report in the brief's format; if there are no issues in a \
severity, write 'none' under it." > "work/qa/review/$n.log" 2>&1 ) &
done
wait
for n in "$@"; do printf '%s: ' "$n"; grep -A1 -i '^### Assessment' "work/qa/review/$n.report.md" | tail -1; done
