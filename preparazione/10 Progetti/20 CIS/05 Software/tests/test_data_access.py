from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.data_access import (  # noqa: E402
    CampaignCreate,
    CampaignRepository,
    ContactCreate,
    ContactRepository,
    Database,
    MessageCreate,
    MessageRepository,
    OrganizationCreate,
    OrganizationRepository,
    OutreachActionCreate,
    OutreachActionRepository,
)


class DatabaseInitializationTests(unittest.TestCase):
    def test_init_db_script_creates_expected_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.sqlite3"
            command = [
                sys.executable,
                str(BASE_DIR / "init_db.py"),
                "--db",
                str(db_path),
            ]

            subprocess.run(command, check=True, cwd=BASE_DIR)

            self.assertTrue(db_path.exists())

            with sqlite3.connect(db_path) as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    ).fetchall()
                }

            self.assertIn("campaigns", tables)
            self.assertIn("organizations", tables)
            self.assertIn("contacts", tables)


class DataAccessCrudTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"
        schema_path = BASE_DIR / "data" / "schema.sql"
        schema_sql = schema_path.read_text(encoding="utf-8")

        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(schema_sql)
            connection.commit()

        self.database = Database(self.db_path)
        self.campaigns = CampaignRepository(self.database)
        self.organizations = OrganizationRepository(self.database)
        self.contacts = ContactRepository(self.database)
        self.outreach_actions = OutreachActionRepository(self.database)
        self.messages = MessageRepository(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_can_create_and_read_organization(self) -> None:
        campaign_id = self.campaigns.create(
            CampaignCreate(
                project_key="melodema",
                name="Spring Outreach",
            )
        )

        organization_id = self.organizations.create(
            OrganizationCreate(
                campaign_id=campaign_id,
                name="Teatro Comunale",
                project_key="melodema",
                city="Parma",
                website="https://example.org",
                employee_count=42,
            )
        )

        organization = self.organizations.get(organization_id)

        self.assertIsNotNone(organization)
        self.assertEqual(organization["name"], "Teatro Comunale")
        self.assertEqual(organization["campaign_id"], campaign_id)
        self.assertEqual(organization["project_key"], "melodema")
        self.assertEqual(organization["employee_count"], 42)

    def test_can_create_and_read_contact(self) -> None:
        organization_id = self.organizations.create(
            OrganizationCreate(
                name="Festival Corale",
                project_key="melodema",
                city="Bologna",
            )
        )

        contact_id = self.contacts.create(
            ContactCreate(
                organization_id=organization_id,
                full_name="Laura Bianchi",
                role="Direzione artistica",
                email="laura@example.org",
            )
        )

        contact = self.contacts.get(contact_id)
        contacts_for_organization = self.contacts.list_by_organization(organization_id)

        self.assertIsNotNone(contact)
        self.assertEqual(contact["full_name"], "Laura Bianchi")
        self.assertEqual(contact["organization_id"], organization_id)
        self.assertEqual(len(contacts_for_organization), 1)

    def test_can_filter_organizations_by_project(self) -> None:
        self.organizations.create(
            OrganizationCreate(
                name="Basilica di Santa Cecilia",
                project_key="melodema",
                city="Bergamo",
            )
        )
        self.organizations.create(
            OrganizationCreate(
                name="Ethics Advisory Group",
                project_key="ethics",
                city="Milano",
            )
        )

        melodema_organizations = self.organizations.list_by_project("melodema")
        ethics_organizations = self.organizations.list_by_project("ethics")

        self.assertEqual(len(melodema_organizations), 1)
        self.assertEqual(melodema_organizations[0]["name"], "Basilica di Santa Cecilia")
        self.assertEqual(len(ethics_organizations), 1)
        self.assertEqual(ethics_organizations[0]["name"], "Ethics Advisory Group")

    def test_can_create_outreach_action_and_message_history(self) -> None:
        organization_id = self.organizations.create(
            OrganizationCreate(
                name="IGSA Srl",
                project_key="ethics",
                city="Barbarano Mossano",
            )
        )
        contact_id = self.contacts.create(
            ContactCreate(
                organization_id=organization_id,
                full_name="Valentina Ciccarella",
                role="Responsabile del personale",
            )
        )

        action_id = self.outreach_actions.create(
            OutreachActionCreate(
                organization_id=organization_id,
                contact_id=contact_id,
                action_type="draft_outreach",
                channel="email",
                status="draft",
                summary="Spunto operativo per il rinnovo UNI/PdR 125",
            )
        )
        message_id = self.messages.create(
            MessageCreate(
                outreach_action_id=action_id,
                organization_id=organization_id,
                contact_id=contact_id,
                channel="email",
                subject="Spunto operativo per il rinnovo UNI/PdR 125 di IGSA Srl",
                body="Bozza outreach di prova.",
                status="draft",
            )
        )

        history = self.messages.list_by_organization(organization_id)

        self.assertGreater(message_id, 0)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["action_type"], "draft_outreach")
        self.assertEqual(history[0]["contact_full_name"], "Valentina Ciccarella")
        self.assertEqual(history[0]["subject"], "Spunto operativo per il rinnovo UNI/PdR 125 di IGSA Srl")


if __name__ == "__main__":
    unittest.main()
