from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import edge_tts
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
OUTPUT = ROOT / "output"
FPS = 30
WIDTH = 1080
HEIGHT = 1920

STYLE_BIBLE = """
Create a clean vertical 9:16 editorial cartoon illustration.
Use the SAME recurring main character in every scene: a simple round-headed adult businessman,
black suit, white shirt, black tie, thick black outlines, minimal facial features.
Warm cream/beige background, sparse props, simple flat 2D vector-like drawing, minimal shading.
Strong readable silhouette, centered composition, no text, no captions, no watermark, no logo.
The image must look like one frame from the same recurring cartoon series.
""".strip()


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def ffprobe_json(path: Path) -> dict[str, Any]:
    result = run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ])
    return json.loads(result.stdout)


def validate_package(data: dict[str, Any]) -> None:
    for key in ("id", "title", "hook", "narration", "scenes", "caption", "hashtags"):
        if key not in data:
            raise ValueError(f"missing required field: {key}")
    if not isinstance(data["scenes"], list) or len(data["scenes"]) < 5:
        raise ValueError("scenes must contain at least 5 items")
    if len(data["narration"].split()) < 55:
        raise ValueError("narration is too short; target roughly 35-60 seconds")
    for i, scene in enumerate(data["scenes"]):
        if not scene.get("visual"):
            raise ValueError(f"scene {i + 1} has no visual prompt")


def safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-")
    return value or "short"


def placeholder_image(path: Path, scene_no: int, visual: str) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), (241, 232, 210))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 58)
        small = ImageFont.truetype("DejaVuSans.ttf", 34)
    except OSError:
        font = ImageFont.load_default()
        small = font
    draw.text((80, 120), f"SCENE {scene_no}", fill=(15, 15, 15), font=font)
    words = visual.split()
    lines, current = [], []
    for word in words:
        current.append(word)
        if len(" ".join(current)) >= 32:
            lines.append(" ".join(current))
            current = []
    if current:
        lines.append(" ".join(current))
    y = 350
    for line in lines[:12]:
        draw.text((80, y), line, fill=(35, 35, 35), font=small)
        y += 58
    img.save(path)


def generate_gemini_image(path: Path, prompt: str) -> None:
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required for IMAGE_PROVIDER=gemini")
    model = os.environ.get("IMAGE_MODEL", "gemini-3.1-flash-image")
    client = genai.Client(api_key=api_key)
    contents: list[Any] = [f"{STYLE_BIBLE}\n\nSCENE:\n{prompt}"]
    ref = ROOT / "assets" / "character_reference.png"
    if ref.exists():
        contents.append(Image.open(ref))
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
            response_format={"image": {"aspect_ratio": "9:16", "image_size": "1K"}},
        ),
    )
    for part in response.parts:
        image = part.as_image()
        if image is not None:
            image.save(path)
            return
    raise RuntimeError("Gemini returned no image")


def generate_images(data: dict[str, Any], work_dir: Path, dry_run: bool) -> list[Path]:
    image_dir = work_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    provider = "placeholder" if dry_run else os.environ.get("IMAGE_PROVIDER", "gemini")
    paths: list[Path] = []
    for idx, scene in enumerate(data["scenes"], start=1):
        path = image_dir / f"scene_{idx:02d}.png"
        if provider == "placeholder":
            placeholder_image(path, idx, scene["visual"])
        elif provider == "gemini":
            generate_gemini_image(path, scene["visual"])
        else:
            raise ValueError(f"unsupported IMAGE_PROVIDER: {provider}")
        paths.append(path)
    return paths


async def create_tts(text: str, audio_path: Path, timings_path: Path) -> list[dict[str, Any]]:
    voice = os.environ.get("TTS_VOICE", "it-IT-IsabellaNeural")
    rate = os.environ.get("TTS_RATE", "+8%")
    communicator = edge_tts.Communicate(text, voice=voice, rate=rate)
    timings: list[dict[str, Any]] = []
    with audio_path.open("wb") as audio:
        async for chunk in communicator.stream():
            if chunk["type"] == "audio":
                audio.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                timings.append({
                    "text": chunk["text"],
                    "start": chunk["offset"] / 10_000_000,
                    "duration": chunk["duration"] / 10_000_000,
                })
    if not timings:
        raise RuntimeError("TTS returned no word timings")
    timings_path.write_text(json.dumps(timings, ensure_ascii=False, indent=2), encoding="utf-8")
    return timings


def scene_windows(data: dict[str, Any], timings: list[dict[str, Any]]) -> list[tuple[float, float]]:
    n = len(timings)
    scenes = data["scenes"]
    windows: list[tuple[float, float]] = []
    cursor = 0
    total_scene_words = sum(max(1, len(s.get("narration", "").split())) for s in scenes)
    for i, scene in enumerate(scenes):
        if "start_word" in scene and "end_word" in scene:
            a = max(0, min(n - 1, int(scene["start_word"])))
            b = max(a, min(n - 1, int(scene["end_word"])))
        else:
            if i == len(scenes) - 1:
                a, b = cursor, n - 1
            else:
                count = max(1, round(n * max(1, len(scene.get("narration", "").split())) / total_scene_words))
                a = cursor
                b = min(n - 1, cursor + count - 1)
                cursor = b + 1
        start = timings[a]["start"]
        end = timings[b]["start"] + timings[b]["duration"]
        if i == 0:
            start = 0.0
        if i == len(scenes) - 1:
            end = timings[-1]["start"] + timings[-1]["duration"] + 0.15
        windows.append((start, max(start + 0.35, end)))
    return windows


def ass_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def ass_escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def create_ass(timings: list[dict[str, Any]], path: Path) -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {WIDTH}
PlayResY: {HEIGHT}
WrapStyle: 2

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,DejaVu Sans,104,&H0000FFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,0,5,80,80,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = [header]
    i = 0
    while i < len(timings):
        group = timings[i:i + (2 if len(timings[i]["text"]) < 8 else 1)]
        start = group[0]["start"]
        end = group[-1]["start"] + group[-1]["duration"]
        text = " ".join(x["text"] for x in group).upper()
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{ass_escape(text)}\n")
        i += len(group)
    path.write_text("".join(lines), encoding="utf-8")


def render_video(images: list[Path], windows: list[tuple[float, float]], audio: Path, ass: Path, output: Path, work_dir: Path) -> None:
    clips: list[Path] = []
    for idx, (image, (start, end)) in enumerate(zip(images, windows), start=1):
        duration = max(0.35, end - start)
        frames = max(1, math.ceil(duration * FPS))
        clip = work_dir / f"clip_{idx:02d}.mp4"
        vf = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},"
            f"zoompan=z='min(zoom+0.00045,1.055)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS},format=yuv420p"
        )
        run(["ffmpeg", "-y", "-loop", "1", "-i", str(image), "-vf", vf, "-t", f"{duration:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast", str(clip)])
        clips.append(clip)

    concat_file = work_dir / "concat.txt"
    concat_file.write_text("\n".join(f"file '{p.resolve()}'" for p in clips), encoding="utf-8")
    silent = work_dir / "silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(silent)])
    ass_filter = f"ass={str(ass.resolve()).replace(':', r'\:')}"
    run([
        "ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-vf", ass_filter,
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(output)
    ])


def qc(video: Path, data: dict[str, Any], report_path: Path) -> dict[str, Any]:
    info = ffprobe_json(video)
    streams = info.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
    duration = float(info.get("format", {}).get("duration", 0) or 0)
    checks = {
        "file_exists": video.exists() and video.stat().st_size > 100_000,
        "vertical_1080x1920": video_stream.get("width") == WIDTH and video_stream.get("height") == HEIGHT,
        "audio_present": bool(audio_stream),
        "duration_30_to_65_seconds": 30 <= duration <= 65,
        "at_least_5_scenes": len(data["scenes"]) >= 5,
        "caption_present": bool(data.get("caption")),
    }
    report = {"passed": all(checks.values()), "duration": duration, "checks": checks}
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def process(input_path: Path, dry_run: bool = False) -> int:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    validate_package(data)
    short_id = safe_name(str(data["id"]))
    work_dir = WORK / short_id
    out_dir = OUTPUT / short_id
    shutil.rmtree(work_dir, ignore_errors=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    images = generate_images(data, work_dir, dry_run=dry_run)
    audio = work_dir / "voice.mp3"
    timings_file = work_dir / "word_timings.json"
    timings = asyncio.run(create_tts(data["narration"], audio, timings_file))
    windows = scene_windows(data, timings)
    ass = work_dir / "captions.ass"
    create_ass(timings, ass)
    final = out_dir / "final_video.mp4"
    render_video(images, windows, audio, ass, final, work_dir)

    metadata = {
        "id": data["id"], "title": data["title"], "caption": data["caption"],
        "hashtags": data["hashtags"], "source_input": str(input_path.relative_to(ROOT)),
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    report = qc(final, data, out_dir / "qc_report.json")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 2


def self_test() -> int:
    for binary in ("ffmpeg", "ffprobe"):
        if not shutil.which(binary):
            print(f"missing binary: {binary}", file=sys.stderr)
            return 2
    print("self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="use placeholder images, but still render the complete video")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.input:
        parser.error("--input is required unless --self-test is used")
    input_path = args.input if args.input.is_absolute() else ROOT / args.input
    return process(input_path, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
