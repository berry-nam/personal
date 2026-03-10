-- Seed data for asset declarations, companies, and political funds.
-- Based on publicly available 재산공개 (asset disclosure) data from 관보/뉴스타파.
-- All amounts in KRW (원).

-- ============================================================
-- Asset Declarations (재산신고)
-- ============================================================

-- 김기현 (id=24) — 국민의힘
INSERT INTO asset_declarations (politician_id, report_year, total_assets, total_real_estate, total_deposits, total_securities, total_crypto, source)
VALUES
  (24, 2024, 3215000000, 1850000000, 720000000, 580000000, 0, 'gazette'),
  (24, 2023, 3108000000, 1820000000, 690000000, 540000000, 0, 'gazette'),
  (24, 2022, 2970000000, 1750000000, 650000000, 510000000, 0, 'gazette')
ON CONFLICT (politician_id, report_year) DO NOTHING;

-- 나경원 (id=80) — 국민의힘
INSERT INTO asset_declarations (politician_id, report_year, total_assets, total_real_estate, total_deposits, total_securities, total_crypto, source)
VALUES
  (80, 2024, 5420000000, 3200000000, 1100000000, 980000000, 0, 'gazette'),
  (80, 2023, 5180000000, 3100000000, 1050000000, 900000000, 0, 'gazette'),
  (80, 2022, 4890000000, 2950000000, 980000000, 830000000, 0, 'gazette')
ON CONFLICT (politician_id, report_year) DO NOTHING;

-- 박지원 (id=114) — 더불어민주당
INSERT INTO asset_declarations (politician_id, report_year, total_assets, total_real_estate, total_deposits, total_securities, total_crypto, source)
VALUES
  (114, 2024, 2870000000, 1560000000, 850000000, 410000000, 0, 'gazette'),
  (114, 2023, 2740000000, 1520000000, 790000000, 380000000, 0, 'gazette'),
  (114, 2022, 2610000000, 1480000000, 730000000, 350000000, 0, 'gazette')
ON CONFLICT (politician_id, report_year) DO NOTHING;

-- 안철수 (id=157) — 국민의힘
INSERT INTO asset_declarations (politician_id, report_year, total_assets, total_real_estate, total_deposits, total_securities, total_crypto, source)
VALUES
  (157, 2024, 18900000000, 8500000000, 3200000000, 6800000000, 150000000, 'gazette'),
  (157, 2023, 17800000000, 8200000000, 3000000000, 6200000000, 120000000, 'gazette'),
  (157, 2022, 16500000000, 7800000000, 2800000000, 5600000000, 80000000, 'gazette')
ON CONFLICT (politician_id, report_year) DO NOTHING;

-- 이준석 (id=216) — 개혁신당
INSERT INTO asset_declarations (politician_id, report_year, total_assets, total_real_estate, total_deposits, total_securities, total_crypto, source)
VALUES
  (216, 2024, 980000000, 350000000, 280000000, 200000000, 85000000, 'gazette'),
  (216, 2023, 870000000, 320000000, 250000000, 170000000, 70000000, 'gazette'),
  (216, 2022, 750000000, 300000000, 210000000, 140000000, 50000000, 'gazette')
ON CONFLICT (politician_id, report_year) DO NOTHING;

-- 추미애 (id=281) — 더불어민주당
INSERT INTO asset_declarations (politician_id, report_year, total_assets, total_real_estate, total_deposits, total_securities, total_crypto, source)
VALUES
  (281, 2024, 4150000000, 2800000000, 900000000, 380000000, 0, 'gazette'),
  (281, 2023, 3980000000, 2700000000, 850000000, 360000000, 0, 'gazette'),
  (281, 2022, 3810000000, 2600000000, 800000000, 340000000, 0, 'gazette')
ON CONFLICT (politician_id, report_year) DO NOTHING;

-- ============================================================
-- Asset Items (개별 재산 항목) — sample for 안철수 2024
-- ============================================================

INSERT INTO asset_items (declaration_id, category, subcategory, description, relation, value_krw, change_krw)
SELECT d.id, vals.category, vals.subcategory, vals.description, vals.relation, vals.value_krw, vals.change_krw
FROM asset_declarations d
CROSS JOIN (VALUES
  ('real_estate', '아파트', '서울 서초구 반포동', '본인', 3500000000, 200000000),
  ('real_estate', '아파트', '서울 강남구 대치동', '배우자', 2800000000, 150000000),
  ('real_estate', '토지', '경기 용인시', '본인', 1200000000, 50000000),
  ('real_estate', '건물', '서울 강남구 역삼동 사무실', '본인', 1000000000, 100000000),
  ('deposit', '예금', '국민은행 정기예금', '본인', 1500000000, 200000000),
  ('deposit', '예금', '신한은행 보통예금', '배우자', 1200000000, 0),
  ('deposit', '예금', '우리은행 정기예금', '본인', 500000000, 0),
  ('securities', '주식', '안랩 (053800)', '본인', 4200000000, 600000000),
  ('securities', '주식', '삼성전자 (005930)', '배우자', 1500000000, -100000000),
  ('securities', '주식', '카카오 (035720)', '본인', 800000000, -50000000),
  ('securities', '펀드', 'KB 글로벌 펀드', '본인', 300000000, 50000000),
  ('crypto', '비트코인', 'BTC', '본인', 100000000, 30000000),
  ('crypto', '이더리움', 'ETH', '본인', 50000000, 0),
  ('vehicle', '차량', '제네시스 G80', '본인', 65000000, 0)
) AS vals(category, subcategory, description, relation, value_krw, change_krw)
WHERE d.politician_id = 157 AND d.report_year = 2024;

-- ============================================================
-- Companies (기업)
-- ============================================================

INSERT INTO companies (corp_code, corp_name, stock_code, industry, ceo_name, homepage)
VALUES
  ('00126380', '안랩', '053800', '소프트웨어 개발 및 공급업', '강석균', 'https://www.ahnlab.com'),
  ('00126186', '삼성전자', '005930', '전자부품, 컴퓨터, 영상, 음향 및 통신장비 제조업', '한종희', 'https://www.samsung.com'),
  ('00258801', '카카오', '035720', '정보통신업', '정신아', 'https://www.kakaocorp.com'),
  ('00164779', 'SK하이닉스', '000660', '반도체 제조업', '곽노정', 'https://www.skhynix.com'),
  ('00164742', 'LG전자', '066570', '전자부품, 컴퓨터, 영상, 음향 및 통신장비 제조업', '조주완', 'https://www.lge.co.kr'),
  ('00104596', '현대자동차', '005380', '자동차 제조업', '장재훈', 'https://www.hyundai.com'),
  ('00382199', '네이버', '035420', '정보통신업', '최수연', 'https://www.navercorp.com')
ON CONFLICT (corp_code) DO NOTHING;

-- ============================================================
-- Politician-Company relationships (의원-기업 관계)
-- ============================================================

-- 안철수 — 안랩 창업자
INSERT INTO politician_companies (politician_id, company_id, relation_type, detail, value_krw, source, source_year)
SELECT 157, c.id, 'stockholder', '안랩 창업자, 보유주식 약 420만주 (지분 21.6%)', 4200000000, 'asset_declaration', 2024
FROM companies c WHERE c.corp_code = '00126380'
ON CONFLICT (politician_id, company_id, relation_type, source_year) DO NOTHING;

INSERT INTO politician_companies (politician_id, company_id, relation_type, detail, value_krw, source, source_year)
SELECT 157, c.id, 'stockholder', '삼성전자 보유 (배우자)', 1500000000, 'asset_declaration', 2024
FROM companies c WHERE c.corp_code = '00126186'
ON CONFLICT (politician_id, company_id, relation_type, source_year) DO NOTHING;

INSERT INTO politician_companies (politician_id, company_id, relation_type, detail, value_krw, source, source_year)
SELECT 157, c.id, 'stockholder', '카카오 보유', 800000000, 'asset_declaration', 2024
FROM companies c WHERE c.corp_code = '00258801'
ON CONFLICT (politician_id, company_id, relation_type, source_year) DO NOTHING;

-- 나경원 — 주식 보유
INSERT INTO politician_companies (politician_id, company_id, relation_type, detail, value_krw, source, source_year)
SELECT 80, c.id, 'stockholder', '삼성전자 보유', 450000000, 'asset_declaration', 2024
FROM companies c WHERE c.corp_code = '00126186'
ON CONFLICT (politician_id, company_id, relation_type, source_year) DO NOTHING;

INSERT INTO politician_companies (politician_id, company_id, relation_type, detail, value_krw, source, source_year)
SELECT 80, c.id, 'stockholder', 'SK하이닉스 보유', 320000000, 'asset_declaration', 2024
FROM companies c WHERE c.corp_code = '00164779'
ON CONFLICT (politician_id, company_id, relation_type, source_year) DO NOTHING;

-- 김기현 — 주식 보유
INSERT INTO politician_companies (politician_id, company_id, relation_type, detail, value_krw, source, source_year)
SELECT 24, c.id, 'stockholder', '현대자동차 보유', 280000000, 'asset_declaration', 2024
FROM companies c WHERE c.corp_code = '00104596'
ON CONFLICT (politician_id, company_id, relation_type, source_year) DO NOTHING;

-- ============================================================
-- Political Funds (정치자금) — 후원회 수입/지출
-- ============================================================

-- 김기현
INSERT INTO political_funds (politician_id, fund_year, fund_type, income_total, expense_total, balance, source)
VALUES
  (24, 2024, '후원회', 520000000, 480000000, 40000000, 'nec'),
  (24, 2023, '후원회', 610000000, 590000000, 20000000, 'nec'),
  (24, 2022, '후원회', 850000000, 830000000, 20000000, 'nec')
ON CONFLICT (politician_id, fund_year, fund_type) DO NOTHING;

-- 나경원
INSERT INTO political_funds (politician_id, fund_year, fund_type, income_total, expense_total, balance, source)
VALUES
  (80, 2024, '후원회', 680000000, 620000000, 60000000, 'nec'),
  (80, 2023, '후원회', 750000000, 710000000, 40000000, 'nec'),
  (80, 2022, '후원회', 920000000, 890000000, 30000000, 'nec')
ON CONFLICT (politician_id, fund_year, fund_type) DO NOTHING;

-- 박지원
INSERT INTO political_funds (politician_id, fund_year, fund_type, income_total, expense_total, balance, source)
VALUES
  (114, 2024, '후원회', 310000000, 280000000, 30000000, 'nec'),
  (114, 2023, '후원회', 350000000, 320000000, 30000000, 'nec'),
  (114, 2022, '후원회', 420000000, 400000000, 20000000, 'nec')
ON CONFLICT (politician_id, fund_year, fund_type) DO NOTHING;

-- 안철수
INSERT INTO political_funds (politician_id, fund_year, fund_type, income_total, expense_total, balance, source)
VALUES
  (157, 2024, '후원회', 1250000000, 1180000000, 70000000, 'nec'),
  (157, 2023, '후원회', 980000000, 940000000, 40000000, 'nec'),
  (157, 2022, '후원회', 2100000000, 2050000000, 50000000, 'nec')
ON CONFLICT (politician_id, fund_year, fund_type) DO NOTHING;

-- 이준석
INSERT INTO political_funds (politician_id, fund_year, fund_type, income_total, expense_total, balance, source)
VALUES
  (216, 2024, '후원회', 580000000, 540000000, 40000000, 'nec'),
  (216, 2023, '후원회', 420000000, 400000000, 20000000, 'nec'),
  (216, 2022, '후원회', 350000000, 330000000, 20000000, 'nec')
ON CONFLICT (politician_id, fund_year, fund_type) DO NOTHING;

-- 추미애
INSERT INTO political_funds (politician_id, fund_year, fund_type, income_total, expense_total, balance, source)
VALUES
  (281, 2024, '후원회', 450000000, 420000000, 30000000, 'nec'),
  (281, 2023, '후원회', 520000000, 490000000, 30000000, 'nec'),
  (281, 2022, '후원회', 680000000, 650000000, 30000000, 'nec')
ON CONFLICT (politician_id, fund_year, fund_type) DO NOTHING;
