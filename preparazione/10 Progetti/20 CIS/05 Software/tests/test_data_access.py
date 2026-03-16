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
    OrganizationCreate,
    OrganizationRepository,
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
                city="Parma",
                website="https://example.org",
            )
        )

        organization = self.organizations.get(organization_id)

        self.assertIsNotNone(organization)
        self.assertEqual(organization["name"], "Teatro Comunale")
        self.assertEqual(organization["campaign_id"], campaign_id)

    def test_can_create_and_read_contact(self) -> None:
        organization_id = self.organizations.create(
            OrganizationCreate(
                name="Festival Corale",
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


if __name__ == "__main__":
    unittest.main()
