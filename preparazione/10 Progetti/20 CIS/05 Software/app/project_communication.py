from __future__ import annotations

from pathlib import Path


def load_project_communication_style(project_key: str, projects_root: Path | str) -> dict[str, object]:
    config_path = Path(projects_root) / project_key / "communication_style.yaml"
    if not config_path.exists():
        return {"tone": {}, "messages": {}, "outreach": {}}

    data: dict[str, object] = {"tone": {}, "messages": {}, "outreach": {}}
    current_section = ""
    current_list_key = ""

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()

        if indent == 0 and stripped.endswith(":"):
            current_section = stripped[:-1]
            current_list_key = ""
            if current_section not in data:
                data[current_section] = {}
            continue

        if indent == 2 and stripped.endswith(":"):
            current_list_key = stripped[:-1]
            section = data.setdefault(current_section, {})
            if isinstance(section, dict):
                section[current_list_key] = []
            continue

        if indent == 2 and ":" in stripped:
            key, value = stripped.split(":", 1)
            section = data.setdefault(current_section, {})
            if isinstance(section, dict):
                section[key.strip()] = value.strip()
            current_list_key = ""
            continue

        if indent == 4 and stripped.startswith("- "):
            section = data.setdefault(current_section, {})
            if isinstance(section, dict):
                section.setdefault(current_list_key, [])
                current_value = section[current_list_key]
                if isinstance(current_value, list):
                    current_value.append(stripped[2:].strip())

    return data
