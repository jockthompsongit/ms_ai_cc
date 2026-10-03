# Vanderbilt MS AI — Command Center

Claude Code–first (Cursor-compatible) ops hub for the Vanderbilt MS in Artificial Intelligence. Knowledge lives in the Obsidian vault (Dropbox); this repo holds agent schema, working contract, personas, skills, convert scripts, and academic/work workflows.

| | |
|--|--|
| **Repo** | `C:\Users\jockt\dev\ms_ai` |
| **GitHub** | https://github.com/jockthompsongit/ms_ai_cc |
| **Vault** | `C:\Users\jockt\Dropbox\Vandy_MS_AI` |
| **Course** | AI 5100 — Foundations of Generative AI (Fall 2026 Module 1) |

## Status

Scaffolding complete 2026-09-12. On 2026-10-03 the repo was updated for the vault relayout (`Coursework/` + `Vandy Other/wiki/`) and adopted patterns from the class-built `personal_assistant` template. See [docs/DECISIONS.md](docs/DECISIONS.md).

## Quick links

| Doc | Purpose |
|-----|---------|
| [CLAUDE.md](CLAUDE.md) | Standing rules + commands (Claude Code loads this) |
| [.claude/identity/operating.md](.claude/identity/operating.md) | Working contract for every persona |
| [docs/QUICK_START.md](docs/QUICK_START.md) | Setup + day-to-day |
| [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) | Working / gaps **now** |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Why this architecture |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers and flows |
| [AGENTS.md](AGENTS.md) | Wiki schema + paths (agents read this) |
| [CHEATSHEET.md](CHEATSHEET.md) | Paths and commands |
| [command-center/HOME.md](command-center/HOME.md) | Weekly dashboard (markdown) |
| Local UI | `python scripts/dashboard.py --open` → http://127.0.0.1:8765 |
| Wiki graph | `python scripts/stage_wiki_graph.py` (skills in `.claude/skills/wiki-to-graph/`) |
| [command-center/personas.md](command-center/personas.md) | Role agents |

## Personas and skills

Say **Librarian**, **Tutor**, **Homework Coach**, or **US Signal Advisor**. Skills live in `.claude/skills/`: `ms-ai-paper-tutor` (Tutor), `lecture-recording-to-lecture-notes`, and the wiki-to-graph family. Cursor's always-on context (`.cursor/rules/ms-ai-core.mdc`) points at them.

## Weekly loop

1. Dump Brightspace/async → `Coursework/AI 5100 Week N/`
2. Granola → `Coursework/.../sessions/granola-YYYYMMDD.md`
3. `python scripts/convert_content.py --week N`
4. **Librarian** ingest → wiki lecture page + `index.md` / `log.md`
5. **Tutor** (`ms-ai-paper-tutor`) / **Homework Coach** / **US Signal Advisor** as needed

## Vault layout

```
Vandy_MS_AI/
  Coursework/          # dumps + sessions/, _inbox/, Homework/ (immutable)
  Vandy Other/
    wiki/              # Obsidian vault root, LLM-maintained knowledge
      raw/             # converted markdown (immutable)
    _archive/          # pre-consolidate snapshots
    AGENTS.md          # pointer to this repo's AGENTS.md
```
