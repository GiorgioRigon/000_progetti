from __future__ import annotations

import io
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app import create_app  # noqa: E402


class ManualFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"
        schema_path = BASE_DIR / "data" / "schema.sql"
        schema_sql = schema_path.read_text(encoding="utf-8")

        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(schema_sql)
            connection.commit()

        self.app = create_app(db_path=self.db_path)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.demo_csv_path = BASE_DIR / "projects" / "melodema" / "demo_leads.csv"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_manual_flow_end_to_end(self) -> None:
        import_response = self._import_demo_csv()
        import_page = import_response.get_data(as_text=True)
        self.assertEqual(import_response.status_code, 200)
        self.assertIn("Import CSV completato correttamente.", import_page)
        self.assertIn("Festival Monteverdi Cremona", import_page)
        self.assertIn("Teatro Comunale di Ferrara", import_page)

        create_response = self.client.post(
            "/organizations",
            data={
                "form_type": "manual",
                "name": "Basilica di Santa Cecilia",
                "organization_type": "ente religioso",
                "sector": "musica sacra e stagioni corali",
                "city": "Bergamo",
                "region": "Lombardia",
                "country": "Italia",
                "website": "https://www.santacecilia-bergamo.it",
                "email": "musica@santacecilia-bergamo.it",
                "phone": "+39 035 123456",
                "notes": "Venue interessante per repertorio liturgico e concerti corali.",
            },
            follow_redirects=True,
        )
        create_page = create_response.get_data(as_text=True)
        self.assertEqual(create_response.status_code, 200)
        self.assertIn("Organization salvata correttamente.", create_page)
        self.assertIn("Basilica di Santa Cecilia", create_page)

        organization_id = self._find_organization_id("Basilica di Santa Cecilia")

        update_response = self.client.post(
            f"/organizations/{organization_id}",
            data={
                "form_type": "organization",
                "name": "Basilica di Santa Cecilia",
                "organization_type": "ente religioso e culturale",
                "sector": "musica sacra e rassegne corali",
                "city": "Bergamo",
                "region": "Lombardia",
                "country": "Italia",
                "website": "https://www.santacecilia-bergamo.it",
                "email": "direzione.artistica@santacecilia-bergamo.it",
                "phone": "+39 035 123456",
                "employee_count": "18",
                "notes": "Interesse plausibile per rassegna autunnale e collaborazione locale.",
            },
            follow_redirects=True,
        )
        update_page = update_response.get_data(as_text=True)
        self.assertEqual(update_response.status_code, 200)
        self.assertIn("Organization aggiornata correttamente.", update_page)
        self.assertIn("ente religioso e culturale", update_page)
        self.assertIn("18", update_page)
        self.assertIn("direzione.artistica@santacecilia-bergamo.it", update_page)

        add_contact_response = self.client.post(
            f"/organizations/{organization_id}",
            data={
                "form_type": "contact",
                "full_name": "Marta Colombo",
                "first_name": "Marta",
                "last_name": "Colombo",
                "role": "Responsabile eventi musicali",
                "email": "marta.colombo@santacecilia-bergamo.it",
                "phone": "+39 333 4445556",
                "linkedin_url": "https://www.linkedin.com/in/marta-colombo-demo",
                "notes": "Preferisce primo contatto via email con proposta sintetica.",
            },
            follow_redirects=True,
        )
        add_contact_page = add_contact_response.get_data(as_text=True)
        self.assertEqual(add_contact_response.status_code, 200)
        self.assertIn("Contatto aggiunto correttamente.", add_contact_page)
        self.assertIn("Marta Colombo", add_contact_page)

        contact_id = self._find_contact_id("Marta Colombo")

        edit_contact_response = self.client.post(
            f"/organizations/{organization_id}",
            data={
                "form_type": "edit_contact",
                "contact_id": str(contact_id),
                "full_name": "Marta Colombo",
                "first_name": "Marta",
                "last_name": "Colombo",
                "role": "Direzione artistica eventi musicali",
                "email": "marta.colombo@santacecilia-bergamo.it",
                "phone": "+39 333 4445556",
                "linkedin_url": "https://www.linkedin.com/in/marta-colombo-demo",
                "notes": "Contatto aggiornato dopo verifica manuale della funzione.",
            },
            follow_redirects=True,
        )
        edit_contact_page = edit_contact_response.get_data(as_text=True)
        self.assertEqual(edit_contact_response.status_code, 200)
        self.assertIn("Contatto aggiornato correttamente.", edit_contact_page)
        self.assertIn("Direzione artistica eventi musicali", edit_contact_page)

        qualification_response = self.client.post(
            f"/organizations/{organization_id}",
            data={
                "form_type": "lead_qualification",
                "fit_label": "alto",
                "priority_level": "alta",
                "opportunity_type": "cliente",
                "qualification_signals": "territorio forte, repertorio coerente",
                "next_step": "fare WB1",
                "qualification_note": "Lead promettente con buona coerenza artistica e logistica.",
            },
            follow_redirects=True,
        )
        qualification_page = qualification_response.get_data(as_text=True)
        self.assertEqual(qualification_response.status_code, 200)
        self.assertIn("Qualificazione lead aggiornata correttamente.", qualification_page)
        self.assertIn("territorio forte, repertorio coerente", qualification_page)

        strategy_response = self.client.post(
            f"/organizations/{organization_id}",
            data={
                "form_type": "wb3_strategy",
                "channel": "email_diretta",
                "channel_reason": "Esiste una email diretta della direzione artistica.",
                "commercial_angle": "Proporre un primo contatto orientato a repertorio coerente e collaborazione locale.",
                "caution_note": "Non dare per scontata la disponibilita di budget o calendario.",
                "next_step": "Preparare una prima mail sintetica e verificare un follow-up entro 5 giorni.",
            },
            follow_redirects=True,
        )
        strategy_page = strategy_response.get_data(as_text=True)
        self.assertEqual(strategy_response.status_code, 200)
        self.assertIn("WB3 aggiornato correttamente.", strategy_page)
        self.assertIn("email_diretta", strategy_page)

        followup_response = self.client.post(
            f"/organizations/{organization_id}",
            data={
                "form_type": "wb5_followup",
                "followup_window": "3-5 giorni lavorativi",
                "channel": "email_breve",
                "micro_script": "Riprendo il messaggio precedente per capire se il tema e attuale.",
                "reason": "Esiste una strategia gia definita e conviene un richiamo leggero.",
                "next_status": "attesa_riscontro",
            },
            follow_redirects=True,
        )
        followup_page = followup_response.get_data(as_text=True)
        self.assertEqual(followup_response.status_code, 200)
        self.assertIn("WB5 aggiornato correttamente.", followup_page)
        self.assertIn("3-5 giorni lavorativi", followup_page)

        relationship_memory_response = self.client.post(
            f"/organizations/{organization_id}",
            data={
                "form_type": "relationship_memory",
                "memory_type": "channel_preference",
                "content": "Preferisce un primo contatto via email con proposta sintetica.",
                "importance": "3",
                "source": "verifica manuale",
                "contact_id": str(contact_id),
            },
            follow_redirects=True,
        )
        relationship_memory_page = relationship_memory_response.get_data(as_text=True)
        self.assertEqual(relationship_memory_response.status_code, 200)
        self.assertIn("Relationship memory aggiornata correttamente.", relationship_memory_page)
        self.assertIn("channel_preference", relationship_memory_page)

        dashboard_response = self.client.get("/organizations")
        dashboard_page = dashboard_response.get_data(as_text=True)
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertIn("Festival Monteverdi Cremona", dashboard_page)
        self.assertIn("Basilica di Santa Cecilia", dashboard_page)

        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT project_key FROM organizations WHERE name = ?",
                ("Basilica di Santa Cecilia",),
            ).fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "melodema")

    def _import_demo_csv(self):
        csv_bytes = self.demo_csv_path.read_bytes()
        return self.client.post(
            "/organizations",
            data={
                "form_type": "csv_import",
                "csv_file": (io.BytesIO(csv_bytes), self.demo_csv_path.name),
            },
            content_type="multipart/form-data",
            follow_redirects=True,
        )

    def _find_organization_id(self, name: str) -> int:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM organizations WHERE name = ?",
                (name,),
            ).fetchone()
        self.assertIsNotNone(row)
        return int(row[0])

    def _find_contact_id(self, full_name: str) -> int:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT id FROM contacts WHERE full_name = ?",
                (full_name,),
            ).fetchone()
        self.assertIsNotNone(row)
        return int(row[0])


if __name__ == "__main__":
    unittest.main()
