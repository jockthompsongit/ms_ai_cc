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

## 2026-09-13 — Adopt wiki-to-graph (sibling clone)

**Decision:** Clone [vanderbilt-ms-ai/wiki-to-graph](https://github.com/vanderbilt-ms-ai/wiki-to-graph) to `C:\Users\jockt\dev\wiki-to-graph`. Use it as the **typed knowledge-graph layer** derived from the Dropbox wiki — better than Obsidian’s untyped graph for validate / PageRank / contradicts / query / HTML viewer. Markdown wiki remains source of truth; do not replace Librarian ingest.

**Fit:** Purpose-built for Karpathy LLM wikis (`[[wikilinks]]` + typed sections). Stdlib-only. Course-adjacent (Darrah / Mangrove). Smoke test: flat staging of `wiki/concepts/*.md` → 17 concepts, related/contradicts/mentions edges, viewer OK.

**Caveat:** Builder only reads **top-level** `*.md` in the wiki folder. Nested vault layout (`concepts/`, `courses/`, …) yields only `index` + `log` unless you stage a flat copy. Helper: `python scripts/stage_wiki_graph.py` (stages `concepts`/`sources`/`syntheses`, builds, opens viewer). License: **CC BY-NC-SA 4.0** — fine for academic/personal use; commercial redistribution of the tool needs inquiry (`tim.darrah@mangrove.ai`).

**Alternatives:** Obsidian graph (already have; untyped); vector RAG (still deferred). **Not** merging into `ms_ai_cc` as a submodule yet — keep as sibling tool.

## 2026-09-27 — Lecture recording → notes skill

**Decision:** Vendor [lecture-recording-to-lecture-notes](https://github.com/jessespencersmith/skill-repo/tree/main/lecture-recording-to-lecture-notes) as a **project Cursor skill** at `.cursor/skills/lecture-recording-to-lecture-notes/`. Procedure, not a fifth persona.

**Adaptations:** Read `Content/`; write derived notes to `raw/courses/AI-5100/week-NN/lecture-notes/`; never mutate `Content/` or commit `.mp4`; Zoom remains gap-fill vs Granola; hand off to Librarian for wiki ingest.

**Deps:** skill scripts may pip-install `pymupdf`, `opencv-python`, `python-pptx` into `.venv` when used. Not added to convert `requirements.txt`.

## 2026-09-27 — Voice layer (house + professor packs)

**Decision:** Personality is a third axis, not a split of `AGENTS.md`. House register: [voices/house.md](../voices/house.md). Per-instructor packs under `voices/professors/` — first pack [darrah.md](../voices/professors/darrah.md) for AI 5100. Dispatch from Tutor and Homework Coach rules only. Librarian / US Signal Advisor stay on house voice.

**Constraint:** Packs are evidence from syllabus / briefs / lecture wiki. No invented rubric text, no mannerism imitation. Vault syllabus outcomes still a gap to paste when Dropbox is available.
