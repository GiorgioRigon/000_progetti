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


@dataclass(slots=True)
class OutreachActionCreate:
    organization_id: int
    action_type: str
    campaign_id: int | None = None
    contact_id: int | None = None
    channel: str | None = None
    status: str = "planned"
    due_date: str | None = None
    completed_at: str | None = None
    summary: str | None = None


@dataclass(slots=True)
class MessageCreate:
    organization_id: int
    channel: str
    outreach_action_id: int | None = None
    contact_id: int | None = None
    direction: str = "outbound"
    subject: str | None = None
    body: str | None = None
    status: str = "draft"


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


class OutreachActionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, outreach_action: OutreachActionCreate) -> int:
        query = """
            INSERT INTO outreach_actions (
                campaign_id, organization_id, contact_id, action_type, channel,
                status, due_date, completed_at, summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            outreach_action.campaign_id,
            outreach_action.organization_id,
            outreach_action.contact_id,
            outreach_action.action_type,
            outreach_action.channel,
            outreach_action.status,
            outreach_action.due_date,
            outreach_action.completed_at,
            outreach_action.summary,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)


class MessageRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, message: MessageCreate) -> int:
        query = """
            INSERT INTO messages (
                outreach_action_id, organization_id, contact_id, direction, channel,
                subject, body, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            message.outreach_action_id,
            message.organization_id,
            message.contact_id,
            message.direction,
            message.channel,
            message.subject,
            message.body,
            message.status,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def list_by_organization(self, organization_id: int) -> list[dict[str, Any]]:
        query = """
            SELECT
                messages.*,
                outreach_actions.action_type,
                outreach_actions.summary AS action_summary,
                outreach_actions.due_date,
                contacts.full_name AS contact_full_name,
                contacts.role AS contact_role
            FROM messages
            LEFT JOIN outreach_actions
                ON outreach_actions.id = messages.outreach_action_id
            LEFT JOIN contacts
                ON contacts.id = messages.contact_id
            WHERE messages.organization_id = ?
            ORDER BY messages.created_at DESC, messages.id DESC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (organization_id,)).fetchall()
        return [dict(row) for row in rows]
