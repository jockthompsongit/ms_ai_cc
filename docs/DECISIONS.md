# Decisions

## 2026-09-05 — Command Center architecture

**Decision:** Cursor-first repo + one Obsidian vault in Dropbox; Karpathy LLM Wiki pattern; no web dashboard or embeddings in v1.

**Alternatives evaluated:**
- Custom web dashboard — deferred until phone/shared ops needed without Cursor
- Vector RAG / embeddings — deferred until ~100+ sources; prefer index.md navigation; later candidate: qmd
- Multi-agent frameworks (CrewAI/AutoGen) — rejected for v1; personas via Cursor rules instead
- markitdown — chosen for Content → markdown conversion (step 3)

**Vault:** `C:\Users\jockt\Dropbox\Vandy_MS_AI` (single root). Merge Knowledge + my-wiki; archive ms_ai_vault.

**Session capture:** Granola primary (live Tue); Brightspace async (Thu); Zoom transcript/link secondary. No Granola API in v1.

**Personas:** Librarian, Tutor, Homework Coach, US Signal Advisor as `.cursor/rules/*.mdc`.
