"""Capture ledger: every Brightspace item, tracked from posted to integrated in the wiki.

Inputs
  Vandy Other/status/brightspace-snapshot.json   written by the sync routine (read-only Brightspace read)
  command-center/readings.json                   public reading links (synced from the snapshot here)
  Coursework/, wiki/raw/, wiki/sources/, wiki/courses/AI-5100/{lectures,lecture-notes}/

Stages (each implies the previous)
  posted      listed in Brightspace
  acquired    file in Coursework / link captured / transcript downloaded
  converted   markdown exists in wiki/raw (transcripts and links count once acquired)
  digested    reading summary in wiki/sources/, or lecture notes for a transcript
  integrated  referenced from that week's lecture page wiki/courses/AI-5100/lectures/Week-NN.md
Items that are not content (quizzes, surveys, Brightspace pages) are "tracked"; links that need a
Vanderbilt login are "manual".

Outputs (private, Dropbox): Vandy Other/status/capture-ledger.{json,md}

  python scripts/capture_ledger.py            # print summary, write ledger
  python scripts/capture_ledger.py --week 5   # one week's detail
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from capture_links import dest_for, slugify as title_slug
from convert_content import slugify as file_slug
from file_transcripts import session_kind
from vault_paths import COMMAND_CENTER, COURSEWORK_DIR, RAW_DIR, WIKI_DIR

STATUS_DIR = WIKI_DIR.parent / "status"
SNAPSHOT = STATUS_DIR / "brightspace-snapshot.json"
READINGS = COMMAND_CENTER / "readings.json"
LECTURES = WIKI_DIR / "courses" / "AI-5100" / "lectures"
LECTURE_NOTES = WIKI_DIR / "courses" / "AI-5100" / "lecture-notes"
SOURCES = WIKI_DIR / "sources"
COURSE_PREFIX = "AI 5100"
STAGES = ["posted", "acquired", "converted", "digested", "integrated"]
NOT_CONTENT = {"quiz", "survey", "assignment", "brightspace"}
PRIVATE_HOSTS = ("zoom.us", "box.com", "brightspace", "vanderbilt.edu")


@dataclass
class Item:
    id: int
    week: int
    title: str
    kind: str
    stage: str
    next_action: str = ""
    evidence: dict = field(default_factory=dict)


# --- filesystem lookups ------------------------------------------------------------

def norm_name(name: str) -> str:
    """Compare file names loosely: drop ' - Copy (1)', case and punctuation."""
    stem = Path(name).stem
    stem = re.sub(r"\s*-\s*copy\s*\(\d+\)", "", stem, flags=re.IGNORECASE)
    return re.sub(r"[^a-z0-9]+", "", stem.lower())


@lru_cache(maxsize=None)
def coursework_index() -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    if COURSEWORK_DIR.is_dir():
        for p in COURSEWORK_DIR.rglob("*"):
            if p.is_file():
                index.setdefault(norm_name(p.name), []).append(p)
    return index


def week_dir(week: int) -> Path:
    return COURSEWORK_DIR / f"{COURSE_PREFIX} Week {week}"


def raw_week(week: int) -> Path:
    return RAW_DIR / "courses" / "AI-5100" / f"week-{week:02d}"


def find_local(name: str, week: int) -> Path | None:
    hits = coursework_index().get(norm_name(name), [])
    in_week = [p for p in hits if week_dir(week) in p.parents]
    return (in_week or hits or [None])[0]


def find_raw(local: Path) -> Path | None:
    slug = file_slug(local.name)
    for p in RAW_DIR.rglob(f"{slug}*.md") if RAW_DIR.is_dir() else []:
        return p
    return None


@lru_cache(maxsize=None)
def lecture_text(week: int) -> str:
    page = LECTURES / f"Week-{week:02d}.md"
    return page.read_text(encoding="utf-8", errors="replace").lower() if page.is_file() else ""


def mentioned_in_lecture(week: int, *needles: str) -> bool:
    text = lecture_text(week)
    return bool(text) and any(n and n.lower() in text for n in needles)


@lru_cache(maxsize=None)
def notes_by_transcript() -> dict[str, Path]:
    """Map source_transcript filename -> lecture-notes markdown (from note frontmatter)."""
    found: dict[str, Path] = {}
    for md in LECTURE_NOTES.rglob("*.md") if LECTURE_NOTES.is_dir() else []:
        for line in md.read_text(encoding="utf-8", errors="replace").splitlines()[:20]:
            if line.startswith("source_transcript:"):
                found[line.split(":", 1)[1].strip().strip('"').lower()] = md
    return found


def week_transcripts(week: int) -> list[tuple[Path, str]]:
    """(.vtt path, live|async) in a week folder; filed names carry the kind, else infer it."""
    out = []
    folder = week_dir(week)
    for p in sorted(folder.rglob("*.vtt")) if folder.is_dir() else []:
        m = re.search(r"-(live|async)\b", p.name)
        kind = m.group(1) if m else session_kind(p.read_text(encoding="utf-8", errors="replace"))
        out.append((p, kind))
    return out


def summary_page(slug: str) -> Path:
    return SOURCES / f"{slug}.md"


# --- per-kind evaluation -----------------------------------------------------------

def eval_file(it: dict) -> Item:
    item = Item(it["id"], it["w"], it["t"], it["k"], "posted")
    local = find_local(it["f"], it["w"])
    if not local:
        item.next_action = f"download `{it['f']}` from Brightspace (say \"download pending\")"
        return item
    item.stage, item.evidence["file"] = "acquired", str(local.relative_to(COURSEWORK_DIR))
    raw = find_raw(local)
    if not raw:
        item.next_action = f"convert: convert_content.py --week {it['w']}"
        return item
    item.stage, item.evidence["raw"] = "converted", str(raw.relative_to(WIKI_DIR))
    stem = Path(it["f"]).stem
    if it["k"] == "paper":
        page = summary_page(stem)
        if not page.is_file():
            item.next_action = f"summarize paper -> wiki/sources/{stem}.md"
            return item
        item.evidence["summary"] = str(page.relative_to(WIKI_DIR))
    elif it["k"] == "transcript":
        notes = notes_by_transcript().get(it["f"].lower())
        if not notes:
            item.next_action = f"lecture notes from `{it['f']}` (converted text in raw)"
            return item
        item.evidence["notes"] = str(notes.relative_to(WIKI_DIR))
    item.stage = "digested"
    if it["w"] == 0:  # course-information items have no lecture page; converted is the end state
        item.stage, item.next_action = "integrated", ""
        return item
    needles = (stem, file_slug(it["f"]), it["t"][:40])
    if mentioned_in_lecture(it["w"], *needles):
        item.stage, item.next_action = "integrated", ""
    else:
        item.next_action = f"reference in lectures/Week-{it['w']:02d}.md"
    return item


def eval_link(it: dict, readings: dict[str, dict]) -> Item:
    item = Item(it["id"], it["w"], it["t"], "link", "posted")
    entry = readings.get(norm_url(it["u"]), {"week": it["w"], "title": it["t"], "url": it["u"], "capture": True})
    slug = title_slug(entry["title"])
    item.title = entry["title"]
    if entry.get("capture", True):
        dest = dest_for(entry)
        if not dest.exists():
            item.next_action = "capture: capture_links.py"
            return item
        item.evidence["raw"] = str(dest.relative_to(WIKI_DIR))
    else:
        item.evidence["note"] = f"{entry.get('kind', 'reference')} (not captured; summarize from the page)"
    item.stage = "converted"
    page = summary_page(slug)
    if not page.is_file():
        item.next_action = f"summarize reading -> wiki/sources/{slug}.md"
        return item
    item.stage, item.evidence["summary"] = "digested", str(page.relative_to(WIKI_DIR))
    if mentioned_in_lecture(it["w"], slug, entry["title"][:40]):
        item.stage, item.next_action = "integrated", ""
    else:
        item.next_action = f"reference in lectures/Week-{it['w']:02d}.md"
    return item


def eval_recording(it: dict, snapshot_items: list[dict]) -> Item:
    item = Item(it["id"], it["w"], it["t"], f"recording-{it['s']}", "posted")
    vtts = [p for p, kind in week_transcripts(it["w"]) if kind == it["s"]]
    # Brightspace sometimes posts the async transcript itself (e.g. Week 6 session-transcript.pdf)
    # ...but it only counts once that file has been downloaded
    posted_text = [
        s for s in snapshot_items
        if s["w"] == it["w"] and s["k"] == "transcript" and it["s"] in s["t"].lower() and find_local(s["f"], s["w"])
    ]
    if not vtts and not posted_text:
        item.next_action = f"download the {it['s']} Zoom transcript (say \"download pending\")"
        return item
    source = vtts[0].name if vtts else posted_text[0]["f"]
    item.stage, item.evidence["transcript"] = "converted", source
    notes = notes_by_transcript().get(source.lower())
    if not notes:
        item.next_action = f"lecture notes from `{source}`"
        return item
    item.stage, item.evidence["notes"] = "digested", str(notes.relative_to(WIKI_DIR))
    if mentioned_in_lecture(it["w"], notes.stem, notes.parent.name):
        item.stage, item.next_action = "integrated", ""
    else:
        item.next_action = f"merge lecture notes into lectures/Week-{it['w']:02d}.md"
    return item


# --- readings sync -----------------------------------------------------------------

def norm_url(url: str) -> str:
    return url.strip().rstrip("/").lower()


def sync_readings(snapshot_items: list[dict]) -> int:
    """Add public links from the snapshot to readings.json (never private hosts). Returns # added."""
    data = json.loads(READINGS.read_text(encoding="utf-8"))
    known = {norm_url(r["url"]) for r in data["readings"]}
    added = 0
    for it in snapshot_items:
        if it["k"] != "link" or norm_url(it["u"]) in known:
            continue
        if any(h in it["u"].lower() for h in PRIVATE_HOSTS):
            continue
        is_ref = "github.com" in it["u"] or "artificialanalysis" in it["u"] or "explainer" in it["u"]
        data["readings"].append({
            "week": it["w"], "title": it["t"], "url": it["u"].strip(),
            "kind": "repo" if "github.com" in it["u"] else ("tool" if is_ref else "article"),
            "capture": not is_ref,
        })
        known.add(norm_url(it["u"]))
        added += 1
    if added:
        data["readings"].sort(key=lambda r: (r["week"], r["title"].lower()))
        READINGS.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return added


# --- build + render ----------------------------------------------------------------

def build() -> dict:
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    items_raw = snap["items"]
    added = sync_readings(items_raw)
    readings = {norm_url(r["url"]): r for r in json.loads(READINGS.read_text(encoding="utf-8"))["readings"]}

    items: list[Item] = []
    for it in items_raw:
        k = it["k"]
        if k in ("paper", "file", "slides", "transcript"):
            items.append(eval_file(it))
        elif k == "link":
            items.append(eval_link(it, readings))
        elif k == "recording":
            items.append(eval_recording(it, items_raw))
        elif k == "private-link":
            items.append(Item(it["id"], it["w"], it["t"], k, "manual", "open in Brightspace (needs Vanderbilt login); save a copy to Coursework if useful"))
        else:
            items.append(Item(it["id"], it["w"], it["t"], k, "tracked", "check homework-queue.md" if k in ("quiz", "assignment") else ""))

    weeks: dict[int, dict] = {}
    for item in items:
        w = weeks.setdefault(item.week, {"stages": Counter(), "content": 0, "integrated": 0})
        w["stages"][item.stage] += 1
        if item.stage in STAGES:
            w["content"] += 1
            w["integrated"] += item.stage == "integrated"
    summary = {
        str(wk): {
            "stages": dict(v["stages"]),
            "complete": v["content"] > 0 and v["integrated"] == v["content"],
            "progress": f"{v['integrated']}/{v['content']}",
        }
        for wk, v in sorted(weeks.items())
    }
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="minutes"),
        "snapshot_taken_at": snap.get("taken_at"),
        "readings_added": added,
        "weeks": summary,
        "items": [asdict(i) for i in items],
    }


def to_markdown(ledger: dict, week: int | None = None) -> str:
    lines = [
        f"# Capture ledger - {ledger['generated_at']}",
        f"Brightspace snapshot: {ledger['snapshot_taken_at']}. Stages: {' > '.join(STAGES)}.",
        "",
        "| Week | Integrated | Stages | Complete |",
        "|------|-----------|--------|----------|",
    ]
    for wk, s in ledger["weeks"].items():
        stages = ", ".join(f"{k} {v}" for k, v in sorted(s["stages"].items(), key=lambda kv: (STAGES + ["manual", "tracked"]).index(kv[0])))
        lines.append(f"| {wk} | {s['progress']} | {stages} | {'yes' if s['complete'] else 'no'} |")
    lines += ["", "## Next actions", ""]
    for it in ledger["items"]:
        if week is not None and it["week"] != week:
            continue
        if it["next_action"] and it["stage"] != "tracked":
            lines.append(f"- W{it['week']} [{it['stage']}] {it['title']} -> {it['next_action']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the course capture ledger")
    parser.add_argument("--week", type=int, help="Only show this week's next actions")
    parser.add_argument("--no-write", action="store_true", help="Print only")
    args = parser.parse_args()
    ledger = build()
    md = to_markdown(ledger, args.week)
    print(md)
    if ledger["readings_added"]:
        print(f"\nAdded {ledger['readings_added']} public link(s) to readings.json")
    if not args.no_write:
        STATUS_DIR.mkdir(parents=True, exist_ok=True)
        (STATUS_DIR / "capture-ledger.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")
        (STATUS_DIR / "capture-ledger.md").write_text(md + "\n", encoding="utf-8")
        print(f"\nWrote {STATUS_DIR / 'capture-ledger.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
