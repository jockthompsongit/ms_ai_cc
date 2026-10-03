"""MS AI Slack bot — Render background worker (Slack Socket Mode).

    python -m bot.app

Answers Jock's messages in #ms-ai (and DMs to the bot) in threads, and posts the
scheduled briefs. Only messages from SLACK_OWNER_USER_ID are acted on.
"""
from __future__ import annotations

import logging
import re

import anthropic
from apscheduler.schedulers.background import BackgroundScheduler
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .agent import answer
from .briefs import run_brief
from .config import Settings
from .slackfmt import ERROR_FOOTER, FOOTER_RE, footer, to_slack
from .vault import Vault

log = logging.getLogger("msai-bot")
MAX_HISTORY = 12


def thread_history(client, channel: str, thread_ts: str, current_ts: str, owner: str, bot_user: str) -> list[dict]:
    """Prior turns of a Slack thread as alternating user/assistant messages."""
    replies = client.conversations_replies(channel=channel, ts=thread_ts, limit=50).get("messages", [])
    turns: list[dict] = []
    for msg in replies:
        if msg.get("ts") == current_ts:
            continue
        if msg.get("user") == bot_user or msg.get("bot_id"):
            role = "assistant"
        elif msg.get("user") == owner:
            role = "user"
        else:
            continue  # never feed other people's text to the model
        text = FOOTER_RE.sub("", msg.get("text", "")).strip()
        if not text:
            continue
        if turns and turns[-1]["role"] == role:
            turns[-1]["content"] += "\n\n" + text
        else:
            turns.append({"role": role, "content": text})
    while turns and turns[0]["role"] != "user":
        turns.pop(0)
    if turns and turns[-1]["role"] == "user":
        turns.pop()  # the new question is appended by the caller
    return turns[-MAX_HISTORY:]


def create_app(settings: Settings) -> tuple[App, anthropic.Anthropic, Vault]:
    app = App(token=settings.slack_bot_token)
    # Org-level API keys must name a workspace on every request
    workspace_headers = {"anthropic-workspace-id": settings.anthropic_workspace_id} if settings.anthropic_workspace_id else None
    claude = anthropic.Anthropic(default_headers=workspace_headers)
    vault = Vault(settings.dropbox_app_key, settings.dropbox_app_secret, settings.dropbox_refresh_token, settings.vault_root)
    bot_user = app.client.auth_test()["user_id"]

    def handle(event: dict, client) -> None:
        if event.get("subtype") or event.get("bot_id"):
            return
        if event.get("user") != settings.owner_user_id:
            return
        channel = event.get("channel", "")
        if channel != settings.channel_id and event.get("channel_type") != "im":
            return
        text = re.sub(rf"<@{bot_user}>", "", event.get("text", "")).strip()
        if not text:
            return
        ts = event["ts"]
        thread_ts = event.get("thread_ts") or ts
        try:
            client.reactions_add(channel=channel, timestamp=ts, name="eyes")
        except Exception:  # noqa: BLE001 — reaction is cosmetic
            pass
        try:
            history = thread_history(client, channel, thread_ts, ts, settings.owner_user_id, bot_user) if event.get("thread_ts") else []
            result = answer(claude, vault, history, text)
            reply = to_slack(result.text) + footer(result)
            log.info(
                "answered ts=%s tier=%s model=%s reason=%s total=%.4f answer=%.4f router=%.4f in=%d cached=%d out=%d",
                ts, result.tier.name, result.served_by, result.reason, result.total_cost, result.cost,
                result.router_cost, result.input_tokens, result.cached_tokens, result.output_tokens,
            )
        except anthropic.RateLimitError:
            reply = "Claude is rate-limited right now; try again in a minute." + ERROR_FOOTER
        except anthropic.APIError as exc:
            log.exception("Claude API error")
            reply = f"Claude API error ({type(exc).__name__}); try again shortly." + ERROR_FOOTER
        except Exception as exc:  # noqa: BLE001 — never leave Jock without a reply
            log.exception("handler failed")
            reply = f"Something broke on my side ({type(exc).__name__}). Logged for review." + ERROR_FOOTER
        client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=reply, unfurl_links=False)

    @app.event("message")
    def on_message(event, client):
        handle(event, client)

    @app.event("app_mention")
    def on_mention(event, client):
        # Mentions in #ms-ai also arrive as message events; only handle mentions elsewhere
        if event.get("channel") != settings.channel_id:
            handle(event, client)

    return app, claude, vault


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    settings = Settings.from_env()
    app, claude, vault = create_app(settings)

    if settings.briefs_enabled:
        scheduler = BackgroundScheduler(timezone=settings.timezone)
        args = (claude, vault, app.client, settings.channel_id, settings.timezone)
        scheduler.add_job(run_brief, "cron", day_of_week="mon-fri", hour=7, minute=30, args=("daily", *args), id="daily-brief", misfire_grace_time=3600)
        scheduler.add_job(run_brief, "cron", day_of_week="sun", hour=18, minute=0, args=("week", *args), id="week-ahead", misfire_grace_time=3600)
        scheduler.start()
        log.info("briefs scheduled (%s)", settings.timezone)

    SocketModeHandler(app, settings.slack_app_token).start()


if __name__ == "__main__":
    main()
