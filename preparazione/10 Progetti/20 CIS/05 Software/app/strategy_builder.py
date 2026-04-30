from __future__ import annotations

from typing import Any


STRATEGY_BLOCK_START = "[WB3 Strategy]"
STRATEGY_BLOCK_END = "[/WB3 Strategy]"
CHANNEL_PREFIX = "Canale:"
CHANNEL_REASON_PREFIX = "Motivo canale:"
COMMERCIAL_ANGLE_PREFIX = "Angolo commerciale:"
CAUTION_PREFIX = "Cautela:"
NEXT_STEP_PREFIX = "Prossimo passo:"


def extract_strategy_data(notes: str | None) -> dict[str, str]:
    data = {
        "channel": "",
        "channel_reason": "",
        "commercial_angle": "",
        "caution_note": "",
        "next_step": "",
    }

    for line in _extract_block_lines(notes or "", STRATEGY_BLOCK_START, STRATEGY_BLOCK_END):
        if line.startswith(CHANNEL_PREFIX):
            data["channel"] = line.split(":", 1)[1].strip()
        elif line.startswith(CHANNEL_REASON_PREFIX):
            data["channel_reason"] = line.split(":", 1)[1].strip()
        elif line.startswith(COMMERCIAL_ANGLE_PREFIX):
            data["commercial_angle"] = line.split(":", 1)[1].strip()
        elif line.startswith(CAUTION_PREFIX):
            data["caution_note"] = line.split(":", 1)[1].strip()
        elif line.startswith(NEXT_STEP_PREFIX):
            data["next_step"] = line.split(":", 1)[1].strip()

    return data


def build_strategy_note(
    channel: str,
    channel_reason: str,
    commercial_angle: str,
    caution_note: str,
    next_step: str,
) -> str:
    lines: list[str] = []
    if channel.strip():
        lines.append(f"{CHANNEL_PREFIX} {channel.strip()}")
    if channel_reason.strip():
        lines.append(f"{CHANNEL_REASON_PREFIX} {channel_reason.strip()}")
    if commercial_angle.strip():
        lines.append(f"{COMMERCIAL_ANGLE_PREFIX} {commercial_angle.strip()}")
    if caution_note.strip():
        lines.append(f"{CAUTION_PREFIX} {caution_note.strip()}")
    if next_step.strip():
        lines.append(f"{NEXT_STEP_PREFIX} {next_step.strip()}")
    return "\n".join(lines)


def merge_strategy_notes(existing_notes: str | None, strategy_note: str) -> str | None:
    cleaned_existing = _remove_block(existing_notes or "", STRATEGY_BLOCK_START, STRATEGY_BLOCK_END).strip()
    sections: list[str] = []

    if cleaned_existing:
        sections.append(cleaned_existing)

    if strategy_note.strip():
        sections.append(
            "\n".join(
                [
                    STRATEGY_BLOCK_START,
                    strategy_note.strip(),
                    STRATEGY_BLOCK_END,
                ]
            )
        )

    return "\n\n".join(sections) if sections else None


def suggest_strategy(
    *,
    organization: dict[str, Any],
    contacts: list[dict[str, Any]],
    qualification_data: dict[str, str],
) -> dict[str, str]:
    best_contact = contacts[0] if contacts else None
    contact_email = str((best_contact or {}).get("email") or "").strip()
    contact_role = str((best_contact or {}).get("role") or "").strip()
    organization_email = str(organization.get("email") or "").strip()
    organization_phone = str(organization.get("phone") or "").strip()
    fit_label = str(qualification_data.get("fit_label") or "").strip().lower()

    signals_text = " ".join(
        [
            str(qualification_data.get("qualification_signals") or ""),
            str(qualification_data.get("qualification_note") or ""),
            str(organization.get("notes") or ""),
            str(contact_role),
            str(organization.get("sector") or ""),
        ]
    ).lower()

    if contact_email:
        channel = "email_diretta"
        channel_reason = "Esiste un contatto nominativo con email diretta gia salvata nel CIS."
        next_step = "Preparare una prima mail personalizzata e verificare un follow-up entro 3-5 giorni lavorativi."
    elif organization_email and organization_phone:
        channel = "email_generale_più_telefonata"
        channel_reason = "Esiste un canale ufficiale verificato, ma non un referente diretto gia confermato."
        next_step = "Inviare una mail breve alla casella generale e programmare una telefonata di instradamento entro 24-72 ore."
    elif organization_email:
        channel = "email_generale"
        channel_reason = "Esiste solo una casella ufficiale generale e conviene usarla per aprire il contatto."
        next_step = "Inviare una mail molto breve finalizzata a identificare il referente corretto."
    elif organization_phone:
        channel = "telefonata"
        channel_reason = "Manca una email affidabile, ma e presente un telefono ufficiale verificato."
        next_step = "Preparare una telefonata breve per capire il referente corretto e il canale migliore."
    else:
        channel = "ricerca_aggiuntiva"
        channel_reason = "Non esiste ancora un canale verificato sufficiente per un primo contatto ordinato."
        next_step = "Completare prima WB1 per trovare almeno un canale ufficiale affidabile."

    if "pdr125" in signals_text:
        commercial_angle = "Possibile supporto operativo a mantenimento o rinnovo UNI/PdR 125, con focus su ordine documentale, evidenze e sostenibilita del presidio interno."
    elif "hr" in signals_text or "people" in signals_text:
        commercial_angle = "Possibile supporto operativo a processi HR e organizzativi che richiedono maggiore ordine, tracciabilita o sostenibilita nel tempo."
    elif "esg" in signals_text or "sustainability" in signals_text or "csr" in signals_text:
        commercial_angle = "Possibile supporto operativo su esigenze ESG o di governance, evitando un approccio troppo ampio o generico nel primo contatto."
    else:
        commercial_angle = "Primo contatto orientato a capire se esiste un'esigenza operativa concreta su cui aprire un confronto breve e credibile."

    caution_reasons: list[str] = []
    if not contact_email and organization_email:
        caution_reasons.append("Il referente non e ancora verificato in modo nominativo.")
    if not best_contact:
        caution_reasons.append("Manca un contatto gia associato alla organization.")
    if fit_label == "basso":
        caution_reasons.append("Il fit attuale del lead e basso: il messaggio deve restare esplorativo e leggero.")
    elif fit_label == "medio":
        caution_reasons.append("Il fit attuale del lead e medio: evitare assunzioni troppo forti sul bisogno.")

    caution_note = " ".join(caution_reasons).strip() or (
        "Non dare per scontato il bisogno del lead: mantenere un tono prudente e verificare l'interesse reale."
    )

    return {
        "channel": channel,
        "channel_reason": channel_reason,
        "commercial_angle": commercial_angle,
        "caution_note": caution_note,
        "next_step": next_step,
    }


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
