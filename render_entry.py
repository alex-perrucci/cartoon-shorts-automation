from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Any

from PIL import ImageFont

import main as renderer

BASE_FONT_SIZE = 104
MIN_FONT_SIZE = 58
SAFE_TEXT_WIDTH = 820
MAX_WORDS_PER_CAPTION = 2
MIN_VIDEO_SECONDS = 60.0
MAX_VIDEO_SECONDS = 120.0
TAIL_HOLD_SECONDS = 1.2
MIN_NARRATION_WORDS = 150
MIN_KEYFRAMES = 2
MAX_KEYFRAMES = 4


_BASE_PREPARE_IMAGES = renderer.prepare_images


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _text_width(text: str, size: int) -> float:
    font = _font(size)
    left, _top, right, _bottom = font.getbbox(text)
    return float(right - left)


def _fit_font_size(text: str) -> int:
    size = BASE_FONT_SIZE
    while size > MIN_FONT_SIZE and _text_width(text, size) > SAFE_TEXT_WIDTH:
        size -= 4
    return max(MIN_FONT_SIZE, size)


def _next_group(timings: list[dict[str, Any]], start_index: int) -> list[dict[str, Any]]:
    group = [timings[start_index]]
    while len(group) < MAX_WORDS_PER_CAPTION and start_index + len(group) < len(timings):
        candidate = group + [timings[start_index + len(group)]]
        candidate_text = " ".join(str(x["text"]) for x in candidate).upper()
        if _text_width(candidate_text, 88) > SAFE_TEXT_WIDTH:
            break
        group = candidate
    return group


def create_safe_ass(timings: list[dict[str, Any]], path: Path) -> None:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {renderer.WIDTH}
PlayResY: {renderer.HEIGHT}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,DejaVu Sans,{BASE_FONT_SIZE},&H0000FFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,7,0,5,130,130,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines = [header]
    i = 0
    while i < len(timings):
        group = _next_group(timings, i)
        start = float(group[0]["start"])
        end = float(group[-1]["start"]) + float(group[-1]["duration"])
        text = " ".join(str(x["text"]) for x in group).upper()
        font_size = _fit_font_size(text)
        escaped = renderer.ass_escape(text)
        lines.append(
            f"Dialogue: 0,{renderer.ass_time(start)},{renderer.ass_time(end)},Default,,0,0,0,,"
            f"{{\\fs{font_size}}}{escaped}\n"
        )
        i += len(group)

    path.write_text("".join(lines), encoding="utf-8")


def _spoken_tokens(text: str) -> list[str]:
    return [
        token.lower().replace("’", "'")
        for token in re.findall(
            r"\d+(?:[.,]\d+)*|[A-Za-zÀ-ÖØ-öø-ÿ]+(?:['’][A-Za-zÀ-ÖØ-öø-ÿ]+)*",
            text,
        )
    ]


def _scene_counts(data: dict[str, Any]) -> tuple[list[int], int]:
    full = _spoken_tokens(str(data["narration"]))
    scene_tokens: list[str] = []
    counts: list[int] = []
    for scene in data["scenes"]:
        tokens = _spoken_tokens(str(scene.get("narration", "")))
        counts.append(len(tokens))
        scene_tokens.extend(tokens)
    if scene_tokens != full:
        raise ValueError(
            "scene narration must be an exact sequential partition of full narration; "
            "this is required for frame-accurate artwork sync"
        )
    return counts, len(full)


def validate_keyframes(data: dict[str, Any], *, require_assets: bool = True) -> None:
    for scene_index, scene in enumerate(data.get("scenes", []), start=1):
        keyframes = scene.get("keyframes")
        if keyframes is None:
            continue
        if not isinstance(keyframes, list) or not MIN_KEYFRAMES <= len(keyframes) <= MAX_KEYFRAMES:
            raise ValueError(
                f"scene {scene_index} keyframes must contain {MIN_KEYFRAMES}-{MAX_KEYFRAMES} items"
            )
        for pose_index, keyframe in enumerate(keyframes, start=1):
            if not isinstance(keyframe, dict):
                raise ValueError(f"scene {scene_index} keyframe {pose_index} must be an object")
            ref = renderer.scene_asset_reference(keyframe)
            if require_assets and ref is None:
                raise ValueError(
                    f"scene {scene_index} keyframe {pose_index} has no image_b64 asset"
                )
            if ref and ref[0] == "file":
                asset_path = renderer.resolve_repo_path(
                    ref[1], field=f"scene {scene_index} keyframe {pose_index} image_b64"
                )
                if asset_path.suffix.lower() != ".b64":
                    raise ValueError(
                        f"scene {scene_index} keyframe {pose_index} image_b64 must point to a .b64 file"
                    )
            sha = keyframe.get("image_sha256")
            if sha is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", str(sha)):
                raise ValueError(
                    f"scene {scene_index} keyframe {pose_index} image_sha256 must be a 64-character hex digest"
                )


def validate_long_package(data: dict[str, Any], *, require_assets: bool = True) -> None:
    renderer.validate_package(data, require_assets=require_assets)
    validate_keyframes(data, require_assets=require_assets)
    counts, total = _scene_counts(data)
    if total < MIN_NARRATION_WORDS:
        raise ValueError(
            f"narration is too short for a 60+ second short: {total} words; "
            f"minimum is {MIN_NARRATION_WORDS}"
        )
    if any(count <= 0 for count in counts):
        raise ValueError("every scene must contain at least one spoken word")


def prepare_images_with_keyframes(
    data: dict[str, Any], work_dir: Path, *, dry_run: bool
) -> tuple[list[Path], list[dict[str, Any]]]:
    paths, manifest = _BASE_PREPARE_IMAGES(data, work_dir, dry_run=dry_run)
    if dry_run:
        return paths, manifest

    image_dir = work_dir / "images"
    for scene_index, scene in enumerate(data["scenes"], start=1):
        keyframes = scene.get("keyframes") or []
        if not keyframes:
            continue
        pose_manifest: list[dict[str, Any]] = []
        for pose_index, keyframe in enumerate(keyframes, start=1):
            pose_path = image_dir / f"scene_{scene_index:02d}_pose_{pose_index:02d}.png"
            metadata = renderer.decode_scene_image(
                keyframe,
                f"{scene_index}.{pose_index}",
                pose_path,
            )
            metadata["pose"] = pose_index
            pose_manifest.append(metadata)
        manifest[scene_index - 1]["keyframes"] = pose_manifest

    (work_dir / "image_manifest.json").write_text(
        renderer.json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return paths, manifest


def scene_windows_exact(
    data: dict[str, Any], timings: list[dict[str, Any]]
) -> list[tuple[float, float]]:
    counts, total_tokens = _scene_counts(data)
    if not timings:
        raise ValueError("cannot map scenes without TTS word timings")

    timing_tokens: list[str] = []
    timing_owner: list[int] = []
    for timing_index, timing in enumerate(timings):
        parts = _spoken_tokens(str(timing.get("text", ""))) or [str(timing.get("text", "")).lower()]
        for part in parts:
            timing_tokens.append(part)
            timing_owner.append(timing_index)

    full_tokens = _spoken_tokens(str(data["narration"]))
    exact_token_match = timing_tokens == full_tokens and len(timing_owner) == total_tokens

    windows: list[tuple[float, float]] = []
    token_cursor = 0
    for scene_index, count in enumerate(counts):
        next_cursor = token_cursor + count
        if exact_token_match:
            start_idx = timing_owner[token_cursor]
            end_idx = timing_owner[next_cursor - 1]
        else:
            start_idx = min(len(timings) - 1, round(token_cursor * len(timings) / total_tokens))
            end_exclusive = max(
                start_idx + 1,
                round(next_cursor * len(timings) / total_tokens),
            )
            end_idx = min(len(timings) - 1, end_exclusive - 1)

        start = float(timings[start_idx]["start"])
        end = float(timings[end_idx]["start"]) + float(timings[end_idx]["duration"])
        if scene_index == 0:
            start = 0.0
        if scene_index == len(counts) - 1:
            last_word_end = float(timings[-1]["start"]) + float(timings[-1]["duration"])
            end = max(end, last_word_end) + TAIL_HOLD_SECONDS
        windows.append((start, max(start + 0.35, end)))
        token_cursor = next_cursor

    return windows


def _render_still_clip(image: Path, duration: float, output: Path, *, pose_index: int = 0) -> None:
    frames = max(1, math.ceil(duration * renderer.FPS))
    horizontal_bias = "iw/2-(iw/zoom/2)"
    if pose_index % 3 == 1:
        horizontal_bias = "iw/2-(iw/zoom/2)-8"
    elif pose_index % 3 == 2:
        horizontal_bias = "iw/2-(iw/zoom/2)+8"
    vf = (
        f"scale={renderer.WIDTH}:{renderer.HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={renderer.WIDTH}:{renderer.HEIGHT},"
        f"zoompan=z='min(zoom+0.00038,1.045)':x='{horizontal_bias}':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={renderer.WIDTH}x{renderer.HEIGHT}:fps={renderer.FPS},format=yuv420p"
    )
    renderer.run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(image), "-vf", vf,
        "-t", f"{duration:.3f}", "-an", "-c:v", "libx264", "-preset", "veryfast", str(output),
    ])


def render_video_with_tail(
    images: list[Path],
    windows: list[tuple[float, float]],
    audio: Path,
    ass: Path,
    output: Path,
    work_dir: Path,
) -> None:
    clips: list[Path] = []
    image_dir = work_dir / "images"
    for idx, (image, (start, end)) in enumerate(zip(images, windows), start=1):
        duration = max(0.35, end - start)
        pose_paths = sorted(image_dir.glob(f"scene_{idx:02d}_pose_*.png"))
        if not pose_paths:
            clip = work_dir / f"clip_{idx:02d}.mp4"
            _render_still_clip(image, duration, clip)
            clips.append(clip)
            continue

        slot = duration / len(pose_paths)
        pose_clips: list[Path] = []
        for pose_index, pose_path in enumerate(pose_paths, start=1):
            pose_clip = work_dir / f"clip_{idx:02d}_pose_{pose_index:02d}.mp4"
            _render_still_clip(pose_path, slot, pose_clip, pose_index=pose_index)
            pose_clips.append(pose_clip)

        scene_concat = work_dir / f"concat_scene_{idx:02d}.txt"
        scene_concat.write_text(
            "\n".join(f"file '{p.resolve()}'" for p in pose_clips), encoding="utf-8"
        )
        clip = work_dir / f"clip_{idx:02d}.mp4"
        renderer.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(scene_concat),
            "-c", "copy", str(clip),
        ])
        clips.append(clip)

    concat_file = work_dir / "concat.txt"
    concat_file.write_text("\n".join(f"file '{p.resolve()}'" for p in clips), encoding="utf-8")
    silent = work_dir / "silent.mp4"
    renderer.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c", "copy", str(silent),
    ])
    ass_path = str(ass.resolve()).replace(":", r"\:")
    renderer.run([
        "ffmpeg", "-y", "-i", str(silent), "-i", str(audio),
        "-vf", f"ass={ass_path}",
        "-af", f"apad=pad_dur={TAIL_HOLD_SECONDS}",
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-shortest",
        "-movflags", "+faststart", str(output),
    ])


def qc_60_plus(
    video: Path,
    data: dict[str, Any],
    report_path: Path,
    image_manifest: list[dict[str, Any]],
) -> dict[str, Any]:
    info = renderer.ffprobe_json(video)
    streams = info.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
    duration = float(info.get("format", {}).get("duration", 0) or 0)
    checks = {
        "file_exists": video.exists() and video.stat().st_size > 100_000,
        "vertical_1080x1920": video_stream.get("width") == renderer.WIDTH
        and video_stream.get("height") == renderer.HEIGHT,
        "audio_present": bool(audio_stream),
        "duration_60_to_120_seconds": MIN_VIDEO_SECONDS <= duration <= MAX_VIDEO_SECONDS,
        "at_least_6_scenes": len(data["scenes"]) >= 6,
        "all_scene_images_prepared": len(image_manifest) == len(data["scenes"]),
        "caption_present": bool(data.get("caption")),
    }
    report = {
        "passed": all(checks.values()),
        "duration": duration,
        "checks": checks,
        "scene_images": image_manifest,
    }
    report_path.write_text(renderer.json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


# Patch only production policies. Base renderer remains backward-compatible.
renderer.create_ass = create_safe_ass
renderer.scene_windows = scene_windows_exact
renderer.prepare_images = prepare_images_with_keyframes
renderer.render_video = render_video_with_tail
renderer.qc = qc_60_plus


def entry_main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--validate-assets", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return renderer.self_test()
    if not args.input:
        parser.error("--input is required unless --self-test is used")

    input_path = args.input if args.input.is_absolute() else renderer.ROOT / args.input
    data = renderer.json.loads(input_path.read_text(encoding="utf-8"))
    validate_long_package(data, require_assets=not args.dry_run)

    if args.validate_assets:
        _paths, manifest = prepare_images_with_keyframes(
            data, renderer.WORK / "_asset_validation_v2", dry_run=False
        )
        print(renderer.json.dumps({"valid": True, "scenes": manifest}, ensure_ascii=False, indent=2))
        return 0
    return renderer.process(input_path, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(entry_main())
