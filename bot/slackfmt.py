"""Markdown → Slack mrkdwn for model output, plus the model/cost footer."""
from __future__ import annotations

import re

MODEL_NAMES = {
    "claude-haiku-4-5": "Haiku 4.5",
    "claude-sonnet-5-5": "Sonnet 5.5",
    "claude-opus-5-5": "Opus 5.5",
    "claude-opus-4-8": "Opus 4.8",
}
# Matches the footer this module writes (and the older "_claude-x · $0.007_" form)
FOOTER_RE = re.compile(r"\n\n_(?:⚙ .*|claude-[\w.-]+ · \$[\d.]+)_\s*$")


def to_slack(text: str) -> str:
    """Convert common Markdown the models emit into Slack mrkdwn."""
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)  # **bold** -> *bold*
    text = re.sub(r"__(.+?)__", r"*\1*", text)  # __bold__ -> *bold*
    text = re.sub(r"^#{1,6}\s+(.+)$", r"*\1*", text, flags=re.MULTILINE)  # headings -> bold line
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"<\2|\1>", text)  # [label](url) -> <url|label>
    return re.sub(r"^(\s*)[-*]\s+", r"\1• ", text, flags=re.MULTILINE)  # list markers -> bullets


def _k(n: int) -> str:
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def footer(ans) -> str:
    """One italic line: model, total cost and its split, tokens, routing tier and reason."""
    served = MODEL_NAMES.get(ans.served_by, ans.served_by)
    if ans.served_by and ans.served_by != ans.tier.model:
        served += f" (fallback from {MODEL_NAMES.get(ans.tier.model, ans.tier.model)})"
    cached = f" ({_k(ans.cached_tokens)} cached)" if ans.cached_tokens else ""
    reason = ans.reason.replace("_", " ").strip().rstrip(".")
    if len(reason) > 70:
        reason = reason[:67].rstrip() + "…"
    return (
        f"\n\n_⚙ {served} · ${ans.total_cost:.4f} total"
        f" (answer ${ans.cost:.4f} + router ${ans.router_cost:.4f})"
        f" · {_k(ans.input_tokens + ans.cached_tokens)} in{cached} / {_k(ans.output_tokens)} out"
        f" · {ans.tier.name}: {reason}_"
    )


ERROR_FOOTER = "\n\n_⚙ no model answer (error) · see Render logs for any partial usage_"
