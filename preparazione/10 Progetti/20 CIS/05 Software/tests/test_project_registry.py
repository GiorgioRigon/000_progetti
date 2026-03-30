from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.project_registry import list_projects, load_project_config  # noqa: E402


class ProjectRegistryTests(unittest.TestCase):
    def test_load_project_config_and_list_projects(self) -> None:
        melodema_config = load_project_config(BASE_DIR / "projects" / "melodema")
        self.assertEqual(melodema_config["key"], "melodema")

        projects = list_projects(BASE_DIR / "projects")
        project_keys = [project["key"] for project in projects]
        self.assertIn("melodema", project_keys)
        self.assertIn("ethics", project_keys)

    def test_list_projects_skips_template_and_uses_fallbacks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "_template").mkdir()
            custom = root / "custom_project"
            custom.mkdir()

            projects = list_projects(root)
            self.assertEqual(projects, [{"key": "custom_project", "name": "Custom Project"}])


if __name__ == "__main__":
    unittest.main()
