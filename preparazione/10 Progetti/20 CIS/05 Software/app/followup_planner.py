from __future__ import annotations

from typing import Any


FOLLOWUP_BLOCK_START = "[WB5 Follow-up]"
FOLLOWUP_BLOCK_END = "[/WB5 Follow-up]"
WINDOW_PREFIX = "Finestra:"
CHANNEL_PREFIX = "Canale:"
SCRIPT_PREFIX = "Micro-script:"
REASON_PREFIX = "Motivo:"
NEXT_STATUS_PREFIX = "Stato successivo:"


def extract_followup_data(notes: str | None) -> dict[str, str]:
    data = {
        "followup_window": "",
        "channel": "",
        "micro_script": "",
        "reason": "",
        "next_status": "",
    }

    for line in _extract_block_lines(notes or "", FOLLOWUP_BLOCK_START, FOLLOWUP_BLOCK_END):
        if line.startswith(WINDOW_PREFIX):
            data["followup_window"] = line.split(":", 1)[1].strip()
        elif line.startswith(CHANNEL_PREFIX):
            data["channel"] = line.split(":", 1)[1].strip()
        elif line.startswith(SCRIPT_PREFIX):
            data["micro_script"] = line.split(":", 1)[1].strip()
        elif line.startswith(REASON_PREFIX):
            data["reason"] = line.split(":", 1)[1].strip()
        elif line.startswith(NEXT_STATUS_PREFIX):
            data["next_status"] = line.split(":", 1)[1].strip()

    return data


def build_followup_note(
    followup_window: str,
    channel: str,
    micro_script: str,
    reason: str,
    next_status: str,
) -> str:
    lines: list[str] = []
    if followup_window.strip():
        lines.append(f"{WINDOW_PREFIX} {followup_window.strip()}")
    if channel.strip():
        lines.append(f"{CHANNEL_PREFIX} {channel.strip()}")
    if micro_script.strip():
        lines.append(f"{SCRIPT_PREFIX} {micro_script.strip()}")
    if reason.strip():
        lines.append(f"{REASON_PREFIX} {reason.strip()}")
    if next_status.strip():
        lines.append(f"{NEXT_STATUS_PREFIX} {next_status.strip()}")
    return "\n".join(lines)


def merge_followup_notes(existing_notes: str | None, followup_note: str) -> str | None:
    cleaned_existing = _remove_block(existing_notes or "", FOLLOWUP_BLOCK_START, FOLLOWUP_BLOCK_END).strip()
    sections: list[str] = []

    if cleaned_existing:
        sections.append(cleaned_existing)

    if followup_note.strip():
        sections.append(
            "\n".join(
                [
                    FOLLOWUP_BLOCK_START,
                    followup_note.strip(),
                    FOLLOWUP_BLOCK_END,
                ]
            )
        )

    return "\n\n".join(sections) if sections else None


def suggest_followup(
    *,
    organization: dict[str, Any],
    qualification_data: dict[str, str],
    strategy_data: dict[str, str],
    outreach_history: list[dict[str, Any]],
) -> dict[str, str]:
    has_outreach_draft = bool(outreach_history)
    strategy_channel = str(strategy_data.get("channel") or "").strip()
    next_step = str(qualification_data.get("next_step") or "").strip()
    organization_phone = str(organization.get("phone") or "").strip()

    if has_outreach_draft:
        if strategy_channel == "email_diretta":
            channel = "telefonata_o_email_breve"
            followup_window = "3-5 giorni lavorativi"
            reason = "Esiste gia una bozza outreach e conviene verificare rapidamente se il primo contatto ha aperto uno spazio reale."
            micro_script = "Riprendo la mail inviata nei giorni scorsi per capire se ha senso un confronto di 10 minuti su questo tema."
            next_status = "attesa_riscontro"
        elif strategy_channel == "email_generale_più_telefonata":
            channel = "telefonata"
            followup_window = "24-72 ore"
            reason = "Dopo una mail a casella generale conviene fare instradamento rapido per individuare il referente corretto."
            micro_script = "Chiamo per verificare chi segue questo tema e a chi conviene inoltrare il messaggio inviato."
            next_status = "da_instradare"
        else:
            channel = "email_breve"
            followup_window = "4-7 giorni lavorativi"
            reason = "Esiste gia una bozza o un primo contatto preparato e serve un richiamo leggero senza appesantire."
            micro_script = "Riprendo il messaggio precedente solo per capire se questo tema e attuale anche per voi."
            next_status = "attesa_riscontro"
    else:
        if strategy_channel in {"telefonata", "email_generale_più_telefonata"} or (organization_phone and not has_outreach_draft):
            channel = "telefonata"
            followup_window = "entro 2-3 giorni"
            reason = "Non risulta ancora una bozza outreach salvata e il canale telefonico e il modo piu rapido per chiarire il referente."
            micro_script = "Chiamo per capire se questo tema e seguito internamente da HR, direzione o altra funzione."
            next_status = "da_contattare"
        else:
            channel = "preparare_primo_contatto"
            followup_window = "prima possibile"
            reason = "Prima del follow-up serve completare almeno un primo contatto ordinato."
            micro_script = next_step or "Preparare il primo contatto e definire subito il canale piu credibile."
            next_status = "da_preparare"

    return {
        "followup_window": followup_window,
        "channel": channel,
        "micro_script": micro_script,
        "reason": reason,
        "next_status": next_status,
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
