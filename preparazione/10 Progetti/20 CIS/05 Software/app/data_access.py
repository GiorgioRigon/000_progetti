from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "cis.sqlite3"


@dataclass(slots=True)
class CampaignCreate:
    project_key: str
    name: str
    description: str | None = None
    status: str = "draft"
    target_type: str | None = None
    geography: str | None = None


@dataclass(slots=True)
class OrganizationCreate:
    name: str
    project_key: str = "melodema"
    campaign_id: int | None = None
    organization_type: str | None = None
    sector: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    source: str | None = None
    notes: str | None = None


@dataclass(slots=True)
class ContactCreate:
    organization_id: int
    first_name: str | None = None
    last_name: str | None = None
    full_name: str | None = None
    role: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin_url: str | None = None
    notes: str | None = None


class Database:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        self._ensure_schema(connection)
        return connection

    def _ensure_schema(self, connection: sqlite3.Connection) -> None:
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(organizations)").fetchall()
        }
        if "project_key" not in columns:
            connection.execute(
                "ALTER TABLE organizations ADD COLUMN project_key TEXT NOT NULL DEFAULT 'melodema'"
            )
            connection.execute(
                "UPDATE organizations SET project_key = 'melodema' WHERE project_key IS NULL OR project_key = ''"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_organizations_project_key ON organizations(project_key)"
            )
            connection.commit()


class CampaignRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, campaign: CampaignCreate) -> int:
        query = """
            INSERT INTO campaigns (
                project_key, name, description, status, target_type, geography
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (
            campaign.project_key,
            campaign.name,
            campaign.description,
            campaign.status,
            campaign.target_type,
            campaign.geography,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def get(self, campaign_id: int) -> dict[str, Any] | None:
        query = "SELECT * FROM campaigns WHERE id = ?"
        with self.database.connect() as connection:
            row = connection.execute(query, (campaign_id,)).fetchone()
        return dict(row) if row else None

    def list_all(self) -> list[dict[str, Any]]:
        query = "SELECT * FROM campaigns ORDER BY created_at DESC, id DESC"
        with self.database.connect() as connection:
            rows = connection.execute(query).fetchall()
        return [dict(row) for row in rows]


class OrganizationRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, organization: OrganizationCreate) -> int:
        query = """
            INSERT INTO organizations (
                project_key, campaign_id, name, organization_type, sector, city, region,
                country, website, phone, email, source, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            organization.project_key,
            organization.campaign_id,
            organization.name,
            organization.organization_type,
            organization.sector,
            organization.city,
            organization.region,
            organization.country,
            organization.website,
            organization.phone,
            organization.email,
            organization.source,
            organization.notes,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def get(self, organization_id: int) -> dict[str, Any] | None:
        query = "SELECT * FROM organizations WHERE id = ?"
        with self.database.connect() as connection:
            row = connection.execute(query, (organization_id,)).fetchone()
        return dict(row) if row else None

    def update(self, organization_id: int, organization: OrganizationCreate) -> None:
        query = """
            UPDATE organizations
            SET
                project_key = ?,
                campaign_id = ?,
                name = ?,
                organization_type = ?,
                sector = ?,
                city = ?,
                region = ?,
                country = ?,
                website = ?,
                phone = ?,
                email = ?,
                source = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        values = (
            organization.project_key,
            organization.campaign_id,
            organization.name,
            organization.organization_type,
            organization.sector,
            organization.city,
            organization.region,
            organization.country,
            organization.website,
            organization.phone,
            organization.email,
            organization.source,
            organization.notes,
            organization_id,
        )
        with self.database.connect() as connection:
            connection.execute(query, values)
            connection.commit()

    def list_all(self) -> list[dict[str, Any]]:
        query = "SELECT * FROM organizations ORDER BY created_at DESC, id DESC"
        with self.database.connect() as connection:
            rows = connection.execute(query).fetchall()
        return [dict(row) for row in rows]

    def list_by_project(self, project_key: str) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM organizations
            WHERE project_key = ?
            ORDER BY created_at DESC, id DESC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (project_key,)).fetchall()
        return [dict(row) for row in rows]

    def list_by_campaign(self, campaign_id: int) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM organizations
            WHERE campaign_id = ?
            ORDER BY created_at DESC, id DESC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (campaign_id,)).fetchall()
        return [dict(row) for row in rows]


class ContactRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, contact: ContactCreate) -> int:
        query = """
            INSERT INTO contacts (
                organization_id, first_name, last_name, full_name, role,
                email, phone, linkedin_url, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            contact.organization_id,
            contact.first_name,
            contact.last_name,
            contact.full_name,
            contact.role,
            contact.email,
            contact.phone,
            contact.linkedin_url,
            contact.notes,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def get(self, contact_id: int) -> dict[str, Any] | None:
        query = "SELECT * FROM contacts WHERE id = ?"
        with self.database.connect() as connection:
            row = connection.execute(query, (contact_id,)).fetchone()
        return dict(row) if row else None

    def update(self, contact_id: int, contact: ContactCreate) -> None:
        query = """
            UPDATE contacts
            SET
                organization_id = ?,
                first_name = ?,
                last_name = ?,
                full_name = ?,
                role = ?,
                email = ?,
                phone = ?,
                linkedin_url = ?,
                notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        values = (
            contact.organization_id,
            contact.first_name,
            contact.last_name,
            contact.full_name,
            contact.role,
            contact.email,
            contact.phone,
            contact.linkedin_url,
            contact.notes,
            contact_id,
        )
        with self.database.connect() as connection:
            connection.execute(query, values)
            connection.commit()

    def list_by_organization(self, organization_id: int) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM contacts
            WHERE organization_id = ?
            ORDER BY created_at DESC, id DESC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (organization_id,)).fetchall()
        return [dict(row) for row in rows]
