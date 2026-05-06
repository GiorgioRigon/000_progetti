from __future__ import annotations

import sqlite3
from dataclasses import dataclass
import json
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
    employee_count: int | None = None
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


@dataclass(slots=True)
class RelationshipMemoryCreate:
    organization_id: int
    memory_type: str
    content: str
    contact_id: int | None = None
    importance: int = 1
    source: str | None = None


@dataclass(slots=True)
class AgentRunCreate:
    project_key: str
    agent_key: str
    title: str
    objective: str | None = None
    status: str = "queued"
    source_type: str | None = None
    source_ref: str | None = None
    input_payload: dict[str, Any] | None = None
    output_payload: dict[str, Any] | None = None
    cost_estimate: float = 0.0


@dataclass(slots=True)
class AgentTaskCreate:
    run_id: int
    task_key: str
    task_type: str
    title: str
    organization_id: int | None = None
    status: str = "queued"
    input_payload: dict[str, Any] | None = None
    result_payload: dict[str, Any] | None = None
    review_notes: str | None = None
    sort_order: int = 0


@dataclass(slots=True)
class QuoteIntakeCreate:
    project_key: str
    organization_id: int
    title: str
    status: str = "draft"
    intake_schema_key: str | None = None
    intake_data: dict[str, Any] | None = None
    summary: str | None = None


@dataclass(slots=True)
class QuoteCreate:
    project_key: str
    organization_id: int
    title: str
    quote_intake_id: int | None = None
    quote_number: str | None = None
    status: str = "draft"
    currency: str = "EUR"
    subtotal_amount: float = 0.0
    discount_amount: float = 0.0
    total_amount: float = 0.0
    valid_until: str | None = None
    version_label: str | None = None
    assumptions: str | None = None
    internal_notes: str | None = None
    client_notes: str | None = None


@dataclass(slots=True)
class QuoteLineItemCreate:
    quote_id: int
    line_type: str
    title: str
    quantity: float
    unit_price: float
    code: str | None = None
    description: str | None = None
    unit: str | None = None
    line_total: float | None = None
    sort_order: int = 0
    pricing_source: str | None = None


@dataclass(slots=True)
class QuoteVersionCreate:
    quote_id: int
    version_label: str
    snapshot: dict[str, Any]


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
        schema_sql = (BASE_DIR / "data" / "schema.sql").read_text(encoding="utf-8")
        connection.executescript(schema_sql)

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
        if "employee_count" not in columns:
            connection.execute(
                "ALTER TABLE organizations ADD COLUMN employee_count INTEGER"
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
                country, website, phone, email, employee_count, source, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            organization.employee_count,
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
                employee_count = ?,
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
            organization.employee_count,
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


class RelationshipMemoryRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, memory: RelationshipMemoryCreate) -> int:
        query = """
            INSERT INTO relationship_memory (
                organization_id, contact_id, memory_type, content, importance, source
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (
            memory.organization_id,
            memory.contact_id,
            memory.memory_type,
            memory.content,
            memory.importance,
            memory.source,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def list_by_organization(self, organization_id: int) -> list[dict[str, Any]]:
        query = """
            SELECT
                relationship_memory.*,
                contacts.full_name AS contact_full_name,
                contacts.role AS contact_role
            FROM relationship_memory
            LEFT JOIN contacts
                ON contacts.id = relationship_memory.contact_id
            WHERE relationship_memory.organization_id = ?
            ORDER BY relationship_memory.importance DESC, relationship_memory.created_at DESC, relationship_memory.id DESC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (organization_id,)).fetchall()
        return [dict(row) for row in rows]


class AgentRunRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, run: AgentRunCreate) -> int:
        query = """
            INSERT INTO agent_runs (
                project_key, agent_key, title, status, objective, source_type, source_ref,
                input_payload_json, output_payload_json, cost_estimate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            run.project_key,
            run.agent_key,
            run.title,
            run.status,
            run.objective,
            run.source_type,
            run.source_ref,
            json.dumps(run.input_payload or {}, ensure_ascii=True),
            json.dumps(run.output_payload or {}, ensure_ascii=True),
            run.cost_estimate,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def get(self, run_id: int) -> dict[str, Any] | None:
        query = "SELECT * FROM agent_runs WHERE id = ?"
        with self.database.connect() as connection:
            row = connection.execute(query, (run_id,)).fetchone()
        if row is None:
            return None
        payload = dict(row)
        payload["input_payload"] = _load_json_object(payload.get("input_payload_json"))
        payload["output_payload"] = _load_json_object(payload.get("output_payload_json"))
        return payload

    def list_by_project(self, project_key: str) -> list[dict[str, Any]]:
        query = """
            SELECT
                agent_runs.*,
                COUNT(agent_tasks.id) AS task_count,
                SUM(CASE WHEN agent_tasks.status = 'queued' THEN 1 ELSE 0 END) AS queued_count,
                SUM(CASE WHEN agent_tasks.status = 'review' THEN 1 ELSE 0 END) AS review_count,
                SUM(CASE WHEN agent_tasks.status = 'approved' THEN 1 ELSE 0 END) AS approved_count,
                SUM(CASE WHEN agent_tasks.status = 'rejected' THEN 1 ELSE 0 END) AS rejected_count,
                SUM(CASE WHEN agent_tasks.status = 'imported' THEN 1 ELSE 0 END) AS imported_count,
                SUM(CASE WHEN agent_tasks.status = 'archived' THEN 1 ELSE 0 END) AS archived_count
            FROM agent_runs
            LEFT JOIN agent_tasks ON agent_tasks.run_id = agent_runs.id
            WHERE agent_runs.project_key = ?
            GROUP BY agent_runs.id
            ORDER BY agent_runs.created_at DESC, agent_runs.id DESC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (project_key,)).fetchall()
        payloads = [dict(row) for row in rows]
        for payload in payloads:
            payload["input_payload"] = _load_json_object(payload.get("input_payload_json"))
            payload["output_payload"] = _load_json_object(payload.get("output_payload_json"))
        return payloads

    def update(
        self,
        run_id: int,
        *,
        status: str,
        output_payload: dict[str, Any] | None = None,
        cost_estimate: float | None = None,
    ) -> None:
        current = self.get(run_id)
        if current is None:
            raise ValueError(f"Agent run {run_id} not found.")
        query = """
            UPDATE agent_runs
            SET
                status = ?,
                output_payload_json = ?,
                cost_estimate = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        with self.database.connect() as connection:
            connection.execute(
                query,
                (
                    status,
                    json.dumps(output_payload if output_payload is not None else current.get("output_payload", {}), ensure_ascii=True),
                    cost_estimate if cost_estimate is not None else float(current.get("cost_estimate", 0) or 0),
                    run_id,
                ),
            )
            connection.commit()


class AgentTaskRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_many(self, tasks: list[AgentTaskCreate]) -> list[int]:
        query = """
            INSERT INTO agent_tasks (
                run_id, organization_id, task_key, task_type, status, title,
                input_payload_json, result_payload_json, review_notes, sort_order
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        task_ids: list[int] = []
        with self.database.connect() as connection:
            for task in tasks:
                cursor = connection.execute(
                    query,
                    (
                        task.run_id,
                        task.organization_id,
                        task.task_key,
                        task.task_type,
                        task.status,
                        task.title,
                        json.dumps(task.input_payload or {}, ensure_ascii=True),
                        json.dumps(task.result_payload or {}, ensure_ascii=True),
                        task.review_notes,
                        task.sort_order,
                    ),
                )
                task_ids.append(int(cursor.lastrowid))
            connection.commit()
        return task_ids

    def get(self, task_id: int) -> dict[str, Any] | None:
        query = """
            SELECT
                agent_tasks.*,
                agent_runs.project_key,
                agent_runs.agent_key,
                organizations.name AS organization_name
            FROM agent_tasks
            JOIN agent_runs ON agent_runs.id = agent_tasks.run_id
            LEFT JOIN organizations ON organizations.id = agent_tasks.organization_id
            WHERE agent_tasks.id = ?
        """
        with self.database.connect() as connection:
            row = connection.execute(query, (task_id,)).fetchone()
        if row is None:
            return None
        payload = dict(row)
        payload["input_payload"] = _load_json_object(payload.get("input_payload_json"))
        payload["result_payload"] = _load_json_object(payload.get("result_payload_json"))
        return payload

    def list_by_run(self, run_id: int) -> list[dict[str, Any]]:
        query = """
            SELECT
                agent_tasks.*,
                organizations.name AS organization_name
            FROM agent_tasks
            LEFT JOIN organizations ON organizations.id = agent_tasks.organization_id
            WHERE agent_tasks.run_id = ?
            ORDER BY agent_tasks.sort_order ASC, agent_tasks.id ASC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (run_id,)).fetchall()
        payloads = [dict(row) for row in rows]
        for payload in payloads:
            payload["input_payload"] = _load_json_object(payload.get("input_payload_json"))
            payload["result_payload"] = _load_json_object(payload.get("result_payload_json"))
        return payloads

    def update(
        self,
        task_id: int,
        *,
        status: str,
        review_notes: str | None = None,
        result_payload: dict[str, Any] | None = None,
    ) -> None:
        current = self.get(task_id)
        if current is None:
            raise ValueError(f"Agent task {task_id} not found.")
        query = """
            UPDATE agent_tasks
            SET
                status = ?,
                review_notes = ?,
                result_payload_json = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        with self.database.connect() as connection:
            connection.execute(
                query,
                (
                    status,
                    review_notes if review_notes is not None else current.get("review_notes"),
                    json.dumps(result_payload if result_payload is not None else current.get("result_payload", {}), ensure_ascii=True),
                    task_id,
                ),
            )
            connection.commit()

    def bulk_update_status(self, run_id: int, from_status: str, to_status: str) -> None:
        query = """
            UPDATE agent_tasks
            SET
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE run_id = ? AND status = ?
        """
        with self.database.connect() as connection:
            connection.execute(query, (to_status, run_id, from_status))
            connection.commit()


class QuoteIntakeRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, intake: QuoteIntakeCreate) -> int:
        query = """
            INSERT INTO quote_intakes (
                project_key, organization_id, title, status, intake_schema_key,
                intake_data_json, summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            intake.project_key,
            intake.organization_id,
            intake.title,
            intake.status,
            intake.intake_schema_key,
            json.dumps(intake.intake_data or {}, ensure_ascii=True),
            intake.summary,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def get(self, intake_id: int) -> dict[str, Any] | None:
        query = "SELECT * FROM quote_intakes WHERE id = ?"
        with self.database.connect() as connection:
            row = connection.execute(query, (intake_id,)).fetchone()
        if row is None:
            return None
        payload = dict(row)
        payload["intake_data"] = _load_json_object(payload.get("intake_data_json"))
        return payload

    def update(
        self,
        intake_id: int,
        *,
        status: str,
        intake_schema_key: str | None,
        intake_data: dict[str, Any],
        summary: str | None,
    ) -> None:
        query = """
            UPDATE quote_intakes
            SET
                status = ?,
                intake_schema_key = ?,
                intake_data_json = ?,
                summary = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        with self.database.connect() as connection:
            connection.execute(
                query,
                (
                    status,
                    intake_schema_key,
                    json.dumps(intake_data, ensure_ascii=True),
                    summary,
                    intake_id,
                ),
            )
            connection.commit()


class QuoteRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, quote: QuoteCreate) -> int:
        query = """
            INSERT INTO quotes (
                project_key, organization_id, quote_intake_id, quote_number, title, status,
                currency, subtotal_amount, discount_amount, total_amount, valid_until,
                version_label, assumptions, internal_notes, client_notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (
            quote.project_key,
            quote.organization_id,
            quote.quote_intake_id,
            quote.quote_number,
            quote.title,
            quote.status,
            quote.currency,
            quote.subtotal_amount,
            quote.discount_amount,
            quote.total_amount,
            quote.valid_until,
            quote.version_label,
            quote.assumptions,
            quote.internal_notes,
            quote.client_notes,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def get(self, quote_id: int) -> dict[str, Any] | None:
        query = """
            SELECT quotes.*, organizations.name AS organization_name
            FROM quotes
            LEFT JOIN organizations ON organizations.id = quotes.organization_id
            WHERE quotes.id = ?
        """
        with self.database.connect() as connection:
            row = connection.execute(query, (quote_id,)).fetchone()
        return dict(row) if row else None

    def list_by_project(self, project_key: str) -> list[dict[str, Any]]:
        query = """
            SELECT quotes.*, organizations.name AS organization_name
            FROM quotes
            LEFT JOIN organizations ON organizations.id = quotes.organization_id
            WHERE quotes.project_key = ?
            ORDER BY quotes.created_at DESC, quotes.id DESC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (project_key,)).fetchall()
        return [dict(row) for row in rows]

    def list_by_organization(self, organization_id: int) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM quotes
            WHERE organization_id = ?
            ORDER BY created_at DESC, id DESC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (organization_id,)).fetchall()
        return [dict(row) for row in rows]

    def update_amounts(
        self,
        quote_id: int,
        subtotal_amount: float,
        discount_amount: float,
        total_amount: float,
    ) -> None:
        query = """
            UPDATE quotes
            SET
                subtotal_amount = ?,
                discount_amount = ?,
                total_amount = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        with self.database.connect() as connection:
            connection.execute(
                query,
                (subtotal_amount, discount_amount, total_amount, quote_id),
            )
            connection.commit()


class QuoteLineItemRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, line_item: QuoteLineItemCreate) -> int:
        query = """
            INSERT INTO quote_line_items (
                quote_id, line_type, code, title, description, quantity, unit,
                unit_price, line_total, sort_order, pricing_source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        computed_line_total = (
            line_item.line_total
            if line_item.line_total is not None
            else float(line_item.quantity) * float(line_item.unit_price)
        )
        values = (
            line_item.quote_id,
            line_item.line_type,
            line_item.code,
            line_item.title,
            line_item.description,
            line_item.quantity,
            line_item.unit,
            line_item.unit_price,
            computed_line_total,
            line_item.sort_order,
            line_item.pricing_source,
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def list_by_quote(self, quote_id: int) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM quote_line_items
            WHERE quote_id = ?
            ORDER BY sort_order ASC, id ASC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (quote_id,)).fetchall()
        return [dict(row) for row in rows]


class QuoteVersionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, version: QuoteVersionCreate) -> int:
        query = """
            INSERT INTO quote_versions (
                quote_id, version_label, snapshot_json
            )
            VALUES (?, ?, ?)
        """
        values = (
            version.quote_id,
            version.version_label,
            json.dumps(version.snapshot, ensure_ascii=True),
        )
        with self.database.connect() as connection:
            cursor = connection.execute(query, values)
            connection.commit()
            return int(cursor.lastrowid)

    def list_by_quote(self, quote_id: int) -> list[dict[str, Any]]:
        query = """
            SELECT * FROM quote_versions
            WHERE quote_id = ?
            ORDER BY created_at DESC, id DESC
        """
        with self.database.connect() as connection:
            rows = connection.execute(query, (quote_id,)).fetchall()
        payloads = [dict(row) for row in rows]
        for payload in payloads:
            payload["snapshot"] = _load_json_object(payload.get("snapshot_json"))
        return payloads


def build_quote_snapshot(
    quote: dict[str, Any],
    intake: dict[str, Any] | None,
    line_items: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "quote": dict(quote),
        "intake": dict(intake) if intake else None,
        "line_items": [dict(line_item) for line_item in line_items],
    }


def _load_json_object(raw_value: Any) -> dict[str, Any]:
    if not raw_value:
        return {}
    if isinstance(raw_value, dict):
        return raw_value
    try:
        parsed = json.loads(str(raw_value))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}
