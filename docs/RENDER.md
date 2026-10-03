# Render Slack bot — setup

An always-on Slack assistant for #ms-ai, running as a Render background worker. It answers
Jock's questions from the Dropbox study wiki and posts the morning brief and Sunday
week-ahead. Code: `bot/`. Blueprint: `render.yaml`.

```text
Slack #ms-ai ──Socket Mode──► Render worker (bot/app.py)
                                 ├─ router.py   Haiku 4.5 picks a tier: Haiku 4.5 / Sonnet 5.5 / Opus 5.5
                                 ├─ agent.py    tool runner, read-only tools
                                 │     ├─ Dropbox API (read-only): wiki, tutor-packs, status/pending.json
                                 │     └─ repo checkout: command-center/*.md (redeploys on push)
                                 └─ briefs.py   Mon–Fri 7:30 AM, Sun 6:00 PM (America/Chicago)

Desktop (when the app is open) ── routine "MS AI Brightspace sync"
   Brightspace check → course-map/readings → capture links → file transcripts
   → pending_work.py --publish → Dropbox status/pending.json → build tutor packs
```

## What it can and cannot do

- Reads only `Vandy Other/wiki`, `Vandy Other/tutor-packs`, `Vandy Other/status` (enforced in
  `bot/vault.py`; Dropbox token is read-only scope), plus the repo's `command-center` files.
- Acts only on messages from `SLACK_OWNER_USER_ID`, in #ms-ai or a DM to the bot.
- Never writes files, sends email, submits work, or messages anyone else. No Brightspace access
  (that needs Jock's browser, so it stays on the desktop).
- Every reply and brief ends with a footer: model that answered (and any safety fallback), total
  cost split into answer + router, tokens in/cached/out, and the routing tier with its reason, e.g.
  `⚙ Opus 5.5 · $0.0412 total (answer $0.0405 + router $0.0007) · 12.3k in (8.2k cached) / 940 out · deep: paper walkthrough`.
  Cost is computed from API usage at list prices (cache writes 1.25×, cache reads per model).
  Start a message with `!haiku`, `!sonnet` or `!opus` to force a tier.

## One-time setup

1. **Anthropic API key**: console.anthropic.com → API keys. Billed separately from the Claude
   Pro plan. Consider a monthly spend limit in the console. Create the key **inside a
   workspace** (Settings → Workspaces → the workspace → API Keys). An org-level key gets
   `400 ... not scoped to a workspace`; either replace it or set `ANTHROPIC_WORKSPACE_ID`
   (the workspace's ID, `wrkspc_…`) in Render.
2. **Dropbox (read-only)**: follow the docstring in `scripts/dropbox_auth.py`
   (create a Scoped, Full Dropbox app with only `files.metadata.read` + `files.content.read`),
   then run `python scripts/dropbox_auth.py` locally to print the refresh token.
3. **Slack app**: api.slack.com/apps → Create New App → From a manifest → paste
   `bot/slack-manifest.yaml`. Generate an app-level token (`connections:write`) →
   `SLACK_APP_TOKEN`. Install to the workspace (a Vanderbilt CCC MSAI admin may need to approve)
   → `SLACK_BOT_TOKEN`. In Slack: `/invite @MS AI Assistant` in #ms-ai.
4. **Render**: New → Blueprint → this repo. Enter the six secrets when prompted
   (`ANTHROPIC_API_KEY`, `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `DROPBOX_APP_KEY`,
   `DROPBOX_APP_SECRET`, `DROPBOX_REFRESH_TOKEN`). Worker plan is paid (Starter).
5. **Smoke test**: post "what's due?" in #ms-ai → expect 👀 then a threaded reply from
   *MS AI Assistant* ending in `claude-haiku-4-5`. Then "walk me through Lost in the Middle"
   → expect `claude-opus-5-5`.
6. **Cut over**: once replies work, tell Claude Code to disable the desktop routines
   `ms-ai-slack-inbox`, `ms-ai-daily-brief`, `ms-ai-week-ahead` (they would double-post).

## Operating notes

- Status freshness: the bot reads `status/pending.json`; the morning brief flags it if older than
  36 hours (desktop app closed).
- Ops-file edits (homework queue, calendar) reach the bot when pushed to `main` (auto-deploy).
- Logs: Render dashboard → msai-slack-bot → Logs (one line per answer with tier, reason, cost).
- Secrets live only in Render env vars. Rotate by regenerating in Slack/Dropbox/Anthropic and
  updating Render.
- Tests (offline, no API spend): `.venv\Scripts\python.exe -m pytest tests -q`
