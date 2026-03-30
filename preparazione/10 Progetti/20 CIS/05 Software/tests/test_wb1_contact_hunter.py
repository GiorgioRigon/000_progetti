from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app  # noqa: E402
from app.data_access import Database, OrganizationCreate, OrganizationRepository  # noqa: E402
from app.wb1_contact_hunter import (  # noqa: E402
    build_research_note,
    build_contact_hunter_prompt,
    extract_research_metadata,
    extract_research_note,
    extract_social_profiles,
    merge_wb1_notes,
)


class Wb1ContactHunterTests(unittest.TestCase):
    def test_build_prompt_and_merge_notes(self) -> None:
        preview = build_contact_hunter_prompt(
            organization_name="Festival Corale Bergamasco",
            organization_type="festival",
            city="Bergamo",
            region="Lombardia",
            country="Italia",
            website="https://festival.example",
            current_email="info@festival.example",
            current_phone="+39 035 123456",
            existing_contacts=[{"full_name": "Marta Colombo", "role": "Direzione artistica"}],
            profile={
                "contact_goal": "Trovare un referente per la programmazione artistica.",
                "priority_roles": ["direzione artistica"],
                "required_fields": ["referente", "email", "telefono"],
            },
        )
        self.assertIn("Organization: Festival Corale Bergamasco", preview)
        self.assertIn("Obiettivo: Trovare un referente per la programmazione artistica.", preview)
        self.assertIn("- Marta Colombo | Direzione artistica", preview)
        self.assertIn("Dati minimi richiesti dal profilo:", preview)

        merged_notes = merge_wb1_notes(
            existing_notes="Nota generale organization.",
            social_profiles=[
                "instagram | https://instagram.com/festival.example",
                "facebook | https://facebook.com/festival.example",
            ],
            research_note="Email verificata su pagina contatti ufficiale.",
        )
        self.assertIn("Nota generale organization.", merged_notes)
        self.assertEqual(
            extract_social_profiles(merged_notes),
            [
                "instagram | https://instagram.com/festival.example",
                "facebook | https://facebook.com/festival.example",
            ],
        )
        self.assertEqual(
            extract_research_note(merged_notes),
            "Email verificata su pagina contatti ufficiale.",
        )

        structured_note = build_research_note(
            research_note="Ruolo coerente con il bisogno.",
            verification_source="pagina team ufficiale",
            contact_level="decision maker",
            qualification_signals="PdR125, HR",
        )
        self.assertIn("Fonte verifica: pagina team ufficiale", structured_note)

        metadata = extract_research_metadata(
            merge_wb1_notes(
                existing_notes=None,
                social_profiles=[],
                research_note=structured_note,
            )
        )
        self.assertEqual(metadata["verification_source"], "pagina team ufficiale")
        self.assertEqual(metadata["contact_level"], "decision maker")
        self.assertEqual(metadata["qualification_signals"], "PdR125, HR")
        self.assertEqual(metadata["research_note"], "Ruolo coerente con il bisogno.")

    def test_wb1_enrichment_updates_organization_and_creates_contact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.sqlite3"
            schema_sql = (BASE_DIR / "data" / "schema.sql").read_text(encoding="utf-8")

            with sqlite3.connect(db_path) as connection:
                connection.executescript(schema_sql)
                connection.commit()

            organizations = OrganizationRepository(Database(db_path))
            organization_id = organizations.create(
                OrganizationCreate(
                    name="Basilica di Santa Cecilia",
                    organization_type="ente culturale",
                    city="Bergamo",
                    region="Lombardia",
                    country="Italia",
                    notes="Lead promettente da approfondire.",
                )
            )

            app = create_app(db_path=db_path)
            app.config["TESTING"] = True
            client = app.test_client()

            response = client.post(
                f"/organizations/{organization_id}",
                data={
                    "form_type": "wb1_enrichment",
                    "website": "https://www.santacecilia-bergamo.it",
                    "general_email": "eventi@santacecilia-bergamo.it",
                    "general_phone": "+39 035 123456",
                    "contact_full_name": "Marta Colombo",
                    "contact_role": "Responsabile eventi musicali",
                    "contact_email": "marta.colombo@santacecilia-bergamo.it",
                    "contact_phone": "+39 333 4445556",
                    "social_profiles": (
                        "instagram | https://instagram.com/santacecilia.bergamo\n"
                        "facebook | https://facebook.com/santacecilia.bergamo"
                    ),
                    "verification_source": "sito ufficiale e pagina contatti",
                    "contact_level": "decision maker",
                    "qualification_signals": "eventi musicali, programmazione culturale",
                    "research_note": "Dati verificati manualmente su sito ufficiale e profili social.",
                },
                follow_redirects=True,
            )

            page = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("WB1 aggiornato correttamente.", page)
            self.assertIn("Prompt preview WB1", page)
            self.assertIn("instagram | https://instagram.com/santacecilia.bergamo", page)

            with sqlite3.connect(db_path) as connection:
                organization_row = connection.execute(
                    "SELECT website, email, phone, notes FROM organizations WHERE id = ?",
                    (organization_id,),
                ).fetchone()
                contact_row = connection.execute(
                    "SELECT full_name, role, email, phone, notes FROM contacts WHERE organization_id = ?",
                    (organization_id,),
                ).fetchone()

            self.assertIsNotNone(organization_row)
            self.assertEqual(organization_row[0], "https://www.santacecilia-bergamo.it")
            self.assertEqual(organization_row[1], "eventi@santacecilia-bergamo.it")
            self.assertEqual(organization_row[2], "+39 035 123456")
            self.assertIn("[WB1 social]", organization_row[3])
            self.assertIn("Dati verificati manualmente", organization_row[3])
            self.assertIn("Fonte verifica: sito ufficiale e pagina contatti", organization_row[3])
            self.assertIn("Livello contatto: decision maker", organization_row[3])
            self.assertIn("Segnali qualificazione: eventi musicali, programmazione culturale", organization_row[3])

            self.assertIsNotNone(contact_row)
            self.assertEqual(contact_row[0], "Marta Colombo")
            self.assertEqual(contact_row[1], "Responsabile eventi musicali")
            self.assertEqual(contact_row[2], "marta.colombo@santacecilia-bergamo.it")
            self.assertEqual(contact_row[3], "+39 333 4445556")
            self.assertEqual(contact_row[4], "Contatto aggiunto da WB1 Contact Hunter.")


if __name__ == "__main__":
    unittest.main()
