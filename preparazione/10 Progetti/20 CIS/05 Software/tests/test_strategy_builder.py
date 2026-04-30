from __future__ import annotations

import sys
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.strategy_builder import (  # noqa: E402
    build_strategy_note,
    extract_strategy_data,
    merge_strategy_notes,
    suggest_strategy,
)


class StrategyBuilderTests(unittest.TestCase):
    def test_build_extract_and_merge_strategy_notes(self) -> None:
        strategy_note = build_strategy_note(
            channel="email_diretta",
            channel_reason="Esiste un referente con email diretta.",
            commercial_angle="Supporto operativo su rinnovo PdR125.",
            caution_note="Non dare per scontato il bisogno reale.",
            next_step="Preparare una prima mail personalizzata.",
        )

        self.assertIn("Canale: email_diretta", strategy_note)
        self.assertIn("Angolo commerciale: Supporto operativo su rinnovo PdR125.", strategy_note)

        merged = merge_strategy_notes("Nota generale organization.", strategy_note)
        self.assertIn("Nota generale organization.", merged)

        extracted = extract_strategy_data(merged)
        self.assertEqual(extracted["channel"], "email_diretta")
        self.assertEqual(extracted["channel_reason"], "Esiste un referente con email diretta.")
        self.assertEqual(extracted["commercial_angle"], "Supporto operativo su rinnovo PdR125.")
        self.assertEqual(extracted["caution_note"], "Non dare per scontato il bisogno reale.")
        self.assertEqual(extracted["next_step"], "Preparare una prima mail personalizzata.")

    def test_suggest_strategy_prefers_direct_email_when_available(self) -> None:
        suggestion = suggest_strategy(
            organization={
                "email": "info@example.com",
                "phone": "+39 0444 123456",
                "notes": "[PdR125]\nStato: certificata\n",
                "sector": "servizi",
            },
            contacts=[
                {
                    "full_name": "Valentina Ciccarella",
                    "role": "Responsabile HR",
                    "email": "valentina@example.com",
                }
            ],
            qualification_data={
                "fit_label": "alto",
                "qualification_signals": "PdR125 certificata, HR strutturata",
                "qualification_note": "",
            },
        )

        self.assertEqual(suggestion["channel"], "email_diretta")
        self.assertIn("email diretta", suggestion["channel_reason"])
        self.assertIn("PdR 125", suggestion["commercial_angle"])


if __name__ == "__main__":
    unittest.main()
