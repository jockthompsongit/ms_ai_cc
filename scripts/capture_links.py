"""Capture web readings from command-center/readings.json into raw/ markdown.

Public pages only (entries with "capture": true). Output:
  raw/courses/AI-5100/week-NN/links/<slug>.md
Existing captures are skipped unless --force (raw is immutable).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date

from vault_paths import COMMAND_CENTER, RAW_DIR

READINGS = COMMAND_CENTER / "readings.json"


def slugify(title: str) -> str:
    s = re.sub(r"[^\w\s-]+", "", title.lower())
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s[:80].rstrip("-") or "untitled"


def dest_for(entry: dict):
    return RAW_DIR / "courses" / "AI-5100" / f"week-{entry['week']:02d}" / "links" / (slugify(entry["title"]) + ".md")


def load_readings() -> list[dict]:
    return json.loads(READINGS.read_text(encoding="utf-8"))["readings"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture web readings into raw markdown")
    parser.add_argument("--week", type=int, help="Only this week")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Re-capture existing files")
    args = parser.parse_args()

    from markitdown import MarkItDown

    md = MarkItDown()
    ok = skipped = failed = 0
    for entry in load_readings():
        if args.week and entry["week"] != args.week:
            continue
        if not entry.get("capture", True):
            print(f"MANUAL week {entry['week']}: {entry['title']} ({entry['kind']})")
            skipped += 1
            continue
        dest = dest_for(entry)
        rel = dest.relative_to(RAW_DIR)
        if dest.exists() and not args.force:
            print(f"SKIP {rel} (exists)")
            skipped += 1
            continue
        if args.dry_run:
            print(f"DRY  {entry['url']} -> {rel}")
            continue
        try:
            text = (md.convert(entry["url"]).text_content or "").strip()
            if len(text) < 200:
                raise ValueError(f"only {len(text)} chars extracted (JS-rendered or blocked?)")
            header = (
                "---\n"
                f"title: \"{entry['title']}\"\n"
                f"source_url: {entry['url']}\n"
                f"week: {entry['week']}\n"
                f"kind: {entry['kind']}\n"
                f"captured: {date.today().isoformat()}\n"
                "---\n\n"
            )
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(header + text + "\n", encoding="utf-8")
            print(f"OK   {rel} ({len(text)} chars)")
            ok += 1
        except Exception as exc:  # noqa: BLE001 — report per-link and continue
            print(f"FAIL {entry['url']}: {exc}", file=sys.stderr)
            failed += 1
    print(f"Done. captured={ok} skipped={skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
