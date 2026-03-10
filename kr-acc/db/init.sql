-- kr-acc database initialization
-- PostgreSQL 16 + Apache AGE

-- Enable AGE extension
CREATE EXTENSION IF NOT EXISTS age;
LOAD 'age';

-- ============================================================
-- Tables (explicitly in public schema)
-- ============================================================

-- Parties (정당)
CREATE TABLE parties (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) UNIQUE NOT NULL,
    color_hex       VARCHAR(7),
    assembly_term   INTEGER DEFAULT 22
);

-- Committees (위원회)
CREATE TABLE committees (
    id              SERIAL PRIMARY KEY,
    committee_id    VARCHAR(50) UNIQUE NOT NULL,
    name            VARCHAR(200) NOT NULL,
    committee_type  VARCHAR(50),
    assembly_term   INTEGER DEFAULT 22
);

-- Politicians (국회의원)
CREATE TABLE politicians (
    id              SERIAL PRIMARY KEY,
    assembly_id     VARCHAR(20) UNIQUE NOT NULL,
    name            VARCHAR(100) NOT NULL,
    name_hanja      VARCHAR(100),
    party           VARCHAR(100),
    constituency    VARCHAR(200),
    elected_count   INTEGER,
    committees      JSONB,
    profile_url     TEXT,
    photo_url       TEXT,
    birth_date      DATE,
    gender          VARCHAR(10),
    assembly_term   INTEGER DEFAULT 22,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Bills (법안)
CREATE TABLE bills (
    id              SERIAL PRIMARY KEY,
    bill_id         VARCHAR(30) UNIQUE NOT NULL,
    bill_no         VARCHAR(20),
    bill_name       TEXT NOT NULL,
    proposer_type   VARCHAR(20),
    propose_date    DATE,
    committee_id    VARCHAR(50),
    committee_name  VARCHAR(200),
    status          VARCHAR(50),
    result          VARCHAR(50),
    assembly_term   INTEGER DEFAULT 22,
    detail_url      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Bill Sponsors (발의자/공동발의자)
CREATE TABLE bill_sponsors (
    id              SERIAL PRIMARY KEY,
    bill_id         VARCHAR(30) REFERENCES bills(bill_id),
    politician_id   INTEGER REFERENCES politicians(id),
    sponsor_type    VARCHAR(20),
    UNIQUE(bill_id, politician_id)
);

-- Votes (본회의 표결)
CREATE TABLE votes (
    id              SERIAL PRIMARY KEY,
    vote_id         VARCHAR(50) UNIQUE NOT NULL,
    bill_id         VARCHAR(30) REFERENCES bills(bill_id),
    vote_date       DATE NOT NULL,
    total_members   INTEGER,
    yes_count       INTEGER,
    no_count        INTEGER,
    abstain_count   INTEGER,
    absent_count    INTEGER,
    result          VARCHAR(30),
    assembly_term   INTEGER DEFAULT 22
);

-- Vote Records (의원별 표결 기록)
CREATE TABLE vote_records (
    id              SERIAL PRIMARY KEY,
    vote_id         VARCHAR(50) REFERENCES votes(vote_id),
    politician_id   INTEGER REFERENCES politicians(id),
    vote_result     VARCHAR(10),
    UNIQUE(vote_id, politician_id)
);

-- ============================================================
-- Indexes
-- ============================================================

CREATE INDEX idx_politicians_party ON politicians(party);
CREATE INDEX idx_politicians_assembly_term ON politicians(assembly_term);
CREATE INDEX idx_politicians_name ON politicians(name);

CREATE INDEX idx_bills_status ON bills(status);
CREATE INDEX idx_bills_propose_date ON bills(propose_date);
CREATE INDEX idx_bills_assembly_term ON bills(assembly_term);
CREATE INDEX idx_bills_committee_id ON bills(committee_id);

CREATE INDEX idx_bill_sponsors_bill_id ON bill_sponsors(bill_id);
CREATE INDEX idx_bill_sponsors_politician_id ON bill_sponsors(politician_id);
CREATE INDEX idx_bill_sponsors_type ON bill_sponsors(sponsor_type);

CREATE INDEX idx_votes_bill_id ON votes(bill_id);
CREATE INDEX idx_votes_vote_date ON votes(vote_date);

CREATE INDEX idx_vote_records_vote_id ON vote_records(vote_id);
CREATE INDEX idx_vote_records_politician_id ON vote_records(politician_id);
CREATE INDEX idx_vote_records_result ON vote_records(vote_result);

-- ============================================================
-- Seed party data (22nd Assembly)
-- ============================================================

INSERT INTO parties (name, color_hex, assembly_term) VALUES
    ('국민의힘',       '#E61E2B', 22),
    ('더불어민주당',   '#004EA2', 22),
    ('조국혁신당',     '#0033A0', 22),
    ('개혁신당',       '#FF7210', 22),
    ('진보당',         '#D6001C', 22),
    ('기본소득당',     '#00B0B9', 22),
    ('사회민주당',     '#43B02A', 22);

-- ============================================================
-- Apache AGE graph
-- ============================================================

SET search_path = ag_catalog, "$user", public;
SELECT create_graph('kr_acc');
