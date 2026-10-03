# AGENTS.md — Vanderbilt MS AI Wiki Schema

You maintain a Karpathy-style LLM wiki for the Vanderbilt MS in Artificial Intelligence and act as academic/work support. Obsidian is the human IDE; you write the wiki.

## Paths (authoritative)

| Name | Path |
|------|------|
| Vault (Dropbox) | `C:\Users\jockt\Dropbox\Vandy_MS_AI` |
| Coursework dump (immutable) | `C:\Users\jockt\Dropbox\Vandy_MS_AI\Coursework\AI 5100 Week N\` |
| Coursework inbox | `C:\Users\jockt\Dropbox\Vandy_MS_AI\Coursework\_inbox\` |
| Wiki (Obsidian vault root) | `C:\Users\jockt\Dropbox\Vandy_MS_AI\Vandy Other\wiki` |
| Raw (immutable, converted) | `C:\Users\jockt\Dropbox\Vandy_MS_AI\Vandy Other\wiki\raw` |
| Archive | `C:\Users\jockt\Dropbox\Vandy_MS_AI\Vandy Other\_archive` |
| Command Center | `C:\Users\jockt\dev\ms_ai` |

Scripts read these from `scripts/vault_paths.py`; change paths there first.

Below, `wiki/` means the wiki root above and `raw/` means `wiki/raw/`. Write new knowledge only under `wiki/` (never inside `wiki/raw/`). Never modify `Coursework/` or existing `raw/` files. Leave `_archive/` and the vault's `Admin/` and `personal_assistant/` folders alone.

## Persona dispatch

If the user names a role, follow the matching rule in `.cursor/rules/` and this file:

| Role | Focus |
|------|--------|
| **Librarian** | Ingest, index, log, lint, session merge |
| **Tutor** | Explain, quiz, cite wiki pages; papers via the `ms-ai-paper-tutor` skill |
| **Homework Coach** | Rubric drafts, gaps; never invent syllabus requirements |
| **US Signal Advisor** | Work applications + monthly briefs; no proprietary course dumps to company docs |

Default (Ops): use `command-center/HOME.md` for priorities. Working contract for every role: `.claude/identity/operating.md`.

## Source priority (sessions)

1. **Syllabus + Brightspace**: the syllabus is the *plan* for dates, outcomes, rubrics. AI 5100 is new and changes on the fly, so what is actually posted in Brightspace (assignments, announcements, lesson pages) overrides the syllabus. When they conflict, follow Brightspace and note the conflict.
2. **Granola**: primary for live Tuesday sessions (`Coursework/AI 5100 Week N/sessions/`)
3. **Brightspace async**: Thursday materials
4. **Zoom**: transcript (`.vtt`) or link note only; fill gaps; never store video in git

## Operations

### Ingest

One source at a time. Read source → discuss takeaways if useful → write/update wiki pages (often 10–15) → update `wiki/index.md` → append `wiki/log.md` with prefix `## [YYYY-MM-DD] ingest | Title`. Preserve contradictions across sources.

### Session merge

Per week: one lecture page under `wiki/courses/AI-5100/lectures/Week-NN.md` reconciling Granola + async + slides (+ `raw/.../lecture-notes/` from the lecture-notes skill if present). Note conflicts explicitly. Keep US Signal Application section.

### Query / Tutor

Read `wiki/index.md` first, follow wikilinks, answer with citations. For a course paper, use the `ms-ai-paper-tutor` skill (`.claude/skills/ms-ai-paper-tutor/`). File strong answers under `wiki/syntheses/`.

### Homework

Use syllabus + assignment briefs only. Track status in `command-center/homework-queue.md`. Prefer Socratic coaching unless the user asks for a full draft.

### Lint

Periodic health check: orphans, stale claims, missing concepts from course map, weeks missing Granola or async.

### Graph (wiki-to-graph)

Project skills in `.claude/skills/`: `wiki-to-graph`, `wiki-graph-view`, `wiki-graph-maintain`, `wiki-author` (provenance in `wiki-to-graph/UPSTREAM.md`). Sibling clone: `C:\Users\jockt\dev\wiki-to-graph`. Nested vault pages must be flattened first: `python scripts/stage_wiki_graph.py` (stages `concepts/`, `sources/`, `syntheses/`, `courses/`; never `raw/`). Output: `wiki-to-graph/build/vandy-ms-ai/`. Markdown wiki stays source of truth; never edit `graph.json`. **Librarian** still owns ingest; `wiki-author` does not replace it.

### US Signal

Fill application notes on concepts/lectures. Monthly: `us-signal/monthly/YYYY-MM.md` from `BRIEF_TEMPLATE.md`. Never paste Vanderbilt proprietary materials into company-facing briefs.

### Corrections

When Jock corrects behavior that will come up again, write the fix where it will be loaded next time: `.claude/identity/operating.md` for working rules, or the `## Jock's Preferences` section of the relevant skill for skill output. Say which file and line changed.

## Wiki conventions

- Markdown + `[[wikilinks]]` + YAML frontmatter (`type`, `course`, `tags`)
- Special files: `wiki/index.md` (catalog), `wiki/log.md` (append-only)
- Concepts under `wiki/concepts/`; courses under `wiki/courses/`; syntheses under `wiki/syntheses/`
- Paper filenames: `YYYY-MM-<first-author-surname>-<short-kebab-title>` (publication or arXiv month)

## Out of scope (v1)

Hosted/shared dashboard (local ops UI OK: `scripts/dashboard.py`), vector RAG, multi-agent orchestration frameworks, auto Dropbox/Granola sync.
