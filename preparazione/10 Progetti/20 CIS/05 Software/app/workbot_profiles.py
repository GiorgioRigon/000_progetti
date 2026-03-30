from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_workbot_profiles(project_key: str, projects_root: Path | str) -> dict[str, Any]:
    profile_path = Path(projects_root) / project_key / "workbot_profiles.json"
    if not profile_path.exists():
        return {}
    return json.loads(profile_path.read_text(encoding="utf-8"))


def load_workbot_profile(
    project_key: str,
    workbot_key: str,
    projects_root: Path | str,
) -> dict[str, Any]:
    profiles = load_workbot_profiles(project_key, projects_root)
    profile = profiles.get(workbot_key, {})
    return profile if isinstance(profile, dict) else {}


def normalize_profile_list(profile: dict[str, Any], key: str) -> list[str]:
    value = profile.get(key, [])
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def normalize_profile_text(profile: dict[str, Any], key: str) -> str:
    value = profile.get(key, "")
    return str(value).strip() if value is not None else ""
