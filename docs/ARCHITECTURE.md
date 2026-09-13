# Architecture

## Purpose

Support Vanderbilt MS AI academics (A-level mastery) and Chief of AI work at US Signal via a compounding markdown wiki — not per-query RAG.

## Layers

| Layer | Location | Role |
|-------|----------|------|
| Command Center | `C:\Users\jockt\dev\ms_ai` | Schema, personas, scripts, homework/US Signal ops, local dashboard |
| Content dump | `vault/Content/` | Immutable weekly dumps (PDF/PPTX/HTML/Granola) |
| Raw | `vault/raw/` | Converted markdown; agent reads, never edits |
| Wiki | `vault/wiki/` | LLM-maintained interlinked knowledge |
| Obsidian | vault root | Human IDE (graph, backlinks) |

```text
Content (+ sessions/Granola)
    → convert_content.py (markitdown)
    → raw/
    → Librarian ingest
    → wiki/ (index.md + log.md)
         ├→ Tutor / Homework Coach
         └→ US Signal Advisor → monthly brief
```

## Repo layout

```
ms_ai/
  AGENTS.md                 # wiki schema
  CONTEXT.md / README.md / CHEATSHEET.md
  docs/                     # QUICK_START, CURRENT_STATE, DECISIONS, ARCHITECTURE
  command-center/           # HOME, homework-queue, calendar, grades
  us-signal/                # BRIEF_TEMPLATE, applications-log, monthly/
  scripts/                  # convert_content.py, vault_paths.py, dashboard.py
  .cursor/rules/            # ms-ai-core + personas
```

### Local dashboard

`python scripts/dashboard.py` serves five panels at `http://127.0.0.1:8765`: this-week focus, homework queue, capture readiness (Content / sessions / raw / lecture wiki), calendar strip, quick links. Reads markdown + filesystem only; no write-back.

## Vault layout

```
Vandy_MS_AI/
  Content/AI 5100 Week N/sessions/
  raw/courses/AI-5100/week-NN/
  wiki/{index,log,concepts,courses,syntheses,us-signal}/
  Templates/
  _archive/
```

## Personas

Thin instruction overlays on shared `AGENTS.md`. One wiki, four roles. No multi-agent runtime.

## Deferred (v1)

Hosted/shared dashboard, embeddings/RAG, Granola API sync, Zoom video in vault/git — see [DECISIONS.md](DECISIONS.md). Local ops UI: `scripts/dashboard.py`.
