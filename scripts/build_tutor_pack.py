"""Build portable tutor packs for Claude / ChatGPT Projects (study while traveling).

Writes to the Dropbox vault so the files are reachable from a phone:
  Vandy Other/tutor-packs/
    tutor-instructions.md        paste into the Project's custom instructions
    week-NN-tutor.md             compact: lecture page, lecture notes, concepts, reading summaries
    week-NN-sources.md           full text: converted papers, slides, captured web readings
    course-to-date-tutor.md      every week's compact pack in one file

Upload the instructions + the week files to a Claude Project or ChatGPT Project.
Re-run after each Librarian ingest; files are regenerated in place.

  python scripts/build_tutor_pack.py --week 5
  python scripts/build_tutor_pack.py --all
"""
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from capture_links import load_readings, slugify
from dashboard import parse_calendar, read_text
from vault_paths import COMMAND_CENTER, RAW_DIR, REPO_ROOT, WIKI_DIR

OUT_DIR = WIKI_DIR.parent / "tutor-packs"
LECTURES = WIKI_DIR / "courses" / "AI-5100" / "lectures"
LECTURE_NOTES = WIKI_DIR / "courses" / "AI-5100" / "lecture-notes"
CONCEPTS = WIKI_DIR / "concepts"
SOURCES = WIKI_DIR / "sources"
WIKILINK = re.compile(r"\[\[([^\]|#]+)")
FRONTMATTER = re.compile(r"^---\n.*?\n---\n", re.DOTALL)

INSTRUCTIONS = """# AI 5100 travel tutor: instructions

You are Jock's tutor for Vanderbilt AI 5100 (Foundations of Generative AI). Jock is an
experienced business executive building technical depth: assume smart and busy, do
not assume math or CS background.

## Ground everything in the uploaded files
- The `week-NN-tutor.md` files are Jock's study wiki for each week; `week-NN-sources.md`
  files hold the full papers, slides and readings. Treat them as the source of truth.
- Cite where each claim comes from (file and section, or paper title). If the files do
  not cover something, say "the course materials don't cover this" before answering
  from general knowledge, and label that part *(not from course materials)*.
- When sources disagree, show both sides.

## How to teach
- Order: intuition → concrete example → the problem → the breakthrough → mechanics →
  evidence → why it matters today. Plain English first; define each technical term
  the first time it appears. Business analogies where they genuinely fit, never in
  place of the precise version. For equations, say what each symbol means.
- Keep answers to one phone screen unless Jock asks for more.

## Quizzing
- "Quiz me" = one question at a time; wait for the answer. No hints unless asked.
- Prefer why / apply / predict / spot-the-error / connect questions over trivia.
- Grade with Correct / Partly / Not yet in the first word, then what was right, the
  gap, and the precise version with its citation.
- "Explain it back" = Jock explains a topic; grade accuracy and gaps, then give a
  short model answer.

## Graded work
If a question looks like a homework or quiz item, say so and teach the concept rather
than writing a submittable answer.
"""


def body(path: Path) -> str:
    return FRONTMATTER.sub("", read_text(path), count=1).strip()


def week_theme(week: int) -> str:
    for row in parse_calendar(read_text(COMMAND_CENTER / "academic-calendar.md"), date.today()):
        if row.week_num == week:
            return f"{row.theme} ({row.dates})"
    return ""


def linked_concepts(texts: list[str]) -> list[Path]:
    names = {m.strip().lower() for t in texts for m in WIKILINK.findall(t)}
    pages = {p.stem.lower(): p for p in CONCEPTS.glob("*.md")} if CONCEPTS.is_dir() else {}
    return [pages[n] for n in sorted(names) if n in pages]


def section(title: str, text: str) -> str:
    return f"\n\n---\n\n## {title}\n\n{text}\n" if text.strip() else ""


def compact_pack(week: int) -> str:
    parts = [f"# AI 5100 Week {week}: {week_theme(week)}"]
    texts = []
    lecture = LECTURES / f"Week-{week:02d}.md"
    if lecture.is_file():
        texts.append(body(lecture))
        parts.append(section(f"Lecture page (Week {week})", texts[-1]))
    notes_dir = LECTURE_NOTES / f"week-{week:02d}"
    for md in sorted(notes_dir.rglob("*.md")) if notes_dir.is_dir() else []:
        texts.append(body(md))
        parts.append(section(f"Lecture notes: {md.stem}", texts[-1]))
    for r in (r for r in load_readings() if r["week"] == week):
        page = SOURCES / (slugify(r["title"]) + ".md")
        if page.is_file():
            texts.append(body(page))
            parts.append(section(f"Reading summary: {r['title']}", texts[-1] + f"\n\nURL: {r['url']}"))
    for concept in linked_concepts(texts):
        parts.append(section(f"Concept: {concept.stem}", body(concept)))
    if len(parts) == 1:
        parts.append("\n\n_No wiki pages for this week yet. Use the sources pack._\n")
    return "".join(parts)


def sources_pack(week: int, max_chars: int) -> str:
    raw_week = RAW_DIR / "courses" / "AI-5100" / f"week-{week:02d}"
    parts = [f"# AI 5100 Week {week} sources: {week_theme(week)}"]
    seen: set[str] = set()
    for md in sorted(raw_week.rglob("*.md")) if raw_week.is_dir() else []:
        if md.stem.startswith("table-of-contents"):
            continue
        text = body(md)
        # Same paper is often posted twice under different names; key on the opening text
        key = re.sub(r"\s+", " ", text[:2000]).strip().lower()
        if key in seen:
            continue
        seen.add(key)
        if len(text) > max_chars:
            note = f"_[Truncated at {max_chars:,} of {len(text):,} chars. Full text: {md.name} in the vault.]_"
            text = text[:max_chars] + "\n\n" + note
        parts.append(section(f"Source: {md.relative_to(raw_week).as_posix()}", text))
    return "".join(parts)


def write(name: str, text: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    path.write_text(text, encoding="utf-8")
    print(f"WROTE {path.name} ({len(text):,} chars)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build tutor packs for Claude/ChatGPT Projects")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--week", type=int, action="append", help="Week number (repeatable)")
    group.add_argument("--all", action="store_true", help="Every week with content, plus course-to-date")
    parser.add_argument("--max-chars", type=int, default=80_000, help="Cap per source in sources packs")
    args = parser.parse_args()

    weeks = args.week or sorted(
        int(p.name.split("-")[1]) for p in (RAW_DIR / "courses" / "AI-5100").glob("week-*") if p.is_dir()
    )
    write("tutor-instructions.md", INSTRUCTIONS)
    compact = {}
    for w in weeks:
        compact[w] = compact_pack(w)
        write(f"week-{w:02d}-tutor.md", compact[w])
        write(f"week-{w:02d}-sources.md", sources_pack(w, args.max_chars))
    if args.all:
        write("course-to-date-tutor.md", "\n\n".join(compact[w] for w in sorted(compact)))
    print(f"Packs in {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
