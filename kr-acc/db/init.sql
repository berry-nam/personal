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
    eng_name        VARCHAR(100),
    bio             TEXT,
    email           VARCHAR(200),
    homepage        TEXT,
    office_address  VARCHAR(300),
    birth_date      DATE,
    gender          VARCHAR(10),
    assembly_term   INTEGER DEFAULT 22,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Bills (법안)
CREATE TABLE bills (
    id              SERIAL PRIMARY KEY,
    bill_id         VARCHAR(50) UNIQUE NOT NULL,
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
    bill_id         VARCHAR(50) REFERENCES bills(bill_id),
    politician_id   INTEGER REFERENCES politicians(id),
    sponsor_type    VARCHAR(20),
    UNIQUE(bill_id, politician_id)
);

-- Votes (본회의 표결)
CREATE TABLE votes (
    id              SERIAL PRIMARY KEY,
    vote_id         VARCHAR(50) UNIQUE NOT NULL,
    bill_id         VARCHAR(50) REFERENCES bills(bill_id),
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
-- Asset Declarations (재산공개)
-- ============================================================

-- Asset disclosure reports (연도별 재산신고)
CREATE TABLE asset_declarations (
    id              SERIAL PRIMARY KEY,
    politician_id   INTEGER REFERENCES politicians(id),
    report_year     INTEGER NOT NULL,
    total_assets    BIGINT,           -- 총 재산 (원)
    total_real_estate BIGINT,         -- 부동산 합계
    total_deposits  BIGINT,           -- 예금 합계
    total_securities BIGINT,          -- 유가증권 합계
    total_crypto    BIGINT,           -- 가상자산 합계
    source          VARCHAR(50),      -- 'newstapa' | 'gazette' | 'manual'
    raw_data        JSONB,            -- 원본 전체 데이터
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(politician_id, report_year)
);

-- Individual asset items (개별 재산 항목)
CREATE TABLE asset_items (
    id              SERIAL PRIMARY KEY,
    declaration_id  INTEGER REFERENCES asset_declarations(id) ON DELETE CASCADE,
    category        VARCHAR(50) NOT NULL,   -- 'real_estate' | 'deposit' | 'securities' | 'vehicle' | 'crypto' | 'other'
    subcategory     VARCHAR(100),           -- '토지' | '건물' | '아파트' | '주식' | '비트코인' etc
    description     TEXT,                   -- 소재지, 종목명 등
    relation        VARCHAR(20),            -- '본인' | '배우자' | '직계존속' | '직계비속'
    value_krw       BIGINT,                 -- 금액 (원)
    change_krw      BIGINT,                 -- 증감액
    note            TEXT
);

-- Companies (기업 — DART 연동)
CREATE TABLE companies (
    id              SERIAL PRIMARY KEY,
    corp_code       VARCHAR(20) UNIQUE,     -- DART 고유번호
    corp_name       VARCHAR(200) NOT NULL,
    stock_code      VARCHAR(20),            -- 종목코드
    industry        VARCHAR(200),           -- 업종
    ceo_name        VARCHAR(100),
    homepage        TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Politician-Company relationships (의원-기업 관계)
CREATE TABLE politician_companies (
    id              SERIAL PRIMARY KEY,
    politician_id   INTEGER REFERENCES politicians(id),
    company_id      INTEGER REFERENCES companies(id),
    relation_type   VARCHAR(50) NOT NULL,   -- 'stockholder' | 'former_executive' | 'family_stockholder' | 'donor'
    detail          TEXT,                   -- 보유 주식 수, 직책 등
    value_krw       BIGINT,                 -- 관련 금액
    source          VARCHAR(50),            -- 'asset_declaration' | 'dart' | 'news'
    source_year     INTEGER,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(politician_id, company_id, relation_type, source_year)
);

-- Political funds (정치자금)
CREATE TABLE political_funds (
    id              SERIAL PRIMARY KEY,
    politician_id   INTEGER REFERENCES politicians(id),
    fund_year       INTEGER NOT NULL,
    fund_type       VARCHAR(50),            -- '후원회' | '정당보조금' | '기탁금'
    income_total    BIGINT,                 -- 수입 합계
    expense_total   BIGINT,                 -- 지출 합계
    balance         BIGINT,                 -- 잔액
    source          VARCHAR(50),            -- 'nec' | 'ohmynews' | 'manual'
    raw_data        JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(politician_id, fund_year, fund_type)
);

-- Political fund donors/expenditures (개별 수입/지출 항목)
CREATE TABLE political_fund_items (
    id              SERIAL PRIMARY KEY,
    fund_id         INTEGER REFERENCES political_funds(id) ON DELETE CASCADE,
    item_type       VARCHAR(20) NOT NULL,   -- 'income' | 'expense'
    category        VARCHAR(100),           -- '개인후원' | '법인후원' | '인건비' | '사무소비' etc
    counterpart     VARCHAR(200),           -- 후원자/지출처명
    amount          BIGINT NOT NULL,
    item_date       DATE,
    note            TEXT
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

CREATE INDEX idx_asset_declarations_politician ON asset_declarations(politician_id);
CREATE INDEX idx_asset_declarations_year ON asset_declarations(report_year);
CREATE INDEX idx_asset_items_declaration ON asset_items(declaration_id);
CREATE INDEX idx_asset_items_category ON asset_items(category);

CREATE INDEX idx_companies_stock_code ON companies(stock_code);
CREATE INDEX idx_companies_name ON companies(corp_name);

CREATE INDEX idx_politician_companies_politician ON politician_companies(politician_id);
CREATE INDEX idx_politician_companies_company ON politician_companies(company_id);
CREATE INDEX idx_politician_companies_type ON politician_companies(relation_type);

CREATE INDEX idx_political_funds_politician ON political_funds(politician_id);
CREATE INDEX idx_political_funds_year ON political_funds(fund_year);
CREATE INDEX idx_political_fund_items_fund ON political_fund_items(fund_id);

-- ============================================================
-- Seed party data (22nd Assembly)
-- ============================================================

INSERT INTO parties (name, color_hex, assembly_term) VALUES
    -- 22대
    ('국민의힘',       '#E61E2B', 22),
    ('더불어민주당',   '#004EA2', 22),
    ('조국혁신당',     '#0033A0', 22),
    ('개혁신당',       '#FF7210', 22),
    ('진보당',         '#D6001C', 22),
    ('기본소득당',     '#00B0B9', 22),
    ('사회민주당',     '#43B02A', 22)
ON CONFLICT (name) DO NOTHING;

-- Historical parties (17~21대)
INSERT INTO parties (name, color_hex) VALUES
    ('새누리당',       '#E61E2B'),
    ('한나라당',       '#E61E2B'),
    ('자유한국당',     '#E61E2B'),
    ('미래통합당',     '#E61E2B'),
    ('새정치민주연합', '#004EA2'),
    ('민주통합당',     '#004EA2'),
    ('열린우리당',     '#009640'),
    ('대통합민주신당', '#004EA2'),
    ('통합민주당',     '#004EA2'),
    ('민주당',         '#004EA2'),
    ('정의당',         '#FFCC00'),
    ('국민의당',       '#EA5504'),
    ('바른미래당',     '#00AACC'),
    ('바른정당',       '#00AACC'),
    ('민생당',         '#00C73C'),
    ('자유선진당',     '#E0007A'),
    ('창조한국당',     '#FF8C00'),
    ('미래희망연대',   '#00A0E2'),
    ('통합진보당',     '#D6001C'),
    ('민주노동당',     '#D6001C'),
    ('새천년민주당',   '#004EA2')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- Apache AGE graph
-- ============================================================

SET search_path = ag_catalog, "$user", public;
SELECT create_graph('kr_acc');
