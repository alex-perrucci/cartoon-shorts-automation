from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts import upload_tiktok_direct


class TikTokDirectMetadataTests(unittest.TestCase):
    def _manifest(self, payload: dict) -> Path:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(payload, tmp, ensure_ascii=False)
        tmp.close()
        return Path(tmp.name)

    def test_caption_appends_relevant_hashtags_and_deduplicates(self) -> None:
        path = self._manifest({
            "tiktok": {
                "caption": "Ti mancano cinque euro e ne spendi venti.",
                "hashtags": ["shoppingonline", "#Marketing", "marketing", "soldi"],
            }
        })
        caption = upload_tiktok_direct.compose_caption(path)
        self.assertIn("#shoppingonline", caption)
        self.assertIn("#Marketing", caption)
        self.assertIn("#soldi", caption)
        self.assertEqual(caption.casefold().count("#marketing"), 1)
        self.assertLessEqual(upload_tiktok_direct._utf16_units(caption), 2200)

    def test_long_caption_is_trimmed_but_keeps_hashtags(self) -> None:
        path = self._manifest({
            "tiktok": {
                "caption": ("parola " * 500).strip(),
                "hashtags": ["marketing", "soldi", "shopping"],
            }
        })
        caption = upload_tiktok_direct.compose_caption(path)
        self.assertLessEqual(upload_tiktok_direct._utf16_units(caption), 2200)
        self.assertTrue(caption.endswith("#marketing #soldi #shopping"))


if __name__ == "__main__":
    unittest.main()
