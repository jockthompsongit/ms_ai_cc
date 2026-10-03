# Context

Lean pointer for AI agents. Load docs by task size — do not read everything every session. `CLAUDE.md` (Claude Code) and `.cursor/rules/ms-ai-core.mdc` (Cursor) already load `AGENTS.md` and the working contract.

| Task | Read first | Add if needed |
|------|------------|---------------|
| Trivial | — | [QUICK_START](docs/QUICK_START.md) |
| Medium | [QUICK_START](docs/QUICK_START.md), [CURRENT_STATE](docs/CURRENT_STATE.md) | [DECISIONS](docs/DECISIONS.md) |
| Large / architecture | QUICK_START, CURRENT_STATE, DECISIONS | [ARCHITECTURE](docs/ARCHITECTURE.md) |
| Wiki ingest / homework | [AGENTS.md](AGENTS.md) + vault `wiki/index.md` | Persona rule in `.cursor/rules/` |
| Study / tutor | `.claude/skills/study/SKILL.md` | `command-center/study-progress.md` |
| Lecture recording → notes | `.claude/skills/lecture-recording-to-lecture-notes/SKILL.md` | Week folder under `Coursework/` |
| Wiki → knowledge graph | `.claude/skills/wiki-to-graph/SKILL.md` | `wiki-graph-view` / `wiki-graph-maintain`; `scripts/stage_wiki_graph.py` |
| Editing CLAUDE.md | `.claude/claude-md-guide.md` | — |

## Doc map

- [CLAUDE.md](CLAUDE.md) — standing rules + commands (loaded every Claude Code session)
- [.claude/identity/operating.md](.claude/identity/operating.md) — working contract for every persona
- [docs/QUICK_START.md](docs/QUICK_START.md) — setup and weekly loop
- [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md) — working / broken / focus
- [docs/DECISIONS.md](docs/DECISIONS.md) — architecture choices
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — layers and data flow
- [AGENTS.md](AGENTS.md) — Karpathy wiki schema + personas + paths
- [CHEATSHEET.md](CHEATSHEET.md) — paths and commands
- [command-center/HOME.md](command-center/HOME.md) — priorities this week
- [README.md](README.md) — human overview

## Authoritative paths

See the table in [AGENTS.md](AGENTS.md); scripts read `scripts/vault_paths.py`.

**Git remote:** `origin` → https://github.com/jockthompsongit/ms_ai_cc (`main`)
