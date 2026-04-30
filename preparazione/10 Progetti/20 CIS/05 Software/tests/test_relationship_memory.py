from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.data_access import (  # noqa: E402
    ContactCreate,
    ContactRepository,
    Database,
    OrganizationCreate,
    OrganizationRepository,
    RelationshipMemoryCreate,
    RelationshipMemoryRepository,
)


class RelationshipMemoryTests(unittest.TestCase):
    def test_create_and_list_relationship_memory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "test.sqlite3"
            schema_sql = (BASE_DIR / "data" / "schema.sql").read_text(encoding="utf-8")

            with sqlite3.connect(db_path) as connection:
                connection.executescript(schema_sql)
                connection.commit()

            organizations = OrganizationRepository(Database(db_path))
            contacts = ContactRepository(Database(db_path))
            memory_repo = RelationshipMemoryRepository(Database(db_path))

            organization_id = organizations.create(
                OrganizationCreate(
                    name="IGSA Srl",
                    project_key="ethics",
                )
            )
            contact_id = contacts.create(
                ContactCreate(
                    organization_id=organization_id,
                    full_name="Valentina Ciccarella",
                    role="Responsabile del personale",
                )
            )

            memory_repo.create(
                RelationshipMemoryCreate(
                    organization_id=organization_id,
                    contact_id=contact_id,
                    memory_type="channel_preference",
                    content="Preferisce primo contatto via email breve e concreta.",
                    importance=3,
                    source="nota operativa",
                )
            )

            items = memory_repo.list_by_organization(organization_id)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["memory_type"], "channel_preference")
            self.assertEqual(items[0]["contact_full_name"], "Valentina Ciccarella")
            self.assertEqual(items[0]["importance"], 3)


if __name__ == "__main__":
    unittest.main()
