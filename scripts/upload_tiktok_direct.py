from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path

import requests

from tiktok_tokens import load_encrypted, refresh_access_token, save_encrypted
from upload_tiktok_draft import _check_api_response, _chunk_plan, upload_file

CREATOR_INFO_ENDPOINT = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
INIT_ENDPOINT = "https://open.tiktokapis.com/v2/post/publish/video/init/"
STATUS_ENDPOINT = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
DEFAULT_STATE_PATH = Path(".auth/tiktok_tokens.enc")
MAX_CAPTION_UTF16 = 2200


def _env(name: str) -> str:
    import os
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def _clean_hashtag(value: str) -> str:
    value = str(value).strip().lstrip("#").replace(" ", "")
    return f"#{value}" if value else ""


def _utf16_units(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def compose_caption(manifest_path: Path) -> str:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    meta = data.get("tiktok")
    if not isinstance(meta, dict):
        raise ValueError("manifest is missing tiktok metadata")

    caption = " ".join(str(meta.get("caption", "")).split()).strip()
    if not caption:
        raise ValueError("tiktok.caption is required")

    hashtags: list[str] = []
    seen: set[str] = set()
    for raw in meta.get("hashtags", []):
        tag = _clean_hashtag(raw)
        if not tag:
            continue
        key = tag.casefold()
        if key in seen:
            continue
        seen.add(key)
        hashtags.append(tag)
        if len(hashtags) >= 6:
            break

    suffix = (" " + " ".join(hashtags)) if hashtags else ""
    budget = MAX_CAPTION_UTF16 - _utf16_units(suffix)
    if budget < 20:
        raise ValueError("TikTok hashtags leave too little room for a useful caption")

    while _utf16_units(caption) > budget:
        cut = caption.rsplit(" ", 1)[0].rstrip()
        if not cut or cut == caption:
            caption = caption[:-1].rstrip()
        else:
            caption = cut
    final = caption + suffix
    if _utf16_units(final) > MAX_CAPTION_UTF16:
        raise AssertionError("internal error: TikTok caption exceeds 2200 UTF-16 code units")
    return final


def query_creator_info(access_token: str) -> dict:
    response = requests.post(
        CREATOR_INFO_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={},
        timeout=30,
    )
    body = _check_api_response(response, "TikTok creator-info query")
    data = body.get("data") or {}
    if not data.get("privacy_level_options"):
        raise RuntimeError(f"TikTok creator-info query returned no privacy options: {body}")
    return data


def probe_duration_seconds(video_path: Path) -> float:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return float(proc.stdout.strip())


def wait_for_publish(access_token: str, publish_id: str, timeout_seconds: int = 180) -> dict:
    deadline = time.time() + timeout_seconds
    last: dict = {}
    while time.time() < deadline:
        response = requests.post(
            STATUS_ENDPOINT,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=UTF-8",
            },
            json={"publish_id": publish_id},
            timeout=30,
        )
        body = _check_api_response(response, "TikTok status fetch")
        last = body.get("data") or {}
        status = last.get("status")
        print(f"TikTok direct-post status: {status}")
        if status == "PUBLISH_COMPLETE":
            return last
        if status == "FAILED":
            raise RuntimeError(f"TikTok direct post failed: {last.get('fail_reason', last)}")
        time.sleep(5)

    # Public moderation can legitimately outlive an Actions job. Submission is
    # considered successful once TikTok accepted the upload and is processing it.
    return last or {"status": "PROCESSING_UPLOAD"}


def direct_post(
    video_path: Path,
    manifest_path: Path,
    token_state_path: Path,
    *,
    privacy_level: str,
    allow_comments: bool,
    allow_duet: bool,
    allow_stitch: bool,
) -> dict:
    if not video_path.is_file():
        raise FileNotFoundError(video_path)

    client_key = _env("TIKTOK_CLIENT_KEY")
    client_secret = _env("TIKTOK_CLIENT_SECRET")
    token_key = _env("TIKTOK_TOKEN_KEY")

    state = load_encrypted(token_state_path, token_key)
    state = refresh_access_token(state, client_key=client_key, client_secret=client_secret)
    save_encrypted(token_state_path, token_key, state)
    access_token = state["access_token"]

    scopes = {x.strip() for x in str(state.get("scope", "")).replace(" ", ",").split(",") if x.strip()}
    if "video.publish" not in scopes:
        raise RuntimeError(
            "TikTok token is missing video.publish. Re-run scripts/oauth_tiktok.py "
            "after Direct Post/video.publish is enabled for the app."
        )

    creator = query_creator_info(access_token)
    allowed_privacy = [str(x) for x in creator.get("privacy_level_options", [])]
    if privacy_level not in allowed_privacy:
        raise RuntimeError(
            f"privacy level {privacy_level!r} is not allowed for this creator; "
            f"available options: {allowed_privacy}"
        )

    if allow_comments and creator.get("comment_disabled"):
        raise RuntimeError("comments were requested but the creator account currently disables comments")
    if allow_duet and creator.get("duet_disabled"):
        raise RuntimeError("duet was requested but the creator account currently disables duet")
    if allow_stitch and creator.get("stitch_disabled"):
        raise RuntimeError("stitch was requested but the creator account currently disables stitch")

    duration = probe_duration_seconds(video_path)
    max_duration = int(creator.get("max_video_post_duration_sec") or 0)
    if max_duration and duration > max_duration + 0.25:
        raise RuntimeError(
            f"video duration {duration:.2f}s exceeds TikTok creator limit {max_duration}s"
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    tiktok_meta = manifest.get("tiktok") if isinstance(manifest.get("tiktok"), dict) else {}
    caption = compose_caption(manifest_path)
    is_aigc = bool(tiktok_meta.get("is_aigc", True))
    brand_content = bool(tiktok_meta.get("brand_content", False))
    brand_organic = bool(tiktok_meta.get("brand_organic", False))

    size = video_path.stat().st_size
    chunk_size, total_chunks = _chunk_plan(size)
    response = requests.post(
        INIT_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={
            "post_info": {
                "title": caption,
                "privacy_level": privacy_level,
                "disable_comment": not allow_comments,
                "disable_duet": not allow_duet,
                "disable_stitch": not allow_stitch,
                "brand_content_toggle": brand_content,
                "brand_organic_toggle": brand_organic,
                "is_aigc": is_aigc,
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunks,
            },
        },
        timeout=30,
    )
    body = _check_api_response(response, "TikTok direct-post init")
    data = body.get("data") or {}
    publish_id = data.get("publish_id")
    upload_url = data.get("upload_url")
    if not publish_id or not upload_url:
        raise RuntimeError(f"TikTok direct-post init returned incomplete data: {body}")

    upload_file(upload_url, video_path, chunk_size, total_chunks)
    status = wait_for_publish(access_token, publish_id)
    result = {
        "platform": "tiktok",
        "mode": "direct_post",
        "publish_id": publish_id,
        "status": status.get("status"),
        "public_post_ids": status.get("publicaly_available_post_id", []),
        "privacy_level": privacy_level,
        "caption": caption,
    }
    print(json.dumps(result, ensure_ascii=False))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Direct-post a rendered short to TikTok.")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--token-state", type=Path, default=DEFAULT_STATE_PATH)
    parser.add_argument("--privacy-level", required=True)
    parser.add_argument("--allow-comments", action="store_true")
    parser.add_argument("--allow-duet", action="store_true")
    parser.add_argument("--allow-stitch", action="store_true")
    args = parser.parse_args()

    direct_post(
        args.video,
        args.manifest,
        args.token_state,
        privacy_level=args.privacy_level,
        allow_comments=args.allow_comments,
        allow_duet=args.allow_duet,
        allow_stitch=args.allow_stitch,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
