"""What needs work right now: feeds the dashboard and the Slack briefs.

Checks, per course week up to the current one:
  transcripts  2 expected (live + async); .vtt in the week folder or transcripts/
  notes        transcripts without lecture-notes output
  convert      week has Coursework files but no raw/ conversion
  lecture      wiki lectures/Week-NN.md missing
  readings     readings.json links not captured, or captured without a wiki summary
plus open homework rows from homework-queue.md.

  python scripts/pending_work.py            # markdown report
  python scripts/pending_work.py --json
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import date

from capture_links import dest_for, load_readings, slugify
from dashboard import parse_calendar, parse_pipe_table, read_text
from vault_paths import COMMAND_CENTER, COURSEWORK_DIR, RAW_DIR, WIKI_DIR

COURSE_PREFIX = "AI 5100"
EXPECTED_TRANSCRIPTS = 2
CONVERTIBLE = {".pdf", ".pptx", ".docx", ".html", ".htm", ".md", ".txt"}


@dataclass
class WeekStatus:
    week: int
    transcripts: list[str] = field(default_factory=list)
    transcripts_missing: int = 0
    notes_pending: list[str] = field(default_factory=list)
    unconverted: list[str] = field(default_factory=list)
    lecture_page: bool = False
    readings_uncaptured: list[str] = field(default_factory=list)
    readings_unsummarized: list[str] = field(default_factory=list)


def week_transcripts(week: int) -> list[str]:
    folder = COURSEWORK_DIR / f"{COURSE_PREFIX} Week {week}"
    if not folder.is_dir():
        return []
    return sorted(p.name for p in folder.rglob("*.vtt"))


def notes_written(week: int) -> set[str]:
    """Transcript filenames already turned into lecture notes (from note frontmatter)."""
    done: set[str] = set()
    notes_root = WIKI_DIR / "courses" / "AI-5100" / "lecture-notes" / f"week-{week:02d}"
    for md in notes_root.rglob("*.md") if notes_root.is_dir() else []:
        for line in read_text(md).splitlines()[:15]:
            if line.startswith("source_transcript:"):
                done.add(line.split(":", 1)[1].strip().strip('"'))
    return done


def unconverted_files(week: int) -> list[str]:
    src = COURSEWORK_DIR / f"{COURSE_PREFIX} Week {week}"
    raw = RAW_DIR / "courses" / "AI-5100" / f"week-{week:02d}"
    if not src.is_dir():
        return []
    from convert_content import slugify as file_slug

    missing = []
    for p in sorted(src.rglob("*")):
        if p.is_file() and p.suffix.lower() in CONVERTIBLE and not p.name.startswith("."):
            if "transcripts" in p.parts:
                continue
            stem = file_slug(p.name)
            if not any(raw.rglob(f"{stem}*.md")) if raw.is_dir() else True:
                missing.append(p.name)
    return missing


def summary_page(entry: dict):
    return WIKI_DIR / "sources" / (slugify(entry["title"]) + ".md")


def current_week(today: date) -> int:
    cal = parse_calendar(read_text(COMMAND_CENTER / "academic-calendar.md"), today)
    cur = next((r.week_num for r in cal if r.is_current and r.week_num), None)
    return cur or 1


def collect(today: date | None = None) -> dict:
    today = today or date.today()
    cur = current_week(today)
    readings = load_readings()
    weeks: list[WeekStatus] = []
    for w in range(1, cur + 1):
        st = WeekStatus(week=w)
        st.transcripts = week_transcripts(w)
        # The current week's sessions may not have happened yet; only count past weeks as missing
        if w < cur:
            st.transcripts_missing = max(0, EXPECTED_TRANSCRIPTS - len(st.transcripts))
        done = notes_written(w)
        st.notes_pending = [t for t in st.transcripts if t not in done]
        st.unconverted = unconverted_files(w)
        st.lecture_page = (WIKI_DIR / "courses" / "AI-5100" / "lectures" / f"Week-{w:02d}.md").is_file()
        for r in readings:
            if r["week"] != w:
                continue
            if r.get("capture", True) and not dest_for(r).exists():
                st.readings_uncaptured.append(r["title"])
            elif not summary_page(r).exists():
                st.readings_unsummarized.append(r["title"])
        weeks.append(st)

    headers, rows = parse_pipe_table(read_text(COMMAND_CENTER / "homework-queue.md"))
    homework = [
        dict(zip(headers, row))
        for row in rows
        if headers and dict(zip(headers, row)).get("Status", "").strip() in {"todo", "in_progress"}
    ]
    return {"today": today.isoformat(), "current_week": cur, "weeks": [asdict(w) for w in weeks], "homework": homework}


def to_markdown(data: dict) -> str:
    lines = [f"# Pending work - {data['today']} (current week {data['current_week']})", ""]
    for hw in data["homework"]:
        lines.append(f"- **Homework** {hw.get('ID', '')} {hw.get('Title', '')}: {hw.get('Status', '')}, due {hw.get('Due', '?')}")
    for w in data["weeks"]:
        items = []
        if w["transcripts_missing"]:
            items.append(f"{w['transcripts_missing']} transcript(s) missing (have {len(w['transcripts'])}/2)")
        if w["notes_pending"]:
            items.append(f"lecture notes to write from {', '.join(w['notes_pending'])}")
        if w["unconverted"]:
            items.append(f"{len(w['unconverted'])} file(s) to convert")
        if not w["lecture_page"]:
            items.append("no wiki lecture page")
        if w["readings_uncaptured"]:
            items.append(f"{len(w['readings_uncaptured'])} reading(s) to capture")
        if w["readings_unsummarized"]:
            items.append(f"{len(w['readings_unsummarized'])} reading(s) to summarize")
        if items:
            lines.append(f"- **Week {w['week']}:** " + "; ".join(items))
    if len(lines) == 2:
        lines.append("Nothing pending.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Report pending course work")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = collect()
    print(json.dumps(data, indent=2) if args.json else to_markdown(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
