# Cheatsheet

## Paths

| What | Path |
|------|------|
| Command Center repo | `C:\Users\jockt\dev\ms_ai` |
| GitHub | https://github.com/jockthompsongit/ms_ai_cc |
| Vault (Dropbox) | `C:\Users\jockt\Dropbox\Vandy_MS_AI` |
| Coursework dump | `...\Vandy_MS_AI\Coursework\AI 5100 Week N\` |
| Granola / sessions | `...\Coursework\AI 5100 Week N\sessions\` |
| Inbox (unsorted drops) | `...\Coursework\_inbox\` |
| Wiki (Obsidian vault root) | `...\Vandy_MS_AI\Vandy Other\wiki\` |
| Converted raw | `...\Vandy Other\wiki\raw\courses\AI-5100\week-NN\` |
| Wiki index / log | `wiki\index.md`, `wiki\log.md` |
| Lectures | `wiki\courses\AI-5100\lectures\Week-NN.md` |
| Lecture notes (from VTT) | `wiki\courses\AI-5100\lecture-notes\week-NN\` |
| Paths module | `scripts\vault_paths.py` |

## Convert

```powershell
cd C:\Users\jockt\dev\ms_ai
.\.venv\Scripts\Activate.ps1
# first time only:
#   python -m venv .venv
#   pip install -r scripts\requirements.txt
python scripts\convert_content.py --week 3 --dry-run
python scripts\convert_content.py --week 3
# existing raw files are skipped; --force overwrites (raw is meant to be immutable)
```

Deps: `markitdown[pdf,pptx,docx]`. Granola `.md` files are copied into `raw/.../sessions/` with a `source_file` header.

## Dashboard (local)

```powershell
python scripts\dashboard.py --open
# http://127.0.0.1:8765 — optional: --port 8765, --print-once
```

Stdlib only. Reads `command-center/*.md` + vault capture paths + the Coursework inbox; markdown stays source of truth. Links open in Obsidian (vault files) or Cursor (repo files).

## Wiki graph (wiki-to-graph)

Upstream: [vanderbilt-ms-ai/wiki-to-graph](https://github.com/vanderbilt-ms-ai/wiki-to-graph). Sibling clone: `C:\Users\jockt\dev\wiki-to-graph`. Skills: `.claude/skills/wiki-to-graph/` (+ `wiki-graph-view`, `wiki-graph-maintain`, `wiki-author`); provenance in `wiki-to-graph/UPSTREAM.md`.

```powershell
python scripts\stage_wiki_graph.py
# stages concepts/sources/syntheses/courses (not raw/ or lecture-notes/) → build → opens graph-viewer.html
# python scripts\stage_wiki_graph.py --no-open --validate
```

Output: `C:\Users\jockt\dev\wiki-to-graph\build\vandy-ms-ai\` (vault wiki untouched). In chat: "turn my wiki into a graph" or "open the graph viewer".

## Lecture notes from recording

Skill: `.claude/skills/lecture-recording-to-lecture-notes/` (upstream original kept as `SKILL.upstream.md`). Ask to turn a Zoom VTT into notes. Reads `Coursework\AI 5100 Week N\`; writes `wiki\courses\AI-5100\lecture-notes\week-NN\<date>-<slug>\`. Then **Librarian** session merge into `Week-NN.md`. Do not commit `.mp4`.

## Paper tutor

Skill: `.claude/skills/ms-ai-paper-tutor/`. Say "Tutor: walk me through the ReAct paper" or "teach me Lost in the Middle". Teaches intuition → example → problem → breakthrough → mechanics → evidence → implications, citing the paper and wiki pages.

## Personas

| Say | Does |
|-----|------|
| Librarian | Ingest, session merge, index/log, lint |
| Tutor | Explain / quiz from wiki; papers via `ms-ai-paper-tutor` |
| Homework Coach | Rubric drafts, gap analysis |
| US Signal Advisor | Work apps + monthly brief |

Voice: `voices/house.md`. AI 5100 pack: `voices/professors/darrah.md` (Tutor / Homework only). Contract for all: `.claude/identity/operating.md`.

## Git

```powershell
git status
git add -A
git commit -m "message"
git push                    # only when asked
```

## Weekly loop

1. Dump Brightspace/async into `Coursework\AI 5100 Week N\`
2. Export Granola → `Coursework\...\sessions\granola-YYYYMMDD.md`
3. Convert → **Librarian** ingest (VTT → lecture-notes skill first if no Granola)
4. Study with **Tutor** (`ms-ai-paper-tutor` for papers); assignments with **Homework Coach**
5. Log US Signal applications; monthly brief end of month
