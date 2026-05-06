PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_key TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    target_type TEXT,
    geography TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_key TEXT NOT NULL DEFAULT 'melodema',
    campaign_id INTEGER,
    name TEXT NOT NULL,
    organization_type TEXT,
    sector TEXT,
    city TEXT,
    region TEXT,
    country TEXT,
    website TEXT,
    phone TEXT,
    email TEXT,
    employee_count INTEGER,
    source TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    role TEXT,
    email TEXT,
    phone TEXT,
    linkedin_url TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS outreach_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    organization_id INTEGER,
    contact_id INTEGER,
    action_type TEXT NOT NULL,
    channel TEXT,
    status TEXT NOT NULL DEFAULT 'planned',
    due_date TEXT,
    completed_at TEXT,
    summary TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outreach_action_id INTEGER,
    organization_id INTEGER,
    contact_id INTEGER,
    direction TEXT NOT NULL DEFAULT 'outbound',
    channel TEXT NOT NULL,
    subject TEXT,
    body TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (outreach_action_id) REFERENCES outreach_actions(id) ON DELETE SET NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS relationship_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id INTEGER NOT NULL,
    contact_id INTEGER,
    memory_type TEXT NOT NULL,
    content TEXT NOT NULL,
    importance INTEGER NOT NULL DEFAULT 1,
    source TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_key TEXT NOT NULL,
    agent_key TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    objective TEXT,
    source_type TEXT,
    source_ref TEXT,
    input_payload_json TEXT,
    output_payload_json TEXT,
    cost_estimate REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agent_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL,
    organization_id INTEGER,
    task_key TEXT NOT NULL,
    task_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    title TEXT NOT NULL,
    input_payload_json TEXT,
    result_payload_json TEXT,
    review_notes TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES agent_runs(id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    organization_id INTEGER,
    asset_type TEXT NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT,
    external_url TEXT,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE SET NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quote_intakes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_key TEXT NOT NULL,
    organization_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    intake_schema_key TEXT,
    intake_data_json TEXT,
    summary TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_key TEXT NOT NULL,
    organization_id INTEGER NOT NULL,
    quote_intake_id INTEGER,
    quote_number TEXT,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    currency TEXT NOT NULL DEFAULT 'EUR',
    subtotal_amount REAL NOT NULL DEFAULT 0,
    discount_amount REAL NOT NULL DEFAULT 0,
    total_amount REAL NOT NULL DEFAULT 0,
    valid_until TEXT,
    version_label TEXT,
    assumptions TEXT,
    internal_notes TEXT,
    client_notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (quote_intake_id) REFERENCES quote_intakes(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS quote_line_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id INTEGER NOT NULL,
    line_type TEXT NOT NULL,
    code TEXT,
    title TEXT NOT NULL,
    description TEXT,
    quantity REAL NOT NULL DEFAULT 1,
    unit TEXT,
    unit_price REAL NOT NULL DEFAULT 0,
    line_total REAL NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,
    pricing_source TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS quote_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id INTEGER NOT NULL,
    version_label TEXT NOT NULL,
    snapshot_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_organizations_campaign_id
    ON organizations(campaign_id);

CREATE INDEX IF NOT EXISTS idx_organizations_project_key
    ON organizations(project_key);

CREATE INDEX IF NOT EXISTS idx_contacts_organization_id
    ON contacts(organization_id);

CREATE INDEX IF NOT EXISTS idx_outreach_actions_campaign_id
    ON outreach_actions(campaign_id);

CREATE INDEX IF NOT EXISTS idx_outreach_actions_organization_id
    ON outreach_actions(organization_id);

CREATE INDEX IF NOT EXISTS idx_outreach_actions_contact_id
    ON outreach_actions(contact_id);

CREATE INDEX IF NOT EXISTS idx_messages_outreach_action_id
    ON messages(outreach_action_id);

CREATE INDEX IF NOT EXISTS idx_messages_organization_id
    ON messages(organization_id);

CREATE INDEX IF NOT EXISTS idx_relationship_memory_organization_id
    ON relationship_memory(organization_id);

CREATE INDEX IF NOT EXISTS idx_agent_runs_project_key
    ON agent_runs(project_key);

CREATE INDEX IF NOT EXISTS idx_agent_runs_agent_key
    ON agent_runs(agent_key);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_run_id
    ON agent_tasks(run_id);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_organization_id
    ON agent_tasks(organization_id);

CREATE INDEX IF NOT EXISTS idx_assets_campaign_id
    ON assets(campaign_id);

CREATE INDEX IF NOT EXISTS idx_quote_intakes_project_key
    ON quote_intakes(project_key);

CREATE INDEX IF NOT EXISTS idx_quote_intakes_organization_id
    ON quote_intakes(organization_id);

CREATE INDEX IF NOT EXISTS idx_quotes_project_key
    ON quotes(project_key);

CREATE INDEX IF NOT EXISTS idx_quotes_organization_id
    ON quotes(organization_id);

CREATE INDEX IF NOT EXISTS idx_quote_line_items_quote_id
    ON quote_line_items(quote_id);

CREATE INDEX IF NOT EXISTS idx_quote_versions_quote_id
    ON quote_versions(quote_id);
