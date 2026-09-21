from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path

import requests

try:
    from tiktok_tokens import load_encrypted, refresh_access_token, save_encrypted
except ModuleNotFoundError:
    from scripts.tiktok_tokens import load_encrypted, refresh_access_token, save_encrypted

INIT_ENDPOINT = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
STATUS_ENDPOINT = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
DEFAULT_STATE_PATH = Path(".auth/tiktok_tokens.enc")
CHUNK_SIZE = 32 * 1024 * 1024


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def _check_api_response(response: requests.Response, action: str) -> dict:
    try:
        body = response.json()
    except ValueError as exc:
        raise RuntimeError(f"{action} returned HTTP {response.status_code} with non-JSON body") from exc
    error = body.get("error") or {}
    if response.status_code >= 400 or (isinstance(error, dict) and error.get("code") not in (None, "ok")):
        raise RuntimeError(f"{action} failed: HTTP {response.status_code} {body}")
    return body


def _chunk_plan(size: int) -> tuple[int, int]:
    if size <= 0:
        raise ValueError("video is empty")
    if size <= 64 * 1024 * 1024:
        return size, 1
    chunk_size = CHUNK_SIZE
    total = max(1, math.floor(size / chunk_size))
    return chunk_size, total


def upload_file(upload_url: str, video_path: Path, chunk_size: int, total_chunks: int) -> None:
    total_size = video_path.stat().st_size
    with video_path.open("rb") as fh:
        start = 0
        for index in range(total_chunks):
            if index == total_chunks - 1:
                length = total_size - start
            else:
                length = min(chunk_size, total_size - start)
            payload = fh.read(length)
            if len(payload) != length:
                raise RuntimeError("failed to read expected TikTok upload chunk")
            end = start + length - 1
            response = requests.put(
                upload_url,
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Length": str(length),
                    "Content-Range": f"bytes {start}-{end}/{total_size}",
                },
                data=payload,
                timeout=120,
            )
            expected = 201 if index == total_chunks - 1 else 206
            if response.status_code != expected:
                raise RuntimeError(
                    f"TikTok file upload failed on chunk {index + 1}/{total_chunks}: "
                    f"expected HTTP {expected}, got {response.status_code}: {response.text[:1000]}"
                )
            start = end + 1


def wait_for_inbox(access_token: str, publish_id: str, timeout_seconds: int = 90) -> dict:
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
        print(f"TikTok status: {status}")
        if status == "SEND_TO_USER_INBOX":
            return last
        if status == "FAILED":
            raise RuntimeError(f"TikTok processing failed: {last.get('fail_reason', last)}")
        time.sleep(4)
    raise RuntimeError(f"TikTok draft did not reach inbox within {timeout_seconds}s; last status: {last}")


def upload(video_path: Path, token_state_path: Path) -> dict:
    if not video_path.is_file():
        raise FileNotFoundError(video_path)

    client_key = _env("TIKTOK_CLIENT_KEY")
    client_secret = _env("TIKTOK_CLIENT_SECRET")
    token_key = _env("TIKTOK_TOKEN_KEY")

    state = load_encrypted(token_state_path, token_key)
    state = refresh_access_token(state, client_key=client_key, client_secret=client_secret)
    save_encrypted(token_state_path, token_key, state)
    access_token = state["access_token"]

    size = video_path.stat().st_size
    chunk_size, total_chunks = _chunk_plan(size)
    response = requests.post(
        INIT_ENDPOINT,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunks,
            }
        },
        timeout=30,
    )
    body = _check_api_response(response, "TikTok upload init")
    data = body.get("data") or {}
    publish_id = data.get("publish_id")
    upload_url = data.get("upload_url")
    if not publish_id or not upload_url:
        raise RuntimeError(f"TikTok upload init returned incomplete data: {body}")

    upload_file(upload_url, video_path, chunk_size, total_chunks)
    status = wait_for_inbox(access_token, publish_id)
    result = {
        "platform": "tiktok",
        "publish_id": publish_id,
        "status": status.get("status"),
    }
    print(json.dumps(result, ensure_ascii=False))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload a rendered short to TikTok's inbox as a draft.")
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--token-state", type=Path, default=DEFAULT_STATE_PATH)
    args = parser.parse_args()
    upload(args.video, args.token_state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
