from __future__ import annotations

import unittest

from scripts import upload_youtube


class YouTubeTitleTests(unittest.TestCase):
    def test_hashtags_are_appended_to_title(self) -> None:
        title = upload_youtube._compose_title(
            "Ti mancano 5 euro e ne spendi 20",
            ["shoppingonline", "marketing", "soldi"],
        )
        self.assertTrue(title.endswith("#shoppingonline #marketing #soldi"))
        self.assertLessEqual(len(title), 100)

    def test_long_title_is_trimmed_to_word_boundary_and_keeps_hashtags(self) -> None:
        base = "Questo è un titolo deliberatamente molto lungo che deve essere accorciato senza superare mai il limite imposto da YouTube"
        title = upload_youtube._compose_title(base, ["marketing", "soldi", "shopping"])
        self.assertLessEqual(len(title), 100)
        self.assertIn("#marketing", title)
        self.assertIn("#soldi", title)
        self.assertIn("#shopping", title)
        self.assertIn("…", title)

    def test_duplicate_hashtags_are_removed(self) -> None:
        title = upload_youtube._compose_title("Titolo", ["marketing", "#Marketing", "soldi"])
        self.assertEqual(title.count("#marketing"), 1)
        self.assertEqual(title.count("#Marketing"), 0)


if __name__ == "__main__":
    unittest.main()
