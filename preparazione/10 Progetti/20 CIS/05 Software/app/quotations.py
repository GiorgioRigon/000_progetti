from __future__ import annotations

from pathlib import Path
from typing import Any


def list_intake_schemas(project_key: str, projects_root: Path | str) -> list[dict[str, str]]:
    schemas_dir = Path(projects_root) / project_key / "intake_schemas"
    if not schemas_dir.exists():
        return []

    schemas: list[dict[str, str]] = []
    for schema_path in sorted(schemas_dir.glob("*.yaml")):
        schema = load_intake_schema(project_key, projects_root, schema_path.stem)
        schemas.append(
            {
                "key": schema["key"],
                "label": str(schema.get("title") or _build_label(schema_path.stem)),
                "path": str(schema_path),
            }
        )
    return schemas


def resolve_default_intake_schema_key(project_key: str, projects_root: Path | str) -> str | None:
    schemas = list_intake_schemas(project_key, projects_root)
    if not schemas:
        return None
    return str(schemas[0]["key"])


def load_intake_schema(
    project_key: str,
    projects_root: Path | str,
    schema_key: str,
) -> dict[str, Any]:
    schema_path = Path(projects_root) / project_key / "intake_schemas" / f"{schema_key}.yaml"
    if not schema_path.exists():
        return {"key": schema_key, "title": _build_label(schema_key), "sections": []}

    return _parse_intake_schema(schema_path, schema_key)


def load_quotation_config(project_key: str, projects_root: Path | str) -> dict[str, str]:
    config_path = Path(projects_root) / project_key / "quotation_config.yaml"
    if not config_path.exists():
        return {}

    config: dict[str, str] = {}
    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if key.strip() in {"module_name", "default_currency", "default_validity_days"}:
            config[key.strip()] = value.strip()
    return config


def load_price_list(project_key: str, projects_root: Path | str) -> list[dict[str, Any]]:
    price_list_path = Path(projects_root) / project_key / "price_list.yaml"
    if not price_list_path.exists():
        return []

    price_list: list[dict[str, Any]] = []
    current_item: dict[str, Any] | None = None
    for raw_line in price_list_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped == "price_list:":
            continue
        if stripped.startswith("- code:"):
            if current_item:
                price_list.append(current_item)
            current_item = {"code": _parse_scalar(stripped.split(":", 1)[1])}
            continue
        if current_item is None or ":" not in stripped:
            continue
        key, raw_value = stripped.split(":", 1)
        current_item[key.strip()] = _parse_scalar(raw_value)

    if current_item:
        price_list.append(current_item)

    return price_list


def build_suggested_line_items(
    project_key: str,
    projects_root: Path | str,
    intake_data: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    intake_data = intake_data or {}
    price_list = load_price_list(project_key, projects_root)
    suggestions: list[dict[str, Any]] = []

    for item in price_list:
        suggestion = _build_line_item_suggestion(item, intake_data)
        if suggestion is not None:
            suggestions.append(suggestion)

    return suggestions


def quote_config_paths(project_key: str, projects_root: Path | str) -> dict[str, str]:
    project_dir = Path(projects_root) / project_key
    return {
        "quotation_config": str(project_dir / "quotation_config.yaml"),
        "price_list": str(project_dir / "price_list.yaml"),
    }


def extract_intake_submission(
    schema: dict[str, Any],
    form_data: Any,
) -> tuple[dict[str, str], list[str]]:
    payload: dict[str, str] = {}
    errors: list[str] = []

    for section in schema.get("sections", []):
        for field in section.get("fields", []):
            field_key = str(field.get("key") or "").strip()
            if not field_key:
                continue
            value = str(form_data.get(field_key, "") or "").strip()
            payload[field_key] = value
            if field.get("required") and not value:
                errors.append(f"Il campo '{field.get('label') or field_key}' e obbligatorio.")

    return payload, errors


def build_intake_initial_data(
    schema: dict[str, Any],
    organization: dict[str, Any] | None,
    stored_data: dict[str, Any] | None,
) -> dict[str, str]:
    initial_data: dict[str, str] = {}
    stored_data = stored_data or {}

    for section in schema.get("sections", []):
        for field in section.get("fields", []):
            field_key = str(field.get("key") or "").strip()
            if not field_key:
                continue
            stored_value = stored_data.get(field_key)
            if stored_value is not None and str(stored_value).strip():
                initial_data[field_key] = str(stored_value)
                continue
            initial_data[field_key] = _prefill_from_organization(field_key, organization)

    return initial_data


def _parse_intake_schema(schema_path: Path, schema_key: str) -> dict[str, Any]:
    schema: dict[str, Any] = {
        "key": schema_key,
        "title": _build_label(schema_key),
        "sections": [],
    }
    current_section: dict[str, Any] | None = None
    current_field: dict[str, Any] | None = None
    inside_fields = False

    for raw_line in schema_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if stripped.startswith("title:"):
            schema["title"] = _parse_scalar(stripped.split(":", 1)[1])
            continue
        if stripped == "sections:":
            continue
        if stripped.startswith("- key:") and indent <= 2:
            current_section = {
                "key": _parse_scalar(stripped.split(":", 1)[1]),
                "label": "",
                "fields": [],
            }
            schema["sections"].append(current_section)
            current_field = None
            inside_fields = False
            continue
        if current_section is None:
            continue
        if stripped == "fields:":
            inside_fields = True
            continue
        if inside_fields and stripped.startswith("- key:"):
            current_field = {
                "key": _parse_scalar(stripped.split(":", 1)[1]),
                "label": "",
                "type": "text",
                "required": False,
                "options": [],
                "placeholder": "",
                "help": "",
                "rows": "3",
            }
            current_section["fields"].append(current_field)
            continue
        if ":" not in stripped:
            continue

        key, raw_value = stripped.split(":", 1)
        value = _parse_scalar(raw_value)
        if inside_fields and current_field is not None:
            _apply_field_property(current_field, key.strip(), value)
        else:
            _apply_section_property(current_section, key.strip(), value)

    return schema


def _apply_section_property(section: dict[str, Any], key: str, value: str) -> None:
    if key == "label":
        section["label"] = value


def _apply_field_property(field: dict[str, Any], key: str, value: str) -> None:
    if key in {"label", "type", "placeholder", "help", "rows"}:
        field[key] = value
        return
    if key == "required":
        field["required"] = value.lower() == "true"
        return
    if key == "options":
        field["options"] = [part.strip() for part in value.split("|") if part.strip()]


def _build_line_item_suggestion(
    price_item: dict[str, Any],
    intake_data: dict[str, Any],
) -> dict[str, Any] | None:
    code = str(price_item.get("code") or "").strip()
    if not code:
        return None

    quantity = _resolve_quantity(price_item, intake_data)
    if quantity is None or quantity <= 0:
        return None

    return {
        "code": code,
        "title": str(price_item.get("title") or code),
        "line_type": str(price_item.get("line_type") or "custom"),
        "description": str(price_item.get("description") or "").strip() or None,
        "quantity": quantity,
        "unit": str(price_item.get("unit") or "").strip() or None,
        "unit_price": _parse_float(price_item.get("unit_price"), default=0.0),
        "pricing_source": str(price_item.get("pricing_source") or "rule_based"),
    }


def _resolve_quantity(price_item: dict[str, Any], intake_data: dict[str, Any]) -> float | None:
    objective_quantities = _parse_mapping(str(price_item.get("objective_quantities") or ""))
    if objective_quantities:
        objective = str(intake_data.get("pdr125_objective") or "").strip().lower()
        if not objective:
            return None
        mapped_quantity = objective_quantities.get(objective)
        return _parse_float(mapped_quantity, default=0.0) if mapped_quantity is not None else None

    trigger_field = str(price_item.get("trigger_field") or "").strip()
    if trigger_field:
        trigger_values = _parse_list(str(price_item.get("trigger_values") or ""))
        field_value = str(intake_data.get(trigger_field) or "").strip().lower()
        if field_value not in trigger_values:
            return None

    keyword_field = str(price_item.get("keyword_trigger_field") or "").strip()
    if keyword_field:
        keywords = _parse_list(str(price_item.get("keyword_trigger_keywords") or ""))
        haystack = str(intake_data.get(keyword_field) or "").strip().lower()
        if not haystack or not any(keyword in haystack for keyword in keywords):
            return None

    default_quantity = _parse_float(price_item.get("default_quantity"), default=1.0)
    return default_quantity


def _parse_scalar(raw_value: str) -> str:
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_list(raw_value: str) -> list[str]:
    return [part.strip().lower() for part in raw_value.split("|") if part.strip()]


def _parse_mapping(raw_value: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for part in raw_value.split("|"):
        cleaned = part.strip()
        if not cleaned or "=" not in cleaned:
            continue
        key, value = cleaned.split("=", 1)
        mapping[key.strip().lower()] = value.strip()
    return mapping


def _parse_float(raw_value: Any, default: float = 0.0) -> float:
    try:
        return float(str(raw_value).strip())
    except (TypeError, ValueError):
        return default


def _prefill_from_organization(field_key: str, organization: dict[str, Any] | None) -> str:
    if organization is None:
        return ""

    aliases = {
        "organization_name": "name",
        "website": "website",
        "city": "city",
        "country": "country",
        "email": "email",
        "phone": "phone",
        "employee_count": "employee_count",
        "sector": "sector",
    }
    mapped_key = aliases.get(field_key, field_key)
    value = organization.get(mapped_key)
    return "" if value is None else str(value)


def _build_label(schema_key: str) -> str:
    return schema_key.replace("_", " ").replace("-", " ").title()
