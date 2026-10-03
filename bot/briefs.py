"""Scheduled Slack posts: weekday morning brief (with due-date nudges) and Sunday week-ahead."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import anthropic

from .agent import answer, status_digest
from .vault import Vault

DAILY = """Write my weekday morning brief for Slack. Today is {today}.

Use ONLY the material below (plus wiki lookups if useful). Shape:
*Morning brief: <Day Mon D>*
*Due soon*: anything due today or within 48 hours, as a nudge; "nothing posted" if none. Only
  homework-queue / course-map items count; syllabus-only items are "planned, not posted".
*Today*: sessions today per the calendar (Tue live 6:00–7:30 PM CT; Thu async).
*Needs work*: top 3–5 pending items, most urgent first, each with the action that clears it.
*Status age*: if the status snapshot is older than 36 hours or missing, say so in one line.
Never invent dates.

{digest}"""

WEEK_AHEAD = """Write my Sunday week-ahead for Slack. Today is {today}; the week starts tomorrow.

Use the material below and the wiki/tutor packs (search or list folders as needed). Shape:
*Week ahead: Week N, <theme> (<dates>)*
*Sessions*: live Tue 6:00–7:30 PM CT, async Thu
*Read before Tuesday*: papers and links for the week, each with a one-line why-it-matters
*Deadlines*: only homework-queue / course-map items; flag syllabus-only items as planned
*Clear this week*: top backlog items with the action for each
Never invent dates.

{digest}"""


def _post(slack_client, channel: str, text: str) -> None:
    slack_client.chat_postMessage(channel=channel, text=text, unfurl_links=False)


def run_brief(kind: str, client: anthropic.Anthropic, vault: Vault, slack_client, channel: str, tz: str) -> None:
    today = datetime.now(ZoneInfo(tz)).strftime("%A %B %d, %Y")
    template = DAILY if kind == "daily" else WEEK_AHEAD
    prompt = template.format(today=today, digest=status_digest(vault))
    try:
        result = answer(client, vault, [], prompt, route_hint="Scheduled brief writing task.")
        footer = f"\n\n_{result.tier.model} · ${result.cost:.3f}_"
        _post(slack_client, channel, result.text + footer)
    except anthropic.APIError as exc:
        _post(slack_client, channel, f"Couldn't write the {kind} brief: Claude API error ({type(exc).__name__}).")
