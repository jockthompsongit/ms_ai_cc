"""What needs work right now: feeds the dashboard and the Slack briefs.

Built on the capture ledger (scripts/capture_ledger.py), which tracks every Brightspace item
from posted to integrated, plus open homework from homework-queue.md and missing weekly
lecture pages.

  python scripts/pending_work.py            # markdown report
  python scripts/pending_work.py --json
  python scripts/pending_work.py --publish  # also write Vandy Other/status/pending.json for the bot
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date, datetime

import capture_ledger
from dashboard import parse_calendar, parse_pipe_table, read_text
from vault_paths import COMMAND_CENTER, WIKI_DIR

# Read by the Render Slack bot through the Dropbox API
STATUS_FILE = WIKI_DIR.parent / "status" / "pending.json"
LECTURES = WIKI_DIR / "courses" / "AI-5100" / "lectures"
# Next-action buckets, most urgent first
BUCKETS = [
    ("download", "posted", "Needs you: download (say \"download pending\" in a desktop session)"),
    ("capture", "posted", "Capture links"),
    ("convert", "acquired", "Convert"),
    ("notes", "converted", "Lecture notes from transcripts"),
    ("summarize", "converted", "Summaries to write"),
    ("integrate", "digested", "Add to lecture pages"),
    ("manual", "manual", "Manual"),
]


def current_week(today: date) -> int:
    cal = parse_calendar(read_text(COMMAND_CENTER / "academic-calendar.md"), today)
    return next((r.week_num for r in cal if r.is_current and r.week_num), None) or 1


def bucket_of(item: dict) -> str | None:
    action = item["next_action"].lower()
    if item["stage"] == "manual":
        return "manual"
    if item["stage"] == "tracked" or not action:
        return None
    if action.startswith("download"):
        return "download"
    if action.startswith("capture"):
        return "capture"
    if action.startswith("convert"):
        return "convert"
    if action.startswith("lecture notes"):
        return "notes"
    if action.startswith("summarize"):
        return "summarize"
    return "integrate"


def collect(today: date | None = None) -> dict:
    today = today or date.today()
    cur = current_week(today)
    ledger = capture_ledger.build()

    actions: dict[str, list[str]] = defaultdict(list)
    for it in ledger["items"]:
        b = bucket_of(it)
        if b:
            actions[b].append(f"W{it['week']} {it['title']}: {it['next_action']}")

    missing_pages = [
        w for w in range(1, cur + 1) if not (LECTURES / f"Week-{w:02d}.md").is_file()
    ]
    headers, rows = parse_pipe_table(read_text(COMMAND_CENTER / "homework-queue.md"))
    homework = [
        dict(zip(headers, row))
        for row in rows
        if headers and dict(zip(headers, row)).get("Status", "").strip() in {"todo", "in_progress"}
    ]
    return {
        "today": today.isoformat(),
        "current_week": cur,
        "homework": homework,
        "weeks": ledger["weeks"],
        "actions": dict(actions),
        "missing_lecture_pages": missing_pages,
        "snapshot_taken_at": ledger["snapshot_taken_at"],
    }


def to_markdown(data: dict) -> str:
    lines = [f"# Pending work - {data['today']} (current week {data['current_week']})", ""]
    for hw in data["homework"]:
        lines.append(f"- *Homework* {hw.get('ID', '')} {hw.get('Title', '')}: {hw.get('Status', '')}, due {hw.get('Due', '?')}")
    progress = ", ".join(
        f"W{wk} {s['progress']}{' done' if s['complete'] else ''}" for wk, s in data["weeks"].items() if wk != "0"
    )
    lines += ["", f"*Capture progress (integrated/total):* {progress}",
              f"_Brightspace snapshot: {data['snapshot_taken_at']}_"]
    if data["missing_lecture_pages"]:
        lines.append("*No lecture page yet:* " + ", ".join(f"Week {w}" for w in data["missing_lecture_pages"]))
    for key, _, label in BUCKETS:
        items = data["actions"].get(key, [])
        if items:
            lines += ["", f"*{label}* ({len(items)})"]
            lines += [f"- {line}" for line in items[:12]]
            if len(items) > 12:
                lines.append(f"- ...and {len(items) - 12} more (see Vandy Other/status/capture-ledger.md)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Report pending course work")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--publish",
        action="store_true",
        help=f"Also write the snapshot (JSON + markdown) to {STATUS_FILE} for the Render Slack bot",
    )
    args = parser.parse_args()
    data = collect()
    print(json.dumps(data, indent=2) if args.json else to_markdown(data))
    if args.publish:
        data["generated_at"] = datetime.now().astimezone().isoformat(timespec="minutes")
        data["markdown"] = to_markdown(data)
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATUS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
        # Keep the ledger files current alongside the status snapshot
        ledger = capture_ledger.build()
        (STATUS_FILE.parent / "capture-ledger.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")
        (STATUS_FILE.parent / "capture-ledger.md").write_text(capture_ledger.to_markdown(ledger) + "\n", encoding="utf-8")
        print(f"Published {STATUS_FILE} (+ capture-ledger.json/.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
