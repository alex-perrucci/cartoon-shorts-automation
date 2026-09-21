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
        self.assertIn(",2,130,130,265,1", content)


class SceneSyncTests(unittest.TestCase):
    def test_scene_windows_follow_exact_scene_word_boundaries(self) -> None:
        data = {
            "narration": "uno due tre quattro cinque sei",
            "scenes": [
                {"narration": "uno due"},
                {"narration": "tre quattro cinque"},
                {"narration": "sei"},
            ],
        }
        timings = [
            {"text": word, "start": i * 0.5, "duration": 0.4}
            for i, word in enumerate("uno due tre quattro cinque sei".split())
        ]
        windows = render_entry.scene_windows_exact(data, timings)
        self.assertEqual(windows[0], (0.0, 0.9))
        self.assertEqual(windows[1], (1.0, 2.4))
        self.assertAlmostEqual(windows[2][0], 2.5)
        self.assertAlmostEqual(windows[2][1], 2.9 + render_entry.TAIL_HOLD_SECONDS)

    def test_scene_narration_must_partition_full_narration(self) -> None:
        data = {
            "narration": "uno due tre quattro",
            "scenes": [
                {"narration": "uno due"},
                {"narration": "quattro tre"},
            ],
        }
        timings = [
            {"text": word, "start": i * 0.5, "duration": 0.4}
            for i, word in enumerate("uno due tre quattro".split())
        ]
        with self.assertRaisesRegex(ValueError, "exact sequential partition"):
            render_entry.scene_windows_exact(data, timings)

    def test_minimum_narration_contract_is_150_words(self) -> None:
        self.assertEqual(render_entry.MIN_NARRATION_WORDS, 150)
        self.assertEqual(render_entry.MIN_VIDEO_SECONDS, 60.0)


if __name__ == "__main__":
    unittest.main()
