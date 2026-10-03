"""File Zoom transcript and Brightspace downloads into the right Coursework week.

Scans ~/Downloads and Coursework/_inbox for Zoom `.vtt` files named
`GMT<YYYYMMDD>-<HHMMSS>_Recording*.vtt`, then copies (never moves) each to
  Coursework/AI 5100 Week N/transcripts/<YYYY-MM-DD>-<live|async>.transcript.vtt

Week: the calendar week whose Mon-Fri range contains the recording date (Central
time); weekend recordings belong to the following week.
Live vs async: more than two distinct speakers = live class; otherwise async.
Files whose content already exists in the week folder are skipped.

Brightspace files: any file in those folders whose name matches an item in
Vandy Other/status/brightspace-snapshot.json (ignoring Chrome's " (1)" suffixes)
is copied to Coursework/AI 5100 Week N/<Brightspace file name>.

  python scripts/file_transcripts.py --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from dashboard import parse_calendar, read_text
import json

from vault_paths import COMMAND_CENTER, COURSEWORK_DIR, INBOX_DIR, WIKI_DIR

COURSE_PREFIX = "AI 5100"
NAME_RE = re.compile(r"GMT(\d{8})-(\d{6})")
SNAPSHOT = WIKI_DIR.parent / "status" / "brightspace-snapshot.json"
SPEAKER_RE = re.compile(r"^([^:\n]{2,60}):\s", re.MULTILINE)

try:
    from zoneinfo import ZoneInfo

    CENTRAL = ZoneInfo("America/Chicago")
except Exception:  # noqa: BLE001 — Windows without tzdata: CDT covers the Fall module
    CENTRAL = timezone(timedelta(hours=-5))


def recorded_at(path: Path) -> datetime | None:
    m = NAME_RE.search(path.name)
    if not m:
        return None
    utc = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    return utc.astimezone(CENTRAL)


def week_for(day: date) -> int | None:
    cal = parse_calendar(read_text(COMMAND_CENTER / "academic-calendar.md"), day)
    weeks = sorted((r for r in cal if r.week_num and r.start and r.end), key=lambda r: r.start)
    for r in weeks:
        if r.start <= day <= r.end:
            return r.week_num
    for r in weeks:  # weekend or gap: next week that starts after this day
        if r.start > day:
            return r.week_num
    return None


def session_kind(text: str) -> str:
    speakers = {s.strip() for s in SPEAKER_RE.findall(text) if "-->" not in s}
    return "live" if len(speakers) > 2 else "async"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def loose_name(name: str) -> str:
    """Match downloads to Brightspace names despite ' (1)' / ' - Copy (1)' suffixes and case."""
    p = Path(name)
    stem = re.sub(r"(\s*-\s*copy)?\s*\(\d+\)$", "", p.stem, flags=re.IGNORECASE)
    return re.sub(r"[^a-z0-9]+", "", stem.lower()) + p.suffix.lower()


def file_vtts(folder: Path, dry_run: bool) -> int:
    filed = 0
    for vtt in sorted(folder.glob("*.vtt")):
        when = recorded_at(vtt)
        if not when:
            print(f"SKIP {vtt.name}: not a Zoom GMT-named transcript")
            continue
        week = week_for(when.date())
        if not week:
            print(f"SKIP {vtt.name}: {when.date()} is outside the course calendar")
            continue
        week_dir = COURSEWORK_DIR / f"{COURSE_PREFIX} Week {week}"
        h = digest(vtt)
        dup = next((p for p in week_dir.rglob("*.vtt") if digest(p) == h), None) if week_dir.is_dir() else None
        if dup:
            print(f"SKIP {vtt.name}: already in Week {week} as {dup.relative_to(week_dir)}")
            continue
        kind = session_kind(vtt.read_text(encoding="utf-8", errors="replace"))
        dest = week_dir / "transcripts" / f"{when.date().isoformat()}-{kind}.transcript.vtt"
        if dest.exists():
            dest = dest.with_name(f"{when.date().isoformat()}-{kind}-{when:%H%M}.transcript.vtt")
        print(f"{'DRY ' if dry_run else 'FILE'} {vtt.name} -> Week {week}/transcripts/{dest.name} ({kind}, {when:%a %b %d %H:%M} CT)")
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(vtt, dest)
            filed += 1
    return filed


def file_brightspace(folder: Path, dry_run: bool) -> int:
    if not SNAPSHOT.is_file():
        return 0
    wanted: dict[str, tuple[int, str]] = {}
    for it in json.loads(SNAPSHOT.read_text(encoding="utf-8"))["items"]:
        if it.get("f"):
            wanted.setdefault(loose_name(it["f"]), (it["w"], it["f"]))
    filed = 0
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.suffix.lower() == ".vtt":
            continue
        match = wanted.get(loose_name(path.name))
        if not match:
            continue
        week, name = match
        week_dir = COURSEWORK_DIR / f"{COURSE_PREFIX} Week {week}" if week else COURSEWORK_DIR / "Course Information"
        dest = week_dir / name
        if dest.exists() or any(loose_name(p.name) == loose_name(name) for p in week_dir.glob("*") if p.is_file()):
            continue
        print(f"{'DRY ' if dry_run else 'FILE'} {path.name} -> {week_dir.name}/{name}")
        if not dry_run:
            week_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
            filed += 1
    return filed


def main() -> int:
    parser = argparse.ArgumentParser(description="File Zoom transcripts and Brightspace downloads into Coursework weeks")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--source", type=Path, action="append", help="Extra folder to scan")
    args = parser.parse_args()

    sources = [Path.home() / "Downloads", INBOX_DIR, *(args.source or [])]
    filed = 0
    for folder in sources:
        if folder.is_dir():
            filed += file_vtts(folder, args.dry_run) + file_brightspace(folder, args.dry_run)
    print(f"Done. filed={filed} dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
