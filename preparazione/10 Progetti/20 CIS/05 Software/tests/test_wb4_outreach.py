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
from app.data_access import (  # noqa: E402
    ContactCreate,
    ContactRepository,
    Database,
    OrganizationCreate,
    OrganizationRepository,
)
from app.outreach_drafter import build_outreach_draft, list_outreach_templates, suggest_outreach_template  # noqa: E402


class Wb4OutreachTests(unittest.TestCase):
    def test_lists_ethics_templates(self) -> None:
        templates = list_outreach_templates("ethics", BASE_DIR / "projects")

        template_names = [template["name"] for template in templates]
        self.assertIn("first_outreach.md", template_names)
        self.assertIn("first_outreach_direct.md", template_names)
        indexed = {template["name"]: template for template in templates}
        self.assertEqual(indexed["first_outreach.md"]["label"], "Prima mail consulenziale")
        self.assertIn("destinatario:hr", indexed["first_outreach.md"]["tags"])
        suggested = suggest_outreach_template(
            templates,
            {"role": "Responsabile del personale"},
        )
        self.assertIsNotNone(suggested)
        self.assertEqual(suggested["name"], "first_outreach.md")

    def test_build_outreach_draft_from_ethics_template(self) -> None:
        draft = build_outreach_draft(
            project_key="ethics",
            projects_root=BASE_DIR / "projects",
            organization={
                "name": "IGSA Srl",
                "city": "Barbarano Mossano",
                "sector": "gestione verde / servizi ambientali",
                "website": "https://www.igsasrl.it/",
                "notes": (
                    "[PdR125]\n"
                    "Stato: certificata\n"
                    "Scadenza certificazione: 2026-05-11\n"
                    "Organismo certificazione: SiCert\n"
                    "Fonte verifica: Accredia e sito aziendale\n"
                    "Settore rilevante: gestione verde\n"
                    "Ipotesi commerciale: possibile interesse al rinnovo triennale e a una gestione documentale piu ordinata\n"
                    "Gancio E-docs: preparazione evidenze e documenti per audit di rinnovo\n"
                ),
            },
            contact={
                "full_name": "Valentina Ciccarella",
                "first_name": "Valentina",
                "role": "Responsabile del personale",
            },
            qualification_data={
                "qualification_signals": "PdR125 certificata, scadenza maggio 2026, documentazione audit",
                "next_step": "Preparare bozza outreach e contattare entro la prossima settimana.",
            },
        )

        self.assertIn("IGSA", draft.subject)
        self.assertIn("11 maggio 2026", draft.subject)
        self.assertIn("Buongiorno Valentina,", draft.body)
        self.assertIn("E-docs", draft.body)
        self.assertIn("sono Giorgio", draft.body)

    def test_outreach_draft_saves_message_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.sqlite3"
            schema_sql = (BASE_DIR / "data" / "schema.sql").read_text(encoding="utf-8")

            with sqlite3.connect(db_path) as connection:
                connection.executescript(schema_sql)
                connection.commit()

            organizations = OrganizationRepository(Database(db_path))
            contacts = ContactRepository(Database(db_path))
            organization_id = organizations.create(
                OrganizationCreate(
                    name="IGSA Srl",
                    project_key="ethics",
                    organization_type="azienda certificata PdR125",
                    sector="gestione verde / servizi ambientali",
                    city="Barbarano Mossano",
                    region="Veneto",
                    country="Italia",
                    website="https://www.igsasrl.it/",
                    email="info@igsasrl.it",
                    notes=(
                        "[PdR125]\n"
                        "Stato: certificata\n"
                        "Scadenza certificazione: 2026-05-11\n"
                        "Organismo certificazione: SiCert\n"
                        "Fonte verifica: Accredia e sito aziendale\n"
                        "Settore rilevante: gestione verde\n"
                        "Ipotesi commerciale: possibile interesse al rinnovo triennale e a una gestione documentale piu ordinata\n"
                        "Gancio E-docs: preparazione evidenze e documenti per audit di rinnovo\n"
                        "\n"
                        "[Lead qualification]\n"
                        "Fit: alto\n"
                        "Tipo opportunita: cliente\n"
                        "Priorita: alta\n"
                        "Segnali: PdR125 certificata, scadenza maggio 2026, documentazione audit\n"
                        "Prossimo passo: Preparare bozza outreach e contattare entro la prossima settimana.\n"
                        "[/Lead qualification]\n"
                    ),
                )
            )
            contact_id = contacts.create(
                ContactCreate(
                    organization_id=organization_id,
                    full_name="Valentina Ciccarella",
                    first_name="Valentina",
                    role="Responsabile del personale",
                )
            )
            second_contact_id = contacts.create(
                ContactCreate(
                    organization_id=organization_id,
                    full_name="Gian Marco Amadei",
                    first_name="Gian Marco",
                    role="Amministratore Delegato",
                )
            )

            app = create_app(
                db_path=db_path,
                projects_root=BASE_DIR / "projects",
                active_project_key="ethics",
            )
            app.config["TESTING"] = True
            client = app.test_client()

            detail_response = client.get(f"/organizations/{organization_id}")
            detail_page = detail_response.get_data(as_text=True)
            self.assertEqual(detail_response.status_code, 200)
            self.assertIn("WB4 Outreach Drafter", detail_page)
            self.assertIn("Supporto operativo per il rinnovo UNI/PdR 125", detail_page)
            self.assertIn("11 maggio 2026", detail_page)
            self.assertIn("sono Giorgio", detail_page)
            self.assertIn("Prima mail consulenziale", detail_page)
            self.assertIn("Prima mail diretta", detail_page)
            self.assertIn("Consigliata:</strong> Prima mail diretta", detail_page)
            self.assertIn("Tag: destinatario:ceo, destinatario:generale", detail_page)

            regenerate_response = client.post(
                f"/organizations/{organization_id}",
                data={
                    "form_type": "outreach_regenerate",
                    "template_name": "first_outreach_direct.md",
                    "contact_id": str(second_contact_id),
                    "subject": "",
                    "body": "",
                },
            )
            regenerate_page = regenerate_response.get_data(as_text=True)
            self.assertEqual(regenerate_response.status_code, 200)
            self.assertIn("Buongiorno Gian Marco,", regenerate_page)
            self.assertIn("Amministratore Delegato", regenerate_page)
            self.assertIn("capire subito se questo tema riguarda anche voi", regenerate_page)

            save_response = client.post(
                f"/organizations/{organization_id}",
                data={
                    "form_type": "outreach_draft",
                    "template_name": "first_outreach.md",
                    "contact_id": str(contact_id),
                    "subject": "Spunto operativo per il rinnovo UNI/PdR 125 di IGSA Srl",
                    "body": (
                        "Buongiorno Valentina,\n\n"
                        "ti contatto per condividere un confronto rapido sul rinnovo UNI/PdR 125.\n"
                    ),
                },
                follow_redirects=True,
            )

            save_page = save_response.get_data(as_text=True)
            self.assertEqual(save_response.status_code, 200)
            self.assertIn("Bozza outreach salvata correttamente.", save_page)
            self.assertIn("Storico outreach", save_page)
            self.assertIn("Spunto operativo per il rinnovo UNI/PdR 125 di IGSA Srl", save_page)
            self.assertIn("Buongiorno Valentina,", save_page)

            with sqlite3.connect(db_path) as connection:
                action_row = connection.execute(
                    (
                        "SELECT action_type, channel, status, summary "
                        "FROM outreach_actions WHERE organization_id = ?"
                    ),
                    (organization_id,),
                ).fetchone()
                message_row = connection.execute(
                    (
                        "SELECT contact_id, channel, status, subject, body "
                        "FROM messages WHERE organization_id = ?"
                    ),
                    (organization_id,),
                ).fetchone()

            self.assertIsNotNone(action_row)
            self.assertEqual(action_row[0], "draft_outreach")
            self.assertEqual(action_row[1], "email")
            self.assertEqual(action_row[2], "draft")
            self.assertIn("Spunto operativo", action_row[3])

            self.assertIsNotNone(message_row)
            self.assertEqual(message_row[0], contact_id)
            self.assertEqual(message_row[1], "email")
            self.assertEqual(message_row[2], "draft")
            self.assertEqual(message_row[3], "Spunto operativo per il rinnovo UNI/PdR 125 di IGSA Srl")
            self.assertIn("rinnovo UNI/PdR 125", message_row[4])


if __name__ == "__main__":
    unittest.main()
