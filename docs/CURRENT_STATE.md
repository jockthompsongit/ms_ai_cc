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
