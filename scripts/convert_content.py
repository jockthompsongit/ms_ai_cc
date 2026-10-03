"""Convert Coursework/ dumps to raw/ markdown via markitdown.

raw/ is immutable: existing outputs are skipped unless --force is given.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from vault_paths import COURSEWORK_DIR, RAW_DIR

CONVERTIBLE = {".pdf", ".pptx", ".ppt", ".docx", ".html", ".htm", ".xlsx", ".xls", ".csv"}
COPY_AS_IS = {".md", ".txt", ".markdown"}


def slugify(name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"[^\w\s\-]+", "", stem, flags=re.UNICODE)
    stem = re.sub(r"[\s_]+", "-", stem.strip()).strip("-").lower()
    return stem or "untitled"


def course_slug(course: str) -> str:
    """'AI 5100' -> 'AI-5100'."""
    return re.sub(r"\s+", "-", course.strip())


def week_source(course: str, week: int) -> Path:
    return COURSEWORK_DIR / f"{course} Week {week}"


def week_dest(course: str, week: int) -> Path:
    return RAW_DIR / "courses" / course_slug(course) / f"week-{week:02d}"


def source_header(src: Path) -> str:
    return f"---\nsource_file: {src.name}\nsource_path: {src}\n---\n\n"


def convert_file(src: Path, dest_md: Path, dry_run: bool, force: bool) -> str:
    rel = dest_md.relative_to(RAW_DIR)
    if dest_md.exists() and not force:
        return f"SKIP {src.name} (exists: {rel})"
    if dry_run:
        return f"DRY  {src.name} -> {rel}"

    dest_md.parent.mkdir(parents=True, exist_ok=True)
    suffix = src.suffix.lower()

    if suffix in COPY_AS_IS:
        text = src.read_text(encoding="utf-8", errors="replace")
        if not text.startswith("---"):
            text = source_header(src) + text
        dest_md.write_text(text, encoding="utf-8")
        return f"COPY {src.name} -> {rel}"

    from markitdown import MarkItDown

    md = MarkItDown()
    result = md.convert(str(src))
    text = (result.text_content or "").strip()
    dest_md.write_text(source_header(src) + text + "\n", encoding="utf-8")
    return f"OK   {src.name} -> {rel}"


def iter_files(src_root: Path):
    for path in sorted(src_root.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if path.suffix.lower() in CONVERTIBLE | COPY_AS_IS:
            yield path


def plan_outputs(src: Path, dest_root: Path) -> list[tuple[Path, Path]]:
    """Map each source file to an output path; disambiguate slug collisions by extension."""
    planned: list[tuple[Path, Path]] = []
    for path in iter_files(src):
        rel = path.relative_to(src)
        # Preserve sessions/ subfolder under raw week
        if rel.parts and rel.parts[0].lower() == "sessions":
            out_dir = dest_root / "sessions"
        else:
            out_dir = dest_root
        planned.append((path, out_dir / (slugify(path.name) + ".md")))

    counts: dict[Path, int] = {}
    for _, out in planned:
        key = Path(str(out).lower())
        counts[key] = counts.get(key, 0) + 1
    result = []
    for path, out in planned:
        if counts[Path(str(out).lower())] > 1:
            ext = path.suffix.lower().lstrip(".")
            out = out.with_name(f"{out.stem}-{ext}.md")
        result.append((path, out))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Coursework week folder to raw markdown")
    parser.add_argument("--week", type=int, required=True, help="Week number, e.g. 1")
    parser.add_argument("--course", default="AI 5100", help="Course folder prefix")
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions only")
    parser.add_argument("--force", action="store_true", help="Overwrite existing raw outputs")
    args = parser.parse_args()

    src = week_source(args.course, args.week)
    dest_root = week_dest(args.course, args.week)

    print(f"Source: {src}")
    print(f"Dest:   {dest_root}")
    if not src.exists():
        print("ERROR: source week folder not found", file=sys.stderr)
        return 1

    # Granola habit: Coursework/.../sessions/granola-YYYYMMDD.md
    print(f"Granola drop: {src / 'sessions'}\\granola-YYYYMMDD.md")

    count = 0
    skipped = 0
    errors = 0
    for path, out_path in plan_outputs(src, dest_root):
        try:
            line = convert_file(path, out_path, args.dry_run, args.force)
            print(line)
            if line.startswith("SKIP"):
                skipped += 1
            else:
                count += 1
        except Exception as exc:  # noqa: BLE001 — report per-file and continue
            print(f"FAIL {path.name}: {exc}", file=sys.stderr)
            errors += 1

    print(f"Done. files={count} skipped={skipped} errors={errors} dry_run={args.dry_run}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
