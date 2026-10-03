"""One-time helper: get a long-lived Dropbox refresh token for the Render bot.

1. https://www.dropbox.com/developers/apps → Create app → Scoped access → Full Dropbox
   (the vault is not in an app folder). Permissions tab: tick ONLY files.metadata.read and
   files.content.read, then Submit. Note the App key and App secret.
2. Run:  python scripts/dropbox_auth.py
   Paste the app key/secret when asked, open the printed URL, approve, paste the code back.
3. Put DROPBOX_APP_KEY, DROPBOX_APP_SECRET and the printed refresh token into Render's
   environment settings. Nothing is written to disk by this script.
"""
from __future__ import annotations

import getpass

from dropbox import DropboxOAuth2FlowNoRedirect


def main() -> int:
    import sys

    # The app key is not secret, so it may be passed as an argument; the secret never is
    app_key = sys.argv[1].strip() if len(sys.argv) > 1 else input("Dropbox app key: ").strip()
    print(f"   (received a {len(app_key)}-character key)")
    if len(app_key) < 10:
        print("   That looks wrong. Re-run and paste the App key from the app's Settings tab.")
        return 1
    app_secret = getpass.getpass("Dropbox app secret (hidden; Ctrl+V then Enter): ").strip()
    # Dropbox app secrets are 15 characters; an empty or short value means the paste failed
    print(f"   (received a {len(app_secret)}-character secret)")
    if len(app_secret) < 10:
        print("   That looks wrong. Re-run and paste the App secret from the app's Settings tab.")
        return 1
    flow = DropboxOAuth2FlowNoRedirect(
        app_key,
        consumer_secret=app_secret,
        token_access_type="offline",
        scope=["files.metadata.read", "files.content.read"],
    )
    print("\n1. Open this URL and click Allow:\n   " + flow.start())
    code = input("2. Paste the authorization code (the whole thing, right away): ").strip()
    print(f"   (received a {len(code)}-character code)")
    try:
        result = flow.finish(code)
    except Exception as exc:  # noqa: BLE001 — show Dropbox's reason instead of a bare 400
        body = getattr(getattr(exc, "response", None), "text", "") or str(exc)
        print(f"\nDropbox rejected the exchange: {body}")
        print("Common fixes: re-copy the App secret; use a fresh code (codes are single-use and")
        print("expire in minutes); make sure the Permissions tab was saved with Submit.")
        return 1
    print("\nDROPBOX_REFRESH_TOKEN for Render (keep it secret):\n" + result.refresh_token)
    print("Granted scopes:", result.scope)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
