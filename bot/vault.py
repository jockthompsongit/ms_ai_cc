"""Read-only access to the Dropbox vault, sandboxed to the study folders."""
from __future__ import annotations

import posixpath
import time

import dropbox
from dropbox.files import FileMetadata, FolderMetadata, SearchOptions

# Folders (relative to the vault root) the bot may read. Admin/, personal_assistant/
# and Coursework/ (raw course binaries) are deliberately excluded.
ALLOWED_PREFIXES = (
    "Vandy Other/wiki",
    "Vandy Other/tutor-packs",
    "Vandy Other/status",
)
TEXT_SUFFIXES = (".md", ".json", ".txt")
CACHE_TTL = 300  # seconds


class VaultError(ValueError):
    pass


def safe_relpath(path: str) -> str:
    """Normalize a vault-relative path and reject anything outside the allowed folders."""
    cleaned = posixpath.normpath("/" + (path or "").replace("\\", "/").strip()).lstrip("/")
    if cleaned in ("", ".") or ".." in cleaned.split("/"):
        raise VaultError(f"path not allowed: {path!r}")
    if not any(cleaned == p or cleaned.startswith(p + "/") for p in ALLOWED_PREFIXES):
        raise VaultError(f"path outside study folders: {path!r} (allowed: {', '.join(ALLOWED_PREFIXES)})")
    return cleaned


class Vault:
    def __init__(self, app_key: str, app_secret: str, refresh_token: str, root: str):
        self._dbx = dropbox.Dropbox(
            oauth2_refresh_token=refresh_token, app_key=app_key, app_secret=app_secret
        )
        self._root = root
        self._cache: dict[str, tuple[float, str]] = {}

    def _full(self, rel: str) -> str:
        return f"{self._root}/{rel}"

    def read(self, path: str, max_chars: int = 60_000) -> str:
        rel = safe_relpath(path)
        if not rel.lower().endswith(TEXT_SUFFIXES):
            raise VaultError("only .md, .json and .txt files can be read")
        hit = self._cache.get(rel)
        if hit and time.time() - hit[0] < CACHE_TTL:
            text = hit[1]
        else:
            _, resp = self._dbx.files_download(self._full(rel))
            text = resp.content.decode("utf-8", errors="replace")
            self._cache[rel] = (time.time(), text)
        if len(text) > max_chars:
            return text[:max_chars] + f"\n\n[truncated at {max_chars:,} of {len(text):,} chars]"
        return text

    def list(self, folder: str) -> list[str]:
        rel = safe_relpath(folder)
        result = self._dbx.files_list_folder(self._full(rel))
        entries = list(result.entries)
        while result.has_more:
            result = self._dbx.files_list_folder_continue(result.cursor)
            entries.extend(result.entries)
        out = []
        for e in sorted(entries, key=lambda e: e.name.lower()):
            if isinstance(e, FolderMetadata):
                out.append(f"{rel}/{e.name}/")
            elif isinstance(e, FileMetadata):
                out.append(f"{rel}/{e.name}")
        return out

    def search(self, query: str, max_results: int = 15) -> list[str]:
        options = SearchOptions(
            path=self._full("Vandy Other/wiki"), max_results=max_results, file_extensions=["md"]
        )
        result = self._dbx.files_search_v2(query, options=options)
        paths = []
        prefix = self._root.lower() + "/"
        for match in result.matches:
            meta = match.metadata.get_metadata()
            full = getattr(meta, "path_display", "")
            if full.lower().startswith(prefix):
                paths.append(full[len(prefix):])
        return paths
