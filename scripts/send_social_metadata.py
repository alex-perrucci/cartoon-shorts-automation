from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import requests

try:
    from upload_youtube import load_metadata
except ModuleNotFoundError:
    from scripts.upload_youtube import load_metadata


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def _hashtags(values) -> str:
    out: list[str] = []
    seen: set[str] = set()
    for raw in values or []:
        tag = str(raw).strip().lstrip("#").replace(" ", "")
        if not tag:
            continue
        key = tag.casefold()
        if key in seen:
            continue
        seen.add(key)
        out.append(f"#{tag}")
    return " ".join(out)


def build_message(manifest_path: Path, youtube_receipt: Path | None = None) -> str:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    yt = data.get("youtube") if isinstance(data.get("youtube"), dict) else {}
    tt = data.get("tiktok") if isinstance(data.get("tiktok"), dict) else {}

    yt_title, yt_description, _ = load_metadata(manifest_path)
    yt_id = ""
    if youtube_receipt and youtube_receipt.is_file():
        try:
            receipt = json.loads(youtube_receipt.read_text(encoding="utf-8"))
            yt_id = str(receipt.get("video_id", "")).strip()
        except Exception:
            yt_id = ""

    tt_caption = " ".join(str(tt.get("caption") or data.get("caption") or "").split()).strip()
    tt_tags = _hashtags(tt.get("hashtags") or data.get("hashtags") or [])
    tt_full = (tt_caption + (" " + tt_tags if tt_tags else "")).strip()

    lines = [
        "✅ SHORT PRONTO",
        "",
        "🎵 TIKTOK",
        "Apri la notifica TikTok → continua il flusso → incolla:",
        tt_full or "(caption non disponibile)",
        "",
        "▶️ YOUTUBE SHORTS",
        f"Titolo: {yt_title}",
        "",
        "Descrizione:",
        yt_description or "(descrizione non disponibile)",
    ]
    if yt_id:
        lines.extend(["", f"Video ID: {yt_id}"])
    return "\n".join(lines).strip()


def send_message(token: str, chat_id: str, text: str) -> None:
    # Telegram sendMessage limit is 4096 chars. Split conservatively on line boundaries.
    chunks: list[str] = []
    current = ""
    for line in text.splitlines(keepends=True):
        if current and len(current) + len(line) > 3900:
            chunks.append(current.rstrip())
            current = ""
        current += line
    if current.strip():
        chunks.append(current.rstrip())

    for chunk in chunks:
        response = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": chunk},
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            raise RuntimeError(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Send final social metadata to Telegram.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--youtube-receipt", type=Path)
    args = parser.parse_args()

    token = _env("TELEGRAM_TOKEN")
    chat_id = _env("TELEGRAM_CHAT_ID")
    message = build_message(args.manifest, args.youtube_receipt)
    send_message(token, chat_id, message)
    print("Telegram social metadata delivered.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
