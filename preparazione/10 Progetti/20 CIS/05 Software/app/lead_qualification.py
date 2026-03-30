from __future__ import annotations


QUALIFICATION_BLOCK_START = "[Lead qualification]"
QUALIFICATION_BLOCK_END = "[/Lead qualification]"
FIT_LABEL_PREFIX = "Fit:"
OPPORTUNITY_TYPE_PREFIX = "Tipo opportunita:"
PRIORITY_LEVEL_PREFIX = "Priorita:"
QUALIFICATION_SIGNALS_PREFIX = "Segnali:"
NEXT_STEP_PREFIX = "Prossimo passo:"


def extract_qualification_data(notes: str | None) -> dict[str, str]:
    data = {
        "fit_label": "",
        "opportunity_type": "",
        "priority_level": "",
        "qualification_signals": "",
        "next_step": "",
        "qualification_note": "",
    }
    note_lines: list[str] = []

    for line in _extract_block_lines(notes or "", QUALIFICATION_BLOCK_START, QUALIFICATION_BLOCK_END):
        if line.startswith(FIT_LABEL_PREFIX):
            data["fit_label"] = line.split(":", 1)[1].strip()
        elif line.startswith(OPPORTUNITY_TYPE_PREFIX):
            data["opportunity_type"] = line.split(":", 1)[1].strip()
        elif line.startswith(PRIORITY_LEVEL_PREFIX):
            data["priority_level"] = line.split(":", 1)[1].strip()
        elif line.startswith(QUALIFICATION_SIGNALS_PREFIX):
            data["qualification_signals"] = line.split(":", 1)[1].strip()
        elif line.startswith(NEXT_STEP_PREFIX):
            data["next_step"] = line.split(":", 1)[1].strip()
        else:
            note_lines.append(line)

    data["qualification_note"] = "\n".join(note_lines).strip()
    return data


def build_qualification_note(
    fit_label: str,
    opportunity_type: str,
    priority_level: str,
    qualification_signals: str,
    next_step: str,
    qualification_note: str,
) -> str:
    lines: list[str] = []
    if fit_label.strip():
        lines.append(f"{FIT_LABEL_PREFIX} {fit_label.strip()}")
    if opportunity_type.strip():
        lines.append(f"{OPPORTUNITY_TYPE_PREFIX} {opportunity_type.strip()}")
    if priority_level.strip():
        lines.append(f"{PRIORITY_LEVEL_PREFIX} {priority_level.strip()}")
    if qualification_signals.strip():
        lines.append(f"{QUALIFICATION_SIGNALS_PREFIX} {qualification_signals.strip()}")
    if next_step.strip():
        lines.append(f"{NEXT_STEP_PREFIX} {next_step.strip()}")
    if qualification_note.strip():
        lines.append(qualification_note.strip())
    return "\n".join(lines)


def merge_qualification_notes(existing_notes: str | None, qualification_note: str) -> str | None:
    cleaned_existing = _remove_block(existing_notes or "", QUALIFICATION_BLOCK_START, QUALIFICATION_BLOCK_END).strip()
    sections: list[str] = []

    if cleaned_existing:
        sections.append(cleaned_existing)

    if qualification_note.strip():
        sections.append(
            "\n".join(
                [
                    QUALIFICATION_BLOCK_START,
                    qualification_note.strip(),
                    QUALIFICATION_BLOCK_END,
                ]
            )
        )

    return "\n\n".join(sections) if sections else None


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
