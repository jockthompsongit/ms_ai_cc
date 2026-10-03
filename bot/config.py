"""Runtime configuration for the Render Slack bot — all secrets come from env vars."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMMAND_CENTER = REPO_ROOT / "command-center"


def _need(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable {name}")
    return value


@dataclass(frozen=True)
class Settings:
    slack_bot_token: str
    slack_app_token: str
    channel_id: str
    owner_user_id: str
    dropbox_app_key: str
    dropbox_app_secret: str
    dropbox_refresh_token: str
    # Dropbox path of the vault (local C:\Users\jockt\Dropbox\Vandy_MS_AI)
    vault_root: str
    timezone: str
    briefs_enabled: bool
    # Only needed for an API key that is not scoped to a workspace (console → Workspaces → ID)
    anthropic_workspace_id: str = ""

    @classmethod
    def from_env(cls) -> "Settings":
        # ANTHROPIC_API_KEY is read by the SDK itself; fail fast if absent
        _need("ANTHROPIC_API_KEY")
        return cls(
            slack_bot_token=_need("SLACK_BOT_TOKEN"),
            slack_app_token=_need("SLACK_APP_TOKEN"),
            channel_id=os.environ.get("SLACK_CHANNEL_ID", "C0C6K3LATKK"),
            owner_user_id=os.environ.get("SLACK_OWNER_USER_ID", "U0BUHB47FLJ"),
            dropbox_app_key=_need("DROPBOX_APP_KEY"),
            dropbox_app_secret=_need("DROPBOX_APP_SECRET"),
            dropbox_refresh_token=_need("DROPBOX_REFRESH_TOKEN"),
            vault_root=os.environ.get("VAULT_ROOT", "/Vandy_MS_AI").rstrip("/"),
            timezone=os.environ.get("BOT_TIMEZONE", "America/Chicago"),
            briefs_enabled=os.environ.get("BRIEFS_ENABLED", "true").lower() == "true",
            anthropic_workspace_id=os.environ.get("ANTHROPIC_WORKSPACE_ID", "").strip(),
        )
