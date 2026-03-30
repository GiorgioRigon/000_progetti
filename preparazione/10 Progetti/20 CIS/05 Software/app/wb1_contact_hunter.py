from __future__ import annotations

from app.workbot_profiles import normalize_profile_list, normalize_profile_text


WB1_SOCIAL_BLOCK_START = "[WB1 social]"
WB1_SOCIAL_BLOCK_END = "[/WB1 social]"
WB1_RESEARCH_BLOCK_START = "[WB1 note]"
WB1_RESEARCH_BLOCK_END = "[/WB1 note]"
WB1_VERIFICATION_SOURCE_PREFIX = "Fonte verifica:"
WB1_CONTACT_LEVEL_PREFIX = "Livello contatto:"
WB1_QUALIFICATION_SIGNALS_PREFIX = "Segnali qualificazione:"


def parse_multiline_field(raw_text: str) -> list[str]:
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def build_contact_hunter_prompt(
    organization_name: str,
    organization_type: str,
    city: str,
    region: str,
    country: str,
    website: str,
    current_email: str,
    current_phone: str,
    existing_contacts: list[dict],
    profile: dict | None = None,
) -> str:
    normalized_profile = profile or {}
    contact_goal = normalize_profile_text(normalized_profile, "contact_goal")
    priority_roles = normalize_profile_list(normalized_profile, "priority_roles")
    secondary_roles = normalize_profile_list(normalized_profile, "secondary_roles")
    sources_to_check = normalize_profile_list(normalized_profile, "sources_to_check")
    required_fields = normalize_profile_list(normalized_profile, "required_fields")
    verification_checks = normalize_profile_list(normalized_profile, "verification_checks")
    output_notes = normalize_profile_list(normalized_profile, "output_notes")
    if not any(
        [
            organization_name.strip(),
            organization_type.strip(),
            city.strip(),
            region.strip(),
            country.strip(),
            website.strip(),
            current_email.strip(),
            current_phone.strip(),
            existing_contacts,
            contact_goal,
            priority_roles,
            secondary_roles,
            sources_to_check,
            required_fields,
            verification_checks,
            output_notes,
        ]
    ):
        return ""

    location = ", ".join(part for part in [city.strip(), region.strip(), country.strip()] if part)
    lines = [
        f"Obiettivo: {contact_goal or 'trovare un referente verificabile per questo lead e raccogliere contatti utili.'}",
        f"Organization: {organization_name.strip() or '[da definire]'}",
        f"Tipo: {organization_type.strip() or '[non indicato]'}",
        f"Territorio: {location or '[non indicato]'}",
        f"Sito attuale: {website.strip() or '[non indicato]'}",
        f"Email attuale: {current_email.strip() or '[non indicata]'}",
        f"Telefono attuale: {current_phone.strip() or '[non indicato]'}",
    ]
    if priority_roles:
        lines.extend(["", "Ruoli prioritari:", *[f"- {item}" for item in priority_roles]])
    if secondary_roles:
        lines.extend(["", "Ruoli secondari accettabili:", *[f"- {item}" for item in secondary_roles]])
    if sources_to_check:
        lines.extend(["", "Fonti da controllare:", *[f"- {item}" for item in sources_to_check]])
    lines.extend(
        [
            "",
            "Cerca e restituisci solo dati verificabili:",
            "- email generale o diretta",
            "- telefono utile",
            "- referente",
            "- ruolo",
            "- sito ufficiale",
            "- social ufficiali rilevanti",
        ]
    )
    if required_fields:
        lines.extend(["", "Dati minimi richiesti dal profilo:", *[f"- {item}" for item in required_fields]])
    if verification_checks:
        lines.extend(["", "Checklist verifica umana:", *[f"- {item}" for item in verification_checks]])

    if existing_contacts:
        lines.extend(["", "Contatti gia presenti nel CIS:"])
        for contact in existing_contacts:
            full_name = str(contact.get("full_name", "")).strip()
            if not full_name:
                first_name = str(contact.get("first_name", "")).strip()
                last_name = str(contact.get("last_name", "")).strip()
                full_name = " ".join(part for part in [first_name, last_name] if part)
            role = str(contact.get("role", "")).strip() or "ruolo non indicato"
            lines.append(f"- {full_name or 'Contatto senza nome'} | {role}")

    lines.extend(
        [
            "",
            "Formato risposta consigliato:",
            "email:",
            "telefono:",
            "referente:",
            "ruolo:",
            "sito:",
            "social:",
            "- piattaforma | url",
            "note_verifica:",
        ]
    )
    if output_notes:
        lines.extend(["", "Note operative del profilo:", *[f"- {item}" for item in output_notes]])
    return "\n".join(lines)


def extract_social_profiles(notes: str | None) -> list[str]:
    return _extract_block_lines(notes or "", WB1_SOCIAL_BLOCK_START, WB1_SOCIAL_BLOCK_END)


def extract_research_note(notes: str | None) -> str:
    lines = _extract_block_lines(notes or "", WB1_RESEARCH_BLOCK_START, WB1_RESEARCH_BLOCK_END)
    return "\n".join(lines)


def extract_research_metadata(notes: str | None) -> dict[str, str]:
    metadata = {
        "verification_source": "",
        "contact_level": "",
        "qualification_signals": "",
        "research_note": "",
    }
    remaining_lines: list[str] = []

    for line in _extract_block_lines(notes or "", WB1_RESEARCH_BLOCK_START, WB1_RESEARCH_BLOCK_END):
        if line.startswith(WB1_VERIFICATION_SOURCE_PREFIX):
            metadata["verification_source"] = line.split(":", 1)[1].strip()
        elif line.startswith(WB1_CONTACT_LEVEL_PREFIX):
            metadata["contact_level"] = line.split(":", 1)[1].strip()
        elif line.startswith(WB1_QUALIFICATION_SIGNALS_PREFIX):
            metadata["qualification_signals"] = line.split(":", 1)[1].strip()
        else:
            remaining_lines.append(line)

    metadata["research_note"] = "\n".join(remaining_lines).strip()
    return metadata


def build_research_note(
    research_note: str,
    verification_source: str,
    contact_level: str,
    qualification_signals: str,
) -> str:
    lines: list[str] = []
    if research_note.strip():
        lines.append(research_note.strip())
    if verification_source.strip():
        lines.append(f"{WB1_VERIFICATION_SOURCE_PREFIX} {verification_source.strip()}")
    if contact_level.strip():
        lines.append(f"{WB1_CONTACT_LEVEL_PREFIX} {contact_level.strip()}")
    if qualification_signals.strip():
        lines.append(f"{WB1_QUALIFICATION_SIGNALS_PREFIX} {qualification_signals.strip()}")
    return "\n".join(lines)


def merge_wb1_notes(
    existing_notes: str | None,
    social_profiles: list[str],
    research_note: str,
) -> str | None:
    note_sections: list[str] = []
    cleaned_existing = _remove_block(
        _remove_block(existing_notes or "", WB1_SOCIAL_BLOCK_START, WB1_SOCIAL_BLOCK_END),
        WB1_RESEARCH_BLOCK_START,
        WB1_RESEARCH_BLOCK_END,
    ).strip()

    if cleaned_existing:
        note_sections.append(cleaned_existing)

    normalized_social_profiles = [profile for profile in social_profiles if profile]
    if normalized_social_profiles:
        note_sections.append(
            "\n".join(
                [
                    WB1_SOCIAL_BLOCK_START,
                    *normalized_social_profiles,
                    WB1_SOCIAL_BLOCK_END,
                ]
            )
        )

    cleaned_research_note = research_note.strip()
    if cleaned_research_note:
        note_sections.append(
            "\n".join(
                [
                    WB1_RESEARCH_BLOCK_START,
                    cleaned_research_note,
                    WB1_RESEARCH_BLOCK_END,
                ]
            )
        )

    return "\n\n".join(note_sections) if note_sections else None


def _extract_block_lines(text: str, block_start: str, block_end: str) -> list[str]:
    inside_block = False
    collected_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == block_start:
            inside_block = True
            continue
        if line == block_end:
            break
        if inside_block and line:
            collected_lines.append(line)

    return collected_lines


def _remove_block(text: str, block_start: str, block_end: str) -> str:
    kept_lines: list[str] = []
    inside_block = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == block_start:
            inside_block = True
            continue
        if line == block_end:
            inside_block = False
            continue
        if not inside_block:
            kept_lines.append(raw_line)

    return "\n".join(kept_lines).strip()
