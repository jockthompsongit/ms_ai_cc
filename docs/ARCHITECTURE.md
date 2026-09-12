# Architecture

## Layers

1. **Command Center** (`C:\Users\jockt\dev\ms_ai`) — agent schema, personas, scripts, academic/work ops markdown
2. **Content dump** (`Dropbox\...\Content\`) — immutable weekly dumps (PDFs, PPTX, HTML, Granola)
3. **raw/** — converted markdown sources (agent reads, never edits) — after vault consolidate
4. **wiki/** — LLM-maintained interlinked knowledge — after vault consolidate
5. **Obsidian** — human IDE over the vault root

## Flows

```text
Content (+ Granola/sessions) → convert → raw → Librarian ingest → wiki
wiki → Tutor / Homework Coach
wiki + applications-log → US Signal Advisor → monthly brief
```

## Personas

Thin instruction overlays on shared `AGENTS.md`. One wiki, four roles. No orchestrator.

## Deferred

Web dashboard, embeddings/RAG, Granola API, Zoom video in vault — see DECISIONS.md.
