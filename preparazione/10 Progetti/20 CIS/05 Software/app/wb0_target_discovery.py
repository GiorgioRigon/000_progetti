from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.workbot_profiles import normalize_profile_list, normalize_profile_text


DEFAULT_PROJECT_KEY = "melodema"


@dataclass(slots=True)
class CandidateOrganization:
    name: str
    organization_type: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    website: str | None = None
    notes: str | None = None
    source: str = "wb0_manual"
    review_status: str = "da_verificare"
    fit_label: str | None = None
    website_confirmed: str = "da_verificare"
    qualification_notes: str | None = None
    final_decision: str = "da_valutare"
    imported_organization_id: int | None = None
    imported_at: str | None = None


@dataclass(slots=True)
class DiscoveryRun:
    project_key: str
    research_goal: str
    project_context: str
    territory_target: str
    target_types: list[str]
    selected_sources: list[str]
    research_prompt: str
    prompt_variants: list[str]
    inclusion_criteria: list[str]
    exclusion_criteria: list[str]
    created_at: str
    candidate_count: int
    candidates: list[CandidateOrganization]


def parse_candidate_lines(raw_text: str) -> list[CandidateOrganization]:
    candidates: list[CandidateOrganization] = []

    for line_number, raw_line in enumerate(raw_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        parts = [part.strip() for part in line.split("|")]
        if not parts or not parts[0]:
            raise ValueError(
                f"Riga {line_number}: il nome della candidate organization e obbligatorio."
            )
        if len(parts) > 7:
            raise ValueError(
                f"Riga {line_number}: usa al massimo 7 campi separati da '|'."
            )

        padded_parts = parts + [""] * (7 - len(parts))
        candidates.append(
            CandidateOrganization(
                name=padded_parts[0],
                organization_type=_clean(padded_parts[1]),
                city=_clean(padded_parts[2]),
                region=_clean(padded_parts[3]),
                country=_clean(padded_parts[4]),
                website=_clean(padded_parts[5]),
                notes=_clean(padded_parts[6]),
            )
        )

    return candidates


def build_discovery_run(
    research_goal: str,
    project_context: str,
    territory_target: str,
    target_types_text: str,
    selected_sources: list[str],
    research_prompt: str,
    prompt_variants_text: str,
    inclusion_criteria_text: str,
    exclusion_criteria_text: str,
    raw_candidates: str,
    project_key: str = DEFAULT_PROJECT_KEY,
) -> DiscoveryRun:
    normalized_goal = research_goal.strip()
    normalized_context = project_context.strip()
    normalized_territory = territory_target.strip()
    normalized_sources = [source.strip() for source in selected_sources if source.strip()]
    normalized_prompt = research_prompt.strip()
    target_types = parse_multiline_field(target_types_text)
    prompt_variants = parse_multiline_field(prompt_variants_text)
    inclusion_criteria = parse_multiline_field(inclusion_criteria_text)
    exclusion_criteria = parse_multiline_field(exclusion_criteria_text)

    if not normalized_goal:
        raise ValueError("L'obiettivo ricerca e obbligatorio.")
    if not normalized_context:
        raise ValueError("Il contesto progetto e obbligatorio.")
    if not normalized_territory:
        raise ValueError("Il territorio target e obbligatorio.")
    if not target_types:
        raise ValueError("Inserisci almeno un tipo di target.")
    if not normalized_sources:
        raise ValueError("Seleziona almeno una fonte da interrogare.")
    if not normalized_prompt:
        raise ValueError("Il prompt di ricerca e obbligatorio.")
    if not inclusion_criteria:
        raise ValueError("Inserisci almeno un criterio di inclusione.")

    candidates = parse_candidate_lines(raw_candidates)
    if not candidates:
        raise ValueError("Inserisci almeno una candidate organization.")

    created_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return DiscoveryRun(
        project_key=project_key,
        research_goal=normalized_goal,
        project_context=normalized_context,
        territory_target=normalized_territory,
        target_types=target_types,
        selected_sources=normalized_sources,
        research_prompt=normalized_prompt,
        prompt_variants=prompt_variants,
        inclusion_criteria=inclusion_criteria,
        exclusion_criteria=exclusion_criteria,
        created_at=created_at,
        candidate_count=len(candidates),
        candidates=candidates,
    )


def save_discovery_run(run: DiscoveryRun, projects_root: Path | str) -> Path:
    root = Path(projects_root)
    output_dir = root / run.project_key / "wb0_target_discovery"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp_slug = run.created_at.replace(":", "").replace("-", "")
    goal_slug = _slugify(run.research_goal)
    run_path = output_dir / f"{timestamp_slug}_{goal_slug}.json"
    latest_path = output_dir / "latest.json"

    payload = _discovery_run_to_payload(run)
    _write_serialized_payload(run_path, latest_path, payload)
    return run_path


def update_discovery_run(
    run: DiscoveryRun,
    projects_root: Path | str,
    run_filename: str,
) -> Path:
    root = Path(projects_root)
    output_dir = root / run.project_key / "wb0_target_discovery"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_path = output_dir / run_filename
    if not run_path.exists():
        raise FileNotFoundError(f"Run file not found: {run_filename}")

    latest_path = output_dir / "latest.json"
    payload = _discovery_run_to_payload(run)
    _write_serialized_payload(run_path, latest_path, payload)
    return run_path


def load_latest_run(project_key: str, projects_root: Path | str) -> dict | None:
    latest_path = Path(projects_root) / project_key / "wb0_target_discovery" / "latest.json"
    if not latest_path.exists():
        return None
    return _normalize_run_payload(json.loads(latest_path.read_text(encoding="utf-8")))


def load_discovery_run(project_key: str, projects_root: Path | str, run_filename: str) -> dict | None:
    run_path = Path(projects_root) / project_key / "wb0_target_discovery" / run_filename
    if not run_path.exists() or not run_path.is_file():
        return None
    return _normalize_run_payload(json.loads(run_path.read_text(encoding="utf-8")))


def list_discovery_runs(project_key: str, projects_root: Path | str) -> list[dict[str, str | int]]:
    output_dir = Path(projects_root) / project_key / "wb0_target_discovery"
    if not output_dir.exists():
        return []

    runs: list[dict[str, str | int]] = []
    for run_path in sorted(output_dir.glob("*.json"), reverse=True):
        if run_path.name == "latest.json":
            continue
        payload = _normalize_run_payload(json.loads(run_path.read_text(encoding="utf-8")))
        runs.append(
            {
                "filename": run_path.name,
                "research_goal": str(payload.get("research_goal", "")),
                "territory_target": str(payload.get("territory_target", "")),
                "created_at": str(payload.get("created_at", "")),
                "candidate_count": int(payload.get("candidate_count", 0)),
            }
        )
    return runs


def delete_discovery_run(project_key: str, projects_root: Path | str, run_filename: str) -> bool:
    output_dir = Path(projects_root) / project_key / "wb0_target_discovery"
    run_path = output_dir / run_filename
    if not run_path.exists() or not run_path.is_file():
        return False
    if run_path.name == "latest.json":
        return False
    run_path.unlink()
    return True


def reset_latest_run(project_key: str, projects_root: Path | str) -> bool:
    latest_path = Path(projects_root) / project_key / "wb0_target_discovery" / "latest.json"
    if not latest_path.exists():
        return False
    latest_path.unlink()
    return True


def update_candidate_review(
    project_key: str,
    projects_root: Path | str,
    run_filename: str,
    candidate_index: int,
    review_status: str,
    fit_label: str,
    website_confirmed: str,
    qualification_notes: str,
    final_decision: str,
) -> dict:
    payload = load_discovery_run(project_key, projects_root, run_filename)
    if payload is None:
        raise FileNotFoundError(f"Run file not found: {run_filename}")
    candidates = payload.get("candidates", [])
    if candidate_index < 0 or candidate_index >= len(candidates):
        raise IndexError("Candidate index out of range")

    candidate = candidates[candidate_index]
    candidate["review_status"] = review_status.strip() or "da_verificare"
    candidate["fit_label"] = _clean(fit_label)
    candidate["website_confirmed"] = website_confirmed.strip() or "da_verificare"
    candidate["qualification_notes"] = _clean(qualification_notes)
    candidate["final_decision"] = final_decision.strip() or "da_valutare"
    _write_run_payload(project_key, projects_root, run_filename, payload)
    return payload


def mark_candidate_imported(
    project_key: str,
    projects_root: Path | str,
    run_filename: str,
    candidate_index: int,
    organization_id: int,
) -> dict:
    payload = load_discovery_run(project_key, projects_root, run_filename)
    if payload is None:
        raise FileNotFoundError(f"Run file not found: {run_filename}")
    candidates = payload.get("candidates", [])
    if candidate_index < 0 or candidate_index >= len(candidates):
        raise IndexError("Candidate index out of range")

    candidate = candidates[candidate_index]
    candidate["final_decision"] = "importata"
    candidate["review_status"] = "importata"
    candidate["imported_organization_id"] = organization_id
    candidate["imported_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    _write_run_payload(project_key, projects_root, run_filename, payload)
    return payload


def parse_multiline_field(raw_text: str) -> list[str]:
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def build_prompt_preview(
    research_goal: str,
    project_context: str,
    territory_target: str,
    target_types_text: str,
    selected_sources: list[str],
    research_prompt: str,
    inclusion_criteria_text: str,
    exclusion_criteria_text: str,
    profile: dict | None = None,
) -> str:
    target_types = parse_multiline_field(target_types_text)
    inclusion_criteria = parse_multiline_field(inclusion_criteria_text)
    exclusion_criteria = parse_multiline_field(exclusion_criteria_text)
    normalized_profile = profile or {}
    profile_focus = normalize_profile_text(normalized_profile, "search_focus")
    profile_target_priorities = normalize_profile_list(normalized_profile, "target_priorities")
    profile_include_signals = normalize_profile_list(normalized_profile, "include_signals")
    profile_exclude_signals = normalize_profile_list(normalized_profile, "exclude_signals")
    profile_required_fields = normalize_profile_list(normalized_profile, "required_fields")
    profile_output_notes = normalize_profile_list(normalized_profile, "output_notes")
    if not any(
        [
            research_goal.strip(),
            project_context.strip(),
            territory_target.strip(),
            target_types,
            selected_sources,
            research_prompt.strip(),
            inclusion_criteria,
            exclusion_criteria,
            profile_focus,
            profile_target_priorities,
            profile_include_signals,
            profile_exclude_signals,
            profile_required_fields,
            profile_output_notes,
        ]
    ):
        return ""

    lines = [
        f"Obiettivo ricerca: {research_goal.strip() or '[da definire]'}",
        f"Contesto progetto: {project_context.strip() or '[da definire]'}",
        f"Territorio target: {territory_target.strip() or '[da definire]'}",
        f"Tipi di target: {', '.join(target_types) if target_types else '[da definire]'}",
        f"Fonti da interrogare: {', '.join(selected_sources) if selected_sources else '[da definire]'}",
    ]
    if profile_focus:
        lines.extend(["", f"Focus operativo del profilo: {profile_focus}"])
    if profile_target_priorities:
        lines.extend(["", "Target prioritari del profilo:", *[f"- {item}" for item in profile_target_priorities]])
    if profile_include_signals:
        lines.extend(["", "Segnali di buon fit:", *[f"- {item}" for item in profile_include_signals]])
    if profile_exclude_signals:
        lines.extend(["", "Segnali di esclusione o cautela:", *[f"- {item}" for item in profile_exclude_signals]])
    if profile_required_fields:
        lines.extend(["", "Campi minimi da raccogliere:", *[f"- {item}" for item in profile_required_fields]])
    lines.extend(
        [
            "",
            "Prompt base:",
            research_prompt.strip() or "[da definire]",
        ]
    )
    if inclusion_criteria:
        lines.extend(["", "Criteri di inclusione:", *[f"- {item}" for item in inclusion_criteria]])
    if exclusion_criteria:
        lines.extend(["", "Criteri di esclusione:", *[f"- {item}" for item in exclusion_criteria]])
    if profile_output_notes:
        lines.extend(["", "Note operative del profilo:", *[f"- {item}" for item in profile_output_notes]])
    return "\n".join(lines)


def load_project_sources(project_key: str, projects_root: Path | str) -> list[dict[str, str | bool]]:
    config_path = Path(projects_root) / project_key / "target_sources.yaml"
    if not config_path.exists():
        return []

    sources: list[dict[str, str | bool]] = []
    current: dict[str, str | bool] | None = None

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("- name:"):
            if current is not None:
                sources.append(current)
            current = {"name": line.split(":", 1)[1].strip(), "enabled": True}
        elif current is not None and ":" in line:
            key, value = line.split(":", 1)
            normalized_key = key.strip()
            normalized_value = value.strip()
            if normalized_key == "enabled":
                current["enabled"] = normalized_value.lower() == "true"
            else:
                current[normalized_key] = normalized_value

    if current is not None:
        sources.append(current)

    return sources


def _discovery_run_to_payload(run: DiscoveryRun) -> dict:
    return {
        "project_key": run.project_key,
        "research_goal": run.research_goal,
        "project_context": run.project_context,
        "territory_target": run.territory_target,
        "target_types": run.target_types,
        "selected_sources": run.selected_sources,
        "research_prompt": run.research_prompt,
        "prompt_variants": run.prompt_variants,
        "inclusion_criteria": run.inclusion_criteria,
        "exclusion_criteria": run.exclusion_criteria,
        "created_at": run.created_at,
        "candidate_count": run.candidate_count,
        "candidates": [asdict(candidate) for candidate in run.candidates],
    }


def _normalize_run_payload(payload: dict) -> dict:
    research_goal = str(payload.get("research_goal") or payload.get("keyword") or "")
    territory_target = str(payload.get("territory_target") or payload.get("geography") or "")
    project_context = str(payload.get("project_context") or "")
    target_types = list(payload.get("target_types") or [])
    selected_sources = list(payload.get("selected_sources") or [])
    research_prompt = str(payload.get("research_prompt") or _legacy_prompt(research_goal, territory_target))
    prompt_variants = list(payload.get("prompt_variants") or payload.get("manual_queries") or [])
    inclusion_criteria = list(payload.get("inclusion_criteria") or [])
    exclusion_criteria = list(payload.get("exclusion_criteria") or [])

    normalized_candidates = []
    for candidate in payload.get("candidates", []):
        normalized = dict(candidate)
        normalized.setdefault("source", "wb0_manual")
        normalized.setdefault("review_status", "da_verificare")
        normalized.setdefault("fit_label", None)
        normalized.setdefault("website_confirmed", "da_verificare")
        normalized.setdefault("qualification_notes", None)
        normalized.setdefault("final_decision", "da_valutare")
        normalized.setdefault("imported_organization_id", None)
        normalized.setdefault("imported_at", None)
        normalized_candidates.append(normalized)

    payload["research_goal"] = research_goal
    payload["project_context"] = project_context
    payload["territory_target"] = territory_target
    payload["target_types"] = target_types
    payload["selected_sources"] = selected_sources
    payload["research_prompt"] = research_prompt
    payload["prompt_variants"] = prompt_variants
    payload["inclusion_criteria"] = inclusion_criteria
    payload["exclusion_criteria"] = exclusion_criteria
    payload["candidate_count"] = int(payload.get("candidate_count", len(normalized_candidates)))
    payload["candidates"] = normalized_candidates
    return payload


def _write_run_payload(project_key: str, projects_root: Path | str, run_filename: str, payload: dict) -> None:
    output_dir = Path(projects_root) / project_key / "wb0_target_discovery"
    output_dir.mkdir(parents=True, exist_ok=True)
    run_path = output_dir / run_filename
    latest_path = output_dir / "latest.json"
    _write_serialized_payload(run_path, latest_path, payload)


def _write_serialized_payload(run_path: Path, latest_path: Path, payload: dict) -> None:
    serialized = json.dumps(payload, indent=2, ensure_ascii=True)
    run_path.write_text(serialized, encoding="utf-8")
    latest_path.write_text(serialized, encoding="utf-8")


def _clean(value: str) -> str | None:
    cleaned = value.strip()
    return cleaned or None


def _legacy_prompt(keyword: str, geography: str) -> str:
    if keyword and geography:
        return f"Cerca organizzazioni rilevanti per {keyword} in {geography}."
    return keyword or geography


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "discovery"
