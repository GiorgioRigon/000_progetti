from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.workbot_profiles import load_workbot_profile, load_workbot_profiles  # noqa: E402


class WorkbotProfilesTests(unittest.TestCase):
    def test_load_existing_project_profiles(self) -> None:
        profiles = load_workbot_profiles("melodema", BASE_DIR / "projects")
        self.assertEqual(profiles["profile_name"], "Melodema base")

        wb1_profile = load_workbot_profile("consulenza_certificazione", "wb1", BASE_DIR / "projects")
        self.assertIn("HR manager o HR director", wb1_profile["priority_roles"])

    def test_missing_profile_file_returns_empty_dict(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(load_workbot_profiles("missing_project", temp_dir), {})
            self.assertEqual(load_workbot_profile("missing_project", "wb0", temp_dir), {})


if __name__ == "__main__":
    unittest.main()
