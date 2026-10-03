"""Stage a flat wiki copy, build wiki-to-graph, optionally open the viewer.

wiki-to-graph only reads top-level *.md. The vault nests pages under concepts/,
sources/, syntheses/, etc. — this script copies hubs + those pages into a
staging dir, then runs build + viewer.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

from vault_paths import WIKI_DIR, WIKI_GRAPH_OUT, WIKI_TO_GRAPH_ROOT

# Nested folders (searched recursively) whose *.md pages become top-level nodes.
# raw/ is deliberately excluded: it holds converted sources, not wiki pages.
STAGE_SUBDIRS = ("concepts", "sources", "syntheses", "courses")
# Long-form derived notes (lecture-recording skill output) are not graph nodes
SKIP_PARTS = {"lecture-notes"}


def scripts_dir() -> Path:
    return WIKI_TO_GRAPH_ROOT / "skills" / "wiki-to-graph" / "scripts"


def stage_flat_wiki(wiki: Path, stage: Path) -> list[str]:
    """Copy index/log + selected subdir pages into a flat staging directory."""
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)

    copied: list[str] = []
    for name in ("index.md", "log.md"):
        src = wiki / name
        if src.is_file():
            shutil.copy2(src, stage / name)
            copied.append(name)

    seen: set[str] = {"index.md", "log.md"}
    for sub in STAGE_SUBDIRS:
        folder = wiki / sub
        if not folder.is_dir():
            continue
        for src in sorted(folder.rglob("*.md")):
            if SKIP_PARTS.intersection(src.relative_to(wiki).parts):
                continue
            # Obsidian resolves [[links]] by filename, so flattening keeps links intact
            dest_name = src.name
            if dest_name.lower() in seen:
                # Avoid clobbering hubs; rare name collisions get a prefix
                dest_name = f"{sub}-{src.name}"
            shutil.copy2(src, stage / dest_name)
            seen.add(dest_name.lower())
            copied.append(src.relative_to(wiki).as_posix())
    return copied


def run_py(script: Path, args: list[str]) -> int:
    cmd = [sys.executable, str(script), *args]
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Flatten vault wiki → wiki-to-graph build → HTML viewer"
    )
    parser.add_argument(
        "--wiki",
        type=Path,
        default=WIKI_DIR,
        help=f"Vault wiki root (default: {WIKI_DIR})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=WIKI_GRAPH_OUT,
        help=f"Output dir for graph + viewer (default: {WIKI_GRAPH_OUT})",
    )
    parser.add_argument(
        "--tool-root",
        type=Path,
        default=WIKI_TO_GRAPH_ROOT,
        help=f"wiki-to-graph clone (default: {WIKI_TO_GRAPH_ROOT})",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open graph-viewer.html in the browser",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validate after build",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Stage only; print counts and exit",
    )
    args = parser.parse_args()

    tool = args.tool_root
    scr = tool / "skills" / "wiki-to-graph" / "scripts"
    build_py = scr / "wiki_to_graph.py"
    viewer_py = scr / "build_graph_viewer.py"
    if not build_py.is_file() or not viewer_py.is_file():
        print(
            f"ERROR: wiki-to-graph scripts not found under {scr}\n"
            f"Clone: git clone https://github.com/vanderbilt-ms-ai/wiki-to-graph.git {tool}",
            file=sys.stderr,
        )
        return 1
    if not args.wiki.is_dir():
        print(f"ERROR: wiki not found: {args.wiki}", file=sys.stderr)
        return 1

    stage = args.out / "_stage"
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    copied = stage_flat_wiki(args.wiki, stage)
    print(f"Staged {len(copied)} files -> {stage}", flush=True)
    for line in copied[:8]:
        print(f"  {line}", flush=True)
    if len(copied) > 8:
        print(f"  ... +{len(copied) - 8} more", flush=True)

    if args.dry_run:
        return 0

    graph_json = out / "graph.json"
    viewer_html = out / "graph-viewer.html"

    rc = run_py(
        build_py,
        ["build", str(stage), "-o", str(graph_json), "--emit", "sqlite,graphml"],
    )
    if rc != 0:
        return rc

    validate_rc = 0
    if args.validate:
        validate_rc = run_py(build_py, ["validate", str(graph_json)])
        if validate_rc != 0:
            print(
                "NOTE: validate reported issues (orphans/dangling). Viewer still built.",
                flush=True,
            )

    rc = run_py(viewer_py, [str(graph_json), "-o", str(viewer_html)])
    if rc != 0:
        return rc

    print(f"Viewer: {viewer_html}", flush=True)
    if not args.no_open:
        webbrowser.open(viewer_html.resolve().as_uri())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
