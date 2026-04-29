from __future__ import annotations

import importlib.util
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_ACCESS_PATH = BASE_DIR / "app" / "data_access.py"
SPEC = importlib.util.spec_from_file_location("cis_data_access", DATA_ACCESS_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load data access module from {DATA_ACCESS_PATH}")
DATA_ACCESS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DATA_ACCESS
SPEC.loader.exec_module(DATA_ACCESS)

CampaignCreate = DATA_ACCESS.CampaignCreate
CampaignRepository = DATA_ACCESS.CampaignRepository
ContactCreate = DATA_ACCESS.ContactCreate
ContactRepository = DATA_ACCESS.ContactRepository
Database = DATA_ACCESS.Database
MessageCreate = DATA_ACCESS.MessageCreate
MessageRepository = DATA_ACCESS.MessageRepository
OrganizationCreate = DATA_ACCESS.OrganizationCreate
OrganizationRepository = DATA_ACCESS.OrganizationRepository
OutreachActionCreate = DATA_ACCESS.OutreachActionCreate
OutreachActionRepository = DATA_ACCESS.OutreachActionRepository
QuoteCreate = DATA_ACCESS.QuoteCreate
QuoteIntakeCreate = DATA_ACCESS.QuoteIntakeCreate
QuoteIntakeRepository = DATA_ACCESS.QuoteIntakeRepository
QuoteLineItemCreate = DATA_ACCESS.QuoteLineItemCreate
QuoteLineItemRepository = DATA_ACCESS.QuoteLineItemRepository
QuoteRepository = DATA_ACCESS.QuoteRepository
QuoteVersionCreate = DATA_ACCESS.QuoteVersionCreate
QuoteVersionRepository = DATA_ACCESS.QuoteVersionRepository
build_quote_snapshot = DATA_ACCESS.build_quote_snapshot


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
            self.assertIn("quote_intakes", tables)
            self.assertIn("quotes", tables)
            self.assertIn("quote_line_items", tables)
            self.assertIn("quote_versions", tables)


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
        self.quote_intakes = QuoteIntakeRepository(self.database)
        self.quotes = QuoteRepository(self.database)
        self.quote_line_items = QuoteLineItemRepository(self.database)
        self.quote_versions = QuoteVersionRepository(self.database)

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

    def test_can_create_quote_intake_quote_and_versions(self) -> None:
        organization_id = self.organizations.create(
            OrganizationCreate(
                name="Ethics Client Spa",
                project_key="ethics",
                city="Vicenza",
            )
        )
        intake_id = self.quote_intakes.create(
            QuoteIntakeCreate(
                project_key="ethics",
                organization_id=organization_id,
                title="Rinnovo ordinato PdR125",
                intake_schema_key="pdr125_edocs",
                intake_data={
                    "requested_by": "Giorgio",
                    "scope_summary": "Supporto per rinnovo e setup E-Docs",
                },
                summary="Supporto per rinnovo e setup E-Docs",
            )
        )
        quote_id = self.quotes.create(
            QuoteCreate(
                project_key="ethics",
                organization_id=organization_id,
                quote_intake_id=intake_id,
                title="Preventivo rinnovo PdR125",
                quote_number="ETH-DRAFT",
                status="draft",
                currency="EUR",
                valid_until="2026-05-31",
                version_label="v1",
            )
        )
        self.quote_line_items.create(
            QuoteLineItemCreate(
                quote_id=quote_id,
                line_type="service",
                code="ETH-CONS",
                title="Consulenza PdR125",
                quantity=2,
                unit="giornata",
                unit_price=450.0,
                pricing_source="manual",
            )
        )

        quote = self.quotes.get(quote_id)
        intake = self.quote_intakes.get(intake_id)
        line_items = self.quote_line_items.list_by_quote(quote_id)
        version_id = self.quote_versions.create(
            QuoteVersionCreate(
                quote_id=quote_id,
                version_label="v1",
                snapshot=build_quote_snapshot(quote or {}, intake, line_items),
            )
        )
        versions = self.quote_versions.list_by_quote(quote_id)
        project_quotes = self.quotes.list_by_project("ethics")
        organization_quotes = self.quotes.list_by_organization(organization_id)

        self.assertIsNotNone(intake)
        self.assertEqual(intake["intake_data"]["requested_by"], "Giorgio")
        self.assertIsNotNone(quote)
        self.assertEqual(quote["quote_number"], "ETH-DRAFT")
        self.assertEqual(len(line_items), 1)
        self.assertEqual(line_items[0]["line_total"], 900.0)
        self.assertGreater(version_id, 0)
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0]["snapshot"]["quote"]["title"], "Preventivo rinnovo PdR125")
        self.assertEqual(len(project_quotes), 1)
        self.assertEqual(len(organization_quotes), 1)


if __name__ == "__main__":
    unittest.main()
