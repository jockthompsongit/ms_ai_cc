"""Markdown → Slack mrkdwn for model output."""
from __future__ import annotations

import re


def to_slack(text: str) -> str:
    """Convert common Markdown the models emit into Slack mrkdwn."""
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)  # **bold** -> *bold*
    text = re.sub(r"__(.+?)__", r"*\1*", text)  # __bold__ -> *bold*
    text = re.sub(r"^#{1,6}\s+(.+)$", r"*\1*", text, flags=re.MULTILINE)  # headings -> bold line
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"<\2|\1>", text)  # [label](url) -> <url|label>
    return re.sub(r"^(\s*)[-*]\s+", r"\1• ", text, flags=re.MULTILINE)  # list markers -> bullets
