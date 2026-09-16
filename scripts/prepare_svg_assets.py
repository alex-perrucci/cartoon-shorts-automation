from __future__ import annotations

import argparse
import base64
import io
import json
import shutil
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 1080
HEIGHT = 1920
MAX_SVG_BYTES = 2 * 1024 * 1024


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


def render_svg(svg_path: Path, *, scene_no: int) -> bytes:
    if not svg_path.is_file():
        raise ValueError(f"scene {scene_no} SVG asset not found: {svg_path.relative_to(ROOT)}")
    if svg_path.suffix.lower() != ".svg":
        raise ValueError(f"scene {scene_no} image_svg_source must point to a .svg file")
    raw_svg = svg_path.read_bytes()
    if not raw_svg or len(raw_svg) > MAX_SVG_BYTES:
        raise ValueError(f"scene {scene_no} SVG asset is empty or too large")
    try:
        png = cairosvg.svg2png(
            bytestring=raw_svg,
            output_width=WIDTH,
            output_height=HEIGHT,
        )
        with Image.open(io.BytesIO(png)) as image:
            image.verify()
    except Exception as exc:
        raise ValueError(f"scene {scene_no} SVG could not be rendered") from exc
    return png


def prepare(manifest_path: Path) -> int:
    manifest_path = manifest_path if manifest_path.is_absolute() else ROOT / manifest_path
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    scenes = data.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise ValueError("manifest has no scenes")

    generated_roots: set[Path] = set()
    prepared = 0
    for idx, scene in enumerate(scenes, start=1):
        source = scene.get("image_svg_source")
        if not source:
            continue
        target = scene.get("image_b64")
        if not target:
            raise ValueError(f"scene {idx} with image_svg_source must also define image_b64")

        svg_path = resolve_repo_path(str(source), field=f"scene {idx} image_svg_source")
        target_path = resolve_repo_path(str(target), field=f"scene {idx} image_b64")
        if target_path.suffix.lower() != ".b64":
            raise ValueError(f"scene {idx} image_b64 must point to a .b64 file")
        if not str(target_path.relative_to(ROOT)).startswith("work/prepared_assets/"):
            raise ValueError(f"scene {idx} generated image_b64 must live under work/prepared_assets/")

        generated_roots.add(ROOT / "work" / "prepared_assets" / str(data.get("id", "package")))
        png = render_svg(svg_path, scene_no=idx)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(base64.b64encode(png).decode("ascii"), encoding="ascii")
        prepared += 1
        print(f"Prepared scene {idx}: {source} -> {target} ({len(png)} PNG bytes)")

    if prepared == 0:
        print("No SVG-backed scenes to prepare; existing image_b64 assets will be used.")
    return prepared


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    prepare(args.manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
