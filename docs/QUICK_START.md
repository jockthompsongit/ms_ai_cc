# Quick start

Vanderbilt MS AI Command Center: Claude Code (primary) or Cursor + Obsidian. Local ops dashboard optional; no hosted web app, no embeddings DB.

## One-time setup

1. Open `C:\Users\jockt\dev\ms_ai` in Claude Code or Cursor. Claude Code loads `CLAUDE.md` (which pulls in `AGENTS.md` and `.claude/identity/operating.md`).
2. Open Obsidian on the wiki folder: `C:\Users\jockt\Dropbox\Vandy_MS_AI\Vandy Other\wiki`
3. Python env:

```powershell
cd C:\Users\jockt\dev\ms_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r scripts\requirements.txt
```

4. Skim [AGENTS.md](../AGENTS.md) and [command-center/HOME.md](../command-center/HOME.md)
5. Optional dashboard: `python scripts\dashboard.py --open` → http://127.0.0.1:8765

## Day-to-day

| Step | Action |
|------|--------|
| 1 | Dump materials → `Coursework\AI 5100 Week N\` |
| 2 | Granola → `Coursework\...\sessions\granola-YYYYMMDD.md` |
| 3 | `python scripts\convert_content.py --week N --dry-run`, then without `--dry-run` |
| 4 | No Granola? Turn the Zoom VTT into notes (lecture-notes skill) |
| 5 | **Librarian**: ingest / session merge |
| 6 | **Tutor** (`ms-ai-paper-tutor` skill) / **Homework Coach** / **US Signal Advisor** as needed |
| — | Ops glance: `python scripts\dashboard.py --open` |
| — | Wiki graph: `python scripts\stage_wiki_graph.py` (or say **turn my wiki into a graph**) |

## More detail

- [CURRENT_STATE.md](CURRENT_STATE.md) — gaps and focus
- [CHEATSHEET.md](../CHEATSHEET.md) — all commands
- [ARCHITECTURE.md](ARCHITECTURE.md) — system diagram
