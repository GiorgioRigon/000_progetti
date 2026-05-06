from __future__ import annotations


WB2_SOCIAL_BLOCK_START = "[WB2 social]"
WB2_SOCIAL_BLOCK_END = "[/WB2 social]"
WB2_RESEARCH_BLOCK_START = "[WB2 note]"
WB2_RESEARCH_BLOCK_END = "[/WB2 note]"
WB2_VERIFICATION_SOURCE_PREFIX = "Fonte verifica:"
WB2_CONTACT_LEVEL_PREFIX = "Livello contatto:"
WB2_EMPLOYEE_COUNT_PREFIX = "Numero dipendenti:"
WB2_ORG_SIGNALS_PREFIX = "Segnali organizzativi:"


def parse_multiline_field(raw_text: str) -> list[str]:
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def build_wb2_note(
    research_note: str,
    verification_source: str,
    contact_level: str,
    employee_count: str,
    org_signals: str,
) -> str:
    lines: list[str] = []
    if research_note.strip():
        lines.append(research_note.strip())
    if verification_source.strip():
        lines.append(f"{WB2_VERIFICATION_SOURCE_PREFIX} {verification_source.strip()}")
    if contact_level.strip():
        lines.append(f"{WB2_CONTACT_LEVEL_PREFIX} {contact_level.strip()}")
    if employee_count.strip():
        lines.append(f"{WB2_EMPLOYEE_COUNT_PREFIX} {employee_count.strip()}")
    if org_signals.strip():
        lines.append(f"{WB2_ORG_SIGNALS_PREFIX} {org_signals.strip()}")
    return "\n".join(lines)


def merge_wb2_notes(
    existing_notes: str | None,
    social_profiles: list[str],
    wb2_note: str,
) -> str | None:
    note_sections: list[str] = []
    cleaned_existing = _remove_block(
        _remove_block(existing_notes or "", WB2_SOCIAL_BLOCK_START, WB2_SOCIAL_BLOCK_END),
        WB2_RESEARCH_BLOCK_START,
        WB2_RESEARCH_BLOCK_END,
    ).strip()

    if cleaned_existing:
        note_sections.append(cleaned_existing)

    normalized_social_profiles = [profile for profile in social_profiles if profile]
    if normalized_social_profiles:
        note_sections.append(
            "\n".join(
                [
                    WB2_SOCIAL_BLOCK_START,
                    *normalized_social_profiles,
                    WB2_SOCIAL_BLOCK_END,
                ]
            )
        )

    cleaned_note = wb2_note.strip()
    if cleaned_note:
        note_sections.append(
            "\n".join(
                [
                    WB2_RESEARCH_BLOCK_START,
                    cleaned_note,
                    WB2_RESEARCH_BLOCK_END,
                ]
            )
        )

    return "\n\n".join(note_sections) if note_sections else None


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
