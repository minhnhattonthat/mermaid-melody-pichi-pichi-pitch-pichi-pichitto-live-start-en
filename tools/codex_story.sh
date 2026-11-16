#!/bin/sh
# codex_story.sh JOBS CHAPTER..: independent read-only codex story pass of work/qa/story/chapters/CHAPTER.txt per
# docs/story-reviewer-brief.md, JOBS at a time; reports land in work/qa/story/reports/CHAPTER.report.md.
# Then: python -X utf8 tools/story_verdicts.py (writes work/qa/story/verdicts/*.tsv from the Assessments).
cd "$(dirname "$0")/.." || exit 1
jobs=$1; shift
mkdir -p work/qa/story/reports
printf '%s\n' "$@" | xargs -P "$jobs" -I{} sh -c '
  timeout 2400 codex exec --sandbox read-only --skip-git-repo-check -o "work/qa/story/reports/{}.report.md" \
    "You are the story reviewer. Read docs/story-reviewer-brief.md and follow it exactly. Chapter file: \
work/qa/story/chapters/{}.txt (read ALL of it). Also read docs/synopsis.md, docs/style-reference.md, glossary.md, \
docs/decisions.md. Read-only: change no files. Your final message is the report in the brief format." \
    > "work/qa/story/reports/{}.log" 2>&1'
python -X utf8 tools/story_verdicts.py
