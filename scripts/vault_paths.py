"""Shared paths for MS AI Command Center scripts."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMAND_CENTER = REPO_ROOT / "command-center"
VAULT_ROOT = Path(r"C:\Users\jockt\Dropbox\Vandy_MS_AI")
CONTENT_DIR = VAULT_ROOT / "Content"
RAW_DIR = VAULT_ROOT / "raw"
WIKI_DIR = VAULT_ROOT / "wiki"
