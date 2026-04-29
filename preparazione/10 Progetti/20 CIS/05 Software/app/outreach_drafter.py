from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.project_communication import load_project_communication_style


DEFAULT_TEMPLATE_NAME = "first_outreach.md"


@dataclass(slots=True)
class OutreachDraft:
    template_name: str
    template_path: str
    subject: str
    body: str


def list_outreach_templates(project_key: str, projects_root: Path | str) -> list[dict[str, str]]:
    templates_dir = Path(projects_root) / project_key / "email_templates"
    if not templates_dir.exists():
        return []

    templates_index = load_outreach_templates_index(project_key, projects_root)
    templates_index_by_name = {item["filename"]: item for item in templates_index}
    templates: list[dict[str, str | list[str]]] = []
    for template_path in sorted(templates_dir.glob("*.md")):
        indexed_template = templates_index_by_name.get(template_path.name, {})
        templates.append(
            {
                "name": template_path.name,
                "label": str(indexed_template.get("label") or _build_template_label(template_path.name)),
                "description": str(indexed_template.get("description") or ""),
                "tags": list(indexed_template.get("tags") or []),
            }
        )
    return templates


def load_outreach_templates_index(project_key: str, projects_root: Path | str) -> list[dict[str, object]]:
    index_path = Path(projects_root) / project_key / "email_templates" / "templates_index.yaml"
    if not index_path.exists():
        return []

    templates: list[dict[str, object]] = []
    current_template: dict[str, object] | None = None
    inside_tags = False

    for raw_line in index_path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped == "templates:":
            continue

        if stripped.startswith("- filename:"):
            if current_template:
                templates.append(current_template)
            current_template = {
                "filename": stripped.split(":", 1)[1].strip(),
                "label": "",
                "description": "",
                "tags": [],
            }
            inside_tags = False
            continue

        if current_template is None:
            continue

        if stripped == "tags:":
            inside_tags = True
            continue

        if inside_tags and stripped.startswith("- "):
            current_tags = current_template.setdefault("tags", [])
            if isinstance(current_tags, list):
                current_tags.append(stripped[2:].strip())
            continue

        inside_tags = False
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            current_template[key.strip()] = value.strip()

    if current_template:
        templates.append(current_template)

    return templates


def suggest_outreach_template(
    available_templates: list[dict[str, object]],
    contact: dict | None = None,
) -> dict[str, object] | None:
    if not available_templates:
        return None

    role = str(contact.get("role") or "").lower().strip() if contact else ""
    desired_tag = "destinatario:generale"
    if any(keyword in role for keyword in ["hr", "personale", "people", "risorse umane"]):
        desired_tag = "destinatario:hr"
    elif any(keyword in role for keyword in ["ceo", "amministratore delegato", "ad", "direzione generale", "founder"]):
        desired_tag = "destinatario:ceo"

    best_template: dict[str, object] | None = None
    best_score = -1
    for template in available_templates:
        tags = template.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        score = 0
        if desired_tag in tags:
            score += 10
        if "tono:diretto" in tags and desired_tag == "destinatario:ceo":
            score += 2
        if "tono:consulenziale" in tags and desired_tag == "destinatario:hr":
            score += 2
        if score > best_score:
            best_score = score
            best_template = template

    return best_template or available_templates[0]


def build_outreach_draft(
    project_key: str,
    projects_root: Path | str,
    organization: dict,
    contact: dict | None = None,
    qualification_data: dict[str, str] | None = None,
    template_name: str = DEFAULT_TEMPLATE_NAME,
) -> OutreachDraft:
    template_path = Path(projects_root) / project_key / "email_templates" / template_name
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template outreach non trovato per il progetto '{project_key}': {template_name}"
        )

    template_text = template_path.read_text(encoding="utf-8").strip()
    subject_template, body_template = _split_template(template_text)
    communication_style = load_project_communication_style(project_key, projects_root)
    replacements = _build_replacements(
        organization=organization,
        contact=contact,
        qualification_data=qualification_data or {},
        communication_style=communication_style,
    )

    return OutreachDraft(
        template_name=template_name,
        template_path=str(template_path),
        subject=_replace_placeholders(subject_template, replacements).strip(),
        body=_replace_placeholders(body_template, replacements).strip(),
    )


def _split_template(template_text: str) -> tuple[str, str]:
    lines = template_text.splitlines()
    if not lines:
        raise ValueError("Il template outreach e vuoto.")

    first_line = lines[0].strip()
    if not first_line.lower().startswith("oggetto:"):
        raise ValueError("Il template outreach deve iniziare con 'Oggetto:'.")

    subject = first_line.split(":", 1)[1].strip()
    body = "\n".join(lines[1:]).strip()
    return subject, body


def _build_replacements(
    organization: dict,
    contact: dict | None,
    qualification_data: dict[str, str],
    communication_style: dict[str, object],
) -> dict[str, str]:
    contact_full_name = ""
    contact_first_name = ""
    contact_last_name = ""
    contact_role = ""
    contact_notes = ""

    if contact:
        contact_full_name = str(contact.get("full_name") or "").strip()
        contact_first_name = str(contact.get("first_name") or "").strip()
        contact_last_name = str(contact.get("last_name") or "").strip()
        if not contact_first_name and contact_full_name:
            contact_first_name = contact_full_name.split(" ", 1)[0]
        if not contact_last_name and contact_full_name and " " in contact_full_name:
            contact_last_name = contact_full_name.rsplit(" ", 1)[-1].strip()
        contact_role = str(contact.get("role") or "").strip()
        contact_notes = str(contact.get("notes") or "")

    saluto = _build_saluto(
        contact_first_name=contact_first_name,
        contact_last_name=contact_last_name,
        contact_full_name=contact_full_name,
        contact_notes=contact_notes,
    )
    organization_name = str(organization.get("name") or "").strip()
    city = str(organization.get("city") or "").strip()
    sector = str(organization.get("sector") or "").strip()
    website = str(organization.get("website") or "").strip()
    notes = str(organization.get("notes") or "")
    pdr125_data = extract_pdr125_data(notes)
    outreach_style = communication_style.get("outreach", {})
    outreach_style = outreach_style if isinstance(outreach_style, dict) else {}

    presentation_company = str(outreach_style.get("presentation_company") or "E-docs").strip()
    presentation_name = str(outreach_style.get("presentation_name") or "").strip()
    presentation_role = str(outreach_style.get("presentation_role") or "").strip()
    presentation_summary = str(
        outreach_style.get("presentation_summary")
        or "un supporto semplice per tenere piu ordinati documenti, evidenze e responsabilita nei percorsi certificativi"
    ).strip()
    cta = str(
        outreach_style.get("cta")
        or "Se puo essere utile, possiamo fare un confronto rapido per capire se questo approccio puo portare valore anche nel vostro contesto."
    ).strip()
    signature_name = str(outreach_style.get("signature_name") or "").strip()
    signature_role = str(outreach_style.get("signature_role") or "").strip()
    signature_company = str(outreach_style.get("signature_company") or presentation_company).strip()

    presentation = _build_presentation(
        presentation_name=presentation_name,
        presentation_role=presentation_role,
        presentation_company=presentation_company,
        presentation_summary=presentation_summary,
    )
    subject_organization = organization_name
    if pdr125_data["expiry_date"]:
        subject_organization = f"{organization_name} - rinnovo {format_pdr125_date(pdr125_data['expiry_date'])}"

    scadenza_testo = _build_scadenza_text(pdr125_data["expiry_date"])
    organismo_testo = (
        f" con certificazione rilasciata da {pdr125_data['certification_body']}"
        if pdr125_data["certification_body"]
        else ""
    )
    ragione_contatto = _build_contact_reason(
        sector=sector or pdr125_data["relevant_sector"],
        qualification_data=qualification_data,
        pdr125_data=pdr125_data,
        contact_role=contact_role,
    )
    firma = _build_signature(signature_name, signature_role, signature_company)

    return {
        "[SALUTO]": saluto,
        "[ENTE]": organization_name,
        "[ENTE_OGGETTO]": subject_organization,
        "[ORGANIZATION]": organization_name,
        "[NOME_REFERENTE]": contact_full_name or "buongiorno",
        "[NOME]": contact_first_name or "",
        "[RUOLO_REFERENTE]": contact_role,
        "[CITTA]": city,
        "[SETTORE]": sector,
        "[SITO]": website,
        "[SCADENZA_PDR125]": pdr125_data["expiry_date"],
        "[SCADENZA_TESTO]": scadenza_testo,
        "[ORGANISMO_CERTIFICAZIONE]": pdr125_data["certification_body"],
        "[ORGANISMO_TESTO]": organismo_testo,
        "[FONTE_PDR125]": pdr125_data["verification_source"],
        "[SETTORE_RILEVANTE]": pdr125_data["relevant_sector"] or sector,
        "[GANCIO_E_DOCS]": pdr125_data["edocs_hook"],
        "[IPOTESI_COMMERCIALE]": pdr125_data["commercial_hypothesis"],
        "[PRESENTAZIONE]": presentation,
        "[RAGIONE_CONTATTO]": ragione_contatto,
        "[CTA]": cta,
        "[QUALIFICATION_SIGNALS]": str(qualification_data.get("qualification_signals") or "").strip(),
        "[PROSSIMO_PASSO]": str(qualification_data.get("next_step") or "").strip(),
        "[FIRMA]": firma,
    }


def _build_saluto(
    contact_first_name: str,
    contact_last_name: str,
    contact_full_name: str,
    contact_notes: str,
) -> str:
    saluto_title = _extract_contact_note_value(contact_notes, "Titolo saluto:")
    if saluto_title and contact_last_name:
        return f"Buongiorno {saluto_title} {contact_last_name},"
    if contact_full_name:
        return f"Buongiorno {contact_full_name},"
    if contact_first_name:
        return f"Buongiorno {contact_first_name},"
    return "Buongiorno,"


def _extract_contact_note_value(notes: str, prefix: str) -> str:
    for raw_line in notes.splitlines():
        line = raw_line.strip()
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""


def extract_pdr125_data(notes: str) -> dict[str, str]:
    data = {
        "status": "",
        "expiry_date": "",
        "certification_body": "",
        "verification_source": "",
        "relevant_sector": "",
        "commercial_hypothesis": "",
        "edocs_hook": "",
    }
    block = _extract_block_lines(notes, "[PdR125]", "[/PdR125]")
    prefix_map = {
        "Stato:": "status",
        "Scadenza certificazione:": "expiry_date",
        "Organismo certificazione:": "certification_body",
        "Fonte verifica:": "verification_source",
        "Settore rilevante:": "relevant_sector",
        "Ipotesi commerciale:": "commercial_hypothesis",
        "Gancio E-docs:": "edocs_hook",
    }

    for line in block:
        for prefix, key in prefix_map.items():
            if line.startswith(prefix):
                data[key] = line.split(":", 1)[1].strip()
                break

    return data


def _extract_block_lines(text: str, block_start: str, block_end: str) -> list[str]:
    inside_block = False
    collected_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == block_start:
            inside_block = True
            continue
        if line == block_end:
            inside_block = False
            continue
        if inside_block and line:
            collected_lines.append(line)

    return collected_lines


def _build_presentation(
    presentation_name: str,
    presentation_role: str,
    presentation_company: str,
    presentation_summary: str,
) -> str:
    if presentation_name and presentation_role:
        opener = f"mi chiamo {presentation_name} e seguo {presentation_role} in {presentation_company}."
    elif presentation_name:
        opener = f"mi chiamo {presentation_name} e ti scrivo da {presentation_company}."
    else:
        opener = f"ti scrivo da {presentation_company}."

    return f"{opener} Lavoriamo su {presentation_summary}."


def _build_scadenza_text(expiry_date: str) -> str:
    if not expiry_date:
        return "nei prossimi mesi"
    return format_pdr125_date(expiry_date)


def _build_contact_reason(
    sector: str,
    qualification_data: dict[str, str],
    pdr125_data: dict[str, str],
    contact_role: str,
) -> str:
    sector_text = sector.strip() or "il vostro contesto operativo"
    qualification_signals = str(qualification_data.get("qualification_signals") or "").strip()

    first_sentence = (
        f"Abbiamo visto che la vostra certificazione UNI/PdR 125 risulta in rinnovo {_build_scadenza_phrase(pdr125_data.get('expiry_date', ''))}"
        f" e che questo puo essere un buon momento per rendere piu semplice la gestione di documenti, evidenze e responsabilita."
    )

    if contact_role:
        second_sentence = (
            f"Ti scrivo perche il tuo ruolo di {contact_role} sembra vicino a questi temi,"
            f" soprattutto in un ambito come {sector_text}."
        )
    else:
        second_sentence = (
            f"Nel vostro caso questo punto ci sembra particolarmente rilevante, soprattutto in un ambito come {sector_text}."
        )

    if qualification_signals:
        second_sentence += f" I segnali emersi finora sono: {qualification_signals}."

    return f"{first_sentence}\n\n{second_sentence}"


def _build_scadenza_phrase(expiry_date: str) -> str:
    if not expiry_date:
        return "nei prossimi mesi"
    return f"il {format_pdr125_date(expiry_date)}"


def _build_signature(signature_name: str, signature_role: str, signature_company: str) -> str:
    parts = [part for part in [signature_name, signature_role, signature_company] if part]
    if not parts:
        return "Team E-docs"
    return "\n".join(parts)


def format_pdr125_date(raw_date: str) -> str:
    cleaned = raw_date.strip()
    if len(cleaned) == 10 and cleaned[4] == "-" and cleaned[7] == "-":
        year, month, day = cleaned.split("-")
        months = {
            "01": "gennaio",
            "02": "febbraio",
            "03": "marzo",
            "04": "aprile",
            "05": "maggio",
            "06": "giugno",
            "07": "luglio",
            "08": "agosto",
            "09": "settembre",
            "10": "ottobre",
            "11": "novembre",
            "12": "dicembre",
        }
        return f"{int(day)} {months.get(month, month)} {year}"
    return cleaned


def _replace_placeholders(text: str, replacements: dict[str, str]) -> str:
    rendered = text
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    return rendered


def _build_template_label(template_name: str) -> str:
    stem = template_name.rsplit(".", 1)[0]
    return stem.replace("_", " ").strip().title()
