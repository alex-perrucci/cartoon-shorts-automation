import base64
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

import main


class AssetPipelineTests(unittest.TestCase):
    def make_image_bytes(self, size=(320, 568), color=(241, 232, 210)) -> bytes:
        image = Image.new("RGB", size, color)
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue()

    def make_scene(self, encoded: str, *, sha256: str | None = None) -> dict:
        scene = {
            "narration": "Una scena di prova abbastanza descrittiva.",
            "visual": "The recurring businessman stands in a simple room.",
            "image_base64": encoded,
        }
        if sha256 is not None:
            scene["image_sha256"] = sha256
        return scene

    def make_package(self, scene: dict) -> dict:
        narration = " ".join(["parola"] * 70)
        return {
            "id": "test-package",
            "title": "Test",
            "hook": "Questo è un test.",
            "narration": narration,
            "scenes": [dict(scene) for _ in range(5)],
            "caption": "Test caption",
            "hashtags": ["test"],
        }

    def test_valid_inline_asset_decodes_and_normalizes(self):
        raw = self.make_image_bytes()
        encoded = base64.b64encode(raw).decode("ascii")
        scene = self.make_scene(encoded, sha256=hashlib.sha256(raw).hexdigest())
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "scene.png"
            metadata = main.decode_scene_image(scene, 1, output)
            self.assertTrue(output.exists())
            with Image.open(output) as image:
                self.assertEqual(image.size, (main.WIDTH, main.HEIGHT))
                self.assertEqual(image.mode, "RGB")
            self.assertEqual(metadata["sha256"], hashlib.sha256(raw).hexdigest())

    def test_invalid_base64_is_rejected(self):
        scene = self.make_scene("not-valid-base64!!!")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "invalid base64"):
                main.decode_scene_image(scene, 1, Path(tmp) / "scene.png")

    def test_sha_mismatch_is_rejected(self):
        raw = self.make_image_bytes()
        encoded = base64.b64encode(raw).decode("ascii")
        scene = self.make_scene(encoded, sha256="0" * 64)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                main.decode_scene_image(scene, 1, Path(tmp) / "scene.png")

    def test_tiny_source_image_is_rejected(self):
        raw = self.make_image_bytes(size=(64, 64))
        encoded = base64.b64encode(raw).decode("ascii")
        scene = self.make_scene(encoded)
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "too small"):
                main.decode_scene_image(scene, 1, Path(tmp) / "scene.png")

    def test_path_traversal_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "escapes the repository root"):
            main.resolve_repo_path("../outside.b64", field="asset")

    def test_production_package_requires_scene_assets(self):
        scene = {
            "narration": "Una scena senza asset.",
            "visual": "The recurring businessman stands in a simple room.",
        }
        package = self.make_package(scene)
        with self.assertRaisesRegex(ValueError, "has no image_b64 asset"):
            main.validate_package(package, require_assets=True)

    def test_dry_run_package_can_omit_scene_assets(self):
        scene = {
            "narration": "Una scena senza asset.",
            "visual": "The recurring businessman stands in a simple room.",
        }
        package = self.make_package(scene)
        main.validate_package(package, require_assets=False)


if __name__ == "__main__":
    unittest.main()
