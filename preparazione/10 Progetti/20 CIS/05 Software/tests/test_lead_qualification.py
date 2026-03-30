from __future__ import annotations

import sys
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.lead_qualification import (  # noqa: E402
    build_qualification_note,
    extract_qualification_data,
    merge_qualification_notes,
)


class LeadQualificationTests(unittest.TestCase):
    def test_build_extract_and_merge_qualification_notes(self) -> None:
        qualification_note = build_qualification_note(
            fit_label="alto",
            opportunity_type="cliente",
            priority_level="alta",
            qualification_signals="PdR125, HR strutturata",
            next_step="fare WB1",
            qualification_note="Lead con segnali concreti e maturita organizzativa sufficiente.",
        )

        self.assertIn("Fit: alto", qualification_note)
        self.assertIn("Tipo opportunita: cliente", qualification_note)

        merged = merge_qualification_notes(
            existing_notes="Nota generale organization.",
            qualification_note=qualification_note,
        )
        self.assertIn("Nota generale organization.", merged)

        extracted = extract_qualification_data(merged)
        self.assertEqual(extracted["fit_label"], "alto")
        self.assertEqual(extracted["opportunity_type"], "cliente")
        self.assertEqual(extracted["priority_level"], "alta")
        self.assertEqual(extracted["qualification_signals"], "PdR125, HR strutturata")
        self.assertEqual(extracted["next_step"], "fare WB1")
        self.assertEqual(
            extracted["qualification_note"],
            "Lead con segnali concreti e maturita organizzativa sufficiente.",
        )


if __name__ == "__main__":
    unittest.main()
