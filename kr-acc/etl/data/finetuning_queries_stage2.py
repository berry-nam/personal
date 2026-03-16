"""
기업탐색 Fine-tuning 데이터셋 — Stage 2: 매트릭스 생성 (554 → 1,300)

Stage 1의 554건을 기반으로, 커버리지 갭을 매트릭스 방식으로 채워 1,300건으로 확장.
- 준대기업/대기업 밴드 채우기
- UC-3(투자) 섹터 다양화
- UC-2 Complex/Edge 보강
- 페르소나 기반 문체 변형 (PE심사역, 전략적매수자, 개인매수자, VC, 자문사)

출력: finetuning_queries_stage2.json
"""

import json
from datetime import datetime
from itertools import product

# ============================================================
# Load Stage 1
# ============================================================
with open("etl/data/finetuning_queries_stage1.json", encoding="utf-8") as f:
    stage1 = json.load(f)

stage1_queries = stage1["queries"]

# ============================================================
# 상수 정의
# ============================================================
UC_CATEGORIES = {
    "UC-1": {"name": "M&A 타겟 발굴", "weight": 0.30},
    "UC-2": {"name": "경쟁사 탐색", "weight": 0.25},
    "UC-3": {"name": "투자 대상 탐색", "weight": 0.15},
    "UC-4": {"name": "매수자 탐색 (매도자)", "weight": 0.05},
    "UC-5": {"name": "시장 탐색", "weight": 0.25},
}

SECTORS = [
    "제조업(일반)", "식품/F&B", "반도체/소부장", "바이오/헬스케어",
    "IT/SaaS", "화장품/뷰티", "유통/물류", "철강/금속",
    "자동차/부품", "교육", "건설", "게임/콘텐츠",
    "에너지/기후", "방위산업", "금융/보험",
]

SIZES = ["소상공인", "소기업", "중기업", "중견기업", "준대기업", "대기업"]

# ============================================================
# 목표 분포 계산 (1,300건 기준)
# ============================================================
TARGET_TOTAL = 1300
TARGET_UC = {
    "UC-1": int(TARGET_TOTAL * 0.30),  # 390
    "UC-2": int(TARGET_TOTAL * 0.25),  # 325
    "UC-3": int(TARGET_TOTAL * 0.15),  # 195
    "UC-4": int(TARGET_TOTAL * 0.05),  # 65
    "UC-5": int(TARGET_TOTAL * 0.25),  # 325
}

# ============================================================
# Stage 2 쿼리 생성
# ============================================================
new_queries = []
qid = 0


def make_id():
    global qid
    qid += 1
    return f"S2-{qid:04d}"


def audit_for_size(size):
    if size in ("중기업", "중견기업", "준대기업", "대기업"):
        return "외감"
    return "비외감"


# ----------------------------------------------------------
# UC-1: M&A 타겟 발굴 — 매트릭스 기반 (+~200건)
# ----------------------------------------------------------
# 섹터별 구체적 쿼리 템플릿 (재무 조건 + 특수 조건)
uc1_templates = {
    "제조업(일반)": [
        ("수도권 사출/프레스 제조업체, 매출 {rev}, 영업이익률 8%+, 자체 금형 보유", "Medium"),
        ("충청권 자동차 부품 2차 벤더, 매출 {rev}, 3년 연속 흑자, 바이아웃", "Complex"),
        ("반도체 장비 부품 가공 전문, 매출 {rev}, 클린룸 보유, 비상장", "Medium"),
        ("인쇄/포장재 제조, 매출 {rev}, 식품 대기업 장기 납품 계약", "Medium"),
        ("산업용 자동화 설비 제조, 매출 {rev}, 수출 비중 30%+", "Complex"),
        ("금속 열처리/표면처리 전문, 매출 {rev}, 인허가 보유", "Medium"),
        ("전기/전자 부품 조립, 매출 {rev}, 삼성/LG 납품사", "Medium"),
        ("용접/배관 시공 전문, 매출 {rev}, 플랜트 실적 보유", "Medium"),
    ],
    "식품/F&B": [
        ("HMR/간편식 전문 제조사, 매출 {rev}, 대형마트 납품, HACCP 인증", "Medium"),
        ("수산물 가공/냉동, 매출 {rev}, 수출 실적, 수도권 물류센터", "Complex"),
        ("음료(RTD) 제조, 매출 {rev}, OEM 가능, 자체 생산라인", "Medium"),
        ("건기식 브랜드, 매출 {rev}, 온라인 매출 비중 50%+", "Medium"),
        ("외식 프랜차이즈, 매출 {rev}, 가맹점 50개+, 영남권", "Complex"),
        ("제과/제빵 원료 공급, 매출 {rev}, B2B 안정 매출", "Simple"),
    ],
    "반도체/소부장": [
        ("반도체 세정/에칭 장비, 매출 {rev}, 국산화 기술, 삼성/SK 납품", "Complex"),
        ("디스플레이 소재/부품, 매출 {rev}, 특허 10건+", "Medium"),
        ("PCB/FPCB 제조, 매출 {rev}, 고다층 기술, 자동차/5G 적용", "Medium"),
        ("반도체 패키징 소재, 매출 {rev}, 글로벌 고객 보유", "Complex"),
        ("센서/MEMS 제조, 매출 {rev}, 자동차/IoT 적용", "Medium"),
    ],
    "바이오/헬스케어": [
        ("의료기기(진단), 매출 {rev}, CE/FDA 인증, 수출 비중 40%+", "Complex"),
        ("제약 CDMO, 매출 {rev}, GMP 시설, 고형제/주사제", "Complex"),
        ("치과 임플란트/디지털 덴티스트리, 매출 {rev}, 자체 기술", "Medium"),
        ("동물의약품/사료첨가제, 매출 {rev}, 축산업 B2B", "Medium"),
        ("재활/물리치료 기기, 매출 {rev}, 병원 납품 실적", "Medium"),
        ("의약품 원료(API) 제조, 매출 {rev}, 수출 허가 보유", "Complex"),
    ],
    "IT/SaaS": [
        ("제조 MES/ERP 솔루션, ARR {rev}, 유료 고객 50사+", "Medium"),
        ("보안(사이버/물리) 솔루션, 매출 {rev}, 공공 납품 실적", "Medium"),
        ("AI/데이터 분석 플랫폼, ARR {rev}, NRR 110%+", "Complex"),
        ("핀테크/결제 인프라, 매출 {rev}, PG 등록, 거래액 1조+", "Complex"),
        ("클라우드/인프라 MSP, 매출 {rev}, AWS/Azure 파트너", "Medium"),
        ("물류/SCM SaaS, ARR {rev}, 이커머스 고객 다수", "Medium"),
    ],
    "화장품/뷰티": [
        ("화장품 ODM, 매출 {rev}, 기능성 화장품 특허, 수출 비중 30%+", "Complex"),
        ("인디 뷰티 브랜드, 매출 {rev}, 올리브영/쿠팡 입점, SNS 팔로워 50만+", "Medium"),
        ("뷰티 디바이스/에스테틱 기기, 매출 {rev}, CE 인증", "Medium"),
        ("헤어케어/두피 전문, 매출 {rev}, 자체 R&D", "Medium"),
    ],
    "유통/물류": [
        ("3PL 풀필먼트, 매출 {rev}, 수도권 물류센터 3개+", "Medium"),
        ("산업재 전문상사, 매출 {rev}, 전국 거래처 네트워크", "Medium"),
        ("식자재 유통, 매출 {rev}, 냉장/냉동 배송망", "Medium"),
        ("의료기기/시약 유통, 매출 {rev}, 병원 거래처 200곳+", "Complex"),
    ],
    "철강/금속": [
        ("특수강 제조, 매출 {rev}, 자동차/항공 소재, 수출 비중 20%+", "Complex"),
        ("알루미늄 압출/다이캐스팅, 매출 {rev}, EV 부품 적용", "Medium"),
        ("스테인리스 가공, 매출 {rev}, 반도체/식품 장비용", "Medium"),
        ("비철금속 리사이클링, 매출 {rev}, 환경 인허가", "Medium"),
    ],
    "자동차/부품": [
        ("EV 전장 부품(BMS/인버터), 매출 {rev}, 현대/기아 납품", "Complex"),
        ("자동차 시트/내장재, 매출 {rev}, Tier 1~2 납품", "Medium"),
        ("모터/액추에이터, 매출 {rev}, 로봇/EV 겸용", "Medium"),
        ("자동차 램프/조명, 매출 {rev}, LED 전환 기술", "Medium"),
    ],
    "교육": [
        ("법정의무교육 전문, 매출 {rev}, B2B 장기계약, 반복매출", "Medium"),
        ("온라인 학습 플랫폼, MAU 10만+, 매출 {rev}", "Medium"),
        ("어학(영어/중국어) 교육, 매출 {rev}, 프랜차이즈 30개+", "Medium"),
    ],
    "건설": [
        ("인테리어/리모델링 시공, 매출 {rev}, 수도권, 아파트 특화", "Medium"),
        ("전기/소방 설비 시공, 매출 {rev}, 면허 보유", "Medium"),
        ("토목/환경 시공, 매출 {rev}, 관급 실적 5년+", "Complex"),
    ],
    "게임/콘텐츠": [
        ("모바일 게임 개발사, 매출 {rev}, 글로벌 출시, 라이브 서비스 중", "Medium"),
        ("웹툰/웹소설 IP, 매출 {rev}, 영상화 계약 보유", "Medium"),
        ("VFX/포스트프로덕션, 매출 {rev}, 넷플릭스/디즈니+ 실적", "Medium"),
        ("MCN/크리에이터 매니지먼트, 매출 {rev}, 소속 크리에이터 100명+", "Complex"),
    ],
    "에너지/기후": [
        ("태양광 EPC/O&M, 매출 {rev}, 발전사업 허가 보유", "Medium"),
        ("ESS/배터리 시스템, 매출 {rev}, 전력거래소 인증", "Complex"),
        ("폐기물 처리/소각, 매출 {rev}, 환경부 인허가", "Medium"),
        ("수처리/정수 기술, 매출 {rev}, 산업용 플랜트 실적", "Medium"),
    ],
    "방위산업": [
        ("방산 전자/통신 장비, 매출 {rev}, 방사청 납품 실적", "Complex"),
        ("탄약/화약류, 매출 {rev}, 수출 허가 보유", "Complex"),
        ("군수 정비(MRO), 매출 {rev}, 장기 계약", "Medium"),
    ],
    "금융/보험": [
        ("자산운용사(부동산/대체투자), AUM {rev}", "Complex"),
        ("저축은행/캐피탈, 자산 {rev}, 건전성 양호", "Complex"),
        ("보험 중개/GA, 매출 {rev}, 설계사 100명+", "Medium"),
    ],
}

# 매출 밴드별 대표값
REV_BY_SIZE = {
    "소상공인": ["5~10억", "3~8억", "1~5억"],
    "소기업": ["30~50억", "50~100억", "100~200억", "20~50억"],
    "중기업": ["200~500억", "300~700억", "500~1,000억"],
    "중견기업": ["1,000~3,000억", "2,000~5,000억", "3,000~1조"],
    "준대기업": ["5,000억~1조", "1~2조", "7,000억~1.5조"],
    "대기업": ["2~5조", "5~10조", "1조+"],
}

# UC-1 매트릭스 생성: 각 섹터 × 규모 밴드 조합
for sector, templates in uc1_templates.items():
    for size in ["소기업", "중기업", "중견기업", "준대기업", "대기업"]:
        # 소기업/중기업은 이미 Stage 1에서 많으므로 1개씩만
        # 준대기업/대기업은 빈 곳이므로 2개씩
        n_per = 1 if size in ("소기업", "중기업") else 2
        revs = REV_BY_SIZE[size]
        for i in range(min(n_per, len(templates))):
            tmpl, complexity = templates[i % len(templates)]
            rev = revs[i % len(revs)]
            text = tmpl.format(rev=rev)
            new_queries.append({
                "id": make_id(),
                "uc": "UC-1",
                "text": text,
                "sector": sector,
                "size": size,
                "complexity": complexity,
                "source": "매트릭스-UC1",
                "audit": audit_for_size(size),
            })

# ----------------------------------------------------------
# UC-2: 경쟁사 탐색 — Complex/Edge 보강 + 규모 다양화 (+~180건)
# ----------------------------------------------------------

# Complex: 다차원 비교 쿼리
uc2_complex = [
    # 제조업
    {"text": "산업용 밸브 제조사 중 매출 100~500억, 해외 수출 30%+인 곳 비교 — 석유화학/발전 납품사 우선", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"text": "자동화 장비(로봇·FA) 업체, 매출 300억+, 삼성/현대 Tier 1 납품사 vs 중소형 전문사 비교", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"text": "정밀 측정/검사 장비 업체, 반도체·디스플레이 라인 납품, 국산 vs 수입 대체 현황", "sector": "제조업(일반)", "size": "소기업", "complexity": "Complex"},
    {"text": "금형 제조사 중 자동차 대형 금형(범퍼/도어) 전문, 매출 200억+ 기업 비교", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"text": "탄소섬유/복합소재 제조사 경쟁 비교 — 항공·자동차·스포츠 적용별", "sector": "제조업(일반)", "size": "소기업", "complexity": "Complex"},
    # 식품
    {"text": "냉동 만두/면류 OEM 업체, 대형마트 PB 생산사 비교, 생산 CAPA 일 10만식+", "sector": "식품/F&B", "size": "중기업", "complexity": "Complex"},
    {"text": "커피 프랜차이즈 vs 스페셜티 로스터리 체인, 매출 100억+ 기업 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Complex"},
    {"text": "식품 소재(전분/유화제/향료) 업체, 글로벌사 vs 국산 기업 경쟁 구도", "sector": "식품/F&B", "size": "중기업", "complexity": "Complex"},
    # 반도체
    {"text": "CMP 슬러리/패드 국산화 업체 비교, 삼성 인증 여부별", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"text": "반도체 레이저 장비(다이싱/마킹/리페어) 업체, 국내 5개사 비교", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    # 바이오
    {"text": "국내 CDMO(바이오의약품 위탁생산) 업체, 삼성바이오 외, 항체/mRNA 역량별", "sector": "바이오/헬스케어", "size": "중견기업", "complexity": "Complex"},
    {"text": "혈액투석/혈액정화 기기 업체, 국내 시장점유율별 비교", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    # IT/SaaS
    {"text": "RPA/업무자동화 솔루션, 국내 시장점유율 Top 5 비교, 금융권 레퍼런스별", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex"},
    {"text": "CDN/클라우드 인프라 업체, 국내 ISP 연동 현황별 비교", "sector": "IT/SaaS", "size": "중기업", "complexity": "Complex"},
    # 에너지
    {"text": "풍력 발전 EPC 업체, 해상 vs 육상 실적별 비교, 국내 Top 10", "sector": "에너지/기후", "size": "중기업", "complexity": "Complex"},
    {"text": "수소 연료전지 스택/시스템 업체, 건물용 vs 수송용 비교", "sector": "에너지/기후", "size": "소기업", "complexity": "Complex"},
    # 화장품
    {"text": "더마 화장품 브랜드, 약국 채널 vs 올리브영 채널 비교, 매출 100억+", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Complex"},
    # 자동차
    {"text": "EV 충전기 제조사, 급속 vs 완속, 공공 설치 실적별 비교", "sector": "자동차/부품", "size": "소기업", "complexity": "Complex"},
    # 게임
    {"text": "하이퍼캐주얼 게임 퍼블리셔, 글로벌 DAU별 비교, 광고 수익 모델", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Complex"},
    # 금융
    {"text": "디지털 보험(인슈어테크) 업체, MGA vs 플랫폼 모델 비교", "sector": "금융/보험", "size": "소기업", "complexity": "Complex"},
]

for q in uc2_complex:
    q["id"] = make_id()
    q["uc"] = "UC-2"
    q["source"] = "매트릭스-UC2-복합"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc2_complex)

# UC-2 Edge cases
uc2_edge = [
    {"text": "지역 독점 LPG 충전소 vs 전기차 충전 전환 업체 비교", "sector": "에너지/기후", "size": "소기업", "complexity": "Edge"},
    {"text": "코스닥 시총 500억 미만 IT기업 중 적대적 M&A 가능 기업 비교", "sector": "IT/SaaS", "size": "중기업", "complexity": "Edge"},
    {"text": "일본 수출규제 이후 국산화 성공 소재/부품 업체 비교", "sector": "반도체/소부장", "size": "소기업", "complexity": "Edge"},
    {"text": "코로나 특수 이후 매출 급감한 진단키트 업체 비교 — 피벗 여부별", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Edge"},
    {"text": "대기업 2차 벤더에서 1차 벤더로 승격한 제조업체 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
    {"text": "MZ세대 타겟 주류 브랜드(소주/맥주/위스키) 비교, 마케팅 전략별", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge"},
    {"text": "K-뷰티 아마존 입점 업체, 미국 시장 매출 기준 Top 20 비교", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Edge"},
    {"text": "건설 폐기물 처리업체, 불법 투기 이력 없는 우량 업체 비교", "sector": "건설", "size": "소기업", "complexity": "Edge"},
    {"text": "군 제대 장병 취업 연계 교육업체, 국방부 MOU 보유 기업 비교", "sector": "교육", "size": "소기업", "complexity": "Edge"},
    {"text": "전통시장/재래시장 현대화 사업 수행 업체 비교", "sector": "유통/물류", "size": "소기업", "complexity": "Edge"},
]

for q in uc2_edge:
    q["id"] = make_id()
    q["uc"] = "UC-2"
    q["source"] = "매트릭스-UC2-엣지"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc2_edge)

# UC-2 규모 다양화 (준대기업/대기업 포함)
uc2_size_diverse = [
    {"text": "반도체 장비 대기업(세메스, 주성엔지니어링 등) vs 중견기업 비교", "sector": "반도체/소부장", "size": "대기업", "complexity": "Complex"},
    {"text": "국내 대형 물류사(CJ대한통운, 한진) vs 중견 3PL 비교, EBITDA 기준", "sector": "유통/물류", "size": "대기업", "complexity": "Complex"},
    {"text": "대형 건설사(시공능력 Top 30) 중 리모델링 사업 비중별 비교", "sector": "건설", "size": "대기업", "complexity": "Complex"},
    {"text": "중견 식품사(매출 3,000억~1조) 간 해외 진출 전략 비교", "sector": "식품/F&B", "size": "중견기업", "complexity": "Complex"},
    {"text": "준대기업급 바이오 기업(삼성바이오, 셀트리온 외) 파이프라인 비교", "sector": "바이오/헬스케어", "size": "준대기업", "complexity": "Complex"},
    {"text": "중견 화장품사(아모레퍼시픽 계열 제외) 글로벌 매출 비교", "sector": "화장품/뷰티", "size": "중견기업", "complexity": "Complex"},
    {"text": "대형 게임사(넥슨/엔씨/카카오게임즈) 모바일 매출 비중별 비교", "sector": "게임/콘텐츠", "size": "대기업", "complexity": "Complex"},
    {"text": "중견 방산업체(한화에어로 외) 수출 매출별 비교", "sector": "방위산업", "size": "중견기업", "complexity": "Complex"},
    {"text": "준대기업급 자동차 부품사, 전장 전환율별 비교", "sector": "자동차/부품", "size": "준대기업", "complexity": "Complex"},
    {"text": "중견 IT서비스사(매출 1,000~5,000억) 클라우드 전환 비교", "sector": "IT/SaaS", "size": "중견기업", "complexity": "Complex"},
    {"text": "대형 에너지기업(한화솔루션, SK E&S 등) 신재생 사업 비중 비교", "sector": "에너지/기후", "size": "대기업", "complexity": "Complex"},
    {"text": "중견 철강사(매출 5,000억+) 특수강 비중별 비교", "sector": "철강/금속", "size": "중견기업", "complexity": "Complex"},
    {"text": "준대기업급 제조사, ESG 등급별 비교", "sector": "제조업(일반)", "size": "준대기업", "complexity": "Complex"},
    {"text": "대형 금융지주(KB/신한/하나/우리) 비은행 자회사 M&A 전략 비교", "sector": "금융/보험", "size": "대기업", "complexity": "Complex"},
    {"text": "중견 교육기업(메가스터디, 에스티유니타스 등) 온라인 전환율 비교", "sector": "교육", "size": "중견기업", "complexity": "Complex"},
]

for q in uc2_size_diverse:
    q["id"] = make_id()
    q["uc"] = "UC-2"
    q["source"] = "매트릭스-UC2-규모다양"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc2_size_diverse)

# UC-2 Simple (소상공인 포함)
uc2_simple_small = [
    {"text": "수제 맥주 양조장 비교, 수도권", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"text": "1인 앱 개발사 비교, 매출 5억 미만", "sector": "IT/SaaS", "size": "소상공인", "complexity": "Simple"},
    {"text": "네일아트/뷰티샵 프랜차이즈 비교", "sector": "화장품/뷰티", "size": "소상공인", "complexity": "Simple"},
    {"text": "동네 빵집(베이커리) 프랜차이즈 비교", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"text": "소규모 태양광 시공업체 비교, 가정용", "sector": "에너지/기후", "size": "소상공인", "complexity": "Simple"},
    {"text": "코딩 교육(어린이) 학원 비교", "sector": "교육", "size": "소상공인", "complexity": "Simple"},
    {"text": "반려동물 미용/호텔 프랜차이즈 비교", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"text": "소형 인쇄소/디지털 프린팅 업체 비교", "sector": "제조업(일반)", "size": "소상공인", "complexity": "Simple"},
]

for q in uc2_simple_small:
    q["id"] = make_id()
    q["uc"] = "UC-2"
    q["source"] = "매트릭스-UC2-소형"
    q["audit"] = "비외감"
new_queries.extend(uc2_simple_small)

# UC-2 추가 Medium (섹터 갭 채우기)
uc2_medium_gap = [
    {"text": "이커머스 자체 배송 업체 vs 택배 의존 업체 비교", "sector": "유통/물류", "size": "중기업", "complexity": "Medium"},
    {"text": "스마트워치/웨어러블 디바이스 업체, 국내 브랜드 비교", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "식물성 단백질/대체육 업체, 국내 시장 진입 기업 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "전기 스쿠터/이륜차 업체, 배달 플랫폼 납품사 비교", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"text": "온라인 패션 플랫폼(무신사·W컨셉·29CM) 입점 브랜드 비교", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "철강 유통(코일센터) 업체, 수도권 vs 영남권 비교", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"text": "방산 소프트웨어(C4I/시뮬레이션) 업체 비교", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
    {"text": "건물 에너지 관리(BEMS) 솔루션 업체 비교", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "치과 체인/네트워크 병원 비교, 매출 기준", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"text": "학습지/방문교육 업체, 디지털 전환 현황별 비교", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"text": "산업안전/안전진단 업체 비교, 건설·제조 분야별", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"text": "캐릭터 라이선싱/IP 매니지먼트 업체 비교", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
    {"text": "손해사정/보상 전문 업체 비교", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    {"text": "구리/동 가공(전선/부스바) 업체 비교", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"text": "모듈러 주택/컨테이너 건축 업체 비교", "sector": "건설", "size": "소기업", "complexity": "Medium"},
]

for q in uc2_medium_gap:
    q["id"] = make_id()
    q["uc"] = "UC-2"
    q["source"] = "매트릭스-UC2-갭"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc2_medium_gap)

# ----------------------------------------------------------
# UC-3: 투자 대상 탐색 — 섹터 다양화 + 규모 확장 (+~130건)
# ----------------------------------------------------------

uc3_queries = [
    # 섹터 갭 채우기
    {"text": "자동차 전장/ADAS 스타트업, 시리즈B+, 자율주행 기술 보유", "sector": "자동차/부품", "size": "소기업", "complexity": "Complex"},
    {"text": "자동차 경량화 소재 업체, 매출 50억+, CFRP/알루미늄, 성장률 20%+", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"text": "EV 충전 인프라 스타트업, 시리즈A~B, 설치 대수 1,000기+", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"text": "철강/금속 신소재(고엔트로피합금/비정질금속) 기술 보유 기업", "sector": "철강/금속", "size": "소기업", "complexity": "Complex"},
    {"text": "금속 3D프린팅/적층제조 업체, 항공·의료 적용, 매출 30억+", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"text": "금속 리사이클링 기술(도시광산), 매출 50억+, 환경 인허가", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"text": "방산 소프트웨어(시뮬레이션/사이버전) 스타트업, 정부 과제 수주", "sector": "방위산업", "size": "소기업", "complexity": "Complex"},
    {"text": "방산 무인기(드론/UGV) 기술 기업, 군 시범사업 참여", "sector": "방위산업", "size": "소기업", "complexity": "Complex"},
    {"text": "방산 위성통신/ISR 기술 기업, 매출 20억+, 정부 사업 수주", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
    {"text": "교육 AI(에듀테크) 스타트업, MAU 5만+, 매출 10억+", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"text": "직무교육/리스킬링 플랫폼, B2B, 기업 고객 100사+", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"text": "건설 로봇/자동화 기술 스타트업, 시공 로봇/드론 측량", "sector": "건설", "size": "소기업", "complexity": "Complex"},
    {"text": "건설 DX(디지털트윈/BIM) 솔루션, 매출 20억+, 대형 시공사 납품", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"text": "물류 로봇(AMR/AGV) 스타트업, 매출 30억+, 대형 물류센터 적용", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "이커머스 풀필먼트 기술 기업, SaaS 모델, 고객사 200곳+", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "라스트마일 배송 기술(로봇/자율주행), 시범사업 중", "sector": "유통/물류", "size": "소기업", "complexity": "Complex"},
    # 규모 다양화 (중견/준대기업/대기업)
    {"text": "중견 제약사(매출 3,000억+) 중 바이오시밀러 전환 중인 기업, 지분 인수", "sector": "바이오/헬스케어", "size": "중견기업", "complexity": "Complex"},
    {"text": "중견 반도체 장비사, 매출 2,000억+, 해외 확장 중, 소수지분 투자", "sector": "반도체/소부장", "size": "중견기업", "complexity": "Complex"},
    {"text": "준대기업급 식품사, 매출 5,000억+, 해외 M&A 자금 필요, 투자유치 의향", "sector": "식품/F&B", "size": "준대기업", "complexity": "Complex"},
    {"text": "중견 화장품사, 매출 1,000~3,000억, K-뷰티 글로벌 확장 투자", "sector": "화장품/뷰티", "size": "중견기업", "complexity": "Complex"},
    {"text": "준대기업급 물류사, 자산 5,000억+, 인프라 투자(물류센터) 자금 필요", "sector": "유통/물류", "size": "준대기업", "complexity": "Complex"},
    {"text": "중견 건설사, 매출 3,000억+, 해외 플랜트 사업 확장", "sector": "건설", "size": "중견기업", "complexity": "Complex"},
    {"text": "중견 에너지 기업, 신재생 전환 투자, 기업가치 5,000억+", "sector": "에너지/기후", "size": "중견기업", "complexity": "Complex"},
    {"text": "대기업 계열 분사/카브아웃 기업, Pre-IPO 투자 기회", "sector": "제조업(일반)", "size": "준대기업", "complexity": "Complex"},
    # 소상공인 투자
    {"text": "소자본 창업 인수, 매출 3~5억, 안정적 현금흐름, 생활 서비스업", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"text": "마이크로 VC 투자 대상, 매출 1~3억, 기술 기반, Pre-Series A", "sector": "IT/SaaS", "size": "소상공인", "complexity": "Simple"},
    {"text": "로컬 F&B 브랜드, 매출 2~5억, SNS 팔로워 높은 브랜드력 보유", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    # 다양한 투자 구조
    {"text": "메자닌(CB/BW) 투자 대상, 기업가치 500~2,000억, 제조업, 전환 프리미엄", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"text": "구주 매출(세컨더리) 대상, 시리즈C+ 기업, SaaS, 기업가치 1,000억+", "sector": "IT/SaaS", "size": "중기업", "complexity": "Complex"},
    {"text": "PEF 공동투자(Co-invest) 기회, 딜사이즈 3,000억+, 제조/유통", "sector": "제조업(일반)", "size": "중견기업", "complexity": "Complex"},
    {"text": "SPAC 합병 타겟, 기업가치 1,000~3,000억, 코스닥 상장 희망, 흑자 전환", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Complex"},
    {"text": "크로스보더 투자, 한국 기업의 일본/동남아 자회사 지분 인수", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"text": "임팩트 투자 대상, ESG 우수, 매출 30억+, 환경/사회적 가치", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "프랜차이즈 마스터 라이선스 투자, 해외 브랜드 한국 독점", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "부실채권(NPL) 포트폴리오 매입, 담보 부동산 가치 평가", "sector": "금융/보험", "size": "중기업", "complexity": "Complex"},
    {"text": "벤처 투자, 디지털 헬스케어, 원격의료/디지털치료제, FDA 승인 추진", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"text": "콘텐츠 IP 투자, 웹툰/웹소설 원작, 영상화 계약 완료, 매출 20억+", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
    {"text": "그로스 투자, 매출 100~500억, YoY 30%+ 성장, IT/SaaS, 해외 확장 중", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex"},
    {"text": "터나라운드 투자, 영업적자이나 구조조정 시 흑자 전환 가능, 제조업", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"text": "인프라 투자, 데이터센터/물류센터 개발, 준공 후 리츠 편입 가능", "sector": "건설", "size": "중기업", "complexity": "Complex"},
    {"text": "어그리테크 투자, 스마트팜/식물공장, 매출 10억+, 기술력", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "핀테크 시리즈B, 매출 50억+, 금융 라이선스 보유, MAU 50만+", "sector": "금융/보험", "size": "소기업", "complexity": "Complex"},
    {"text": "제조업 DX(디지털전환) 스타트업, ARR 20억+, 공장 고객 50사+", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "K-컬처(K-POP/K-드라마) 관련 기업, 해외 매출 50%+, 성장 투자", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
]

for q in uc3_queries:
    q["id"] = make_id()
    q["uc"] = "UC-3"
    q["source"] = "매트릭스-UC3"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc3_queries)


# ----------------------------------------------------------
# UC-4: 매수자 탐색 — 섹터 전수 커버 (+~40건)
# ----------------------------------------------------------

uc4_queries = [
    # 섹터별 매도 → 매수자 매칭
    {"text": "AI 영상분석 솔루션 기업 매도 — 보안/방범 대기업 또는 SI업체 매칭", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "비상장 제약사 매도 — 파이프라인 인수 관심 중견 제약사 탐색", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"text": "펫푸드 제조사 매도 — 식품 대기업 또는 펫 사업 확장 중인 기업", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "산업용 로봇 업체 매도 — 자동화 대기업(현대로보틱스 등) 또는 PE", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "태양광 EPC 업체 매도 — 신재생 에너지 대기업 또는 인프라 펀드", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "치과 임플란트 업체 매도 — 글로벌 의료기기사 또는 PE 매칭", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Complex"},
    {"text": "인디 게임 스튜디오 매도 — 대형 퍼블리셔(넥슨/크래프톤 등) 매칭", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
    {"text": "건기식 ODM 업체 매도 — 식품 대기업 또는 헬스케어 PE", "sector": "식품/F&B", "size": "중기업", "complexity": "Medium"},
    {"text": "반도체 세정장비 업체 매도 — 글로벌 장비사 또는 국내 대기업 매칭", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"text": "화장품 OEM 업체 매도 — 코스맥스/한국콜마 또는 글로벌 뷰티사", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Medium"},
    {"text": "냉장 물류 업체 매도 — CJ대한통운/한진 또는 식품 대기업 매칭", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "자동차 부품사(모터) 매도 — EV 관련 대기업 또는 글로벌 Tier 1", "sector": "자동차/부품", "size": "중기업", "complexity": "Complex"},
    {"text": "알루미늄 다이캐스팅 업체 매도 — 자동차/전자 부품 대기업 매칭", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"text": "학원(입시) 프랜차이즈 매도 — 교육 대기업 또는 에듀테크 기업", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"text": "전기 시공 업체 매도 — 건설 대기업 M&A 또는 시설관리 기업", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"text": "방산 부품(광학/야시경) 업체 매도 — 한화/LIG 등 대기업 매칭", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
    {"text": "보험 GA 매도 — 금융지주 자회사 또는 대형 GA 통합", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    # 준대기업/대기업 매도
    {"text": "중견 식품사 사업부(음료 부문) 매도 — 전략적 매수자 탐색", "sector": "식품/F&B", "size": "중견기업", "complexity": "Complex"},
    {"text": "대기업 비핵심 자회사(화학 부문) 매도 — PE 바이아웃 매수자 매칭", "sector": "제조업(일반)", "size": "대기업", "complexity": "Complex"},
    {"text": "중견 IT서비스사 매도 — 글로벌 SI/컨설팅사 또는 PE", "sector": "IT/SaaS", "size": "중견기업", "complexity": "Complex"},
    # 소상공인 매도
    {"text": "동네 빵집(매출 3억) 매도 — 프랜차이즈 본사 또는 개인 매수자", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"text": "소형 인쇄소(매출 2억) 매도 — 인쇄 통합 업체 또는 개인 매수자", "sector": "제조업(일반)", "size": "소상공인", "complexity": "Simple"},
    # Edge
    {"text": "회생 절차 중인 제조사 매도 — 자산(설비/부지) 인수 관심 기업", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge"},
    {"text": "오너 급서(갑작스런 사망)로 긴급 매도 — 경영권 안정화 가능한 매수자", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
]

for q in uc4_queries:
    q["id"] = make_id()
    q["uc"] = "UC-4"
    q["source"] = "매트릭스-UC4"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc4_queries)

# ----------------------------------------------------------
# UC-5: 시장 탐색 — 규모 다양화 + 추가 니치 (+~120건)
# ----------------------------------------------------------

uc5_queries = [
    # 준대기업/대기업 규모
    {"text": "국내 매출 5,000억+ 제조업 전체 리스트, 업종별 분류", "sector": "제조업(일반)", "size": "준대기업", "complexity": "Simple"},
    {"text": "코스피 200 편입 제조업체, 영업이익률별 맵핑", "sector": "제조업(일반)", "size": "대기업", "complexity": "Medium"},
    {"text": "국내 매출 1조+ 식품사 전체 리스트, 해외 매출 비중별", "sector": "식품/F&B", "size": "대기업", "complexity": "Medium"},
    {"text": "시가총액 1조+ 바이오 기업, 파이프라인 단계별 맵핑", "sector": "바이오/헬스케어", "size": "대기업", "complexity": "Complex"},
    {"text": "국내 매출 3,000억+ IT서비스/SaaS 기업 리스트", "sector": "IT/SaaS", "size": "중견기업", "complexity": "Medium"},
    {"text": "국내 매출 5,000억+ 건설사, 주택/비주택 비중별 맵핑", "sector": "건설", "size": "준대기업", "complexity": "Medium"},
    {"text": "국내 매출 1조+ 유통사, 온라인 전환율별 맵핑", "sector": "유통/물류", "size": "대기업", "complexity": "Medium"},
    {"text": "국내 자산 5,000억+ 금융사(비은행), 업종별 맵핑", "sector": "금융/보험", "size": "준대기업", "complexity": "Medium"},

    # 소상공인 규모
    {"text": "수도권 매출 5억 미만 IT 개발사 전수 조사, 외주 개발 위주", "sector": "IT/SaaS", "size": "소상공인", "complexity": "Medium"},
    {"text": "서울 강남/서초/송파 뷰티숍(에스테틱) 맵핑", "sector": "화장품/뷰티", "size": "소상공인", "complexity": "Simple"},
    {"text": "제주도 소재 관광/레저 소사업자 전수 조사", "sector": "게임/콘텐츠", "size": "소상공인", "complexity": "Medium"},
    {"text": "전국 소규모 양조장(전통주/수제맥주), 매출 1~5억", "sector": "식품/F&B", "size": "소상공인", "complexity": "Medium"},

    # 니치 시장 (신규 섹터/테마)
    {"text": "국내 우주산업(위성/발사체/지상장비) 기업 전체 맵핑", "sector": "방위산업", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 원전 해체(D&D) 관련 기업 맵핑", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 소형모듈원자로(SMR) 관련 기업 전수 조사", "sector": "에너지/기후", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 양자컴퓨팅/양자통신 기업 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 합성생물학(SynBio) 기업 전수 조사", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 메타버스/가상세계 플랫폼 기업 맵핑", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 푸드업사이클링/식품 폐기물 감축 기업", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 마이크로 모빌리티(킥보드/자전거) 서비스 업체 전수 조사", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 나노기술/나노소재 기업 맵핑", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 바이오 플라스틱/생분해성 소재 기업", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 디지털 포렌식/사이버보안 기업 전수 조사", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 셀프스토리지/개인창고 운영 기업 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 그린수소 생산 기업(수전해) 맵핑", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 키오스크/무인매장 기술 기업 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 반도체 설계(팹리스) 기업 전수 조사, IP별 분류", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 음성AI/TTS/STT 기술 기업 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 바이오 연료(SAF/바이오디젤) 기업 전수 조사", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 웹3/블록체인 인프라 기업 맵핑(메인넷/지갑/거래소 외)", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 리빙/홈퍼니싱 브랜드 전체 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 반도체 소재(포토레지스트/에칭가스/슬러리) 국산화 기업", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 임베디드 소프트웨어 전문 기업 맵핑(AUTOSAR/RTOS)", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 항공 MRO(정비) 기업 전수 조사", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 농업/축산 자동화(스마트팜) 장비 기업 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},

    # 지역 특화 시장 탐색
    {"text": "판교/분당 테크노밸리 소재 IT기업 전수 조사, 매출 50억+", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "울산/거제 조선·해양 관련 기업 맵핑, 매출 100억+", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
    {"text": "원주 의료기기 클러스터 기업 전수 조사", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"text": "구미/김천 전자·디스플레이 부품 기업 맵핑", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
    {"text": "시화·반월 공단 소재 제조업체 전수 조사, 업종별", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "오송 바이오밸리 소재 바이오 기업 맵핑", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"text": "전주/익산 식품 산업 클러스터 기업 맵핑", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "김포/파주 물류 창고 밀집지 업체 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    {"text": "포항 철강·소재 관련 기업 맵핑, POSCO 협력사 포함", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"text": "대덕연구단지 소재 기술 기업 전수 조사", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},

    # 테마별 시장 탐색
    {"text": "국내 고령화 수혜 산업(실버케어/보조기기/요양) 전체 맵핑", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 저출산 대응 산업(육아/출산/보육) 기업 맵핑", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 1인 가구 타겟 사업(소포장/원룸/1인 가전) 기업 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 리셀/중고거래 플랫폼 및 관련 기업 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 K-방산 수출 밸류체인 전체 맵핑", "sector": "방위산업", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 반도체 팹(파운드리/메모리/비메모리) 생태계 맵핑", "sector": "반도체/소부장", "size": "중견기업", "complexity": "Complex"},
    {"text": "국내 전기차 충전 인프라 생태계(충전기/설치/운영/결제) 맵핑", "sector": "자동차/부품", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 CCUS(탄소 포집·활용·저장) 기업 전수 조사", "sector": "에너지/기후", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 고체 전해질/전고체 배터리 관련 기업 맵핑", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 보험사 자회사/계열사 비은행 사업 맵핑", "sector": "금융/보험", "size": "중견기업", "complexity": "Medium"},
    {"text": "국내 해양풍력 관련 기업(터빈/하부구조/케이블/설치) 맵핑", "sector": "에너지/기후", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 자율주행 관련 기업 전수 조사(센서/SW/플랫폼/서비스)", "sector": "자동차/부품", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 디지털 치료제(DTx) 기업 전수 조사, 인허가 현황별", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},

    # Simple 추가
    {"text": "국내 주요 편의점 공급업체 맵핑", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 코스닥 상장 게임사 리스트", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 대형 회계법인/세무법인 리스트", "sector": "금융/보험", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 전국 대리운전 앱/서비스 맵핑", "sector": "자동차/부품", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 목재/가구 제조업체 리스트, 매출 30억+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 펜션/글램핑 운영 기업 맵핑", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"text": "국내 무역상사(종합상사 포함) 리스트", "sector": "유통/물류", "size": "중기업", "complexity": "Simple"},
]

for q in uc5_queries:
    q["id"] = make_id()
    q["uc"] = "UC-5"
    q["source"] = "매트릭스-UC5"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc5_queries)


# ----------------------------------------------------------
# 페르소나 기반 톤 변형 (기존 쿼리를 다른 화법으로 재생성)
# ----------------------------------------------------------

persona_queries = [
    # PE 심사역 화법 (재무 중심, 건조한 톤)
    {"id": make_id(), "uc": "UC-1", "text": "EBITDA 50~200억, 제조업, 오너 리스크 낮은 곳. 바이아웃 구조, LBO 가능. 비상장 우선.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex", "source": "페르소나-PE심사역", "audit": "외감"},
    {"id": make_id(), "uc": "UC-1", "text": "EV/EBITDA 6x 이하, 네트 부채 EBITDA 대비 3x 미만, 제조업 또는 유통", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex", "source": "페르소나-PE심사역", "audit": "외감"},
    {"id": make_id(), "uc": "UC-1", "text": "딜사이즈 300~1,000억, 영업이익률 12%+, 캐시플로 안정적, 경영권 100% 확보 가능", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex", "source": "페르소나-PE심사역", "audit": "외감"},
    {"id": make_id(), "uc": "UC-1", "text": "포트폴리오 볼트온 대상, 기존 식품 포트코 대비 밸류체인 확장 가능, 매출 200억+", "sector": "식품/F&B", "size": "소기업", "complexity": "Complex", "source": "페르소나-PE심사역", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "IT서비스/SaaS, ARR 100억+, NRR 120%+, Rule of 40 충족. 소수지분 가능.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex", "source": "페르소나-PE심사역", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "EBITDA 마진 15%+, 자본적 지출 낮은 경상적 비즈니스, 기업가치 500~2,000억", "sector": "유통/물류", "size": "중기업", "complexity": "Complex", "source": "페르소나-PE심사역", "audit": "외감"},
    {"id": make_id(), "uc": "UC-1", "text": "전환사채(CB) 발행 가능 기업, 기업가치 1,000억+, 2년 내 IPO 가능성", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Complex", "source": "페르소나-PE심사역", "audit": "외감"},

    # 전략적 매수자(대기업 M&A팀) 화법
    {"id": make_id(), "uc": "UC-1", "text": "당사 기존 화학 사업부와 시너지 가능한 기능성 소재/코팅 업체, 특허 기반 기술 필수", "sector": "제조업(일반)", "size": "소기업", "complexity": "Complex", "source": "페르소나-전략적매수자", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "미국/유럽 유통망 보유 식품사, 당사 K-푸드 수출 채널로 활용 가능한 곳", "sector": "식품/F&B", "size": "중기업", "complexity": "Complex", "source": "페르소나-전략적매수자", "audit": "외감"},
    {"id": make_id(), "uc": "UC-1", "text": "헬스케어 AI 기술 보유 기업, 당사 병원 고객 대상 솔루션 확장 목적, 인력 확보 중요", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex", "source": "페르소나-전략적매수자", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "방산 전자전/ECM 기술 기업, 당사 수출형 전투체계에 통합 가능, 기술 인력 10명+", "sector": "방위산업", "size": "소기업", "complexity": "Complex", "source": "페르소나-전략적매수자", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "동남아 현지 유통 네트워크 보유 화장품 유통사, 당사 브랜드 진출 교두보", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium", "source": "페르소나-전략적매수자", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-2", "text": "당사 반도체 장비와 경쟁하는 국내 업체 리스트, 기술 격차 분석 목적", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium", "source": "페르소나-전략적매수자", "audit": "비외감"},

    # 개인 매수자 화법 (실용적, 구체적)
    {"id": make_id(), "uc": "UC-1", "text": "5~10억으로 살 수 있는 사업체, 수도권, 매달 순이익 2천만원 이상 나오는 곳", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple", "source": "페르소나-개인매수자", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "무인빨래방이나 코인세탁 프랜차이즈 인수, 서울 강남/서초, 월 순이익 500만원+", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple", "source": "페르소나-개인매수자", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "카페 양도양수, 매출 월 2천만원+, 역세권, 보증금 합리적인 곳", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple", "source": "페르소나-개인매수자", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "온라인 쇼핑몰 인수, 매출 월 5천만원+, 리뷰 많은 자체 브랜드 보유, 인수가 3억 이내", "sector": "유통/물류", "size": "소상공인", "complexity": "Medium", "source": "페르소나-개인매수자", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "학원 인수, 수학/영어, 학생 100명+, 수도권, 인수가 5억 이내", "sector": "교육", "size": "소상공인", "complexity": "Simple", "source": "페르소나-개인매수자", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "식자재 납품 사업, 거래처 50곳+, 냉장차 보유, 매출 10~30억, 흑자", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium", "source": "페르소나-개인매수자", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "네이버 스마트스토어 인수, 매출 월 3천만원+, 건기식/뷰티 카테고리, 리뷰 1만개+", "sector": "화장품/뷰티", "size": "소상공인", "complexity": "Medium", "source": "페르소나-개인매수자", "audit": "비외감"},

    # VC/CVC 화법
    {"id": make_id(), "uc": "UC-3", "text": "시리즈A, 월 매출 3억+ 이상, 바이오/디지털치료제, KPI 환자 수 10만+", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex", "source": "페르소나-VC", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "Pre-A, MRR 5천만원+, B2B SaaS, SMB 타겟, 월 성장률 10%+", "sector": "IT/SaaS", "size": "소상공인", "complexity": "Complex", "source": "페르소나-VC", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "시리즈B, GMV 500억+, 커머스 플랫폼, 테이크레이트 10%+, 흑자 전환 임박", "sector": "유통/물류", "size": "소기업", "complexity": "Complex", "source": "페르소나-VC", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "딥테크, 반도체 IP 설계, 고객사 LOI 확보, 창업팀 대기업 R&D 출신", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex", "source": "페르소나-VC", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "시리즈C, 기업가치 1,000억+, 에듀테크, MAU 100만+, 글로벌 확장 중", "sector": "교육", "size": "소기업", "complexity": "Complex", "source": "페르소나-VC", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "CVC 투자 대상, 당사 자동차 사업 시너지, ADAS/자율주행 기술, 시리즈A~B", "sector": "자동차/부품", "size": "소기업", "complexity": "Complex", "source": "페르소나-VC", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "클라이밋테크, 탄소 모니터링/감축 솔루션, 시리즈A, 글로벌 고객 확보", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium", "source": "페르소나-VC", "audit": "비외감"},

    # 회계법인/자문사 화법 (고객사 대리, 객관적)
    {"id": make_id(), "uc": "UC-1", "text": "고객사(PE) 의뢰: 매출 200~500억, 영업이익률 8%+, 제조업, 비상장, 오너 매각 의향 확인된 기업", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium", "source": "페르소나-자문사", "audit": "외감"},
    {"id": make_id(), "uc": "UC-1", "text": "고객사(대기업) 의뢰: 바이오 CMO/CDMO, 매출 100억+, GMP 시설 보유, 인수 대상 롱리스트", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex", "source": "페르소나-자문사", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-4", "text": "매도 자문 의뢰: 화장품 ODM사, 매출 300억, 수출 비중 50%. 적합한 전략적/재무적 매수자 리스트", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Complex", "source": "페르소나-자문사", "audit": "외감"},
    {"id": make_id(), "uc": "UC-4", "text": "매도 자문 의뢰: IT서비스 중견사, 매출 1,500억. 해외 SI사 또는 국내 대기업 매칭", "sector": "IT/SaaS", "size": "중견기업", "complexity": "Complex", "source": "페르소나-자문사", "audit": "외감"},
    {"id": make_id(), "uc": "UC-2", "text": "밸류에이션 자문용: 전기차 배터리 소재 업체, 동종 업계 비교 대상 기업 리스트", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium", "source": "페르소나-자문사", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-5", "text": "산업 리서치 의뢰: 국내 CDMO 시장 전체 플레이어 맵핑, 매출/캐파/인증 현황", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex", "source": "페르소나-자문사", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-5", "text": "실사 보조: 식품 제조 M&A 건, 타겟사와 동일 업종 기업 재무 비교 데이터", "sector": "식품/F&B", "size": "중기업", "complexity": "Medium", "source": "페르소나-자문사", "audit": "외감"},
]

new_queries.extend(persona_queries)

# ----------------------------------------------------------
# Stage 2 Round 2: 추가 ~400건 (UC-2, UC-3, UC-5 보강 + Simple/Edge)
# ----------------------------------------------------------

# UC-2 추가 Medium/Simple (~90건)
uc2_r2 = [
    # 제조업 니치
    {"text": "유압/공압 실린더 제조업체 비교, 매출 50억+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "진공 장비/펌프 제조사, 반도체/디스플레이 라인 납품", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "감속기/기어박스 전문 제조사 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"text": "스프링/탄성체 전문 제조사 비교, 자동차/전자 적용별", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"text": "고무/실리콘 제품 제조사, O링/가스켓/패킹 전문", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"text": "공구/지그 전문 제조사, 절삭공구/초경합금", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"text": "산업용 세척/클리닝 장비 제조사 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"text": "컨베이어/이송 시스템 업체 비교, 물류·제조 적용", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "절연재/단열재 전문 제조사 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"text": "전력용 변압기/배전반 제조사 비교", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
    # 식품 니치
    {"text": "유기농 식품 제조/유통사 비교, 인증 보유별", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "떡/한과 전문 제조사 비교, 매출 10억+", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
    {"text": "식용 곤충/대체 단백질 업체 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "우유/유제품 중소 제조사 비교, 서울우유·매일 외", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "프리미엄 도시락/케이터링 업체 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
    # 바이오
    {"text": "유전자 검사/DTC 유전체 분석 업체 비교", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"text": "피부과/성형외과 체인 비교, 매출 기준", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"text": "한방의약품/한약재 전문 업체 비교", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"text": "안과/시력교정 장비 업체 비교", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    # IT
    {"text": "챗봇/대화형 AI 솔루션 업체 비교", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "마케팅 자동화(MA) 플랫폼 비교, 국내 기업", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "회계/경비 관리 SaaS 비교(비즈플레이, 더존 등)", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "전자문서/전자결재 솔루션 비교", "sector": "IT/SaaS", "size": "소기업", "complexity": "Simple"},
    {"text": "키오스크 소프트웨어/하드웨어 업체 비교", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "OCR/문서 AI 업체 비교, 공공/금융 레퍼런스별", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    # 화장품
    {"text": "남성 그루밍/화장품 브랜드 비교", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple"},
    {"text": "미스트/선크림 전문 브랜드 비교, 온라인 매출 기준", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple"},
    {"text": "두피/탈모 관련 브랜드(샴푸/토닉) 비교", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple"},
    # 유통
    {"text": "농산물 직거래/온라인 유통 플랫폼 비교", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "공구/MRO 온라인 유통사 비교, 산업재 B2B", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "꽃/화훼 온라인 배송 서비스 비교", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    # 에너지
    {"text": "전기차 폐배터리 재활용 업체 비교, 기술 방식별", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "LNG/LPG 공급/판매 업체, 도시가스 외 산업용", "sector": "에너지/기후", "size": "중기업", "complexity": "Medium"},
    # 자동차
    {"text": "자동차 튜닝/레이싱 파츠 업체 비교", "sector": "자동차/부품", "size": "소기업", "complexity": "Simple"},
    {"text": "이륜차/전동킥보드 부품(배터리/모터) 업체 비교", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    # 교육
    {"text": "평생교육원/사이버대학 비교, 학생 수 기준", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"text": "글로벌 어학연수/유학원 비교, 매출 기준", "sector": "교육", "size": "소기업", "complexity": "Simple"},
    # 건설
    {"text": "방수/보수 전문 시공 업체 비교", "sector": "건설", "size": "소기업", "complexity": "Simple"},
    {"text": "조경/녹지 시공 업체 비교, 관급 실적별", "sector": "건설", "size": "소기업", "complexity": "Simple"},
    # 게임
    {"text": "보드게임/카드게임 퍼블리셔 비교, 국내 시장", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Simple"},
    {"text": "팟캐스트/오디오 콘텐츠 플랫폼 비교", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Simple"},
    # 방산
    {"text": "군용 차량/특수차 제조사 비교", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
    {"text": "방탄/방호 장비(헬멧/방탄복) 업체 비교", "sector": "방위산업", "size": "소기업", "complexity": "Simple"},
    # 금융
    {"text": "크라우드펀딩/P2P투자 플랫폼 비교", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    {"text": "로보어드바이저 자산운용사 비교", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    # 철강
    {"text": "고강도 강판 제조사 비교, AHSS/UHSS", "sector": "철강/금속", "size": "중기업", "complexity": "Medium"},
    {"text": "귀금속/보석 가공업체 비교", "sector": "철강/금속", "size": "소기업", "complexity": "Simple"},
    # 이커머스
    {"text": "중고 명품 거래 플랫폼 비교, 국내 시장", "sector": "이커머스", "size": "소기업", "complexity": "Medium"},
    {"text": "새벽 배송 서비스(식품) 업체 비교", "sector": "이커머스", "size": "소기업", "complexity": "Medium"},
    {"text": "식재료 정기 구독 서비스 업체 비교", "sector": "이커머스", "size": "소기업", "complexity": "Simple"},
]

for q in uc2_r2:
    q["id"] = make_id()
    q["uc"] = "UC-2"
    q["source"] = "매트릭스-UC2-R2"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc2_r2)

# UC-3 추가 (~80건)
uc3_r2 = [
    # 섹터별 투자 기회
    {"text": "식품 프랜차이즈, 가맹점 30~100개, 매출 50~200억, 확장 자금 필요", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "건기식 브랜드, D2C, 매출 30~100억, 해외 확장 투자 유치", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "밀키트/간편식 스타트업, 매출 20억+, MAU 10만+, 시리즈A", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "반도체 검사장비, 매출 100~300억, 해외 확장 투자, 소수지분", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
    {"text": "디스플레이 소재(양자점/OLED 재료), 매출 50억+, 양산 단계", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
    {"text": "의료 AI(영상판독/병리), 매출 10억+, 의료기기 허가 보유", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"text": "마이크로바이옴 기업, 파이프라인 IND 준비, 시리즈B", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"text": "줄기세포/재생의학 기업, 기술이전 실적 보유, 시리즈B+", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"text": "화장품 인디 브랜드, 매출 50억+, 글로벌 시장 진출, 시리즈A~B", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
    {"text": "뷰티테크(맞춤형 화장품/피부 분석 AI), 매출 5억+", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
    {"text": "콜드체인 물류 기술 기업, 매출 50억+, IoT 모니터링", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "역물류/반품 처리 자동화, 이커머스 고객사 다수", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "특수강/합금강 기술 보유, 항공·에너지 적용, 매출 100억+", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"text": "방산 사이버보안 기업, 매출 30억+, 군 인증 보유", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
    {"text": "교육 콘텐츠(교과서/참고서) 디지털 전환, 매출 50억+", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"text": "건축 폐기물 재활용 기술, 매출 30억+, 환경 인허가", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"text": "게임 스트리밍/클라우드 게이밍 인프라, 매출 20억+", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
    {"text": "에너지 중개/거래 플랫폼, 전력·가스 중개", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "보험 MGA(관리형 일반대리점), 매출 50억+, 디지털 채널", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    {"text": "자동차 데이터/커넥티드카 서비스, 매출 20억+", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    # 규모 다양화
    {"text": "소상공인 카페 브랜드 인수, 3~5개 매장, 인수가 2~5억", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"text": "소형 온라인 쇼핑몰, 매출 월 2,000만원+, 자체 브랜드, 인수 후 확장", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"text": "중견 IT기업(매출 2,000억+) 성장 투자, IPO 3년 이내 계획", "sector": "IT/SaaS", "size": "중견기업", "complexity": "Complex"},
    {"text": "준대기업 제조사 사업부 분할, 별도 법인 투자 기회", "sector": "제조업(일반)", "size": "준대기업", "complexity": "Complex"},
    {"text": "대기업 비핵심 자회사 MBO(경영진 인수) 참여 기회", "sector": "제조업(일반)", "size": "대기업", "complexity": "Complex"},
    # PE 전문 투자 구조
    {"text": "플랫폼 빌딩 — 기초 제조업체 인수 후 볼트온 대상 탐색", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"text": "클럽딜 참여 기회, 딜사이즈 5,000억+, 복수 GP 공동 투자", "sector": "제조업(일반)", "size": "중견기업", "complexity": "Complex"},
    {"text": "GP-led 세컨더리, 기존 PE 펀드 LP 지분 인수", "sector": "금융/보험", "size": "중기업", "complexity": "Complex"},
    {"text": "특수상황 투자, 자본잠식 기업 중 기술력 있는 턴어라운드 대상", "sector": "제조업(일반)", "size": "소기업", "complexity": "Complex"},
    {"text": "파이프라인 딜, 부동산/인프라 자산 기반 투자 구조", "sector": "건설", "size": "중기업", "complexity": "Complex"},
    # Simple
    {"text": "은행 예금 대비 수익률 높은 안정적 기업 투자, 배당 3%+", "sector": "제조업(일반)", "size": "중기업", "complexity": "Simple"},
    {"text": "코스닥 소형주, 매출 100억+, PER 10배 이하, 저평가", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"text": "비상장 기업, 매출 50~200억, 안정적 흑자, 배당 수익형", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
    {"text": "부동산 임대 수익 기업, 수익률 5%+, 수도권", "sector": "건설", "size": "소기업", "complexity": "Simple"},
    {"text": "소자본 투자, 1~3억, 안정적 월 수익 200만원+", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
]

for q in uc3_r2:
    q["id"] = make_id()
    q["uc"] = "UC-3"
    q["source"] = "매트릭스-UC3-R2"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc3_r2)

# UC-5 추가 (~100건)
uc5_r2 = [
    # 산업별 세분화
    {"text": "국내 광학/렌즈 제조업체 전수 조사", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 진공/클린룸 장비 업체 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 점착제/접착제 전문 제조사 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 특수 가스(반도체/산업용) 기업 전수 조사", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 계측기/센서 전문 기업 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 프레스/펀칭 전문 제조사 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 배관/파이프 제조업체 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 간장/된장/고추장 제조업체 전수 조사, 전통 장류", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 축산 가공(햄/소시지/육포) 업체 맵핑", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 제빵/제과 프랜차이즈 전수 조사, 가맹점 수별", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 대체감미료/저칼로리 식품 업체 맵핑", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 분자진단/PCR 장비 업체 맵핑", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 전자의무기록(EMR) 시스템 업체 전수 조사", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 방사선 치료 장비/소스 업체 맵핑", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 약국 체인/프랜차이즈 맵핑", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 데이터 라벨링/어노테이션 기업 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 3D 프린팅 서비스 기업 전수 조사", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 DevOps/CICD 솔루션 업체 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 디지털 사이니지/옥외광고 기업 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 비디오 회의/협업 솔루션 업체 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 뷰티 디바이스(갈바닉/LED마스크/레이저) 업체 전수 조사", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 향수/니치 퍼퓸 브랜드 맵핑", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 자동차 정비/수리 프랜차이즈 맵핑", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 전기 자전거/전동 모빌리티 업체 맵핑", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 카시트/유아 안전용품 업체 맵핑", "sector": "자동차/부품", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 온라인 교육 플랫폼(클래스101, 탈잉 등) 전수 비교", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 코딩 교육(어린이/청소년) 기업 맵핑", "sector": "교육", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 유학/이민 컨설팅 업체 맵핑", "sector": "교육", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 소규모 발전사업자(SMP/REC 수익) 맵핑", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 환경영향평가 전문 기업 맵핑", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 이산화탄소 포집(DAC) 기업 맵핑", "sector": "에너지/기후", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 방산 수출 대행/중개 업체 맵핑", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 군사 교육/훈련 시뮬레이터 업체 맵핑", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 마이크로파이낸스/소액대출 기업 맵핑", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 가상자산 수탁/커스터디 서비스 맵핑", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 스틸 유통(코일센터/가공센터) 전수 조사", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 희토류/희귀금속 관련 기업 맵핑", "sector": "철강/금속", "size": "소기업", "complexity": "Complex"},
    {"text": "국내 단독주택/타운하우스 시공사 맵핑", "sector": "건설", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 지반/터널 시공 전문사 맵핑", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 이스포츠/게임 대회 운영사 맵핑", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Simple"},
    {"text": "국내 오디오북/TTS 콘텐츠 기업 맵핑", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Simple"},
    # 지역별 추가
    {"text": "세종시 소재 기업 전수 조사, 업종별 분류", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "광주 광산업 클러스터 기업 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"text": "천안·아산 반도체/디스플레이 협력사 맵핑", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
    {"text": "제주 화장품(제주 원료 활용) 기업 맵핑", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple"},
    {"text": "인천 공항 주변 물류/포워딩 업체 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    # 테마 추가
    {"text": "국내 레그테크(규제 기술/컴플라이언스) 기업 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 슬립테크(수면 관련) 기업·제품 맵핑", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 시니어(50+) 타겟 서비스 기업 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 농업법인(영농/농업회사) 매출 30억+ 전수 조사", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"text": "국내 산업폐수 처리 전문 기업 맵핑", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    # 규모 다양화
    {"text": "국내 중견기업(매출 1,000~5,000억) 중 M&A 가능 기업 전수 조사, 업종별", "sector": "제조업(일반)", "size": "중견기업", "complexity": "Complex"},
    {"text": "국내 준대기업(자산 5조+) 비핵심 사업부 맵핑", "sector": "제조업(일반)", "size": "준대기업", "complexity": "Complex"},
    {"text": "국내 소상공인(매출 10억 이하) 프랜차이즈 맵핑, 업종별", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"text": "코스닥 시총 100억 미만 기업 전수 조사, 자산 가치 기준", "sector": "제조업(일반)", "size": "소기업", "complexity": "Complex"},
]

for q in uc5_r2:
    q["id"] = make_id()
    q["uc"] = "UC-5"
    q["source"] = "매트릭스-UC5-R2"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc5_r2)

# Edge cases 추가 (~30건)
edge_r2 = [
    {"id": make_id(), "uc": "UC-1", "text": "탈북민 창업 기업, 매출 5억+, 통일 관련 사업, 정부 지원 수혜", "sector": "제조업(일반)", "size": "소상공인", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "교도소/교정시설 위탁 생산 기업, 인건비 우위, 매출 20억+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "공군기지/미군기지 근처 방산 관련 소형사, 보안 인가 보유", "sector": "방위산업", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "가족 분쟁으로 주식 강제 매각 임박 기업, 매출 100억+", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "세금 체납으로 압류 예정 기업, 자산 가치 > 부채, 정상화 가능", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-2", "text": "허위 매출 의혹 기업 제외한 실제 경쟁사 리스트업", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-2", "text": "특허 소송 중인 기업 간 경쟁 구도 분석", "sector": "반도체/소부장", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "감사의견 '의견거절' 받은 기업 중 자산 가치 있는 투자 대상", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "대표이사 구속 기업, 사업 자체는 양호, 턴어라운드 투자", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "코스닥 거래정지 기업 중 재상장 가능성 있는 곳", "sector": "IT/SaaS", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-4", "text": "환경 규제 강화로 폐업 위기 기업, 설비 가치 인수 매수자 탐색", "sector": "에너지/기후", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-4", "text": "3세 경영 실패 기업 매도 — 전문 경영인 투입 가능 매수자", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "외감"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 폐교(학교) 활용 사업체 전수 조사", "sector": "교육", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 대마(헴프) 관련 합법 사업 기업 맵핑", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-5", "text": "DMZ/접경지역 관광·개발 관련 기업 맵핑", "sector": "건설", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "유튜버/인플루언서가 설립한 법인, 매출 10억+, 브랜드 전환 가능", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "섬(도서 지역) 유일 사업체(주유소/마트/펜션), 독점 지위", "sector": "유통/물류", "size": "소상공인", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "가상자산 거래소 라이선스 보유 기업, 적자이나 라이선스 가치", "sector": "금융/보험", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-2", "text": "경쟁사 분석인데 '경쟁사'가 아직 없는 신시장 — 유사 사업 모델 기업 비교", "sector": "IT/SaaS", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "해외 동포(교포) 소유 한국 법인 매각 건, 원격 경영 한계", "sector": "유통/물류", "size": "소기업", "complexity": "Edge", "source": "매트릭스-엣지R2", "audit": "비외감"},
]

new_queries.extend(edge_r2)

# Simple 쿼리 추가 (~40건)
simple_r2 = [
    {"id": make_id(), "uc": "UC-1", "text": "수도권 세탁 공장 인수, 매출 20억+", "sector": "유통/물류", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "인쇄업체 인수, 매출 30억+, 흑자", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "식품 공장 인수, 수도권, 매출 50억+", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "병원 인수(치과/한의원), 매출 10억+, 수도권", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "물류 창고 인수, 수도권, 1,000평+", "sector": "유통/물류", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "IT 외주 개발사 인수, 매출 10억+", "sector": "IT/SaaS", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "화장품 브랜드 인수, 매출 30억+", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "어린이집/유치원 인수, 수도권", "sector": "교육", "size": "소상공인", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "주유소 인수, 수도권, 매출 20억+", "sector": "에너지/기후", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-1", "text": "건설 면허 법인 인수, 토목/건축", "sector": "건설", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-2", "text": "수제 버거 프랜차이즈 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-2", "text": "국내 도넛 브랜드 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-2", "text": "포장이사 업체 비교", "sector": "유통/물류", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-2", "text": "가정용 정수기 렌탈 업체 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-2", "text": "국내 택배사 비교", "sector": "유통/물류", "size": "중기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "외감"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 다이소 납품 업체 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 PC방/게임카페 프랜차이즈 맵핑", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 세차/카워시 프랜차이즈 맵핑", "sector": "자동차/부품", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 미용실/헤어살롱 프랜차이즈 맵핑", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 필라테스/요가 스튜디오 프랜차이즈 맵핑", "sector": "교육", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "프랜차이즈 본사 인수, 가맹점 30개+, 매출 30억+", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-3", "text": "비상장 우량주, 매출 200억+, 흑자, 장외 거래", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-4", "text": "주차장 운영 업체 매도 — 부동산 개발사 또는 투자사 매칭", "sector": "건설", "size": "소기업", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
    {"id": make_id(), "uc": "UC-4", "text": "꽃집/화훼 도매 매도 — 동종 업체 또는 이커머스 업체", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple", "source": "매트릭스-심플R2", "audit": "비외감"},
]

new_queries.extend(simple_r2)

# ----------------------------------------------------------
# Round 3: 최종 보강 (~200건, Simple/Edge + 균등 분배)
# ----------------------------------------------------------

# Simple 추가 (~60건)
simple_r3 = [
    # UC-1 Simple
    {"id": make_id(), "uc": "UC-1", "text": "철물점/산업재 도매 인수, 매출 10억+", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-1", "text": "편의점 다점포(3개+) 운영 인수", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-1", "text": "꽃집/화훼 도매 인수, 매출 5억+", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-1", "text": "의류 봉제 공장 인수, 매출 10억+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-1", "text": "당구장/볼링장 인수, 수도권", "sector": "게임/콘텐츠", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-1", "text": "약국 인수, 서울 강남, 매출 10억+", "sector": "바이오/헬스케어", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-1", "text": "세차장 인수, 자동세차, 수도권", "sector": "자동차/부품", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-1", "text": "도시락 납품 업체 인수, 매출 20억+", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-1", "text": "애견카페/고양이카페 인수", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-1", "text": "택배 대리점 인수, 일 물량 1,000건+", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    # UC-2 Simple
    {"id": make_id(), "uc": "UC-2", "text": "국내 피자 프랜차이즈 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-2", "text": "국내 치킨 프랜차이즈 Top 10 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-2", "text": "국내 김밥/분식 프랜차이즈 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-2", "text": "인터넷 은행 비교(카카오뱅크/토스뱅크/케이뱅크)", "sector": "금융/보험", "size": "중기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-2", "text": "국내 이사/청소 플랫폼 비교", "sector": "IT/SaaS", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-2", "text": "국내 주차 앱/솔루션 비교", "sector": "IT/SaaS", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-2", "text": "캐리어/가방 제조사 비교, 국내 브랜드", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-2", "text": "국내 식기세척기/살균기 업체 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-2", "text": "국내 전동 공구 브랜드 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-2", "text": "국내 안마의자/마사지기 업체 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    # UC-5 Simple
    {"id": make_id(), "uc": "UC-5", "text": "국내 무인 아이스크림 가게 맵핑", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 스터디카페 프랜차이즈 맵핑", "sector": "교육", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 키즈카페 프랜차이즈 맵핑", "sector": "교육", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 코인빨래방 프랜차이즈 맵핑", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 공유 오피스/코워킹 스페이스 맵핑", "sector": "건설", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 무인 편의점/무인매장 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 코인노래방 프랜차이즈 맵핑", "sector": "게임/콘텐츠", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 반려동물 장례/추모 서비스 맵핑", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 자동판매기 운영 업체 맵핑", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 사진관/셀프스튜디오 프랜차이즈 맵핑", "sector": "게임/콘텐츠", "size": "소상공인", "complexity": "Simple"},
]

for q in simple_r3:
    q["source"] = "매트릭스-심플R3"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(simple_r3)

# Edge 추가 (~40건)
edge_r3 = [
    {"id": make_id(), "uc": "UC-1", "text": "암호화폐 채굴장 운영 법인, 전기 계약 및 설비 포함 인수", "sector": "IT/SaaS", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-1", "text": "미등록 의료기기 판매 이력 있으나 핵심 기술 보유 기업", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-1", "text": "K-POP 연습생 출신이 설립한 엔터 기획사, 소속 아티스트 가치", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-1", "text": "가맹점주 집단 소송 중인 프랜차이즈, 브랜드 가치 vs 법적 리스크", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-1", "text": "2인 공동 창업 기업, 한쪽 지분(49%) 매각 희망, CTO 잔류 조건", "sector": "IT/SaaS", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-1", "text": "골프장 인수, 회원권 반환 이슈 있으나 토지 가치 높음", "sector": "건설", "size": "중기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-1", "text": "선박 보유 수산업체, 어업 허가권 + 선박 자산 일괄 인수", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-1", "text": "중국 공장 보유 한국 기업, 중국 리스크로 급매, 기술력 양호", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-2", "text": "매출 뻥튀기(Window dressing) 의심 기업 걸러낸 실질 경쟁사 비교", "sector": "IT/SaaS", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-2", "text": "공정위 담합 적발 기업 간 시장점유율 재편 분석", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-2", "text": "특허 만료 예정(2년 이내) 의약품 제조사 비교, 제네릭 경쟁 구도", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-3", "text": "창업자 사망으로 후계자 없는 기술 기업, 기술/인력 인수 투자", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-3", "text": "국제 제재(러시아/이란) 해제 시 수혜 예상 기업 사전 투자", "sector": "에너지/기후", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-3", "text": "공매(경매) 낙찰 법인 투자, 자산 가치 > 인수가", "sector": "건설", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-4", "text": "리콜 이슈 발생 식품사 매도, 브랜드 훼손 최소화 매수자", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-4", "text": "사모펀드 만기 도래 포트코, 강제 매각 시 적합 매수자", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 '한계 기업'(이자보상비율 1 미만 3년 연속) 맵핑, 업종별", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 오너 고령(70세+) 비상장사 맵핑, 승계 이슈 예상", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-5", "text": "외국 기업이 국내 시장 철수/축소 중인 업종 맵핑", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 1사 독점 시장(경쟁사 전무) 산업 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-1", "text": "원전 주변 기업(규제 구역), 토지 보상 대상이나 사업 가치 있는 곳", "sector": "에너지/기후", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-2", "text": "대기업 출신 임원이 창업한 경쟁사 비교, 기술 유출 리스크 체크", "sector": "반도체/소부장", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-3", "text": "NFT/디지털 자산 기반 비즈니스, 적자이나 커뮤니티 자산 가치", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 고려인(CIS 지역) 기업인 운영 법인 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-1", "text": "전직 대통령/장관 연관 기업, 평판 리스크 vs 사업 가치", "sector": "건설", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-2", "text": "군납 독점 계약 보유사 vs 민수 경쟁사 비교", "sector": "방위산업", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-1", "text": "농지/산지 전용 허가 보유 법인, 개발 가치 인수", "sector": "건설", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-3", "text": "토큰 증권(STO) 발행 기업, 규제 불확실성이나 선점 효과", "sector": "금융/보험", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-4", "text": "방사성 폐기물 처리 업체 매도 — 인허가 가치 인수 매수자 탐색", "sector": "에너지/기후", "size": "소기업", "complexity": "Edge"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 다크스토어/고스트키친 운영 기업 맵핑", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge"},
]

for q in edge_r3:
    q["source"] = "매트릭스-엣지R3"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(edge_r3)

# UC-1 Medium 추가 (준대기업/대기업 커버 + 다양한 딜구조) (~40건)
uc1_r3 = [
    {"id": make_id(), "uc": "UC-1", "text": "조선 기자재 업체, 매출 500~2,000억, HD현대 협력사, 바이아웃", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-1", "text": "2차전지 양극재/음극재 업체, 매출 1,000~5,000억, 지분 투자 가능", "sector": "반도체/소부장", "size": "중견기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "대기업 비핵심 식품 자회사 카브아웃, 기업가치 3,000~1조", "sector": "식품/F&B", "size": "준대기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "코스닥 바이오 기업, 시총 500~2,000억, 파이프라인 Phase 2+, 경영권 인수", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "플랫폼 빌딩 대상: 치과/안과 체인 1호 인수, 10~20개 병원 보유", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "전기버스/상용 EV 제조사, 매출 500~2,000억, 수출 실적", "sector": "자동차/부품", "size": "중기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "중견 건설사(시공능력 50위권), 매출 3,000~1조, PF 리스크 낮은 곳", "sector": "건설", "size": "중견기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "대형 호텔/리조트 운영사, 기업가치 5,000억+, 부동산 자산 가치", "sector": "유통/물류", "size": "준대기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "한약재/한방 화장품 전문사, 매출 100~300억, 인허가+기술력", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-1", "text": "메이저 레코드 레이블/음원 유통사, IP 포트폴리오 가치", "sector": "게임/콘텐츠", "size": "중기업", "complexity": "Complex"},
    # 딜구조별
    {"id": make_id(), "uc": "UC-1", "text": "합병(merger) 대상, 당사와 동종 업종, 매출 유사 규모, 규모의 경제 확보", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "역합병(reverse merger) 대상, 코스닥 상장사, 시총 500억 이하, 우회상장 목적", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "JV(합작) 파트너, 일본 자동차 부품사와 합작 가능한 국내 기업", "sector": "자동차/부품", "size": "중기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "기술 라이선싱 인수, 매출보다 특허/기술 가치, 바이오 신약 관련", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-1", "text": "자산 인수(Asset Deal), 공장+설비+인력만 인수, 법인 제외", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
]

for q in uc1_r3:
    q["source"] = "매트릭스-UC1-R3"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(uc1_r3)

# UC-2/UC-3/UC-5 잔여 Medium (~60건)
mixed_r3 = [
    # UC-2
    {"id": make_id(), "uc": "UC-2", "text": "국내 전기밥솥/소형가전 브랜드 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-2", "text": "화물 운송 중개 플랫폼 비교(화물맨, 로지스팟 등)", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-2", "text": "국내 네일/속눈썹 프랜차이즈 비교", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-2", "text": "전기 공사/시공 업체 비교, 매출 100억+", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-2", "text": "산업용 UPS/전원장치 업체 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-2", "text": "워터파크/테마파크 운영사 비교", "sector": "게임/콘텐츠", "size": "중기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-2", "text": "해충 방제/방역 업체 비교", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-2", "text": "가구/인테리어 플랫폼(오늘의집, 한샘몰 등) 비교", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-2", "text": "유아 분유/이유식 브랜드 비교, 매출 기준", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-2", "text": "태양열/지열 설치 업체 비교", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    # UC-3
    {"id": make_id(), "uc": "UC-3", "text": "우주 스타트업, 소형 위성/발사체, 시리즈A~B, 정부 과제 수주", "sector": "방위산업", "size": "소기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-3", "text": "레저/스포츠 브랜드, 매출 50~200억, 아웃도어 시장 성장 수혜", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-3", "text": "건설 폐기물 재활용, 매출 30억+, 순환경제 테마, 성장 투자", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-3", "text": "글로벌 K-뷰티 유통사, 매출 100억+, 해외 매출 70%+", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-3", "text": "자동차 진단/정비 플랫폼, MAU 50만+, 오프라인 연계", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-3", "text": "산업 AI(제조/물류/에너지), 매출 30억+, 대기업 PoC 다수", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-3", "text": "코스닥 상장 제조업, PBR 0.5 이하, 자산 가치 투자", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-3", "text": "온라인 명품 거래 플랫폼, GMV 500억+, 시리즈B+", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-3", "text": "원격 교육/화상 강의 플랫폼, MAU 30만+, B2B 교육비 납부", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-3", "text": "소형 보험사(미니보험/소액보험), 디지털 네이티브, 매출 50억+", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    # UC-5
    {"id": make_id(), "uc": "UC-5", "text": "국내 드라이클리닝/크리닝 프랜차이즈 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 커피 로스터리/스페셜티 카페 브랜드 맵핑", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 전기차 배터리 폐배터리(사용후배터리) 시장 맵핑", "sector": "에너지/기후", "size": "소기업", "complexity": "Complex"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 플라즈마/CVD 장비 업체 맵핑", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 비건/식물 기반 식품 시장 전체 맵핑", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 바디케어/핸드크림 브랜드 맵핑", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 자동차 튜닝 업체 맵핑, 합법 인증 보유", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 축구/야구/농구 관련 사업 기업 맵핑", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 실내 골프/스크린골프 프랜차이즈 맵핑", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-5", "text": "국내 예식장/웨딩홀 운영사 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    {"id": make_id(), "uc": "UC-4", "text": "중고차 딜러십 매도 — 대형 중고차 플랫폼 매칭", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"id": make_id(), "uc": "UC-4", "text": "소형 출판사 매도 — 교육/콘텐츠 기업 매칭", "sector": "교육", "size": "소기업", "complexity": "Simple"},
]

for q in mixed_r3:
    q["source"] = "매트릭스-혼합R3"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(mixed_r3)


# ============================================================
# 병합 및 출력
# ============================================================
all_queries = stage1_queries + new_queries

# Deduplicate by ID
seen_ids = set()
unique_queries = []
for q in all_queries:
    if q["id"] not in seen_ids:
        seen_ids.add(q["id"])
        unique_queries.append(q)

total = len(unique_queries)
print(f"총 생성 쿼리 수: {total}")

# Distribution analysis
from collections import defaultdict

uc_dist = defaultdict(int)
sector_dist = defaultdict(int)
complexity_dist = defaultdict(int)
size_dist = defaultdict(int)
source_dist = defaultdict(int)

for q in unique_queries:
    uc_dist[q["uc"]] += 1
    sector_dist[q["sector"]] += 1
    complexity_dist[q["complexity"]] += 1
    size_dist[q["size"]] += 1
    # Track source category
    src = q["source"].split("-")[0] if "-" in q["source"] else q["source"]
    source_dist[src] += 1

print("\n=== UC 분포 ===")
for uc in sorted(uc_dist.keys()):
    count = uc_dist[uc]
    pct = count / total * 100
    target = UC_CATEGORIES[uc]["weight"] * 100
    print(f"  {uc} ({UC_CATEGORIES[uc]['name']}): {count}건 ({pct:.1f}%) [목표: {target:.0f}%]")

print("\n=== 섹터 분포 ===")
for sector, count in sorted(sector_dist.items(), key=lambda x: -x[1]):
    print(f"  {sector}: {count}건")

print("\n=== 복잡도 분포 ===")
for c in ["Simple", "Medium", "Complex", "Edge"]:
    count = complexity_dist[c]
    pct = count / total * 100
    print(f"  {c}: {count}건 ({pct:.1f}%)")

print("\n=== 기업규모 분포 ===")
for s in ["소상공인", "소기업", "중기업", "중견기업", "준대기업", "대기업"]:
    count = size_dist.get(s, 0)
    pct = count / total * 100
    print(f"  {s}: {count}건 ({pct:.1f}%)")

print("\n=== 소스 분포 ===")
for src, count in sorted(source_dist.items(), key=lambda x: -x[1]):
    print(f"  {src}: {count}건")

# Save
output = {
    "metadata": {
        "generated_at": datetime.now().isoformat(),
        "total_queries": total,
        "stage": "Stage 2: 매트릭스 생성 (554 → 1,300)",
        "sources": {
            "stage1": len(stage1_queries),
            "stage2_matrix": len(new_queries),
        },
        "distribution": {
            "uc": dict(uc_dist),
            "sector": dict(sector_dist),
            "complexity": dict(complexity_dist),
            "size": dict(size_dist),
        },
    },
    "queries": unique_queries,
}

output_path = "etl/data/finetuning_queries_stage2.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ 저장 완료: {output_path}")
