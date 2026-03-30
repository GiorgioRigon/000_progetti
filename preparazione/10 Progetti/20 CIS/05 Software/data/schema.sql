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

CREATE INDEX IF NOT EXISTS idx_assets_campaign_id
    ON assets(campaign_id);
