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
MAX_TITLE_CHARS = 100
MAX_TITLE_HASHTAGS = 3


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def _clean_hashtag(value: str) -> str:
    value = str(value).strip().lstrip("#").replace(" ", "")
    return f"#{value}" if value else ""


def _compose_title(base_title: str, hashtags: list[str]) -> str:
    title = " ".join(str(base_title).split()).strip()
    if not title:
        raise ValueError("youtube.title is required")

    clean: list[str] = []
    seen: set[str] = set()
    for raw in hashtags:
        tag = _clean_hashtag(raw)
        if not tag:
            continue
        key = tag.casefold()
        if key in seen:
            continue
        seen.add(key)
        clean.append(tag)
        if len(clean) >= MAX_TITLE_HASHTAGS:
            break

    if not clean:
        if len(title) > MAX_TITLE_CHARS:
            raise ValueError("youtube.title exceeds YouTube's 100-character limit")
        return title

    suffix = " " + " ".join(clean)
    budget = MAX_TITLE_CHARS - len(suffix)
    if budget < 8:
        raise ValueError("youtube hashtags leave too little room for a readable title")

    if len(title) > budget:
        cut = title[: max(1, budget - 1)].rstrip()
        if " " in cut:
            word_cut = cut.rsplit(" ", 1)[0].rstrip()
            if len(word_cut) >= max(8, budget // 2):
                cut = word_cut
        title = cut.rstrip(" .,:;-") + "…"

    final_title = title + suffix
    if len(final_title) > MAX_TITLE_CHARS:
        raise AssertionError("internal error: composed YouTube title exceeds 100 characters")
    return final_title


def load_metadata(manifest_path: Path) -> tuple[str, str, list[str]]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    meta = data.get("youtube")
    if not isinstance(meta, dict):
        raise ValueError("manifest is missing youtube metadata")

    base_title = str(meta.get("title", "")).strip()
    description = str(meta.get("description", "")).strip()
    tags = [str(x).strip() for x in meta.get("tags", []) if str(x).strip()]
    hashtags = [_clean_hashtag(x) for x in meta.get("hashtags", [])]
    hashtags = [x for x in hashtags if x]
    title = _compose_title(base_title, hashtags)
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


def _service():
    return build("youtube", "v3", credentials=build_credentials(), cache_discovery=False)


def update_metadata(video_id: str, manifest_path: Path) -> dict:
    video_id = str(video_id).strip()
    if not video_id:
        raise ValueError("video_id is required")
    title, description, tags = load_metadata(manifest_path)
    youtube = _service()
    response = youtube.videos().update(
        part="snippet",
        body={
            "id": video_id,
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "27",
                "defaultLanguage": "it",
            },
        },
    ).execute()
    result = {
        "platform": "youtube",
        "video_id": video_id,
        "privacy": "unchanged",
        "title": response.get("snippet", {}).get("title", title),
        "metadata_updated": True,
    }
    print(json.dumps(result, ensure_ascii=False))
    return result


def upload(video_path: Path, manifest_path: Path) -> dict:
    if not video_path.is_file():
        raise FileNotFoundError(video_path)
    title, description, tags = load_metadata(manifest_path)
    youtube = _service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "27",
            "defaultLanguage": "it",
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
    parser = argparse.ArgumentParser(description="Upload or reconcile a rendered short on YouTube.")
    parser.add_argument("--video", type=Path)
    parser.add_argument("--video-id")
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    if bool(args.video) == bool(args.video_id):
        parser.error("provide exactly one of --video or --video-id")
    if args.video_id:
        update_metadata(args.video_id, args.manifest)
    else:
        upload(args.video, args.manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
