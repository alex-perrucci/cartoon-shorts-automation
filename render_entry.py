from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import ImageFont

import main as renderer

BASE_FONT_SIZE = 104
MIN_FONT_SIZE = 58
SAFE_TEXT_WIDTH = 820
MAX_WORDS_PER_CAPTION = 2


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
        # Keep the preferred large subtitle size whenever possible. If the
        # second word would force a major shrink, display it in the next card.
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
        # Explicit font size makes every card deterministic and guarantees
        # unusually long words still fit inside the horizontal safe area.
        lines.append(
            f"Dialogue: 0,{renderer.ass_time(start)},{renderer.ass_time(end)},Default,,0,0,0,,"
            f"{{\\fs{font_size}}}{escaped}\n"
        )
        i += len(group)

    path.write_text("".join(lines), encoding="utf-8")


# Keep the mature renderer and replace only the subtitle layout policy.
renderer.create_ass = create_safe_ass


if __name__ == "__main__":
    raise SystemExit(renderer.main())
