from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
TOKEN_URI = "https://oauth2.googleapis.com/token"


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def _clean_hashtag(value: str) -> str:
    value = str(value).strip().lstrip("#").replace(" ", "")
    return f"#{value}" if value else ""


def load_metadata(manifest_path: Path) -> tuple[str, str, list[str]]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    meta = data.get("youtube")
    if not isinstance(meta, dict):
        raise ValueError("manifest is missing youtube metadata")

    title = str(meta.get("title", "")).strip()
    description = str(meta.get("description", "")).strip()
    tags = [str(x).strip() for x in meta.get("tags", []) if str(x).strip()]
    hashtags = [_clean_hashtag(x) for x in meta.get("hashtags", [])]
    hashtags = [x for x in hashtags if x]

    if not title:
        raise ValueError("youtube.title is required")
    if len(title) > 100:
        raise ValueError("youtube.title exceeds YouTube's 100-character limit")
    if hashtags:
        suffix = " ".join(hashtags)
        description = f"{description}\n\n{suffix}" if description else suffix
    if len(description) > 5000:
        raise ValueError("youtube.description exceeds YouTube's 5000-character limit")
    if sum(len(t) for t in tags) > 450:
        raise ValueError("youtube.tags are too long; keep total tag text comfortably below 500 characters")
    return title, description, tags


def build_credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=_env("YOUTUBE_REFRESH_TOKEN"),
        token_uri=TOKEN_URI,
        client_id=_env("YOUTUBE_CLIENT_ID"),
        client_secret=_env("YOUTUBE_CLIENT_SECRET"),
        scopes=[YOUTUBE_UPLOAD_SCOPE],
    )
    creds.refresh(Request())
    return creds


def upload(video_path: Path, manifest_path: Path) -> dict:
    if not video_path.is_file():
        raise FileNotFoundError(video_path)
    title, description, tags = load_metadata(manifest_path)
    youtube = build("youtube", "v3", credentials=build_credentials(), cache_discovery=False)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": "private",
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        chunksize=8 * 1024 * 1024,
        resumable=True,
    )
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        progress, response = request.next_chunk()
        if progress:
            print(f"YouTube upload: {int(progress.progress() * 100)}%")

    result = {
        "platform": "youtube",
        "video_id": response.get("id"),
        "privacy": response.get("status", {}).get("privacyStatus", "private"),
        "title": response.get("snippet", {}).get("title", title),
    }
    print(json.dumps(result, ensure_ascii=False))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload a rendered short to YouTube as private.")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    upload(args.video, args.manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
