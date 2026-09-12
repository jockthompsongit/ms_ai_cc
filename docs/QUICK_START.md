# Quick start

Vanderbilt MS AI Command Center: Cursor + Obsidian. No web app, no embeddings DB.

## One-time setup

1. Open `C:\Users\jockt\dev\ms_ai` in Cursor
2. Open Obsidian vault root: `C:\Users\jockt\Dropbox\Vandy_MS_AI` (not a nested folder)
3. Python env:

```powershell
cd C:\Users\jockt\dev\ms_ai
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r scripts\requirements.txt
```

4. Skim [AGENTS.md](../AGENTS.md) and [command-center/HOME.md](../command-center/HOME.md)

## Day-to-day

| Step | Action |
|------|--------|
| 1 | Dump materials → `Content\AI 5100 Week N\` |
| 2 | Granola → `Content\...\sessions\granola-YYYYMMDD.md` |
| 3 | `python scripts\convert_content.py --week N` |
| 4 | Cursor: **Librarian** — ingest / session merge |
| 5 | **Tutor** / **Homework Coach** / **US Signal Advisor** as needed |

## Already done (as of 2026-09-12)

- Weeks 1–2 converted under `raw/courses/AI-5100/`
- Lecture pages: `wiki/courses/AI-5100/lectures/Week-01.md`, `Week-02.md`
- Repo on GitHub: `jockthompsongit/ms_ai_cc`

## More detail

- [CURRENT_STATE.md](CURRENT_STATE.md) — gaps and focus
- [CHEATSHEET.md](../CHEATSHEET.md) — all commands
- [ARCHITECTURE.md](ARCHITECTURE.md) — system diagram
