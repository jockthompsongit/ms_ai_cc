"""Shared paths for MS AI Command Center scripts."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMAND_CENTER = REPO_ROOT / "command-center"
VAULT_ROOT = Path(r"C:\Users\jockt\Dropbox\Vandy_MS_AI")
# Source dumps (Brightspace, papers, Granola, VTT) — never modified
COURSEWORK_DIR = VAULT_ROOT / "Coursework"
INBOX_DIR = COURSEWORK_DIR / "_inbox"
# Obsidian wiki root; converted raw/ lives inside it
WIKI_DIR = VAULT_ROOT / "Vandy Other" / "wiki"
RAW_DIR = WIKI_DIR / "raw"
ARCHIVE_DIR = VAULT_ROOT / "Vandy Other" / "_archive"
# Sibling clone of https://github.com/vanderbilt-ms-ai/wiki-to-graph
WIKI_TO_GRAPH_ROOT = Path(r"C:\Users\jockt\dev\wiki-to-graph")
WIKI_GRAPH_OUT = WIKI_TO_GRAPH_ROOT / "build" / "vandy-ms-ai"
