# Decisions

## 2026-09-05 — Command Center architecture

**Decision:** Cursor-first repo + one Obsidian vault in Dropbox; Karpathy LLM Wiki pattern; no web dashboard or embeddings in v1.

**Alternatives evaluated:**
- Custom web dashboard — deferred until phone/shared ops needed without Cursor
- Vector RAG / embeddings — deferred until ~100+ sources; prefer `wiki/index.md`; later candidate: [qmd](https://github.com/tobi/qmd)
- Multi-agent frameworks (CrewAI/AutoGen) — rejected for v1; personas via Cursor rules instead
- markitdown — chosen for Content → markdown (`[pdf,pptx,docx]`)

**Vault:** `C:\Users\jockt\Dropbox\Vandy_MS_AI` as single Obsidian root. Pre-consolidate trees archived under `_archive/2026-09-07-pre-consolidate/`.

**Session capture:** Granola primary (live Tue); Brightspace async (Thu); Zoom transcript/link secondary. No Granola API in v1.

**Personas:** Librarian, Tutor, Homework Coach, US Signal Advisor as `.cursor/rules/*.mdc` + always-on `ms-ai-core.mdc`.

## 2026-09-08 — Vault consolidate completed

**Decision:** Merge `Knowledge/` + `my-wiki/` into `wiki/` + `raw/`; retire nested vaults (`ms_ai_vault`, nested `.obsidian` under my-wiki).

## 2026-09-12 — Scaffolding complete + GitHub

**Decision:** Initial commit and push to `jockthompsongit/ms_ai_cc` on `main`. Wiki content stays in Dropbox (not git); Command Center markdown/scripts are versioned.

## 2026-09-12 — Local ops dashboard

**Decision:** Ship a **local-only** Command Center dashboard (`scripts/dashboard.py` → `http://127.0.0.1:8765`). Stdlib HTTP server; parses `command-center/*.md` + vault path probes. No auth, DB, Brightspace scrape, or new pip deps. Markdown remains source of truth.

**Alternatives evaluated:**
- StudentOS / MoodleOS / Learnora — rejected (full LMS stacks; too heavy)
- ZEN-OS / Obsidian Dataview — weaker for repo ops files; plugin-coupled
- Cursor Canvas — not a durable always-on ops UI

**Still deferred:** hosted/shared dashboard, embeddings/RAG, Granola API.
