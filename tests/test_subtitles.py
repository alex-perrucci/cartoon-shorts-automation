from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import render_entry


class SubtitleLayoutTests(unittest.TestCase):
    def test_long_word_is_scaled_inside_safe_area(self) -> None:
        text = "RIPROGRAMMAZIONE"
        size = render_entry._fit_font_size(text)
        self.assertGreaterEqual(size, render_entry.MIN_FONT_SIZE)
        self.assertLessEqual(
            render_entry._text_width(text, size),
            render_entry.SAFE_TEXT_WIDTH + 2,
        )

    def test_two_word_group_is_split_when_too_wide(self) -> None:
        timings = [
            {"text": "STRAORDINARIAMENTE", "start": 0.0, "duration": 0.3},
            {"text": "CONVENIENTE", "start": 0.3, "duration": 0.3},
        ]
        group = render_entry._next_group(timings, 0)
        self.assertEqual(len(group), 1)

    def test_ass_uses_explicit_dynamic_font_size(self) -> None:
        timings = [
            {"text": "QUESTO", "start": 0.0, "duration": 0.25},
            {"text": "CAMBIA", "start": 0.25, "duration": 0.25},
            {"text": "TUTTO", "start": 0.5, "duration": 0.25},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "captions.ass"
            render_entry.create_safe_ass(timings, path)
            content = path.read_text(encoding="utf-8")
        self.assertIn("{\\fs", content)
        self.assertIn("MarginL,MarginR", content)
        self.assertIn("130,130", content)


if __name__ == "__main__":
    unittest.main()
