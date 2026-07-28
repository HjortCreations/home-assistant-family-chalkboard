from __future__ import annotations

import importlib.util
import json
import struct
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_FILE = PROJECT_ROOT / "custom_components" / "family_chalkboard" / "model.py"
SPEC = importlib.util.spec_from_file_location("family_chalkboard_model", MODEL_FILE)
assert SPEC is not None and SPEC.loader is not None
model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(model)

VALID_STATE = {
    "version": 1,
    "note": "Swimming bag by the door",
    "strokes": [
        {
            "mode": "draw",
            "color": "#F29AB2",
            "width": 8,
            "points": [
                {"x": 0.1, "y": 0.2},
                {"x": 0.3, "y": 0.4},
            ],
        }
    ],
}


class HomeAssistantModelTests(unittest.TestCase):
    def test_valid_state_is_normalized(self) -> None:
        normalized = model.validate_state(VALID_STATE)
        self.assertEqual(normalized["version"], 1)
        self.assertEqual(normalized["strokes"][0]["color"], "#f29ab2")
        self.assertEqual(normalized["strokes"][0]["width"], 8.0)

    def test_rejects_non_json_value(self) -> None:
        invalid = dict(VALID_STATE)
        invalid["extra"] = object()
        with self.assertRaises(model.InvalidState):
            model.validate_state(invalid)

    def test_rejects_invalid_width(self) -> None:
        invalid = json.loads(json.dumps(VALID_STATE))
        invalid["strokes"][0]["width"] = 100
        with self.assertRaises(model.InvalidState):
            model.validate_state(invalid)

    def test_rejects_point_outside_board(self) -> None:
        invalid = json.loads(json.dumps(VALID_STATE))
        invalid["strokes"][0]["points"][0]["y"] = -0.01
        with self.assertRaises(model.InvalidState):
            model.validate_state(invalid)

    def test_rejects_oversized_note(self) -> None:
        invalid = {"note": "x" * 1001, "strokes": []}
        with self.assertRaises(model.InvalidState):
            model.validate_state(invalid)


class HacsLayoutTests(unittest.TestCase):
    def test_hacs_manifest_and_integration_layout(self) -> None:
        hacs = json.loads((PROJECT_ROOT / "hacs.json").read_text(encoding="utf-8"))
        manifest = json.loads(
            (
                PROJECT_ROOT
                / "custom_components"
                / "family_chalkboard"
                / "manifest.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(hacs["name"], "Family Chalkboard")
        self.assertEqual(manifest["domain"], "family_chalkboard")
        self.assertTrue(manifest["config_flow"])
        self.assertTrue(manifest["single_config_entry"])
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+$")

    def test_required_runtime_files_are_inside_integration(self) -> None:
        integration = PROJECT_ROOT / "custom_components" / "family_chalkboard"
        for relative_path in (
            "__init__.py",
            "config_flow.py",
            "manifest.json",
            "brand/icon.png",
            "brand/icon@2x.png",
            "translations/en.json",
            "translations/sv.json",
            "frontend/family-chalkboard-panel.js",
        ):
            with self.subTest(relative_path=relative_path):
                self.assertTrue((integration / relative_path).is_file())

    def test_brand_icons_have_home_assistant_dimensions(self) -> None:
        brand = PROJECT_ROOT / "custom_components" / "family_chalkboard" / "brand"
        for filename, expected_size in (
            ("icon.png", 256),
            ("icon@2x.png", 512),
        ):
            with self.subTest(filename=filename):
                data = (brand / filename).read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                width, height = struct.unpack(">II", data[16:24])
                self.assertEqual((width, height), (expected_size, expected_size))


if __name__ == "__main__":
    unittest.main()
