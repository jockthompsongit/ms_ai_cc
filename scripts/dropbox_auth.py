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
    app_key = input("Dropbox app key: ").strip()
    app_secret = getpass.getpass("Dropbox app secret (hidden): ").strip()
    flow = DropboxOAuth2FlowNoRedirect(
        app_key,
        consumer_secret=app_secret,
        token_access_type="offline",
        scope=["files.metadata.read", "files.content.read"],
    )
    print("\n1. Open this URL and click Allow:\n   " + flow.start())
    code = input("2. Paste the authorization code: ").strip()
    result = flow.finish(code)
    print("\nDROPBOX_REFRESH_TOKEN for Render (keep it secret):\n" + result.refresh_token)
    print("Granted scopes:", result.scope)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
