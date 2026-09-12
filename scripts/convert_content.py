"""Convert Content/ dumps to raw/ markdown via markitdown."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from vault_paths import CONTENT_DIR, RAW_DIR

CONVERTIBLE = {".pdf", ".pptx", ".ppt", ".docx", ".html", ".htm", ".xlsx", ".xls", ".csv"}
COPY_AS_IS = {".md", ".txt", ".markdown"}


def slugify(name: str) -> str:
    stem = Path(name).stem
    stem = re.sub(r"[^\w\s\-]+", "", stem, flags=re.UNICODE)
    stem = re.sub(r"[\s_]+", "-", stem.strip()).strip("-").lower()
    return stem or "untitled"


def week_source(course: str, week: int) -> Path:
    return CONTENT_DIR / f"{course} Week {week}"


def week_dest(week: int) -> Path:
    return RAW_DIR / "courses" / "AI-5100" / f"week-{week:02d}"


def convert_file(src: Path, dest_md: Path, dry_run: bool) -> str:
    if dry_run:
        return f"DRY  {src.name} -> {dest_md.relative_to(RAW_DIR)}"

    dest_md.parent.mkdir(parents=True, exist_ok=True)
    suffix = src.suffix.lower()

    if suffix in COPY_AS_IS:
        dest_md.write_text(src.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        return f"COPY {src.name}"

    from markitdown import MarkItDown

    md = MarkItDown()
    result = md.convert(str(src))
    text = (result.text_content or "").strip()
    header = f"---\nsource_file: {src.name}\nsource_path: {src}\n---\n\n"
    dest_md.write_text(header + text + "\n", encoding="utf-8")
    return f"OK   {src.name}"


def iter_files(src_root: Path):
    for path in sorted(src_root.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        if path.suffix.lower() in CONVERTIBLE | COPY_AS_IS:
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Content week folder to raw markdown")
    parser.add_argument("--week", type=int, required=True, help="Week number, e.g. 1")
    parser.add_argument("--course", default="AI 5100", help="Course folder prefix")
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions only")
    args = parser.parse_args()

    src = week_source(args.course, args.week)
    dest_root = week_dest(args.week)

    print(f"Source: {src}")
    print(f"Dest:   {dest_root}")
    if not src.exists():
        print("ERROR: source week folder not found", file=sys.stderr)
        return 1

    # Granola habit: Content/.../sessions/granola-YYYYMMDD.md
    sessions = src / "sessions"
    print(f"Granola drop: {sessions}\\granola-YYYYMMDD.md")

    count = 0
    errors = 0
    for path in iter_files(src):
        rel = path.relative_to(src)
        out_name = slugify(path.name) + ".md"
        # Preserve sessions/ subfolder under raw week
        if rel.parts and rel.parts[0].lower() == "sessions":
            out_path = dest_root / "sessions" / out_name
        else:
            out_path = dest_root / out_name
        try:
            print(convert_file(path, out_path, args.dry_run))
            count += 1
        except Exception as exc:  # noqa: BLE001 — report per-file and continue
            print(f"FAIL {path.name}: {exc}", file=sys.stderr)
            errors += 1

    print(f"Done. files={count} errors={errors} dry_run={args.dry_run}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
