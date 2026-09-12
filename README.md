# Vanderbilt MS AI — Command Center

Cursor-first ops hub for the Vanderbilt MS in Artificial Intelligence. Knowledge lives in the Obsidian vault (Dropbox); this repo holds agent schema, personas, convert scripts, and academic/work workflows.

| | |
|--|--|
| **Repo** | `C:\Users\jockt\dev\ms_ai` |
| **GitHub** | https://github.com/jockthompsongit/ms_ai_cc |
| **Vault** | `C:\Users\jockt\Dropbox\Vandy_MS_AI` |
| **Course** | AI 5100 — Foundations of Generative AI (Fall 2026 Module 1) |

## Status

Scaffolding is **complete** (2026-09-12): vault consolidated, Weeks 1–2 converted + ingested, personas live, `main` pushed to GitHub.

## Quick links

| Doc | Purpose |
|-----|---------|
| [docs/QUICK_START.md](docs/QUICK_START.md) | Setup + day-to-day |
| [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) | Working / gaps **now** |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Why this architecture |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers and flows |
| [AGENTS.md](AGENTS.md) | Wiki + tutor schema (agents read this) |
| [CHEATSHEET.md](CHEATSHEET.md) | Paths and commands |
| [command-center/HOME.md](command-center/HOME.md) | Weekly dashboard |
| [command-center/personas.md](command-center/personas.md) | Role agents |

## Personas

In Cursor chat, say **Librarian**, **Tutor**, **Homework Coach**, or **US Signal Advisor**. Always-on context: `.cursor/rules/ms-ai-core.mdc`.

## Weekly loop

1. Dump Brightspace/async → `vault/Content/AI 5100 Week N/`
2. Granola → `Content/.../sessions/granola-YYYYMMDD.md`
3. `python scripts/convert_content.py --week N`
4. **Librarian** ingest → wiki lecture page + `index.md` / `log.md`
5. **Tutor** / **Homework Coach** / **US Signal Advisor** as needed

## Vault layout (Obsidian root)

```
Vandy_MS_AI/
  Content/     # dumps + sessions/
  raw/         # converted markdown (immutable)
  wiki/        # LLM-maintained knowledge
  Templates/
  AGENTS.md
  _archive/    # pre-consolidate snapshots
```
