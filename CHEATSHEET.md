# Cheatsheet

## Paths

| What | Path |
|------|------|
| Command Center repo | `C:\Users\jockt\dev\ms_ai` |
| GitHub | https://github.com/jockthompsongit/ms_ai_cc |
| Obsidian vault | `C:\Users\jockt\Dropbox\Vandy_MS_AI` |
| Content dump | `...\Vandy_MS_AI\Content\` |
| Granola / sessions | `...\Content\AI 5100 Week N\sessions\` |
| Converted raw | `...\Vandy_MS_AI\raw\courses\AI-5100\week-NN\` |
| Wiki | `...\Vandy_MS_AI\wiki\` |
| Wiki index / log | `wiki\index.md`, `wiki\log.md` |
| Lectures | `wiki\courses\AI-5100\lectures\` |

## Convert

```powershell
cd C:\Users\jockt\dev\ms_ai
.\.venv\Scripts\Activate.ps1
# first time only:
#   python -m venv .venv
#   pip install -r scripts\requirements.txt
python scripts\convert_content.py --week 1
python scripts\convert_content.py --week 2
python scripts\convert_content.py --week 3 --dry-run
```

Deps: `markitdown[pdf,pptx,docx]`. Granola `.md` files are copied as-is into `raw/.../sessions/`.

## Dashboard (local)

```powershell
cd C:\Users\jockt\dev\ms_ai
.\.venv\Scripts\Activate.ps1
python scripts\dashboard.py --open
# http://127.0.0.1:8765 — optional: --port 8765
```

Stdlib only. Reads `command-center/*.md` + vault capture paths; markdown stays source of truth.

## Personas (Cursor chat)

| Say | Does |
|-----|------|
| Librarian | Ingest, session merge, index/log, lint |
| Tutor | Explain / quiz from wiki |
| Homework Coach | Rubric drafts, gap analysis |
| US Signal Advisor | Work apps + monthly brief |

## Git

```powershell
cd C:\Users\jockt\dev\ms_ai
git status
git add -A
git commit -m "message"
git push                    # only when asked
```

## Weekly loop

1. Dump Brightspace/async into `Content\AI 5100 Week N\`
2. Export Granola → `Content\...\sessions\granola-YYYYMMDD.md`
3. Convert → **Librarian** ingest
4. Study with **Tutor**; assignments with **Homework Coach**
5. Log US Signal applications; monthly brief end of month
