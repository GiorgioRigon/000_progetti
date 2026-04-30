from __future__ import annotations

import sys
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.followup_planner import (  # noqa: E402
    build_followup_note,
    extract_followup_data,
    merge_followup_notes,
    suggest_followup,
)


class FollowupPlannerTests(unittest.TestCase):
    def test_build_extract_and_merge_followup_notes(self) -> None:
        followup_note = build_followup_note(
            followup_window="3-5 giorni lavorativi",
            channel="telefonata_o_email_breve",
            micro_script="Riprendo la mail inviata per capire se il tema e attuale.",
            reason="Esiste gia una bozza outreach e conviene verificare il riscontro.",
            next_status="attesa_riscontro",
        )

        self.assertIn("Finestra: 3-5 giorni lavorativi", followup_note)
        self.assertIn("Canale: telefonata_o_email_breve", followup_note)

        merged = merge_followup_notes("Nota generale organization.", followup_note)
        self.assertIn("Nota generale organization.", merged)

        extracted = extract_followup_data(merged)
        self.assertEqual(extracted["followup_window"], "3-5 giorni lavorativi")
        self.assertEqual(extracted["channel"], "telefonata_o_email_breve")
        self.assertEqual(extracted["micro_script"], "Riprendo la mail inviata per capire se il tema e attuale.")
        self.assertEqual(extracted["reason"], "Esiste gia una bozza outreach e conviene verificare il riscontro.")
        self.assertEqual(extracted["next_status"], "attesa_riscontro")

    def test_suggest_followup_uses_outreach_history(self) -> None:
        suggestion = suggest_followup(
            organization={"phone": "+39 0444 123456"},
            qualification_data={"next_step": "Preparare bozza outreach."},
            strategy_data={"channel": "email_generale_più_telefonata"},
            outreach_history=[{"subject": "Prima bozza"}],
        )

        self.assertEqual(suggestion["channel"], "telefonata")
        self.assertIn("24-72 ore", suggestion["followup_window"])
        self.assertEqual(suggestion["next_status"], "da_instradare")


if __name__ == "__main__":
    unittest.main()
