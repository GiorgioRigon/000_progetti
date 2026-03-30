from __future__ import annotations

from pathlib import Path


def list_projects(projects_root: Path | str) -> list[dict[str, str]]:
    root = Path(projects_root)
    if not root.exists():
        return []

    projects: list[dict[str, str]] = []
    for project_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        if project_dir.name.startswith("_"):
            continue
        project_config = load_project_config(project_dir)
        project_key = project_config.get("key", project_dir.name)
        project_name = project_config.get("name", project_dir.name.replace("_", " ").title())
        projects.append({"key": project_key, "name": project_name})
    return projects


def load_project_config(project_dir: Path | str) -> dict[str, str]:
    config_path = Path(project_dir) / "project_config.yaml"
    if not config_path.exists():
        return {}

    config: dict[str, str] = {}
    inside_project_block = False

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "project:":
            inside_project_block = True
            continue
        if inside_project_block and not raw_line.startswith("  "):
            break
        if inside_project_block and ":" in stripped:
            key, value = stripped.split(":", 1)
            config[key.strip()] = value.strip()

    return config
