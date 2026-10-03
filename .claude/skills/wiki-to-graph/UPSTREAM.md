# Upstream

These four skills (`wiki-to-graph`, `wiki-author`, `wiki-graph-maintain`,
`wiki-graph-view`) are a local copy of the wiki-to-graph plugin, kept here so
they can be modified.

- Source: https://github.com/vanderbilt-ms-ai/wiki-to-graph
- Copied at commit: 6d334d07d50ca1cba815da7feb87178321a358ef (2026-09-27)
- License: CC BY-NC-SA 4.0 (`LICENSE.md`). Free for personal/academic use;
  commercial use requires a paid license from the author.

Local changes from upstream:
- `wiki-author/SKILL.md`, `wiki-graph-maintain/SKILL.md`: `docs/` links point to
  `../wiki-to-graph/docs/` (docs were moved inside this skill).

MS AI Command Center changes (ported from personal_assistant on 2026-10-03):
- All four `SKILL.md` files: a "Provenance" line and an `## MS AI vault overlay`
  section after the H1 (vault paths, Librarian owns ingest, rebuild via
  `scripts/stage_wiki_graph.py`, viewer port 8766).
- `scripts/` is the upstream copy for standalone skill use. The Command Center
  build runs the sibling clone at `C:\Users\jockt\dev\wiki-to-graph` instead.

To see what upstream has changed since the copy:
`gh api repos/vanderbilt-ms-ai/wiki-to-graph/compare/6d334d07...main`
