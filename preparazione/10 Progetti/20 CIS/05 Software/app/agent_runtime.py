from __future__ import annotations

from typing import Any

from app.wb0_target_discovery import build_search_query_pack, parse_multiline_field


AGENT_STATUSES = [
    "queued",
    "running",
    "review",
    "approved",
    "rejected",
    "imported",
    "archived",
]


def build_wb0_run_spec(discovery_run: dict[str, Any], run_filename: str) -> dict[str, Any]:
    project_key = str(discovery_run.get("project_key") or "melodema")
    research_goal = str(discovery_run.get("research_goal") or "").strip()
    territory_target = str(discovery_run.get("territory_target") or "").strip()
    candidates = list(discovery_run.get("candidates") or [])
    title = f"WB0 batch | {research_goal or run_filename}"

    tasks = []
    for index, candidate in enumerate(candidates):
        candidate_name = str(candidate.get("name") or f"candidate-{index + 1}").strip()
        tasks.append(
            {
                "task_key": f"candidate_{index + 1}",
                "task_type": "wb0_candidate_review",
                "title": candidate_name,
                "status": "queued",
                "input_payload": {
                    "candidate_index": index,
                    "source_run_file": run_filename,
                    "candidate": dict(candidate),
                },
                "result_payload": {
                    "review_status": str(candidate.get("review_status") or "da_verificare"),
                    "final_decision": str(candidate.get("final_decision") or "da_valutare"),
                },
                "sort_order": index,
            }
        )

    return {
        "project_key": project_key,
        "agent_key": "wb0",
        "title": title,
        "objective": research_goal,
        "source_type": "wb0_discovery_run",
        "source_ref": run_filename,
        "input_payload": {
            "research_goal": research_goal,
            "territory_target": territory_target,
            "candidate_count": len(candidates),
        },
        "output_payload": {},
        "cost_estimate": float(len(candidates)) * 0.01,
        "tasks": tasks,
    }


def build_wb0_mission_spec(
    *,
    project_key: str,
    research_goal: str,
    project_context: str,
    territory_target: str,
    target_types_text: str,
    selected_sources: list[str],
    research_prompt: str,
    prompt_variants_text: str,
    inclusion_criteria_text: str,
    exclusion_criteria_text: str,
) -> dict[str, Any]:
    normalized_goal = research_goal.strip()
    normalized_context = project_context.strip()
    normalized_territory = territory_target.strip()
    normalized_sources = [source.strip() for source in selected_sources if source.strip()]
    target_types = parse_multiline_field(target_types_text)
    inclusion_criteria = parse_multiline_field(inclusion_criteria_text)
    exclusion_criteria = parse_multiline_field(exclusion_criteria_text)

    if not normalized_goal:
        raise ValueError("L'obiettivo ricerca WB0 e obbligatorio.")
    if not normalized_context:
        raise ValueError("Il contesto progetto WB0 e obbligatorio.")
    if not normalized_territory:
        raise ValueError("Il territorio target WB0 e obbligatorio.")
    if not target_types:
        raise ValueError("Inserisci almeno un tipo di target per la missione WB0.")
    if not normalized_sources:
        raise ValueError("Seleziona almeno una fonte per la missione WB0.")
    if not inclusion_criteria:
        raise ValueError("Inserisci almeno un criterio di inclusione per la missione WB0.")

    query_pack = build_search_query_pack(
        research_goal=normalized_goal,
        territory_target=normalized_territory,
        target_types_text=target_types_text,
        selected_sources=normalized_sources,
        research_prompt=research_prompt,
        prompt_variants_text=prompt_variants_text,
        inclusion_criteria_text=inclusion_criteria_text,
    )
    if not query_pack:
        raise ValueError("Non e stato possibile generare query operative per la missione WB0.")

    tasks = []
    for index, query in enumerate(query_pack):
        source_hint = normalized_sources[index % len(normalized_sources)]
        tasks.append(
            {
                "task_key": f"mission_query_{index + 1}",
                "task_type": "wb0_search_slice",
                "title": query,
                "status": "queued",
                "input_payload": {
                    "search_query": query,
                    "source_hint": source_hint,
                    "territory_target": normalized_territory,
                    "research_goal": normalized_goal,
                    "target_types": target_types,
                    "inclusion_criteria": inclusion_criteria,
                    "exclusion_criteria": exclusion_criteria,
                    "capture_format": "nome | tipo | citta | regione | paese | sito | nota fit",
                },
                "result_payload": {
                    "collection_status": "da_avviare",
                    "candidate_count": 0,
                },
                "sort_order": index,
            }
        )

    return {
        "project_key": project_key,
        "agent_key": "wb0",
        "title": f"WB0 mission | {normalized_goal}",
        "objective": normalized_goal,
        "source_type": "wb0_search_mission",
        "source_ref": ",".join(normalized_sources),
        "input_payload": {
            "project_context": normalized_context,
            "territory_target": normalized_territory,
            "target_types": target_types,
            "selected_sources": normalized_sources,
            "research_prompt": research_prompt.strip(),
            "prompt_variants": parse_multiline_field(prompt_variants_text),
            "inclusion_criteria": inclusion_criteria,
            "exclusion_criteria": exclusion_criteria,
            "query_pack": query_pack,
        },
        "output_payload": {},
        "cost_estimate": float(len(tasks)) * 0.005,
        "tasks": tasks,
    }


def build_wb1_run_spec(
    *,
    project_key: str,
    organizations: list[dict[str, Any]],
    batch_label: str,
    filter_mode: str,
) -> dict[str, Any]:
    title = f"WB1 batch | {batch_label}"
    tasks = []
    for index, organization in enumerate(organizations):
        tasks.append(
            {
                "task_key": f"organization_{organization['id']}",
                "task_type": "wb1_enrichment_review",
                "title": str(organization.get("name") or f"organization-{organization['id']}"),
                "organization_id": int(organization["id"]),
                "status": "queued",
                "input_payload": {
                    "organization_id": int(organization["id"]),
                    "organization_name": str(organization.get("name") or ""),
                    "website": str(organization.get("website") or ""),
                    "email": str(organization.get("email") or ""),
                    "phone": str(organization.get("phone") or ""),
                    "contact_count": int(organization.get("contact_count") or 0),
                    "filter_mode": filter_mode,
                },
                "result_payload": {
                    "enrichment_status": "da_avviare",
                },
                "sort_order": index,
            }
        )

    return {
        "project_key": project_key,
        "agent_key": "wb1",
        "title": title,
        "objective": "Batch di arricchimento e review per organization gia presenti nel CIS.",
        "source_type": "organizations_batch",
        "source_ref": filter_mode,
        "input_payload": {
            "organization_count": len(organizations),
            "filter_mode": filter_mode,
        },
        "output_payload": {},
        "cost_estimate": float(len(organizations)) * 0.02,
        "tasks": tasks,
    }


def build_wb2_run_spec(
    *,
    project_key: str,
    organizations: list[dict[str, Any]],
    batch_label: str,
    filter_mode: str,
) -> dict[str, Any]:
    title = f"WB2 batch | {batch_label}"
    tasks = []
    for index, organization in enumerate(organizations):
        tasks.append(
            {
                "task_key": f"organization_{organization['id']}",
                "task_type": "wb2_contact_enrichment",
                "title": str(organization.get("name") or f"organization-{organization['id']}"),
                "organization_id": int(organization["id"]),
                "status": "queued",
                "input_payload": {
                    "organization_id": int(organization["id"]),
                    "organization_name": str(organization.get("name") or ""),
                    "website": str(organization.get("website") or ""),
                    "email": str(organization.get("email") or ""),
                    "phone": str(organization.get("phone") or ""),
                    "employee_count": int(organization.get("employee_count") or 0),
                    "contact_count": int(organization.get("contact_count") or 0),
                    "filter_mode": filter_mode,
                },
                "result_payload": {
                    "enrichment_status": "da_avviare",
                },
                "sort_order": index,
            }
        )

    return {
        "project_key": project_key,
        "agent_key": "wb2",
        "title": title,
        "objective": "Batch di ricerca contatti e dettagli organizzativi per organization gia qualificate nel CIS.",
        "source_type": "organizations_batch",
        "source_ref": filter_mode,
        "input_payload": {
            "organization_count": len(organizations),
            "filter_mode": filter_mode,
        },
        "output_payload": {},
        "cost_estimate": float(len(organizations)) * 0.03,
        "tasks": tasks,
    }


def infer_run_status(tasks: list[dict[str, Any]]) -> str:
    statuses = {str(task.get("status") or "") for task in tasks}
    if not statuses:
        return "queued"
    if "review" in statuses:
        return "review"
    if "running" in statuses:
        return "running"
    if "queued" in statuses:
        return "queued"
    if statuses.issubset({"imported"}):
        return "imported"
    if statuses.issubset({"archived", "rejected"}):
        return "archived"
    if statuses.issubset({"approved", "imported"}):
        return "approved"
    if "approved" in statuses or "imported" in statuses:
        return "approved"
    return "queued"


def summarize_task_counts(tasks: list[dict[str, Any]]) -> dict[str, int]:
    summary = {status: 0 for status in AGENT_STATUSES}
    for task in tasks:
        status = str(task.get("status") or "queued")
        summary[status] = summary.get(status, 0) + 1
    summary["total"] = len(tasks)
    return summary
