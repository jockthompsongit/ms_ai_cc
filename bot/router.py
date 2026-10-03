"""Semantic router: pick the cheapest model that can answer each message well.

A short Claude Haiku 4.5 call classifies the request into a tier:
  simple   -> claude-haiku-4-5   status, dates, lookups, short factual answers
  standard -> claude-sonnet-5-5  explanations, comparisons, briefs, quizzes
  deep     -> claude-opus-5-5    paper walkthroughs, multi-source synthesis, hard math
Jock can force a tier by starting a message with !haiku, !sonnet or !opus.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import anthropic
from pydantic import BaseModel

ROUTER_MODEL = "claude-haiku-4-5"


@dataclass(frozen=True)
class Tier:
    name: str
    model: str
    input_per_mtok: float
    cache_read_per_mtok: float
    output_per_mtok: float
    max_tokens: int
    effort: str | None  # None = model does not take output_config.effort
    fallbacks: bool


TIERS = {
    "simple": Tier("simple", "claude-haiku-4-5", 1.00, 0.10, 5.00, 4_000, None, False),
    "standard": Tier("standard", "claude-sonnet-5-5", 2.00, 0.20, 10.00, 16_000, "medium", True),
    "deep": Tier("deep", "claude-opus-5-5", 4.00, 0.20, 20.00, 16_000, "high", True),
}
OVERRIDES = {"!haiku": "simple", "!sonnet": "standard", "!opus": "deep"}

ROUTER_SYSTEM = """You route messages for a graduate student's AI-course study assistant to the
cheapest model tier that will answer them well. Classify the request only; do not answer it.

simple: status or logistics (what's due, what's pending, dates, where a file is), greetings,
  one-line definitions, yes/no lookups, "thanks".
standard: explain a concept, compare two ideas, quiz me, summarize a reading or a week,
  write the daily brief or week-ahead, follow-up questions in an ongoing explanation.
deep: walk through or teach a research paper, synthesize across several papers or weeks,
  math/derivations, critique an argument, exam-style practice needing careful grading,
  anything where a wrong or shallow answer would mislead the student.

When unsure between two tiers, pick the higher one."""


class Route(BaseModel):
    tier: Literal["simple", "standard", "deep"]
    reason: str


def strip_override(text: str) -> tuple[str | None, str]:
    head, _, rest = text.strip().partition(" ")
    tier = OVERRIDES.get(head.lower())
    return (tier, rest.strip()) if tier else (None, text)


@dataclass(frozen=True)
class Decision:
    tier: Tier
    reason: str
    cost: float = 0.0  # what the router call itself cost


def route(client: anthropic.Anthropic, text: str, context_hint: str = "") -> Decision:
    """Pick a tier. Falls back to 'standard' if the router call fails."""
    forced, _ = strip_override(text)
    if forced:
        return Decision(TIERS[forced], "forced by Jock")
    try:
        response = client.messages.parse(
            model=ROUTER_MODEL,
            max_tokens=200,
            system=ROUTER_SYSTEM,
            messages=[{"role": "user", "content": f"{context_hint}\n\nMessage:\n{text[:4000]}".strip()}],
            output_format=Route,
        )
        spent = cost_usd(TIERS["simple"], response.usage.input_tokens or 0, response.usage.output_tokens or 0)
        parsed = response.parsed_output
        if parsed is None:
            return Decision(TIERS["standard"], "router returned no decision", spent)
        return Decision(TIERS[parsed.tier], parsed.reason, spent)
    except anthropic.APIError as exc:
        return Decision(TIERS["standard"], f"router unavailable ({type(exc).__name__})")


def cost_usd(tier: Tier, input_tokens: int, output_tokens: int, cache_read: int = 0) -> float:
    return (
        (input_tokens * tier.input_per_mtok)
        + (cache_read * tier.cache_read_per_mtok)
        + (output_tokens * tier.output_per_mtok)
    ) / 1_000_000
