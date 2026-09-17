#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont


def clean_tag(value: str) -> str:
    value = re.sub(r"[^\wàèéìòùÀÈÉÌÒÙ]+", "", str(value), flags=re.UNICODE)
    return value.strip("_")


def hashtags(values) -> str:
    out = []
    for item in values or []:
        tag = clean_tag(item)
        if tag:
            out.append("#" + tag)
    return " ".join(out)


def font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def make_thumbnail(video: Path, title: str, output: Path):
    frame = output.with_suffix(".frame.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-ss", "00:00:01.500", "-i", str(video), "-frames:v", "1",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", str(frame)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    img = Image.open(frame).convert("RGB")
    img = ImageEnhance.Brightness(img).enhance(0.58)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((65, 120, 1015, 790), radius=45, fill=(0, 0, 0, 170))
    draw.rounded_rectangle((65, 120, 285, 205), radius=28, fill=(255, 255, 255, 235))
    draw.text((100, 140), "TI FREGANO COSÌ", font=font(31, True), fill=(0, 0, 0, 255))

    words = title.strip().split()
    lines, current = [], []
    fnt = font(76, True)
    for word in words:
        trial = " ".join(current + [word])
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= 820:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    lines = lines[:5]
    y = 255
    for line in lines:
        draw.text((105, y), line, font=fnt, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
        y += 98

    draw.rounded_rectangle((65, 1650, 730, 1770), radius=34, fill=(0, 0, 0, 180))
    draw.text((105, 1680), "SHORT PRONTO DA PUBBLICARE", font=font(34, True), fill=(255, 255, 255, 255))
    img.save(output, "JPEG", quality=92, optimize=True)
    frame.unlink(missing_ok=True)


def telegram(method: str, token: str, data=None, files=None):
    response = requests.post(f"https://api.telegram.org/bot{token}/{method}", data=data, files=files, timeout=180)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(payload)
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--thumbnail", required=True)
    args = parser.parse_args()

    token = os.environ.get("TELEGRAM_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("Telegram not configured; skipping delivery.")
        return 0

    video = Path(args.video)
    manifest = Path(args.manifest)
    thumb = Path(args.thumbnail)
    if not video.is_file():
        raise FileNotFoundError(video)

    data = json.loads(manifest.read_text(encoding="utf-8"))
    yt = data.get("youtube") or {}
    tt = data.get("tiktok") or {}

    yt_title = yt.get("title") or data.get("title") or "Nuovo Short"
    yt_desc = yt.get("description") or data.get("caption") or ""
    yt_tags = hashtags(yt.get("hashtags") or data.get("hashtags") or [])
    tt_caption = tt.get("caption") or data.get("caption") or data.get("title") or "Nuovo video"
    tt_tags = hashtags(tt.get("hashtags") or data.get("hashtags") or [])

    make_thumbnail(video, yt_title, thumb)

    photo_caption = f"🖼 MINIATURA\n{yt_title}"
    with thumb.open("rb") as fh:
        telegram("sendPhoto", token, {"chat_id": chat_id, "caption": photo_caption}, {"photo": fh})

    video_caption = f"🎬 VIDEO PRONTO\n\nTikTok: {tt_caption}\n{tt_tags}"
    if len(video_caption) > 1000:
        video_caption = video_caption[:997] + "..."
    with video.open("rb") as fh:
        telegram("sendVideo", token, {"chat_id": chat_id, "caption": video_caption, "supports_streaming": "true"}, {"video": fh})

    metadata = (
        "📦 PACCHETTO PUBBLICAZIONE\n\n"
        f"▶️ YOUTUBE SHORTS\nTitolo: {yt_title}\n\nDescrizione:\n{yt_desc}\n\nHashtag:\n{yt_tags}\n\n"
        f"🎵 TIKTOK\nCaption:\n{tt_caption}\n\nHashtag:\n{tt_tags}"
    )
    for chunk in textwrap.wrap(metadata, width=3900, replace_whitespace=False, drop_whitespace=False):
        telegram("sendMessage", token, {"chat_id": chat_id, "text": chunk})

    print(f"Telegram package delivered: {video.name}, {thumb.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
