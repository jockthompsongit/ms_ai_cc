# Architecture

## Purpose

Support Vanderbilt MS AI academics (A-level mastery) and Chief of AI work at US Signal via a compounding markdown wiki — not per-query RAG.

## Layers

| Layer | Location | Role |
|-------|----------|------|
| Command Center | `C:\Users\jockt\dev\ms_ai` | Schema, contract, personas, skills, scripts, homework/US Signal ops, local dashboard |
| Coursework dump | `vault/Coursework/` | Immutable weekly dumps (PDF/PPTX/HTML/VTT/Granola) + `_inbox/` |
| Wiki | `vault/Vandy Other/wiki/` | LLM-maintained interlinked knowledge; Obsidian vault root |
| Raw | `vault/Vandy Other/wiki/raw/` | Converted markdown; agent reads, never edits |
| Knowledge graph | sibling `wiki-to-graph` + `.claude/skills/wiki-to-graph/` | Typed graph derived from wiki (`stage_wiki_graph.py` → viewer) |
| Obsidian | `Vandy Other/wiki` | Human IDE (graph, backlinks) |

```text
Coursework (+ sessions/Granola, VTT)
    → convert_content.py (markitdown)   → wiki/raw/
    → lecture-notes skill (VTT)         → wiki/courses/AI-5100/lecture-notes/
    → Librarian ingest / session merge
    → wiki/ (index.md + log.md)
         ├→ Tutor (ms-ai-paper-tutor skill)
         ├→ Homework Coach
         ├→ wiki-to-graph (`stage_wiki_graph.py`) → typed viewer
         └→ US Signal Advisor → monthly brief
```

## Agent instruction layers

| Layer | File | Loaded |
|-------|------|--------|
| Standing rules + commands | `CLAUDE.md` | Every Claude Code session (`@`-includes the next two) |
| Wiki schema + paths | `AGENTS.md` | Always (Claude Code via CLAUDE.md; Cursor via `ms-ai-core.mdc`) |
| Working contract | `.claude/identity/operating.md` | Always; grows when Jock corrects behavior |
| Persona overlays | `.cursor/rules/*.mdc` | On request (by name) |
| Skills | `.claude/skills/*/SKILL.md` | On match; each has `## Jock's Preferences` and upstream provenance |
| Voice | `voices/house.md`, `voices/professors/*.md` | Tutor / Homework Coach |
| Guardrails | `.claude/settings.json` | Claude Code denies edits to Coursework, wiki/raw, _archive and reads of Admin |

## Repo layout

```
ms_ai/
  CLAUDE.md / AGENTS.md / CONTEXT.md / README.md / CHEATSHEET.md
  .claude/                  # settings.json, identity/operating.md, claude-md-guide.md, skills/
  .cursor/rules/            # ms-ai-core + personas (point at .claude/)
  docs/                     # QUICK_START, CURRENT_STATE, DECISIONS, ARCHITECTURE
  command-center/           # HOME, homework-queue, calendar, grades
  us-signal/                # BRIEF_TEMPLATE, applications-log, monthly/
  scripts/                  # convert_content.py, vault_paths.py, dashboard.py, stage_wiki_graph.py
  voices/                   # house + professor packs
```

### Local dashboard

`python scripts/dashboard.py` serves at `http://127.0.0.1:8765`: this-week focus, homework queue, capture readiness (Coursework / sessions / raw / lecture wiki), Coursework inbox, calendar strip, quick links (Obsidian / Cursor URIs). Reads markdown + filesystem only; no write-back.

## Vault layout

```
Vandy_MS_AI/
  Coursework/AI 5100 Week N/sessions/
  Coursework/_inbox/  Coursework/Homework/
  Vandy Other/wiki/{index,log,concepts,courses,sources,syntheses,us-signal}/
  Vandy Other/wiki/raw/courses/AI-5100/week-NN/
  Vandy Other/_archive/
  Admin/  personal_assistant/          # out of scope for this repo
```

## Personas

Thin instruction overlays on shared `AGENTS.md` + `operating.md`. One wiki, four roles. No multi-agent runtime.

## Deferred (v1)

Hosted/shared dashboard, embeddings/RAG, Granola API sync, Zoom video in vault/git — see [DECISIONS.md](DECISIONS.md).
