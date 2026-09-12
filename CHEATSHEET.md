# Cheatsheet

## Paths

| What | Path |
|------|------|
| Command Center repo | `C:\Users\jockt\dev\ms_ai` |
| Obsidian vault | `C:\Users\jockt\Dropbox\Vandy_MS_AI` |
| Content dump | `...\Vandy_MS_AI\Content\` |
| Granola / sessions | `...\Content\AI 5100 Week N\sessions\` |
| Converted raw | `...\Vandy_MS_AI\raw\` (after step 2) |
| Wiki | `...\Vandy_MS_AI\wiki\` (after step 2) |

## Convert

```powershell
cd C:\Users\jockt\dev\ms_ai
.\.venv\Scripts\Activate.ps1
# first time: pip install -r scripts\requirements.txt
python scripts\convert_content.py --week 1          # or --week 2
python scripts\convert_content.py --week 1 --dry-run
```

Granola: `Content\AI 5100 Week N\sessions\granola-YYYYMMDD.md` → then convert (copies `.md` as-is).

## Personas (in Cursor chat)

| Say | Does |
|-----|------|
| Librarian | Ingest source, update wiki, lint |
| Tutor | Explain / quiz from wiki |
| Homework Coach | Rubric drafts, gap analysis |
| US Signal Advisor | Work apps + monthly brief |

## Git

```powershell
cd C:\Users\jockt\dev\ms_ai
git status
git add -A
git commit -m "message"
# git push -u origin main   # only when asked
```

## Weekly loop

1. Dump Brightspace/async into `Content\AI 5100 Week N\`
2. Export Granola → `Content\...\sessions\granola-YYYYMMDD.md`
3. Convert → ingest with Librarian
4. Study with Tutor; assignments with Homework Coach
5. Log US Signal applications; monthly brief end of month
