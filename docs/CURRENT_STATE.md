# Current state

Updated: 2026-10-03

## What's working

- **Command Center** at `C:\Users\jockt\dev\ms_ai`. GitHub: https://github.com/jockthompsongit/ms_ai_cc
- **Vault relayout handled (2026-10-03):** sources in `Coursework/`, wiki at `Vandy Other/wiki/`, raw inside the wiki. `scripts/vault_paths.py`, `AGENTS.md`, rules, skills and docs all point there. The vault's `Vandy Other/AGENTS.md` is now a pointer to the repo copy.
- **Convert:** `convert_content.py` reads `Coursework/`, skips existing raw outputs (`--force` to overwrite), disambiguates slug collisions, and adds a `source_file` header to copied `.md`/`.txt`.
- **Dashboard:** capture probes work again (Weeks 1–2 show raw + lecture). Quick links open in Obsidian/Cursor. Shows the Coursework inbox.
- **Graph staging** includes `courses/` (lectures, assignments, syllabus, project) and excludes `raw/` and `lecture-notes/`. 26 pages staged on 2026-10-03.
- **Calendar:** Weeks 1–8 dated, plus the assessment list, from the vault syllabus page.
- **Claude Code layer** (adopted from `personal_assistant`): `CLAUDE.md`, `.claude/identity/operating.md` (working contract), `.claude/claude-md-guide.md`, and `.claude/settings.json` deny rules (Coursework, wiki/raw, _archive; no reads of Admin).
- **Skills (single copy in `.claude/skills/`):** `ms-ai-paper-tutor` (Tutor engine, now with a vault overlay and Jock's Preferences), `lecture-recording-to-lecture-notes` (PA version with Jock's Preferences + quiz + wiki linking), and the wiki-to-graph family (with `UPSTREAM.md`, `docs/`, `LICENSE.md`). PA's `study` skill was tried and removed at Jock's request. `.cursor/skills/` and `.agents/` were removed.

- **Brightspace map** (`command-center/course-map.md`, `readings.json`), read via Claude in Chrome 2026-10-03.
- **Readings:** 13 public links captured to `raw/.../links/` (`capture_links.py`); 5 manual (tools, repos, Box).
- **Pending work:** `scripts/pending_work.py` (transcripts, notes, conversion, lecture pages, reading summaries, homework).
- **Transcripts:** `scripts/file_transcripts.py` files Zoom VTT downloads by week + live/async. Automatic in-browser capture was blocked by the safety classifier; downloads stay manual.
- **Tutor packs:** `scripts/build_tutor_pack.py --all` → Dropbox `Vandy Other/tutor-packs/` for Claude/ChatGPT Projects.
- **Slack #ms-ai** (`command-center/slack.md`): served by the Render bot below. The earlier desktop routines (`ms-ai-daily-brief`, `ms-ai-week-ahead`, `ms-ai-slack-inbox`) are disabled and kept only as a fallback.

- **Render Slack bot (live 2026-10-03):** `bot/` + `render.yaml`, setup in `docs/RENDER.md`. Semantic router (Haiku 4.5 classifier → Haiku 4.5 / Sonnet 5.5 / Opus 5.5), read-only Dropbox tools, briefs in-worker. 20 offline tests pass (`pytest tests`). Smoke test: "what's due" → Haiku 4.5, $0.007. Desktop Slack routines disabled.
- **Desktop sync routine** `ms-ai-brightspace-sync` (6:30 AM/PM): Brightspace → readings → transcripts → `pending_work.py --publish` → tutor packs. Posts nothing.

## Gaps

- **Weeks 3–6 not converted or ingested** (all in `Coursework/`). Weeks 3–4 have Zoom VTTs. Module ends Oct 16.
- **Homework:** only one assignment has actually been posted (HW-W2); its status still needs confirming. The syllabus's HW1–4 and assessment dates are plans; Brightspace overrides them (course changes on the fly).
- `Coursework/_inbox/` has an unsorted homework `.docx`.
- Granola still not landing in `sessions/`.
- First US Signal monthly brief not written; grade tracker empty.

## Known issues

- Claude Code deny rules use absolute `//c/...` paths. Confirm in a fresh session that an edit under `wiki/raw/` is denied.
- Cursor reads skills via the pointer list in `ms-ai-core.mdc`, not native discovery.

## Current focus

Convert + ingest Weeks 3–6, reconcile the homework queue against the syllabus, then paper-tutor walkthroughs for the Week 5–7 readings.
