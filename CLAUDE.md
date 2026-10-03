# CLAUDE.md

<!-- Loaded at the start of every session. Standing instructions, not documentation.
     Read .claude/claude-md-guide.md before editing. Keep under ~80 lines. -->

MS AI Command Center: agent schema, personas, scripts, and ops files for Jock's
Vanderbilt MS in AI. Knowledge lives in the Dropbox vault wiki; this repo is versioned
tooling and ops markdown.

@AGENTS.md

@.claude/identity/operating.md

## Commands

Use the repo venv; `python3` does not exist on this machine.

- Convert a week: `.venv\Scripts\python.exe scripts\convert_content.py --week N` (add `--dry-run` first; `--force` only when Jock asks to overwrite raw)
- Dashboard: `.venv\Scripts\python.exe scripts\dashboard.py --open` (or `--print-once` to check output)
- Wiki graph: `.venv\Scripts\python.exe scripts\stage_wiki_graph.py` (`--dry-run`, `--no-open`, `--validate`)
- New deps for convert go in `scripts/requirements.txt`. Skill scripts print an install hint instead of installing.

## Rules

Never:

- Never edit `Coursework/`, `wiki/raw/`, or `_archive/` in the vault. `.claude/settings.json` enforces this. New raw files come only from `convert_content.py`. Lecture-notes skill output goes to `wiki/courses/AI-5100/lecture-notes/week-NN/`.
- Never read the vault's `Admin/` folder (insurance cards, bills).
- Never invent syllabus dates, weights, or rubric language. If the syllabus page doesn't say it, ask.
- Never paste Vanderbilt proprietary materials into `us-signal/` briefs or other company-facing docs.
- Never commit course binaries or video (`*.pdf`, `*.pptx`, `*.mp4`, …); `.gitignore` covers them.
- Never push to GitHub unless Jock asks.

## Workflow

- Skills live in `.claude/skills/` only. Cursor rules point at them; don't create copies in `.cursor/skills/` or `.agents/`.
- Vendored skills keep upstream provenance: `UPSTREAM.md` or `SKILL.upstream.md` next to them. Record local changes there.
- Skill output preferences go in that skill's `## Jock's Preferences` section, not here.
- Commit in logical chunks with imperative messages. Update `docs/CURRENT_STATE.md` when what works or what's broken changes.

## Domain notes

- Ops priorities: `command-center/HOME.md`. Calendar and assessments: `command-center/academic-calendar.md` (copied from the syllabus page in the vault).
- Study progress (spaced review): `command-center/study-progress.md`, owned by the `study` skill.
- Read PDFs over ~20 pages in page ranges, not all at once.
