import unittest

import render_entry


class KeyframeValidationTests(unittest.TestCase):
    def base_data(self):
        return {
            "scenes": [
                {
                    "narration": "beat",
                    "visual": "A visual beat.",
                    "keyframes": [
                        {"image_b64": "work/prepared_assets/test/scene_01_pose_01.b64"},
                        {"image_b64": "work/prepared_assets/test/scene_01_pose_02.b64"},
                    ],
                }
            ]
        }

    def test_two_keyframes_are_valid(self):
        render_entry.validate_keyframes(self.base_data(), require_assets=True)

    def test_one_keyframe_is_rejected(self):
        data = self.base_data()
        data["scenes"][0]["keyframes"] = [
            {"image_b64": "work/prepared_assets/test/scene_01_pose_01.b64"}
        ]
        with self.assertRaisesRegex(ValueError, "2-4"):
            render_entry.validate_keyframes(data, require_assets=True)

    def test_five_keyframes_are_rejected(self):
        data = self.base_data()
        data["scenes"][0]["keyframes"] = [
            {"image_b64": f"work/prepared_assets/test/pose_{i}.b64"}
            for i in range(5)
        ]
        with self.assertRaisesRegex(ValueError, "2-4"):
            render_entry.validate_keyframes(data, require_assets=True)

    def test_keyframe_path_must_be_b64(self):
        data = self.base_data()
        data["scenes"][0]["keyframes"][1]["image_b64"] = "work/prepared_assets/test/pose.png"
        with self.assertRaisesRegex(ValueError, "must point to a .b64"):
            render_entry.validate_keyframes(data, require_assets=True)

    def test_no_keyframes_remains_backward_compatible(self):
        data = {"scenes": [{"narration": "beat", "visual": "A visual beat."}]}
        render_entry.validate_keyframes(data, require_assets=True)


if __name__ == "__main__":
    unittest.main()
