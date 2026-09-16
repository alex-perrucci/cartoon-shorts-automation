from __future__ import annotations

import argparse
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"


def main() -> int:
    parser = argparse.ArgumentParser(description="One-time YouTube OAuth bootstrap.")
    parser.add_argument(
        "--client-secrets",
        required=True,
        type=Path,
        help="OAuth Desktop client JSON downloaded from Google Cloud Console",
    )
    args = parser.parse_args()

    flow = InstalledAppFlow.from_client_secrets_file(
        str(args.client_secrets), scopes=[YOUTUBE_UPLOAD_SCOPE]
    )
    credentials = flow.run_local_server(
        host="127.0.0.1",
        port=0,
        open_browser=True,
        access_type="offline",
        prompt="consent",
    )

    if not credentials.refresh_token:
        raise RuntimeError(
            "Google did not return a refresh token. Revoke this app's access and run again with consent."
        )

    print("\nYouTube OAuth complete. Add these three values as GitHub Actions secrets:")
    print(f"YOUTUBE_CLIENT_ID={credentials.client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={credentials.client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={credentials.refresh_token}")
    print("\nTreat these values as secrets and do not commit them to the repository.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
