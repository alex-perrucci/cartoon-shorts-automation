from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.send_social_metadata import build_message


class SocialMetadataTelegramTests(unittest.TestCase):
    def test_message_contains_tiktok_and_final_youtube_metadata(self) -> None:
        manifest = {
            "title": "Base",
            "caption": "Fallback",
            "youtube": {
                "title": "Titolo YouTube",
                "description": "Descrizione utile.",
                "hashtags": ["BNPL", "Rate", "Soldi"],
                "tags": ["bnpl"],
            },
            "tiktok": {
                "caption": "Caption TikTok pronta",
                "hashtags": ["BNPL", "rate", "soldi"],
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            receipt = Path(tmp) / "youtube.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            receipt.write_text(json.dumps({"video_id": "abc123"}), encoding="utf-8")
            message = build_message(path, receipt)

        self.assertIn("Caption TikTok pronta #BNPL #rate #soldi", message)
        self.assertIn("Titolo: Titolo YouTube #BNPL #Rate #Soldi", message)
        self.assertIn("Descrizione utile.", message)
        self.assertIn("Video ID: abc123", message)


if __name__ == "__main__":
    unittest.main()
