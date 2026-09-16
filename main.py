from __future__ import annotations

import argparse
import asyncio
import base64
import binascii
import hashlib
import io
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
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
OUTPUT = ROOT / "output"
FPS = 30
WIDTH = 1080
HEIGHT = 1920
MAX_ENCODED_ASSET_BYTES = 16 * 1024 * 1024
MAX_DECODED_ASSET_BYTES = 12 * 1024 * 1024
MIN_SOURCE_SIDE = 256
MAX_SOURCE_PIXELS = 40_000_000
Image.MAX_IMAGE_PIXELS = MAX_SOURCE_PIXELS


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(cmd))
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def ffprobe_json(path: Path) -> dict[str, Any]:
    result = run([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ])
    return json.loads(result.stdout)


def safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-")
    return value or "short"


def resolve_repo_path(value: str, *, field: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty repository-relative path")
    candidate = Path(value)
    if candidate.is_absolute():
        raise ValueError(f"{field} must be repository-relative")
    resolved = (ROOT / candidate).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"{field} escapes the repository root") from exc
    return resolved


def scene_asset_reference(scene: dict[str, Any]) -> tuple[str, str] | None:
    path = scene.get("image_b64")
    if path:
        return "file", str(path)
    inline = scene.get("image_base64")
    if inline:
        return "inline", str(inline)
    return None


def validate_package(data: dict[str, Any], *, require_assets: bool = True) -> None:
    for key in ("id", "title", "hook", "narration", "scenes", "caption", "hashtags"):
        if key not in data:
            raise ValueError(f"missing required field: {key}")

    if not isinstance(data["id"], str) or not data["id"].strip():
        raise ValueError("id must be a non-empty string")
    if not isinstance(data["scenes"], list) or not 5 <= len(data["scenes"]) <= 12:
        raise ValueError("scenes must contain 5-12 items")
    if len(str(data["narration"]).split()) < 55:
        raise ValueError("narration is too short; target roughly 35-60 seconds")
    if not isinstance(data["hashtags"], list):
        raise ValueError("hashtags must be a JSON array")

    for i, scene in enumerate(data["scenes"], start=1):
        if not isinstance(scene, dict):
            raise ValueError(f"scene {i} must be an object")
        if not str(scene.get("narration", "")).strip():
            raise ValueError(f"scene {i} has no narration beat")
        if not str(scene.get("visual", "")).strip():
            raise ValueError(f"scene {i} has no visual prompt")
        ref = scene_asset_reference(scene)
        if require_assets and ref is None:
            raise ValueError(f"scene {i} has no image_b64 asset")
        if ref and ref[0] == "file":
            asset_path = resolve_repo_path(ref[1], field=f"scene {i} image_b64")
            if asset_path.suffix.lower() != ".b64":
                raise ValueError(f"scene {i} image_b64 must point to a .b64 file")
        sha = scene.get("image_sha256")
        if sha is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", str(sha)):
            raise ValueError(f"scene {i} image_sha256 must be a 64-character hex digest")


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
    lines: list[str] = []
    current: list[str] = []
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


def _decode_base64_text(encoded: str, *, scene_no: int) -> bytes:
    text = encoded.strip()
    if text.startswith("data:"):
        if "," not in text:
            raise ValueError(f"scene {scene_no} has malformed data URI")
        header, text = text.split(",", 1)
        if ";base64" not in header.lower():
            raise ValueError(f"scene {scene_no} data URI is not base64 encoded")

    compact = "".join(text.split())
    if not compact:
        raise ValueError(f"scene {scene_no} image base64 is empty")
    if len(compact.encode("ascii", errors="ignore")) > MAX_ENCODED_ASSET_BYTES:
        raise ValueError(f"scene {scene_no} base64 asset exceeds {MAX_ENCODED_ASSET_BYTES // (1024 * 1024)} MiB")
    try:
        raw = base64.b64decode(compact, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"scene {scene_no} contains invalid base64") from exc
    if not raw:
        raise ValueError(f"scene {scene_no} decoded image is empty")
    if len(raw) > MAX_DECODED_ASSET_BYTES:
        raise ValueError(f"scene {scene_no} decoded image exceeds {MAX_DECODED_ASSET_BYTES // (1024 * 1024)} MiB")
    return raw


def decode_scene_image(scene: dict[str, Any], scene_no: int, output_path: Path) -> dict[str, Any]:
    ref = scene_asset_reference(scene)
    if ref is None:
        raise ValueError(f"scene {scene_no} has no image_b64 asset")

    source_kind, source_value = ref
    if source_kind == "file":
        source_path = resolve_repo_path(source_value, field=f"scene {scene_no} image_b64")
        if not source_path.is_file():
            raise ValueError(f"scene {scene_no} asset not found: {source_value}")
        if source_path.stat().st_size > MAX_ENCODED_ASSET_BYTES:
            raise ValueError(f"scene {scene_no} base64 file is too large")
        encoded = source_path.read_text(encoding="ascii")
    else:
        encoded = source_value

    raw = _decode_base64_text(encoded, scene_no=scene_no)
    digest = hashlib.sha256(raw).hexdigest()
    expected_digest = scene.get("image_sha256")
    if expected_digest and digest.lower() != str(expected_digest).lower():
        raise ValueError(
            f"scene {scene_no} SHA-256 mismatch: expected {expected_digest}, got {digest}"
        )

    try:
        with Image.open(io.BytesIO(raw)) as probe:
            probe.verify()
        with Image.open(io.BytesIO(raw)) as source:
            source = ImageOps.exif_transpose(source)
            source.load()
            source_width, source_height = source.size
            if source_width < MIN_SOURCE_SIDE or source_height < MIN_SOURCE_SIDE:
                raise ValueError(
                    f"scene {scene_no} source image is too small: {source_width}x{source_height}"
                )
            if source_width * source_height > MAX_SOURCE_PIXELS:
                raise ValueError(f"scene {scene_no} source image has too many pixels")
            normalized = ImageOps.fit(
                source.convert("RGB"),
                (WIDTH, HEIGHT),
                method=Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            normalized.save(output_path, format="PNG", optimize=True)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"scene {scene_no} decoded bytes are not a valid image") from exc

    return {
        "scene": scene_no,
        "source": source_value if source_kind == "file" else "inline",
        "sha256": digest,
        "normalized_width": WIDTH,
        "normalized_height": HEIGHT,
    }


def prepare_images(
    data: dict[str, Any], work_dir: Path, *, dry_run: bool
) -> tuple[list[Path], list[dict[str, Any]]]:
    image_dir = work_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    manifest: list[dict[str, Any]] = []

    for idx, scene in enumerate(data["scenes"], start=1):
        path = image_dir / f"scene_{idx:02d}.png"
        if dry_run:
            placeholder_image(path, idx, str(scene["visual"]))
            manifest.append({"scene": idx, "source": "placeholder", "sha256": None})
        else:
            manifest.append(decode_scene_image(scene, idx, path))
        paths.append(path)

    (work_dir / "image_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return paths, manifest


def validate_assets(data: dict[str, Any]) -> list[dict[str, Any]]:
    validate_package(data, require_assets=True)
    temp_dir = WORK / "_asset_validation"
    shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    try:
        _, manifest = prepare_images(data, temp_dir, dry_run=False)
        return manifest
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


async def create_tts(text: str, audio_path: Path, timings_path: Path) -> list[dict[str, Any]]:
    voice = os.environ.get("TTS_VOICE", "it-IT-IsabellaNeural")
    rate = os.environ.get("TTS_RATE", "+8%")
    communicator = edge_tts.Communicate(text, voice=voice, rate=rate, boundary="WordBoundary")
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
                a, b = min(cursor, n - 1), n - 1
            else:
                count = max(
                    1,
                    round(
                        n
                        * max(1, len(scene.get("narration", "").split()))
                        / total_scene_words
                    ),
                )
                a = min(cursor, n - 1)
                b = min(n - 1, a + count - 1)
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
        group = timings[i : i + (2 if len(timings[i]["text"]) < 8 else 1)]
        start = group[0]["start"]
        end = group[-1]["start"] + group[-1]["duration"]
        text = " ".join(x["text"] for x in group).upper()
        lines.append(
            f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{ass_escape(text)}\n"
        )
        i += len(group)
    path.write_text("".join(lines), encoding="utf-8")


def render_video(
    images: list[Path],
    windows: list[tuple[float, float]],
    audio: Path,
    ass: Path,
    output: Path,
    work_dir: Path,
) -> None:
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
        run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(image), "-vf", vf,
            "-t", f"{duration:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast", str(clip),
        ])
        clips.append(clip)

    concat_file = work_dir / "concat.txt"
    concat_file.write_text("\n".join(f"file '{p.resolve()}'" for p in clips), encoding="utf-8")
    silent = work_dir / "silent.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(silent)])
    ass_path = str(ass.resolve()).replace(":", r"\:")
    run([
        "ffmpeg", "-y", "-i", str(silent), "-i", str(audio), "-vf", f"ass={ass_path}",
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(output),
    ])


def qc(
    video: Path,
    data: dict[str, Any],
    report_path: Path,
    image_manifest: list[dict[str, Any]],
) -> dict[str, Any]:
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
        "all_scene_images_prepared": len(image_manifest) == len(data["scenes"]),
        "caption_present": bool(data.get("caption")),
    }
    report = {
        "passed": all(checks.values()),
        "duration": duration,
        "checks": checks,
        "scene_images": image_manifest,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def process(input_path: Path, *, dry_run: bool = False) -> int:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    validate_package(data, require_assets=not dry_run)
    short_id = safe_name(str(data["id"]))
    work_dir = WORK / short_id
    out_dir = OUTPUT / short_id
    shutil.rmtree(work_dir, ignore_errors=True)
    shutil.rmtree(out_dir, ignore_errors=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    images, image_manifest = prepare_images(data, work_dir, dry_run=dry_run)
    audio = work_dir / "voice.mp3"
    timings_file = work_dir / "word_timings.json"
    timings = asyncio.run(create_tts(str(data["narration"]), audio, timings_file))
    windows = scene_windows(data, timings)
    ass = work_dir / "captions.ass"
    create_ass(timings, ass)
    final = out_dir / "final_video.mp4"
    render_video(images, windows, audio, ass, final, work_dir)

    metadata = {
        "id": data["id"],
        "title": data["title"],
        "caption": data["caption"],
        "hashtags": data["hashtags"],
        "source_input": str(input_path.relative_to(ROOT)),
        "image_source": "placeholder" if dry_run else "packaged_base64",
    }
    (out_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "image_manifest.json").write_text(
        json.dumps(image_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report = qc(final, data, out_dir / "qc_report.json", image_manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 2


def self_test() -> int:
    for binary in ("ffmpeg", "ffprobe"):
        if not shutil.which(binary):
            print(f"missing binary: {binary}", file=sys.stderr)
            return 2

    sample = Image.new("RGB", (320, 568), (241, 232, 210))
    buf = io.BytesIO()
    sample.save(buf, format="PNG")
    raw = buf.getvalue()
    encoded = base64.b64encode(raw).decode("ascii")
    if _decode_base64_text(encoded, scene_no=1) != raw:
        print("base64 self-test failed", file=sys.stderr)
        return 2

    print("self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="use placeholder images but still render the complete video",
    )
    parser.add_argument(
        "--validate-assets",
        action="store_true",
        help="validate manifest and base64 scene images, then exit",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.input:
        parser.error("--input is required unless --self-test is used")

    input_path = args.input if args.input.is_absolute() else ROOT / args.input
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if args.validate_assets:
        manifest = validate_assets(data)
        print(json.dumps({"valid": True, "scenes": manifest}, ensure_ascii=False, indent=2))
        return 0
    return process(input_path, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
