"""
기업탐색 Fine-tuning 데이터셋 — Stage 1: 증강 (260 → 550)

기존 90개 정밀 설계 쿼리(Seed 50 + LinkedIn 40)를 기반으로
조건 변형, 섹터 교차, 규모 밴드 변형을 적용하여 550개로 확장.

출력: finetuning_queries_stage1.json
"""

import json
from datetime import datetime

# ============================================================
# 카테고리/축 정의
# ============================================================

UC_CATEGORIES = {
    "UC-1": {"name": "M&A 타겟 발굴", "weight": 0.30},
    "UC-2": {"name": "경쟁사 탐색", "weight": 0.25},
    "UC-3": {"name": "투자 대상 탐색", "weight": 0.15},
    "UC-4": {"name": "매수자 탐색 (매도자)", "weight": 0.05},
    "UC-5": {"name": "시장 탐색", "weight": 0.25},
}

COMPLEXITY = ["Simple", "Medium", "Complex", "Edge"]

SIZE_BANDS = [
    "소상공인",  # 매출 10~120억 이하
    "소기업",    # 중소기업기본법 별표3
    "중기업",    # 자산 5,000억 미만
    "중견기업",  # 자산 10조 미만
    "준대기업",  # 자산 5조+
    "대기업",    # 자산 10조+
]

SECTORS = [
    "제조업(일반)", "식품/F&B", "반도체/소부장", "바이오/헬스케어",
    "IT/SaaS", "화장품/뷰티", "유통/물류", "철강/금속",
    "자동차/부품", "교육", "건설", "게임/콘텐츠",
    "에너지/기후", "방위산업", "금융/보험",
]

DEAL_STRUCTURES = ["바이아웃", "소수지분", "카브아웃", "전략적 인수", "합병"]

REGIONS = ["수도권", "충청권", "영남권", "호남권", "전국", "해외"]

# ============================================================
# Phase 0: 기존 Seed 쿼리 (50 + 40 = 90개)
# ============================================================

seed_queries = [
    # === Category A: M&A 타겟 발굴 (20개) ===
    {"id": "A-01", "uc": "UC-1", "text": "TRS 사업자 / VAN 대리점·총판 / 통신 대리점 / B2B 렌탈, 매출 50~200억, 영업이익 5~50억, 결제·데이터 결합 확장 가능", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex", "source": "고객-페이히어", "audit": "외감"},
    {"id": "A-02", "uc": "UC-1", "text": "B2B 교육(법정의무교육) / B2B 퀵(장기계약 반복매출), 100% 경영권 인수", "sector": "교육", "size": "소기업", "complexity": "Medium", "source": "고객-위펀", "audit": "비외감"},
    {"id": "A-03", "uc": "UC-1", "text": "급여 대행 업체, 매출 10억+, 수도권, 최근 3개년 흑자, IT 공급 제외, 노무법인 제외", "sector": "IT/SaaS", "size": "소상공인", "complexity": "Complex", "source": "고객-래티스", "audit": "비외감"},
    {"id": "A-04", "uc": "UC-1", "text": "반도체 장비(노광/식각/이온주입/박막증착/불량검측/패키징), 지분매각가 1,200억 이내, 경영권 확보, 비상장 위주", "sector": "반도체/소부장", "size": "중기업", "complexity": "Complex", "source": "고객-앤디스파트너스", "audit": "외감"},
    {"id": "A-05", "uc": "UC-1", "text": "정수기 솔레노이드밸브/온도·수위센서 관련, 딜사이즈 20~200억", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium", "source": "고객-코엠테크", "audit": "비외감"},
    {"id": "A-06", "uc": "UC-1", "text": "수도권 흑자기업, 공장보유 변압기 제조 관련", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium", "source": "설문-하재욱", "audit": "비외감"},
    {"id": "A-07", "uc": "UC-1", "text": "매출 10~50억, 흑자, 유동부채 200% 미만, 수출 가능, 20인 미만, 업력 10년", "sector": "제조업(일반)", "size": "소기업", "complexity": "Complex", "source": "설문-임호균", "audit": "비외감"},
    {"id": "A-08", "uc": "UC-1", "text": "매출 500억+, 영업이익률 10%+, 일가/개인 대주주, 바이아웃 가능", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium", "source": "설문-이상윤", "audit": "외감"},
    {"id": "A-09", "uc": "UC-1", "text": "매출 50~300억, 영업이익 5~30억, 3년 흑자, 조선·해양 제조 및 서비스", "sector": "제조업(일반)", "size": "소기업", "complexity": "Complex", "source": "설문-찰스류", "audit": "외감"},
    {"id": "A-10", "uc": "UC-1", "text": "매출 200억+, 3개년 성장, 영업이익률 8%+, 제조업, 투자유치 미수", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium", "source": "설문-정승욱", "audit": "외감"},
    {"id": "A-11", "uc": "UC-1", "text": "식품/식품서비스, 수도권, 매출 50억+, 차입금 의존도 30% 이하, 대주주 50%+ 보유", "sector": "식품/F&B", "size": "소기업", "complexity": "Complex", "source": "설문-박종호", "audit": "비외감"},
    {"id": "A-12", "uc": "UC-1", "text": "상속 이슈 딜/카브아웃, 매출 100억+, EBITDA 50억+, 캐시플로우 흑자", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex", "source": "설문-홍민식", "audit": "외감"},
    {"id": "A-13", "uc": "UC-1", "text": "B2B 렌탈 중개 사업자 중 연매출 100~200억, 기존 사업 안정적이나 단독 성장 한계, 플랫폼 결합 확장 가능", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex", "source": "AI변형", "audit": "외감"},
    {"id": "A-14", "uc": "UC-1", "text": "물류/재고관리/스마트팩토리 관련, 흑자, 바이아웃 또는 소수지분 무관", "sector": "유통/물류", "size": "소기업", "complexity": "Simple", "source": "AI변형", "audit": "비외감"},
    {"id": "A-15", "uc": "UC-1", "text": "니치마켓 B2B SaaS, 매출 20~50억, 흑자, 직원 20명 이하", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium", "source": "AI변형", "audit": "비외감"},
    {"id": "A-16", "uc": "UC-1", "text": "뿌리산업 수도권 제조업체, 3년 연속 흑자, 매출 30억+, 영업이익률 8%+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium", "source": "AI변형", "audit": "비외감"},
    {"id": "A-17", "uc": "UC-1", "text": "용기(캔/유리/PET) 생산업체, 매출 50억+, 영업이익률 5%+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium", "source": "AI변형", "audit": "비외감"},
    {"id": "A-18", "uc": "UC-1", "text": "냉동 해산물/신선제품 공급업체, 수도권, 매출 100억+", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple", "source": "AI변형", "audit": "외감"},
    {"id": "A-19", "uc": "UC-1", "text": "국방 관련 비상장사, 200억원 미만", "sector": "방위산업", "size": "소기업", "complexity": "Simple", "source": "AI변형", "audit": "비외감"},
    {"id": "A-20", "uc": "UC-1", "text": "인허가 업종, EBITDA 3년+ 흑자, 연매출 증가 중", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium", "source": "AI변형", "audit": "비외감"},

    # === Category B: 경쟁사 탐색 (12개) ===
    {"id": "B-01", "uc": "UC-2", "text": "철강 업종 내 경쟁사 탐색 (냉연, 열연 등 세부 품목별)", "sector": "철강/금속", "size": "중기업", "complexity": "Medium", "source": "CompanySearchLog", "audit": "외감"},
    {"id": "B-02", "uc": "UC-2", "text": "식품/식자재 제조업체 경쟁 구도", "sector": "식품/F&B", "size": "중기업", "complexity": "Simple", "source": "CompanySearchLog", "audit": "외감"},
    {"id": "B-03", "uc": "UC-2", "text": "화장품 업체 경쟁 비교", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Simple", "source": "CompanySearchLog", "audit": "외감"},
    {"id": "B-04", "uc": "UC-2", "text": "반도체 부품/장비 업체 맵핑", "sector": "반도체/소부장", "size": "중기업", "complexity": "Medium", "source": "CompanySearchLog", "audit": "외감"},
    {"id": "B-05", "uc": "UC-2", "text": "자동차 부품 업체 비교", "sector": "자동차/부품", "size": "중기업", "complexity": "Simple", "source": "CompanySearchLog", "audit": "외감"},
    {"id": "B-06", "uc": "UC-2", "text": "IT/소프트웨어 업체 경쟁 구도", "sector": "IT/SaaS", "size": "소기업", "complexity": "Simple", "source": "CompanySearchLog", "audit": "비외감"},
    {"id": "B-07", "uc": "UC-2", "text": "유통/물류 업체 비교", "sector": "유통/물류", "size": "중기업", "complexity": "Simple", "source": "CompanySearchLog", "audit": "외감"},
    {"id": "B-08", "uc": "UC-2", "text": "밸브/산업용 부품 니치 탐색", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium", "source": "CompanySearchLog", "audit": "비외감"},
    {"id": "B-09", "uc": "UC-2", "text": "바이오/의료기기 업체 맵핑", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Medium", "source": "CompanySearchLog", "audit": "외감"},
    {"id": "B-10", "uc": "UC-2", "text": "교육 업체 경쟁 비교", "sector": "교육", "size": "소기업", "complexity": "Simple", "source": "CompanySearchLog", "audit": "비외감"},
    {"id": "B-11", "uc": "UC-2", "text": "게임/콘텐츠 업체 비교", "sector": "게임/콘텐츠", "size": "중기업", "complexity": "Simple", "source": "CompanySearchLog", "audit": "외감"},
    {"id": "B-12", "uc": "UC-2", "text": "방위산업 업체 맵핑", "sector": "방위산업", "size": "중기업", "complexity": "Medium", "source": "CompanySearchLog", "audit": "외감"},

    # === Category C: 투자 대상 탐색 (10개) ===
    {"id": "C-01", "uc": "UC-3", "text": "기업가치 300~1,500억, 흑자기업", "sector": "제조업(일반)", "size": "중기업", "complexity": "Simple", "source": "설문-정재민", "audit": "외감"},
    {"id": "C-02", "uc": "UC-3", "text": "매출 100억+, 영업이익률 5%+, 기후기술/에너지전환", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium", "source": "설문-정진호", "audit": "외감"},
    {"id": "C-03", "uc": "UC-3", "text": "스타트업, 전년비 영업이익률·매출성장률 20%+", "sector": "IT/SaaS", "size": "소상공인", "complexity": "Medium", "source": "설문-강남규", "audit": "비외감"},
    {"id": "C-04", "uc": "UC-3", "text": "벤처인증, 매출 100억+, 영업이익 BEP+", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium", "source": "설문-강응권", "audit": "외감"},
    {"id": "C-05", "uc": "UC-3", "text": "Series B~Pre IPO, 구주매출 니즈, 의료기기/헬스케어/로봇, 매출 50억+", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex", "source": "설문-임병오", "audit": "외감"},
    {"id": "C-06", "uc": "UC-3", "text": "기업가치 2,500억~1조, 반도체/화장품/헬스케어/식음료/바이오", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Medium", "source": "설문-MichaelYoo", "audit": "외감"},
    {"id": "C-07", "uc": "UC-3", "text": "ARR 40억+, 고객이탈률 15% 이하, B2B 소프트웨어", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex", "source": "설문-김혁", "audit": "비외감"},
    {"id": "C-08", "uc": "UC-3", "text": "코스닥 상장사 중 영업이익률 낮은 M&A 가능 기업", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium", "source": "설문-LeeNomura", "audit": "외감"},
    {"id": "C-09", "uc": "UC-3", "text": "업종무관, 기업가치 100억 이하, 영업흑자, 자본잠식 아닌 기업", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium", "source": "설문-박종서", "audit": "비외감"},
    {"id": "C-10", "uc": "UC-3", "text": "일부 지분 인수, 10~50억 규모, IR 가능 기업", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple", "source": "설문-남창록", "audit": "비외감"},

    # === Category D: 매수자 탐색 (3개) ===
    {"id": "D-01", "uc": "UC-4", "text": "프로스이앤에프 매도 — 이 기업을 인수할 만한 전략적 매수자", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium", "source": "고객", "audit": "비외감"},
    {"id": "D-02", "uc": "UC-4", "text": "우일기전 매도 — 기전 분야 시너지 가능한 매수자", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium", "source": "고객", "audit": "비외감"},
    {"id": "D-03", "uc": "UC-4", "text": "웃담에프엔비 매도 — F&B 인수 의향 있는 대기업/PE", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium", "source": "고객", "audit": "비외감"},

    # === Category E: Edge Case (3개) ===
    {"id": "E-01", "uc": "UC-1", "text": "매출 월 500만원+, 영업이익률 15%+, 애완견 용품 온라인스토어", "sector": "이커머스", "size": "소상공인", "complexity": "Edge", "source": "설문-송정규", "audit": "비외감"},
    {"id": "E-02", "uc": "UC-1", "text": "B2B 유통 중소기업(커피 원두 유통), 수도권, 인수금액 5억 이하", "sector": "식품/F&B", "size": "소상공인", "complexity": "Edge", "source": "설문-장병준", "audit": "비외감"},
    {"id": "E-03", "uc": "UC-1", "text": "매출 1억+, 서울 경기, 뷰티/패션/라이프스타일/엔터 브랜드", "sector": "화장품/뷰티", "size": "소상공인", "complexity": "Edge", "source": "설문-김선빈", "audit": "비외감"},

    # === Category L: LinkedIn 역공학 (40개) ===
    {"id": "L-01", "uc": "UC-1", "text": "방산 핵심부품(포·포탑 구동장치) 제조, 매출 3,000~5,000억, 영업이익률 10%+, PE 바이아웃", "sector": "방위산업", "size": "중기업", "complexity": "Complex", "source": "LinkedIn-엠앤씨솔루션", "audit": "외감"},
    {"id": "L-02", "uc": "UC-3", "text": "신재생에너지/태양광/풍력, 딜사이즈 3,000~5,000억, 인프라 펀드 투자 적합", "sector": "에너지/기후", "size": "중기업", "complexity": "Medium", "source": "LinkedIn-SK이터닉스", "audit": "외감"},
    {"id": "L-03", "uc": "UC-1", "text": "바이오 기업, 기업가치 5,000~8,000억, 대기업 계열 카브아웃, PE 바이아웃", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Complex", "source": "LinkedIn-시자바이오", "audit": "외감"},
    {"id": "L-04", "uc": "UC-3", "text": "바이오 기업, CB/지분투자 300~500억 규모, 화장품 원료 시너지", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium", "source": "LinkedIn-우정바이오", "audit": "외감"},
    {"id": "L-05", "uc": "UC-1", "text": "식품 소재/소스 제조, 대기업 수직계열화 인수 대상", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple", "source": "LinkedIn-지앤에프", "audit": "비외감"},
    {"id": "L-06", "uc": "UC-1", "text": "렌터카/모빌리티 서비스, 국내 상위권, PE 포트폴리오 매물", "sector": "유통/물류", "size": "중기업", "complexity": "Medium", "source": "LinkedIn-SK렌터카", "audit": "외감"},
    {"id": "L-07", "uc": "UC-1", "text": "K뷰티 해외(미국) 유통사, 기업가치 ~1,000억", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium", "source": "LinkedIn-한성USA", "audit": "비외감"},
    {"id": "L-08", "uc": "UC-1", "text": "탄약 제조, K-방산 수출 핵심, 영업이익 기여 70%+, 카브아웃", "sector": "방위산업", "size": "중견기업", "complexity": "Complex", "source": "LinkedIn-풍산탄약", "audit": "외감"},
    {"id": "L-09", "uc": "UC-1", "text": "기내식·기내면세 사업, 기업가치 1.5조+, PE 엑시트", "sector": "식품/F&B", "size": "중기업", "complexity": "Medium", "source": "LinkedIn-대한항공씨앤디", "audit": "외감"},
    {"id": "L-10", "uc": "UC-1", "text": "제지 사업, EBITDA 1,800~2,000억, 캐시카우형 안정 사업, PE 바이아웃", "sector": "제조업(일반)", "size": "중견기업", "complexity": "Complex", "source": "LinkedIn-글로벌세아제지", "audit": "외감"},
    {"id": "L-11", "uc": "UC-1", "text": "수처리/환경 사업부, 대기업 카브아웃, 딜사이즈 1조+", "sector": "제조업(일반)", "size": "중견기업", "complexity": "Medium", "source": "LinkedIn-LG화학수처리", "audit": "외감"},
    {"id": "L-12", "uc": "UC-1", "text": "에스테틱/미용 사업부, 대기업 카브아웃, PE 바이아웃", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Medium", "source": "LinkedIn-LG화학에스테틱", "audit": "외감"},
    {"id": "L-13", "uc": "UC-1", "text": "인디 화장품 브랜드, 급성장, 대기업 전략적 인수 대상", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple", "source": "LinkedIn-토리든", "audit": "비외감"},
    {"id": "L-14", "uc": "UC-1", "text": "석유화학/윤활유, 딜사이즈 4,000~6,000억, 크로스보더(일본 매수자)", "sector": "에너지/기후", "size": "중기업", "complexity": "Complex", "source": "LinkedIn-대경오앤티", "audit": "외감"},
    {"id": "L-15", "uc": "UC-1", "text": "FPCB/연성회로기판, 딜사이즈 7,000~1조, PE 바이아웃", "sector": "반도체/소부장", "size": "중기업", "complexity": "Medium", "source": "LinkedIn-넥스플렉스", "audit": "외감"},
    {"id": "L-16", "uc": "UC-1", "text": "전자부품 제조, 딜사이즈 2,000~3,000억, 인수금융 활용", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium", "source": "LinkedIn-삼흥전자", "audit": "외감"},
    {"id": "L-17", "uc": "UC-1", "text": "한약/한방 사업, 딜사이즈 1조+, 사업부 매각", "sector": "바이오/헬스케어", "size": "중견기업", "complexity": "Medium", "source": "LinkedIn-풀산한약", "audit": "외감"},
    {"id": "L-18", "uc": "UC-1", "text": "미용의료기기, 글로벌 기업, PE 바이아웃", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Medium", "source": "LinkedIn-InMode", "audit": "외감"},
    {"id": "L-19", "uc": "UC-1", "text": "LCC 항공사, 딜사이즈 5,000~7,000억, PE 엑시트", "sector": "유통/물류", "size": "중기업", "complexity": "Medium", "source": "LinkedIn-이스타항공", "audit": "외감"},
    {"id": "L-20", "uc": "UC-1", "text": "모바일 캐주얼 게임 플랫폼, 70% 지분 인수, 해외(독일)", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Complex", "source": "LinkedIn-JustPlay", "audit": "비외감"},
    {"id": "L-21", "uc": "UC-3", "text": "바이오 전문 VC/자산운용, 300억 규모, 전략적 인수", "sector": "금융/보험", "size": "소기업", "complexity": "Medium", "source": "LinkedIn-솔리더스인베", "audit": "외감"},
    {"id": "L-22", "uc": "UC-1", "text": "엘리베이터/빌딩설비 제조, 대기업 카브아웃, 글로벌", "sector": "제조업(일반)", "size": "중견기업", "complexity": "Medium", "source": "LinkedIn-도시바엘리베이터", "audit": "외감"},
    {"id": "L-23", "uc": "UC-1", "text": "택시 플랫폼/모빌리티, 대기업 계열 매각", "sector": "IT/SaaS", "size": "중기업", "complexity": "Simple", "source": "LinkedIn-카카오모빌리티", "audit": "외감"},
    {"id": "L-24", "uc": "UC-1", "text": "반도체 IP 설계, PE 매각, 팹리스", "sector": "반도체/소부장", "size": "소기업", "complexity": "Simple", "source": "LinkedIn-칩스앤미디어", "audit": "외감"},
    {"id": "L-25", "uc": "UC-1", "text": "반도체 웨이퍼, 전략적 인수, 대기업 간 M&A", "sector": "반도체/소부장", "size": "중견기업", "complexity": "Medium", "source": "LinkedIn-SK실트론", "audit": "외감"},
    {"id": "L-26", "uc": "UC-1", "text": "바이오시밀러 유통/직판, 해외 파트너사 인수, 크로스보더", "sector": "바이오/헬스케어", "size": "중견기업", "complexity": "Complex", "source": "LinkedIn-오가논", "audit": "외감"},
    {"id": "L-27", "uc": "UC-1", "text": "엑소좀/재생의학 바이오, PE 바이아웃", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium", "source": "LinkedIn-엑소코바이오", "audit": "외감"},
    {"id": "L-28", "uc": "UC-1", "text": "음료 제조/유통, 대기업 비핵심 자산 매각", "sector": "식품/F&B", "size": "중기업", "complexity": "Simple", "source": "LinkedIn-해태htb", "audit": "외감"},
    {"id": "L-29", "uc": "UC-1", "text": "T커머스/홈쇼핑, 이커머스 플랫폼의 오프라인 채널 확보", "sector": "유통/물류", "size": "중기업", "complexity": "Medium", "source": "LinkedIn-SK스토아", "audit": "외감"},
    {"id": "L-30", "uc": "UC-1", "text": "의약용 아미노산, 해외(독일), 식품→바이오 사업 확장", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex", "source": "LinkedIn-대상독일", "audit": "비외감"},
    {"id": "L-31", "uc": "UC-3", "text": "부동산 자산운용사, 은행권 비은행 포트폴리오 확장", "sector": "금융/보험", "size": "소기업", "complexity": "Medium", "source": "LinkedIn-트리니티자산운용", "audit": "외감"},
    {"id": "L-32", "uc": "UC-1", "text": "해외 보험사, 딜사이즈 2조+, 크로스보더(미국)", "sector": "금융/보험", "size": "중견기업", "complexity": "Complex", "source": "LinkedIn-DB손보미국", "audit": "외감"},
    {"id": "L-33", "uc": "UC-1", "text": "바이오 CDMO 해외 공장, 생산 캐파 확보", "sector": "바이오/헬스케어", "size": "중견기업", "complexity": "Medium", "source": "LinkedIn-삼성바이오GSK", "audit": "외감"},
    {"id": "L-34", "uc": "UC-5", "text": "디스플레이 산업 내 지분 구조 재편, 그룹 내 구조 재편", "sector": "반도체/소부장", "size": "대기업", "complexity": "Complex", "source": "LinkedIn-삼성SDI", "audit": "외감"},
    {"id": "L-35", "uc": "UC-3", "text": "AI 데이터센터 지분, 2조 규모, 인프라 투자", "sector": "IT/SaaS", "size": "중견기업", "complexity": "Medium", "source": "LinkedIn-SK울산DC", "audit": "외감"},
    {"id": "L-36", "uc": "UC-5", "text": "전장(automotive)/공조 B2B 기업 시장 맵핑", "sector": "자동차/부품", "size": "중기업", "complexity": "Medium", "source": "LinkedIn-LG전자", "audit": "외감"},
    {"id": "L-37", "uc": "UC-1", "text": "미생물 배양/발효 기업, 경영권 인수", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Simple", "source": "LinkedIn-대성미생물", "audit": "비외감"},
    {"id": "L-38", "uc": "UC-1", "text": "차량 디스플레이 경량 부품 제조사", "sector": "자동차/부품", "size": "소기업", "complexity": "Simple", "source": "쿠키딜프로젝트", "audit": "비외감"},
    {"id": "L-39", "uc": "UC-1", "text": "고급 디저트 제조·유통", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple", "source": "쿠키딜프로젝트", "audit": "비외감"},
    {"id": "L-40", "uc": "UC-1", "text": "전기설비 특화 강소 제조사", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple", "source": "쿠키딜프로젝트", "audit": "비외감"},
]


# ============================================================
# Phase 1: 증강 규칙
# ============================================================

def augment_revenue_band(query, idx):
    """매출 밴드 변형"""
    base = query.copy()
    variants = []

    revenue_shifts = [
        ("10~50억", "소기업"),
        ("50~200억", "소기업"),
        ("200~500억", "중기업"),
        ("500~1,000억", "중기업"),
        ("1,000~3,000억", "중기업"),
        ("3,000~5,000억", "중견기업"),
    ]

    for rev, size in revenue_shifts:
        if rev not in base["text"]:
            v = base.copy()
            v["id"] = f"AUG-R{idx:03d}"
            v["size"] = size
            v["source"] = f"증강-매출변형({base['id']})"
            # Adjust text based on original
            if "매출" in v["text"]:
                # Replace first revenue mention
                import re
                v["text"] = re.sub(
                    r"매출\s*[\d,~억원조]+",
                    f"매출 {rev}",
                    v["text"],
                    count=1
                )
            else:
                v["text"] = v["text"] + f", 매출 {rev}"
            variants.append(v)
            idx += 1
            if len(variants) >= 2:
                break
    return variants, idx


def augment_sector_swap(query, idx):
    """섹터 교차 — 동일 재무 조건 + 다른 섹터"""
    variants = []
    sector_pairs = {
        "제조업(일반)": ["식품/F&B", "화장품/뷰티", "자동차/부품"],
        "식품/F&B": ["화장품/뷰티", "유통/물류"],
        "바이오/헬스케어": ["화장품/뷰티", "식품/F&B"],
        "IT/SaaS": ["게임/콘텐츠", "교육"],
        "반도체/소부장": ["자동차/부품", "제조업(일반)"],
        "에너지/기후": ["건설", "제조업(일반)"],
        "방위산업": ["제조업(일반)", "자동차/부품"],
        "화장품/뷰티": ["바이오/헬스케어", "식품/F&B"],
        "유통/물류": ["식품/F&B", "제조업(일반)"],
        "금융/보험": ["IT/SaaS"],
        "게임/콘텐츠": ["IT/SaaS", "교육"],
    }

    orig_sector = query["sector"]
    targets = sector_pairs.get(orig_sector, [])

    for target in targets[:1]:
        v = query.copy()
        v["id"] = f"AUG-S{idx:03d}"
        v["sector"] = target
        v["source"] = f"증강-섹터교차({query['id']}→{target})"
        # Simplistic text adaptation
        sector_keywords = {
            "식품/F&B": "식품/F&B",
            "화장품/뷰티": "화장품/뷰티",
            "자동차/부품": "자동차 부품",
            "IT/SaaS": "IT/소프트웨어",
            "바이오/헬스케어": "바이오/헬스케어",
            "제조업(일반)": "제조업",
            "게임/콘텐츠": "게임/콘텐츠",
            "에너지/기후": "에너지/신재생",
            "교육": "교육",
            "건설": "건설",
        }
        v["text"] = f"[{sector_keywords.get(target, target)}] " + v["text"]
        variants.append(v)
        idx += 1

    return variants, idx


def augment_deal_structure(query, idx):
    """딜구조 변형"""
    variants = []
    if query["uc"] != "UC-1":
        return variants, idx

    structures = [
        ("바이아웃", "경영권 100% 인수"),
        ("소수지분", "소수지분 투자(20~30%)"),
        ("카브아웃", "사업부 분리 인수(카브아웃)"),
    ]

    for struct_name, struct_text in structures:
        if struct_name.lower() not in query["text"].lower() and struct_text not in query["text"]:
            v = query.copy()
            v["id"] = f"AUG-D{idx:03d}"
            v["source"] = f"증강-딜구조({query['id']}→{struct_name})"
            v["text"] = v["text"] + f", {struct_text}"
            variants.append(v)
            idx += 1
            if len(variants) >= 1:
                break

    return variants, idx


def augment_region(query, idx):
    """지역 변형"""
    variants = []
    if "수도권" in query["text"]:
        v = query.copy()
        v["id"] = f"AUG-G{idx:03d}"
        v["source"] = f"증강-지역({query['id']}→전국)"
        v["text"] = v["text"].replace("수도권", "전국(지역 무관)")
        variants.append(v)
        idx += 1
    elif "전국" not in query["text"] and "해외" not in query["text"]:
        v = query.copy()
        v["id"] = f"AUG-G{idx:03d}"
        v["source"] = f"증강-지역({query['id']}→수도권)"
        v["text"] = v["text"] + ", 수도권 소재"
        variants.append(v)
        idx += 1

    return variants, idx


def augment_audit_tag(query, idx):
    """외감/비외감 교차"""
    variants = []
    opposite = "비외감" if query.get("audit") == "외감" else "외감"

    v = query.copy()
    v["id"] = f"AUG-A{idx:03d}"
    v["audit"] = opposite
    v["source"] = f"증강-외감교차({query['id']}→{opposite})"
    if opposite == "외감":
        v["text"] = v["text"] + ", 외감 대상"
    else:
        v["text"] = v["text"] + ", 비외감 포함"
    variants.append(v)
    idx += 1

    return variants, idx


def generate_market_exploration_queries():
    """UC-5 시장 탐색 쿼리 생성 (25% 비중 맞추기 위해 추가)"""
    queries = []

    market_queries = [
        {"text": "국내 FPCB(연성회로기판) 제조사 전체 리스트, 매출 기준 정렬", "sector": "반도체/소부장", "size": "중기업", "complexity": "Simple"},
        {"text": "한국 화장품 OEM/ODM 기업 전체 맵핑", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Simple"},
        {"text": "국내 식품 제조 기업 중 매출 100억~500억 구간", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
        {"text": "K-방산 수출 관련 기업 전체 리스트", "sector": "방위산업", "size": "중기업", "complexity": "Simple"},
        {"text": "바이오시밀러 개발/생산 기업 전체 맵핑", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Simple"},
        {"text": "국내 SaaS 기업 중 ARR 10억+ 기업 리스트", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"text": "전기차 배터리 소재/부품 기업 전체 맵핑", "sector": "에너지/기후", "size": "중기업", "complexity": "Simple"},
        {"text": "국내 게임 개발사 중 매출 50억~300억 구간", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Simple"},
        {"text": "물류 자동화/로보틱스 기업 시장 현황", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
        {"text": "국내 반도체 후공정(패키징/테스트) 기업 전체", "sector": "반도체/소부장", "size": "중기업", "complexity": "Simple"},
        {"text": "헬스케어 디지털/원격의료 기업 맵핑", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
        {"text": "국내 프랜차이즈 본사 중 매출 100억+ 기업", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
        {"text": "자동차 전장(ADAS/자율주행) 부품 기업 리스트", "sector": "자동차/부품", "size": "중기업", "complexity": "Medium"},
        {"text": "국내 에듀테크 기업 시장 맵핑", "sector": "교육", "size": "소기업", "complexity": "Simple"},
        {"text": "국내 건설 장비/중장비 제조사 리스트", "sector": "건설", "size": "중기업", "complexity": "Simple"},
        {"text": "인공지능(AI) 솔루션 기업 중 매출 발생 기업", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"text": "국내 수산물/해산물 가공/유통 기업 맵핑", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
        {"text": "2차전지 장비 기업 전체 리스트", "sector": "에너지/기후", "size": "중기업", "complexity": "Simple"},
        {"text": "국내 CDMO/CMO(바이오 위탁생산) 기업 현황", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Medium"},
        {"text": "국내 보안(물리보안/사이버보안) 기업 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"text": "의료기기 제조사 중 매출 100억~1,000억", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Simple"},
        {"text": "국내 철강/비철금속 가공업체 전체 맵핑", "sector": "철강/금속", "size": "중기업", "complexity": "Simple"},
        {"text": "펫(반려동물) 산업 기업 리스트 — 사료/의료/용품", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"text": "국내 폐기물 처리/재활용 기업 시장 현황", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
        {"text": "핀테크/결제 인프라 기업 전체 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Simple"},
        {"text": "국내 화학/정밀화학 기업 중 매출 500억~3,000억", "sector": "제조업(일반)", "size": "중기업", "complexity": "Simple"},
        {"text": "국내 포장재(플라스틱/종이/유리) 제조사 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
        {"text": "농업 테크/스마트팜 기업 시장 맵핑", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"text": "엔터테인먼트/매니지먼트 기업 리스트", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Simple"},
        {"text": "국내 저축은행/캐피탈/리스 금융사 맵핑", "sector": "금융/보험", "size": "중기업", "complexity": "Simple"},
        {"text": "국내 호텔/리조트/숙박업 기업 전체 리스트", "sector": "건설", "size": "소기업", "complexity": "Simple"},
        {"text": "국내 데이터센터 운영/투자 기업 맵핑", "sector": "IT/SaaS", "size": "중기업", "complexity": "Medium"},
        {"text": "클라우드 인프라/MSP 기업 리스트", "sector": "IT/SaaS", "size": "소기업", "complexity": "Simple"},
        {"text": "국내 전기설비/전력기자재 기업 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
        {"text": "국내 산업용 밸브/펌프 제조사 리스트", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    ]

    for i, mq in enumerate(market_queries):
        q = {
            "id": f"MKT-{i+1:02d}",
            "uc": "UC-5",
            "text": mq["text"],
            "sector": mq["sector"],
            "size": mq["size"],
            "complexity": mq["complexity"],
            "source": "증강-시장탐색생성",
            "audit": "외감" if mq["size"] in ["중기업", "중견기업", "대기업"] else "비외감",
        }
        queries.append(q)

    return queries


def generate_competitor_augmented():
    """UC-2 경쟁사 탐색 추가 쿼리"""
    queries = []

    comp_queries = [
        {"text": "CJ제일제당과 비슷한 규모의 식품 제조 기업들", "sector": "식품/F&B", "size": "중견기업", "complexity": "Medium"},
        {"text": "토스와 유사한 핀테크/간편결제 기업들", "sector": "IT/SaaS", "size": "중기업", "complexity": "Medium"},
        {"text": "코스맥스와 경쟁하는 화장품 ODM/OEM 기업", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Medium"},
        {"text": "한화에어로스페이스와 유사 방산 부품/시스템 기업", "sector": "방위산업", "size": "중견기업", "complexity": "Medium"},
        {"text": "SK바이오사이언스와 경쟁하는 백신/바이오 CDMO", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Medium"},
        {"text": "쿠팡과 경쟁하는 이커머스/유통 플랫폼", "sector": "유통/물류", "size": "중견기업", "complexity": "Simple"},
        {"text": "LS전선과 유사한 전선/케이블 제조 기업들", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
        {"text": "HD현대일렉트릭과 경쟁하는 전력기기(변압기/차단기) 기업", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
        {"text": "두산에너빌리티와 유사한 발전 설비/플랜트 기업", "sector": "에너지/기후", "size": "중견기업", "complexity": "Medium"},
        {"text": "에코프로비엠과 경쟁하는 2차전지 양극재 기업들", "sector": "에너지/기후", "size": "중기업", "complexity": "Medium"},
        {"text": "카카오엔터와 경쟁하는 콘텐츠/IP 기업들", "sector": "게임/콘텐츠", "size": "중기업", "complexity": "Medium"},
        {"text": "메가스터디와 유사한 교육 기업 (온라인/오프라인)", "sector": "교육", "size": "소기업", "complexity": "Simple"},
        {"text": "현대건설과 유사한 건설/플랜트 기업들", "sector": "건설", "size": "중견기업", "complexity": "Simple"},
        {"text": "POSCO와 유사한 철강/소재 기업들", "sector": "철강/금속", "size": "중견기업", "complexity": "Simple"},
        {"text": "현대모비스와 경쟁하는 자동차 부품(모듈/전장) 기업", "sector": "자동차/부품", "size": "중견기업", "complexity": "Medium"},
        {"text": "DB손해보험과 경쟁하는 손해보험사", "sector": "금융/보험", "size": "중견기업", "complexity": "Simple"},
        {"text": "삼성바이오로직스와 경쟁하는 바이오 CMO/CDMO", "sector": "바이오/헬스케어", "size": "중견기업", "complexity": "Medium"},
        {"text": "네이버클라우드와 경쟁하는 국내 클라우드/AI 인프라", "sector": "IT/SaaS", "size": "중기업", "complexity": "Medium"},
        {"text": "CJ대한통운과 유사한 물류/택배 기업들", "sector": "유통/물류", "size": "중견기업", "complexity": "Simple"},
        {"text": "한국콜마와 경쟁하는 화장품 제조/ODM 기업", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Medium"},
    ]

    for i, cq in enumerate(comp_queries):
        q = {
            "id": f"COMP-{i+1:02d}",
            "uc": "UC-2",
            "text": cq["text"],
            "sector": cq["sector"],
            "size": cq["size"],
            "complexity": cq["complexity"],
            "source": "증강-경쟁사탐색생성",
            "audit": "외감",
        }
        queries.append(q)

    return queries


# ============================================================
# Main: 전체 증강 실행
# ============================================================

def main():
    all_queries = list(seed_queries)  # Start with 90 seeds
    aug_idx = 1

    # Apply augmentation rules to seed queries
    for q in seed_queries:
        # 1. Revenue band shift (selective)
        if q["uc"] in ["UC-1", "UC-3"] and q["complexity"] in ["Medium", "Complex"]:
            variants, aug_idx = augment_revenue_band(q, aug_idx)
            all_queries.extend(variants[:1])  # Take 1 variant per query

        # 2. Sector swap (selective)
        if q["uc"] in ["UC-1", "UC-3"] and q["sector"] in ["제조업(일반)", "바이오/헬스케어", "IT/SaaS"]:
            variants, aug_idx = augment_sector_swap(q, aug_idx)
            all_queries.extend(variants[:1])

        # 3. Deal structure change
        if q["uc"] == "UC-1" and q["complexity"] == "Medium":
            variants, aug_idx = augment_deal_structure(q, aug_idx)
            all_queries.extend(variants[:1])

        # 4. Region change
        if "수도권" in q["text"]:
            variants, aug_idx = augment_region(q, aug_idx)
            all_queries.extend(variants[:1])

    # 5. Add market exploration queries (UC-5)
    market_queries = generate_market_exploration_queries()
    all_queries.extend(market_queries)

    # 6. Add competitor augmented queries (UC-2)
    comp_queries = generate_competitor_augmented()
    all_queries.extend(comp_queries)

    # 7. Add additional UC-4 매수자 탐색 queries
    seller_queries = [
        {"id": "SELL-01", "uc": "UC-4", "text": "바이오 기업 매도 시 — 인수 의향 있는 대기업/PE 리스트", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색", "audit": "외감"},
        {"id": "SELL-02", "uc": "UC-4", "text": "IT/SaaS 기업 매도 시 — 전략적 매수자 후보 탐색", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색", "audit": "비외감"},
        {"id": "SELL-03", "uc": "UC-4", "text": "식품 제조업체 매도 시 — 수직계열화 관심 대기업/중견기업", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색", "audit": "비외감"},
        {"id": "SELL-04", "uc": "UC-4", "text": "제조업체 매도 시 — 해외 전략적 투자자/PE 매칭", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex", "source": "증강-매수자탐색", "audit": "외감"},
        {"id": "SELL-05", "uc": "UC-4", "text": "화장품 브랜드 매도 시 — 인수 관심 있는 뷰티 대기업/PE", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색", "audit": "비외감"},
        {"id": "SELL-06", "uc": "UC-4", "text": "게임 스튜디오 매도 시 — 인수 관심 대형 게임사/PE", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색", "audit": "비외감"},
        {"id": "SELL-07", "uc": "UC-4", "text": "에너지 사업부 매도 시 — 글로벌 인프라 펀드/전략적 투자자", "sector": "에너지/기후", "size": "중기업", "complexity": "Complex", "source": "증강-매수자탐색", "audit": "외감"},
    ]
    all_queries.extend(seller_queries)

    # 8. Additional UC-2 경쟁사 탐색 (섹터별 세분화)
    more_comp = [
        # 제조업 세분화
        {"text": "자동차 시트/내장재 제조사 경쟁 구도 — 매출 100억~500억 구간", "sector": "자동차/부품", "size": "소기업"},
        {"text": "자동차 조향/제동 부품 제조사 비교", "sector": "자동차/부품", "size": "중기업"},
        {"text": "산업용 로봇/자동화 장비 기업 경쟁 맵", "sector": "제조업(일반)", "size": "중기업"},
        {"text": "국내 PCB(인쇄회로기판) 제조사 경쟁 비교", "sector": "반도체/소부장", "size": "중기업"},
        {"text": "반도체 세정/CMP 장비 기업 경쟁 맵핑", "sector": "반도체/소부장", "size": "소기업"},
        {"text": "국내 플라스틱 사출 성형 제조사 경쟁 구도", "sector": "제조업(일반)", "size": "소기업"},
        {"text": "국내 표면처리/도금 전문 기업 비교", "sector": "제조업(일반)", "size": "소기업"},
        {"text": "금형/정밀 가공 기업 경쟁 맵핑", "sector": "제조업(일반)", "size": "소기업"},
        # 서비스/IT 세분화
        {"text": "HR SaaS/인사관리 솔루션 기업 경쟁 구도", "sector": "IT/SaaS", "size": "소기업"},
        {"text": "물류 SaaS/WMS(창고관리) 기업 비교", "sector": "IT/SaaS", "size": "소기업"},
        {"text": "국내 RPA/업무자동화 기업 경쟁 맵핑", "sector": "IT/SaaS", "size": "소기업"},
        {"text": "국내 CCTV/영상보안 기업 경쟁 구도", "sector": "IT/SaaS", "size": "소기업"},
        {"text": "마케팅 테크(애드테크/퍼포먼스 마케팅) 기업 비교", "sector": "IT/SaaS", "size": "소기업"},
        # F&B 세분화
        {"text": "국내 건기식(건강기능식품) 제조/유통 기업 경쟁 맵", "sector": "식품/F&B", "size": "소기업"},
        {"text": "국내 커피 프랜차이즈/로스팅 기업 비교", "sector": "식품/F&B", "size": "소기업"},
        {"text": "국내 냉동식품 제조사 경쟁 구도", "sector": "식품/F&B", "size": "중기업"},
        {"text": "국내 밀키트/HMR 기업 경쟁 맵핑", "sector": "식품/F&B", "size": "소기업"},
        # 바이오 세분화
        {"text": "국내 줄기세포/세포치료제 기업 경쟁 구도", "sector": "바이오/헬스케어", "size": "소기업"},
        {"text": "국내 진단키트/체외진단 기업 비교", "sector": "바이오/헬스케어", "size": "소기업"},
        {"text": "국내 치과 임플란트/의료기기 기업 경쟁 맵", "sector": "바이오/헬스케어", "size": "중기업"},
        # 에너지/건설 세분화
        {"text": "국내 태양광 모듈/셀 제조사 경쟁 구도", "sector": "에너지/기후", "size": "중기업"},
        {"text": "국내 ESS(에너지저장) 시스템 기업 비교", "sector": "에너지/기후", "size": "소기업"},
        {"text": "국내 인테리어/리모델링 건설사 경쟁 맵", "sector": "건설", "size": "소기업"},
        # 화장품/유통 세분화
        {"text": "국내 더마코스메틱(기능성 화장품) 기업 경쟁 비교", "sector": "화장품/뷰티", "size": "소기업"},
        {"text": "국내 향수/퍼퓸 브랜드 경쟁 맵핑", "sector": "화장품/뷰티", "size": "소기업"},
        {"text": "국내 풀필먼트/3PL 물류 기업 경쟁 구도", "sector": "유통/물류", "size": "소기업"},
        {"text": "국내 새벽배송/신선식품 배송 기업 비교", "sector": "유통/물류", "size": "중기업"},
        # 금융 세분화
        {"text": "국내 PG(결제대행)/VAN 사업자 경쟁 구도", "sector": "금융/보험", "size": "중기업"},
        {"text": "국내 P2P/대출중개 플랫폼 경쟁 맵핑", "sector": "금융/보험", "size": "소기업"},
        # 철강/금속 세분화
        {"text": "국내 알루미늄 압출/가공 기업 경쟁 비교", "sector": "철강/금속", "size": "소기업"},
        {"text": "국내 스테인리스/특수강 제조사 경쟁 맵", "sector": "철강/금속", "size": "중기업"},
    ]
    for i, mc in enumerate(more_comp):
        q = {"id": f"COMP2-{i+1:02d}", "uc": "UC-2", "text": mc["text"], "sector": mc["sector"], "size": mc["size"], "complexity": "Medium", "source": "증강-경쟁사세분화", "audit": "외감" if mc["size"] in ["중기업", "중견기업"] else "비외감"}
        all_queries.append(q)

    # 9. Additional UC-5 시장 탐색 (더 많은 섹터/니치)
    more_market = [
        {"text": "국내 탄소배출권/탄소중립 관련 기업 전체 맵핑", "sector": "에너지/기후", "size": "소기업"},
        {"text": "국내 수소 밸류체인(생산/저장/운송/충전) 기업 리스트", "sector": "에너지/기후", "size": "중기업"},
        {"text": "국내 반려동물 의료(동물병원 체인/의약품) 기업 맵핑", "sector": "바이오/헬스케어", "size": "소기업"},
        {"text": "국내 웹툰/웹소설 IP 기업 전체 리스트", "sector": "게임/콘텐츠", "size": "소기업"},
        {"text": "국내 전자상거래 풀필먼트 센터 운영사 맵핑", "sector": "유통/물류", "size": "소기업"},
        {"text": "국내 무인 키오스크/자동화 매장 기업 리스트", "sector": "IT/SaaS", "size": "소기업"},
        {"text": "국내 드론/UAM(도심항공모빌리티) 기업 맵핑", "sector": "제조업(일반)", "size": "소기업"},
        {"text": "국내 정보보호/ISMS 컨설팅 기업 리스트", "sector": "IT/SaaS", "size": "소기업"},
        {"text": "국내 전기차 충전 인프라 기업 맵핑", "sector": "에너지/기후", "size": "소기업"},
        {"text": "국내 선박 부품/조선 기자재 기업 전체 리스트", "sector": "제조업(일반)", "size": "중기업"},
        {"text": "국내 항공 MRO(정비/수리) 기업 맵핑", "sector": "제조업(일반)", "size": "중기업"},
        {"text": "국내 원자력 관련 기업(소형모듈원전/부품) 맵핑", "sector": "에너지/기후", "size": "중기업"},
        {"text": "국내 식물성 대체식품 기업 시장 현황", "sector": "식품/F&B", "size": "소기업"},
        {"text": "국내 화장품 원료(기능성 소재) 공급사 맵핑", "sector": "화장품/뷰티", "size": "소기업"},
        {"text": "국내 치과/안과 의료 체인 기업 리스트", "sector": "바이오/헬스케어", "size": "소기업"},
        {"text": "국내 유아/키즈 교육 기업(영어유치원/학원) 맵핑", "sector": "교육", "size": "소기업"},
        {"text": "국내 산업가스(질소/산소/아르곤) 공급 기업 리스트", "sector": "제조업(일반)", "size": "중기업"},
        {"text": "국내 중고차/자동차 리사이클링 기업 맵핑", "sector": "유통/물류", "size": "소기업"},
        {"text": "국내 디지털 사이니지/옥외광고 기업 리스트", "sector": "게임/콘텐츠", "size": "소기업"},
        {"text": "국내 식품 포장 기계/장비 제조사 맵핑", "sector": "제조업(일반)", "size": "소기업"},
        {"text": "국내 CRO(임상시험 수탁) 기업 전체 리스트", "sector": "바이오/헬스케어", "size": "소기업"},
        {"text": "국내 정수/수처리 기업 전체 맵핑", "sector": "제조업(일반)", "size": "소기업"},
        {"text": "국내 피부과/성형외과 관련 의료기기 기업 리스트", "sector": "바이오/헬스케어", "size": "소기업"},
        {"text": "국내 자동차 튜닝/애프터마켓 부품 기업 맵핑", "sector": "자동차/부품", "size": "소기업"},
        {"text": "국내 방산 소프트웨어(C4I/시뮬레이션) 기업 리스트", "sector": "방위산업", "size": "소기업"},
        {"text": "국내 여행/OTA(온라인 여행사) 기업 맵핑", "sector": "IT/SaaS", "size": "소기업"},
        {"text": "국내 웨딩/이벤트 기업 시장 맵핑", "sector": "유통/물류", "size": "소기업"},
        {"text": "국내 세라믹/내화물 기업 전체 리스트", "sector": "제조업(일반)", "size": "소기업"},
        {"text": "국내 식물공장/LED 농업 기업 맵핑", "sector": "식품/F&B", "size": "소기업"},
        {"text": "국내 지능형 빌딩(BMS/BEMS) 기업 리스트", "sector": "건설", "size": "소기업"},
    ]
    for i, mm in enumerate(more_market):
        q = {"id": f"MKT2-{i+1:02d}", "uc": "UC-5", "text": mm["text"], "sector": mm["sector"], "size": mm["size"], "complexity": "Simple" if "리스트" in mm["text"] else "Medium", "source": "증강-시장탐색추가", "audit": "외감" if mm["size"] in ["중기업", "중견기업"] else "비외감"}
        all_queries.append(q)

    # 10. Additional UC-3 투자 대상 (다양한 시리즈/유형)
    more_invest = [
        {"text": "Pre-IPO 단계, 매출 200억+, 영업흑자, 코스닥 상장 예정 기업", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
        {"text": "시리즈A 단계, AI/ML 기반, ARR 5억+, 빠른 성장", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"text": "성장 단계 VC 투자, 매출 50~200억, 영업이익 BEP 근처, 헬스케어", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
        {"text": "임팩트 투자, ESG 관련 기업, 매출 10억+, 사회적 가치 창출", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
        {"text": "코스피 상장사 중 저평가, PBR 0.5 이하, 영업이익 흑자", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
        {"text": "턴어라운드 투자, 과거 3년 적자 → 최근 흑자 전환, 제조업", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
        {"text": "메자닌 투자, CB/BW 발행 가능, 기업가치 500~2,000억", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
        {"text": "벤처투자, 초기 단계, 딥테크(반도체/로봇/우주), 기술력 보유", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
        {"text": "부동산 관련 투자, 물류센터/데이터센터 운영사, 수익률 안정적", "sector": "건설", "size": "중기업", "complexity": "Medium"},
        {"text": "크로스보더 투자, 해외(동남아) 진출 한국 기업, 매출 100억+", "sector": "유통/물류", "size": "소기업", "complexity": "Complex"},
        {"text": "세컨더리 투자, 기존 VC 보유 지분 인수, 시리즈B+ 기업", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"text": "SPAC 합병 대상, 기업가치 1,000~3,000억, 코스닥 상장 희망", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Complex"},
        {"text": "레버리지 바이아웃 가능, EBITDA 100억+, 안정적 현금흐름, 비상장", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
        {"text": "성장형 PE 투자, 매출 300~1,000억, CAGR 15%+, 화장품/뷰티", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Complex"},
        {"text": "배당 수익형 투자, 배당성향 30%+, ROE 10%+, 안정적 제조업", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
        {"text": "신재생에너지 PF 투자, 태양광/풍력 발전사업자", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
        {"text": "초기 바이오텍, 파이프라인 Phase 2+, 기술이전 가능성", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
        {"text": "콘텐츠 IP 투자, 매출 50억+, 글로벌 진출 가능, 애니/웹툰", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
    ]
    for i, mi in enumerate(more_invest):
        q = {"id": f"INV-{i+1:02d}", "uc": "UC-3", "text": mi["text"], "sector": mi["sector"], "size": mi["size"], "complexity": mi["complexity"], "source": "증강-투자대상추가", "audit": "외감" if mi["size"] in ["중기업", "중견기업"] else "비외감"}
        all_queries.append(q)

    # 11. Additional UC-4 매수자 탐색
    more_seller = [
        {"text": "반도체 장비사 매도 — 해외 전략적 매수자(일본/미국) 또는 국내 대기업", "sector": "반도체/소부장", "size": "중기업", "complexity": "Complex", "source": "증강-매수자탐색추가"},
        {"text": "건기식(건강기능식품) 브랜드 매도 — 인수 관심 F&B 대기업/PE", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색추가"},
        {"text": "물류 자동화 장비사 매도 — 인수 관심 물류 대기업/SI", "sector": "유통/물류", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색추가"},
        {"text": "교육 플랫폼 매도 — 에듀테크 인수 관심 기업/PE 탐색", "sector": "교육", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색추가"},
        {"text": "자동차 부품사 매도 — 전장/EV 시너지 있는 전략적 매수자", "sector": "자동차/부품", "size": "중기업", "complexity": "Complex", "source": "증강-매수자탐색추가"},
        {"text": "철강/금속 가공업체 매도 — 수직계열화 매수자 또는 PE", "sector": "철강/금속", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색추가"},
        {"text": "방산 부품사 매도 — 한화/LIG넥스원 등 방산 대기업 매칭", "sector": "방위산업", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색추가"},
        {"text": "에너지 서비스 기업 매도 — 글로벌 인프라 펀드 매칭", "sector": "에너지/기후", "size": "중기업", "complexity": "Complex", "source": "증강-매수자탐색추가"},
        {"text": "부동산 자산운용사 매도 — 금융지주/은행 비은행 확장 매수자", "sector": "금융/보험", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색추가"},
        {"text": "콘텐츠/IP 기업 매도 — 글로벌 미디어/게임사 매칭", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색추가"},
        {"text": "건설 장비/자재 기업 매도 — 건설 대기업 수직계열화", "sector": "건설", "size": "소기업", "complexity": "Medium", "source": "증강-매수자탐색추가"},
    ]
    for i, ms in enumerate(more_seller):
        q = {"id": f"SELL2-{i+1:02d}", "uc": "UC-4", "text": ms["text"], "sector": ms["sector"], "size": ms["size"], "complexity": ms["complexity"], "source": ms["source"], "audit": "외감" if ms["size"] in ["중기업", "중견기업"] else "비외감"}
        all_queries.append(q)

    # 12. More Edge cases
    edge_cases = [
        {"id": "EDGE-01", "uc": "UC-1", "text": "1인 법인, 매출 3억, IP(특허 3건 이상) 보유, 기술 인수 목적", "sector": "IT/SaaS", "size": "소상공인", "complexity": "Edge", "source": "증강-엣지", "audit": "비외감"},
        {"id": "EDGE-02", "uc": "UC-1", "text": "부도/회생 절차 기업 중 핵심 설비/인허가 보유, 제조업", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge", "source": "증강-엣지", "audit": "비외감"},
        {"id": "EDGE-03", "uc": "UC-1", "text": "해외(동남아) 소재 한국인 오너 기업, 매출 50억+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge", "source": "증강-엣지", "audit": "비외감"},
        {"id": "EDGE-04", "uc": "UC-1", "text": "대학 연구실 스핀오프 기업, 기술이전 완료, 매출 미발생", "sector": "바이오/헬스케어", "size": "소상공인", "complexity": "Edge", "source": "증강-엣지", "audit": "비외감"},
        {"id": "EDGE-05", "uc": "UC-1", "text": "업력 50년+ 장수 기업, 오너 고령, 승계 이슈, 매출 100억+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge", "source": "증강-엣지", "audit": "외감"},
        {"id": "EDGE-06", "uc": "UC-3", "text": "사회적 기업/소셜벤처, 매출 5억+, 임팩트 투자 적합", "sector": "교육", "size": "소상공인", "complexity": "Edge", "source": "증강-엣지", "audit": "비외감"},
        {"id": "EDGE-07", "uc": "UC-5", "text": "코스닥 상장폐지 기업 중 자산 가치 있는 기업 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge", "source": "증강-엣지", "audit": "외감"},
        {"id": "EDGE-08", "uc": "UC-1", "text": "군납 실적 보유 식품 제조사, 매출 30억+, 수도권", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge", "source": "증강-엣지", "audit": "비외감"},
        {"id": "EDGE-09", "uc": "UC-1", "text": "제주도 소재 관광/F&B 기업, 매출 10~50억, 브랜드력", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge", "source": "증강-엣지", "audit": "비외감"},
        {"id": "EDGE-10", "uc": "UC-1", "text": "분쟁/소송 없는 클린한 비상장 기업, 매출 200억+, 오너 매각 의향", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge", "source": "증강-엣지", "audit": "외감"},
    ]
    all_queries.extend(edge_cases)

    # 13. Massive UC-2 경쟁사 탐색 추가 (+75건)
    comp3_queries = [
        # 제조업 세분화
        {"id": "COMP3-01", "text": "플라스틱 사출 성형 전문 제조업체, 매출 50~300억, 수도권", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-02", "text": "CNC 정밀가공 업체, 항공/방산 부품 납품 실적, 매출 30억+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-03", "text": "산업용 로봇 통합 솔루션 업체 비교, 국내 매출 기준", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
        {"id": "COMP3-04", "text": "자동화 설비/FA 장비 업체 경쟁 구도, 삼성·LG 납품사 위주", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
        {"id": "COMP3-05", "text": "금형 제조업체, 자동차/전자 금형, 매출 100억+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-06", "text": "도장/표면처리 전문업체, 자동차 부품 Tier 2", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-07", "text": "포장재(골판지/플라스틱 용기) 제조업체, 식품 납품 비중 높은 곳", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-08", "text": "전선/케이블 제조업체 경쟁 비교, LS전선 외 중소규모", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
        {"id": "COMP3-09", "text": "주조/단조 전문업체, 자동차·조선 부품 납품사", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-10", "text": "필터/여과 장비 제조업체, 산업용·환경용", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
        # 식품/F&B 세분화
        {"id": "COMP3-11", "text": "간편식(HMR) 제조업체, OEM/ODM 포함, 유통사 납품 실적", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-12", "text": "냉동 수산물 가공업체, 수출 비중 30%+", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-13", "text": "커피 로스팅/원두 유통 업체, B2B 납품 위주", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
        {"id": "COMP3-14", "text": "김치/발효식품 제조업체, 해외 수출 실적 보유", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-15", "text": "건강기능식품 ODM/OEM 업체, 매출 100억+", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-16", "text": "식용유/식품첨가물 제조업체 경쟁 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
        {"id": "COMP3-17", "text": "프랜차이즈 외식업체, 가맹점 100개+, 한식/치킨/카페", "sector": "식품/F&B", "size": "중기업", "complexity": "Medium"},
        # 바이오/헬스케어
        {"id": "COMP3-18", "text": "체외진단(IVD) 기업, 매출 50억+, 자체 기술 보유", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-19", "text": "의료용 소모품(일회용 의료기기) 제조업체 비교", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Simple"},
        {"id": "COMP3-20", "text": "CRO(임상시험수탁기관) 경쟁 구도, 국내 매출 기준", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Medium"},
        {"id": "COMP3-21", "text": "동물용 의약품/사료첨가제 제조업체", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-22", "text": "재활/물리치료 기기 제조업체, 수출 실적 보유", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
        # IT/SaaS
        {"id": "COMP3-23", "text": "ERP/MES 솔루션 업체, 제조업 특화, 매출 30억+", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-24", "text": "사이버보안/정보보안 업체 경쟁 비교, 공공 납품 실적", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-25", "text": "AI/머신러닝 솔루션 업체, B2B, ARR 20억+", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-26", "text": "클라우드 MSP(관리형 서비스) 업체 비교, AWS/Azure 파트너", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-27", "text": "HR테크/인사관리 SaaS 업체, 유료 고객 100사+", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-28", "text": "핀테크/결제 솔루션 업체, PG/VAN 면허 보유", "sector": "IT/SaaS", "size": "중기업", "complexity": "Complex"},
        # 화장품/뷰티
        {"id": "COMP3-29", "text": "화장품 OEM/ODM 업체, 코스맥스·한국콜마 외 중소규모", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-30", "text": "인디 화장품 브랜드, 올리브영 입점, 매출 30~100억", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-31", "text": "화장품 원료/소재 업체, 기능성 원료 보유", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
        # 유통/물류
        {"id": "COMP3-32", "text": "3PL 물류 대행 업체, 이커머스 풀필먼트 특화", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-33", "text": "산업재 B2B 유통/도매 업체, 전국 배송망 보유", "sector": "유통/물류", "size": "중기업", "complexity": "Medium"},
        {"id": "COMP3-34", "text": "냉장/냉동 물류 전문업체, 콜드체인", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
        # 반도체
        {"id": "COMP3-35", "text": "반도체 세정/화학소재 업체, SK/삼성 납품사", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-36", "text": "반도체 테스트/검사 장비 업체 경쟁 비교", "sector": "반도체/소부장", "size": "소기업", "complexity": "Simple"},
        {"id": "COMP3-37", "text": "MLCC/수동부품 제조업체, 삼성전기 외", "sector": "반도체/소부장", "size": "중기업", "complexity": "Medium"},
        # 에너지
        {"id": "COMP3-38", "text": "태양광 모듈/셀 제조업체 경쟁 비교, 국내 생산", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-39", "text": "ESS(에너지저장장치) 업체, 배터리 팩/시스템 통합", "sector": "에너지/기후", "size": "중기업", "complexity": "Medium"},
        {"id": "COMP3-40", "text": "폐기물 처리/재활용 업체 경쟁 구도, 허가 보유", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
        # 자동차/부품
        {"id": "COMP3-41", "text": "EV 충전 인프라/충전기 제조업체, 매출 50억+", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-42", "text": "자동차 와이어링 하네스 업체, 현대기아 Tier 2", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-43", "text": "자동차 시트/내장재 부품 업체 비교", "sector": "자동차/부품", "size": "소기업", "complexity": "Simple"},
        # 교육
        {"id": "COMP3-44", "text": "어학원/영어교육 프랜차이즈, 가맹점 50개+", "sector": "교육", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-45", "text": "에듀테크/온라인 학습 플랫폼, MAU 10만+", "sector": "교육", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-46", "text": "직무/자격증 교육 업체, B2B·B2G 납품 실적", "sector": "교육", "size": "소기업", "complexity": "Medium"},
        # 건설
        {"id": "COMP3-47", "text": "인테리어/리모델링 시공 업체, 매출 100억+, 수도권", "sector": "건설", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-48", "text": "건축 자재(창호/단열재) 제조업체 비교", "sector": "건설", "size": "소기업", "complexity": "Simple"},
        # 게임/콘텐츠
        {"id": "COMP3-49", "text": "모바일 게임 개발사, 글로벌 매출 100억+, 캐주얼 장르", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-50", "text": "웹툰/웹소설 제작사, 카카오/네이버 플랫폼 연재", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-51", "text": "영상 제작/VFX 업체, 넷플릭스·디즈니+ 납품", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
        # 금융
        {"id": "COMP3-52", "text": "저축은행/캐피탈사 비교, 자산 5,000억+", "sector": "금융/보험", "size": "중기업", "complexity": "Complex"},
        {"id": "COMP3-53", "text": "손해사정/보험 중개 업체, 매출 30억+", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
        # 철강
        {"id": "COMP3-54", "text": "특수강/합금강 제조업체, 자동차·공구 소재", "sector": "철강/금속", "size": "중기업", "complexity": "Medium"},
        {"id": "COMP3-55", "text": "알루미늄 압출/가공 업체 비교, 건축·자동차용", "sector": "철강/금속", "size": "소기업", "complexity": "Simple"},
        # 방위산업
        {"id": "COMP3-56", "text": "탄약/화약 관련 업체, 풍산 외 납품사", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-57", "text": "군용 통신/전자전 장비 업체 경쟁 비교", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
        # Cross-sector 니치
        {"id": "COMP3-58", "text": "산업용 펌프/밸브 전문업체, 석유화학·발전소 납품", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-59", "text": "HVAC(공조/냉난방) 설비 업체 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
        {"id": "COMP3-60", "text": "제약 포장재/블리스터 제조업체", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-61", "text": "PCB(인쇄회로기판) 제조업체, 다층/HDI 기술 보유", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-62", "text": "LED 조명/디스플레이 업체, B2B·관공서 납품", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-63", "text": "세탁/린넨 서비스 업체, 호텔·병원 B2B", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
        {"id": "COMP3-64", "text": "자판기/무인 매장 운영 업체 비교", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
        {"id": "COMP3-65", "text": "위성/GPS 기술 업체, 정밀 측위 솔루션", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-66", "text": "스마트팜/농업 테크 업체, 시설원예 자동화", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-67", "text": "애완동물 사료/간식 제조업체, 매출 30억+", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-68", "text": "치과/정형외과 임플란트 업체 경쟁 비교", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-69", "text": "전자계약/전자서명 SaaS 업체, 공공 조달 실적", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-70", "text": "수소 관련(생산/저장/운송) 업체 맵핑", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-71", "text": "CCTV/영상보안 장비 업체, B2G 납품 위주", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-72", "text": "식물성 대체육/대체식품 제조업체", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-73", "text": "원자력/방사선 장비/서비스 업체", "sector": "에너지/기후", "size": "소기업", "complexity": "Complex"},
        {"id": "COMP3-74", "text": "드론 제조/서비스 업체, 산업용(측량/농업/물류)", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "COMP3-75", "text": "유아동 의류/용품 브랜드 업체 비교", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    ]
    for cq in comp3_queries:
        cq["uc"] = "UC-2"
        cq["source"] = "증강-경쟁사3차"
        cq["audit"] = "외감" if cq["size"] in ["중기업", "중견기업"] else "비외감"
    all_queries.extend(comp3_queries)

    # 14. Massive UC-5 시장 탐색 추가 (+70건)
    mkt3_queries = [
        {"id": "MKT3-01", "text": "국내 정수기/공기청정기 렌탈 시장 전체 기업 맵핑", "sector": "제조업(일반)", "size": "중기업", "complexity": "Simple"},
        {"id": "MKT3-02", "text": "반도체 후공정(패키징/테스트) 전체 밸류체인 맵핑", "sector": "반도체/소부장", "size": "중기업", "complexity": "Complex"},
        {"id": "MKT3-03", "text": "국내 바이오시밀러 파이프라인 보유 기업 전수 조사", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Complex"},
        {"id": "MKT3-04", "text": "전기차 배터리 소재(양극재/음극재/분리막/전해질) 시장 맵", "sector": "반도체/소부장", "size": "중기업", "complexity": "Complex"},
        {"id": "MKT3-05", "text": "K-뷰티 해외 수출 기업 전수 조사, 매출 50억+", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-06", "text": "국내 SaaS 기업 전체 리스트, ARR 10억+", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-07", "text": "국내 프롭테크(부동산 테크) 시장 전체 기업 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-08", "text": "국내 건기식(건강기능식품) 시장 전체 제조사 맵", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-09", "text": "국내 방위산업 Tier 2~3 부품사 전수 조사", "sector": "방위산업", "size": "소기업", "complexity": "Complex"},
        {"id": "MKT3-10", "text": "제주도 소재 전체 법인 기업 맵핑, 매출 10억+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-11", "text": "국내 2차전지 재활용/리사이클링 기업 전수 조사", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-12", "text": "대구·경북 지역 섬유/직물 제조업체 시장 맵", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-13", "text": "국내 로봇 산업 전체 밸류체인(제조/부품/소프트웨어)", "sector": "제조업(일반)", "size": "소기업", "complexity": "Complex"},
        {"id": "MKT3-14", "text": "이커머스 물류 풀필먼트 시장 전체 플레이어 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-15", "text": "국내 펫(반려동물) 산업 전체 맵, 사료·용품·의료·서비스", "sector": "식품/F&B", "size": "소기업", "complexity": "Complex"},
        {"id": "MKT3-16", "text": "국내 디지털 헬스케어(원격의료/디지털치료제) 시장", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
        {"id": "MKT3-17", "text": "충남·세종 지역 제조업체 전체 맵핑, 매출 30억+", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-18", "text": "국내 수소 경제 밸류체인 맵핑(생산/저장/충전/활용)", "sector": "에너지/기후", "size": "소기업", "complexity": "Complex"},
        {"id": "MKT3-19", "text": "국내 자동차 전장(ADAS/인포테인먼트) 부품사 맵", "sector": "자동차/부품", "size": "중기업", "complexity": "Complex"},
        {"id": "MKT3-20", "text": "한국 게임사 전체 리스트, 매출 50억+, 장르별 분류", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-21", "text": "국내 ESG 컨설팅/인증 업체 시장 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-22", "text": "국내 레저/아웃도어 브랜드 시장 전체 맵", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-23", "text": "호남권(광주·전남·전북) 식품 제조업체 전수 조사", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-24", "text": "국내 AI 반도체(NPU/가속기) 설계 업체 맵핑", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-25", "text": "국내 웰니스(스파/뷰티디바이스/건강관리) 시장 맵", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-26", "text": "국내 항공우주(위성/발사체/드론) 산업 전체 기업 맵", "sector": "방위산업", "size": "소기업", "complexity": "Complex"},
        {"id": "MKT3-27", "text": "경남 지역 조선/해양 장비 업체 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-28", "text": "국내 클린룸/반도체 시설 시공 업체 맵", "sector": "건설", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-29", "text": "국내 블록체인/가상자산 관련 기업 전수 조사", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-30", "text": "국내 인슈어테크 기업 전체 맵핑", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-31", "text": "수도권 비상장 제약사 전수 조사, 매출 100억+", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-32", "text": "국내 스마트 팩토리 솔루션 업체 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-33", "text": "국내 차량용 반도체(MCU/전력반도체) 업체 맵", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-34", "text": "국내 실버/시니어 케어 산업 전체 맵핑", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-35", "text": "국내 식물공장/수직농업 업체 맵핑", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-36", "text": "강원 지역 관광/레저 관련 기업 맵핑", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-37", "text": "국내 산업용 가스 제조/유통 시장 맵", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
        {"id": "MKT3-38", "text": "국내 전기설비/전력기기(변압기/차단기) 시장 맵", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
        {"id": "MKT3-39", "text": "국내 코스메슈티컬(기능성 화장품) 시장 전체 맵핑", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-40", "text": "국내 애그리테크(농업 테크) 기업 전수 조사", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-41", "text": "국내 보안(물리보안/출입관리/CCTV) 시장 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-42", "text": "국내 모빌리티/MaaS 플랫폼 맵핑(택시/렌터카/킥보드)", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-43", "text": "국내 해양/수산 양식 업체 전수 조사", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-44", "text": "인천 지역 물류 센터/창고 운영 기업 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-45", "text": "국내 탄소배출권 관련 기업(컨설팅/거래/감축) 맵", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-46", "text": "국내 유아교육/키즈 콘텐츠 시장 전체 맵핑", "sector": "교육", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-47", "text": "국내 리걸테크(법률 기술) 기업 전수 조사", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-48", "text": "국내 데이터센터 운영/개발 업체 맵핑", "sector": "건설", "size": "중기업", "complexity": "Medium"},
        {"id": "MKT3-49", "text": "국내 푸드테크(대체식품/배양육/식품AI) 스타트업 맵", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-50", "text": "국내 K-POP/엔터테인먼트 에이전시 전체 맵핑", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-51", "text": "국내 군수 정비/MRO 업체 전수 조사", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-52", "text": "국내 코스닥 바이오 기업 중 적자, 파이프라인 가치 보유", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
        {"id": "MKT3-53", "text": "국내 전자상거래 플랫폼/마켓플레이스 전체 맵핑", "sector": "이커머스", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-54", "text": "부산·울산 지역 자동차 부품 클러스터 기업 맵", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-55", "text": "국내 OTT/스트리밍 콘텐츠 제작사 맵핑", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-56", "text": "국내 캠핑/아웃도어 장비 제조업체 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
        {"id": "MKT3-57", "text": "국내 치과 기자재/디지털 덴티스트리 기업 맵", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-58", "text": "대전·세종 지역 IT/연구소 기반 기업 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-59", "text": "국내 전통주/크래프트 주류 제조업체 전수 조사", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-60", "text": "국내 웨어러블/IoT 디바이스 기업 맵핑", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-61", "text": "국내 폐배터리 수거/처리 기업 전수 조사", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-62", "text": "국내 스포츠/피트니스 관련 기업 맵핑(장비·브랜드·서비스)", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-63", "text": "국내 수처리/정수 기술 업체 전수 조사", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-64", "text": "국내 건축 모듈러/프리패브 시장 기업 맵핑", "sector": "건설", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-65", "text": "국내 자동차 경량화 소재(알루미늄/CFRP) 업체 맵", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-66", "text": "국내 VR/AR/XR 콘텐츠·장비 기업 맵핑", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-67", "text": "국내 반려동물 병원 프랜차이즈/동물병원 체인 맵핑", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-68", "text": "국내 금융 SaaS/핀인프라 기업 맵핑", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
        {"id": "MKT3-69", "text": "국내 세라믹/요업 제조업체 전수 조사", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
        {"id": "MKT3-70", "text": "국내 소방/안전 장비 제조업체 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    ]
    for mq in mkt3_queries:
        mq["uc"] = "UC-5"
        mq["source"] = "증강-시장탐색3차"
        mq["audit"] = "외감" if mq["size"] in ["중기업", "중견기업"] else "비외감"
    all_queries.extend(mkt3_queries)

    # 15. More Edge cases (+35건)
    edge2_cases = [
        {"id": "EDGE2-01", "text": "폐업 예정이나 인허가(위험물/의약품 제조) 가치 있는 기업", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-02", "text": "매출 0원이나 특허 50건+ 보유 연구개발 법인", "sector": "바이오/헬스케어", "size": "소상공인", "complexity": "Edge"},
        {"id": "EDGE2-03", "text": "부동산 자산만 보유한 비활동 법인(페이퍼컴퍼니 아닌)", "sector": "건설", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-04", "text": "정부 R&D 과제 수주만으로 운영 중인 기업, 상용화 직전", "sector": "IT/SaaS", "size": "소상공인", "complexity": "Edge"},
        {"id": "EDGE2-05", "text": "공장 부지 3,000평+ 보유, 매출 대비 토지 자산 가치 큰 기업", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-06", "text": "북한 접경지역(파주·연천·철원) 소재 기업, 통일 관련 사업", "sector": "건설", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-07", "text": "매출 급감(전년비 -50% 이상) 했으나 핵심 기술/고객 보유", "sector": "IT/SaaS", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-08", "text": "다중 사업자 등록(2개+ 업종), 분할 매각 대상", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge"},
        {"id": "EDGE2-09", "text": "적자이나 정부 보조금/탄소배출권으로 실질 흑자인 기업", "sector": "에너지/기후", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-10", "text": "공동대표/지분 50:50 분쟁 기업, 한쪽 지분 인수 기회", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-11", "text": "국내 유일/독점 기술 보유 기업, 매출 10억 미만", "sector": "반도체/소부장", "size": "소상공인", "complexity": "Edge"},
        {"id": "EDGE2-12", "text": "법정관리 졸업 직후 기업, 부채 정리 완료, 정상 가동", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-13", "text": "수출 100% 기업(내수 매출 없음), 해외 거래처 리스크", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-14", "text": "부부 공동 경영 기업, 이혼/분쟁으로 급매", "sector": "식품/F&B", "size": "소상공인", "complexity": "Edge"},
        {"id": "EDGE2-15", "text": "군납/관급 매출 80%+ 기업, 수의계약 리스크", "sector": "방위산업", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-16", "text": "매출 1,000억+ 이나 영업이익 0원대, 구조조정 가능 기업", "sector": "유통/물류", "size": "중기업", "complexity": "Edge"},
        {"id": "EDGE2-17", "text": "한약재/전통의약 제조 면허 보유 기업, 면허 가치 인수", "sector": "바이오/헬스케어", "size": "소상공인", "complexity": "Edge"},
        {"id": "EDGE2-18", "text": "대기업 협력사(전속 거래), 원청 의존도 90%+", "sector": "자동차/부품", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-19", "text": "상속세 납부 위해 급매 중인 기업, 실적 양호", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge"},
        {"id": "EDGE2-20", "text": "가상화폐/NFT 관련 기업, 규제 리스크 있으나 기술력", "sector": "IT/SaaS", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-21", "text": "프리미엄 수입차 딜러/서비스센터, 수도권, 독점 계약", "sector": "자동차/부품", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-22", "text": "산업단지 내 환경오염 이력 있는 부지+설비, 할인 매각", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-23", "text": "매출 10억 미만 1인 게임 스튜디오, IP 가치 높은 타이틀 보유", "sector": "게임/콘텐츠", "size": "소상공인", "complexity": "Edge"},
        {"id": "EDGE2-24", "text": "소셜미디어 인플루언서 법인(유튜버/인스타), 팔로워 100만+", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-25", "text": "특수법인(사회적협동조합/영농법인), 일반 인수 가능 여부", "sector": "식품/F&B", "size": "소상공인", "complexity": "Edge"},
        {"id": "EDGE2-26", "text": "코스닥 관리종목 편입 기업, 저평가 자산주", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge"},
        {"id": "EDGE2-27", "text": "일본 오너 기업의 한국 자회사 매각 건", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-28", "text": "대학교 근처 학원가 교육 기업, 부동산+사업 일괄 매각", "sector": "교육", "size": "소상공인", "complexity": "Edge"},
        {"id": "EDGE2-29", "text": "계절성 매출(성수기/비수기 10배 차이) 기업, 연평균 흑자", "sector": "식품/F&B", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-30", "text": "면세점 입점 브랜드, 코로나 이후 회복 중, 매출 급등", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Edge"},
        {"id": "EDGE2-31", "text": "기업분할(물적/인적) 후 비핵심 사업부 매각 예정", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge"},
        {"id": "EDGE2-32", "text": "ESG 등급 최하위이나 개선 시 가치 상승 큰 기업", "sector": "제조업(일반)", "size": "중기업", "complexity": "Edge"},
        {"id": "EDGE2-33", "text": "원격지(울릉도/흑산도 등 도서 지역) 소재 수산업 법인", "sector": "식품/F&B", "size": "소상공인", "complexity": "Edge"},
        {"id": "EDGE2-34", "text": "외국인 투자 기업(FDI), 본사 철수로 한국 법인 매각", "sector": "IT/SaaS", "size": "중기업", "complexity": "Edge"},
        {"id": "EDGE2-35", "text": "매출 5,000만원 미만 초소형 법인, 특수 면허/인허가만 보유", "sector": "건설", "size": "소상공인", "complexity": "Edge"},
    ]
    for ec in edge2_cases:
        ec["uc"] = "UC-1"  # Most edge cases are M&A target type
        ec["source"] = "증강-엣지2차"
        ec["audit"] = "외감" if ec["size"] in ["중기업", "중견기업"] else "비외감"
    # Distribute some edge cases to other UCs
    for ec in edge2_cases[15:20]:
        ec["uc"] = "UC-5"
    for ec in edge2_cases[20:25]:
        ec["uc"] = "UC-2"
    for ec in edge2_cases[25:28]:
        ec["uc"] = "UC-3"
    for ec in edge2_cases[28:30]:
        ec["uc"] = "UC-4"
    all_queries.extend(edge2_cases)

    # Deduplicate by ID
    seen_ids = set()
    unique_queries = []
    for q in all_queries:
        if q["id"] not in seen_ids:
            seen_ids.add(q["id"])
            unique_queries.append(q)

    # Trim or pad to target ~550
    print(f"총 생성 쿼리 수: {len(unique_queries)}")

    # Distribution analysis
    uc_dist = {}
    sector_dist = {}
    complexity_dist = {}
    size_dist = {}

    for q in unique_queries:
        uc_dist[q["uc"]] = uc_dist.get(q["uc"], 0) + 1
        sector_dist[q["sector"]] = sector_dist.get(q["sector"], 0) + 1
        complexity_dist[q["complexity"]] = complexity_dist.get(q["complexity"], 0) + 1
        size_dist[q["size"]] = size_dist.get(q["size"], 0) + 1

    print("\n=== UC 분포 ===")
    for uc, count in sorted(uc_dist.items()):
        pct = count / len(unique_queries) * 100
        target = UC_CATEGORIES[uc]["weight"] * 100
        print(f"  {uc} ({UC_CATEGORIES[uc]['name']}): {count}건 ({pct:.1f}%) [목표: {target:.0f}%]")

    print("\n=== 섹터 분포 ===")
    for sector, count in sorted(sector_dist.items(), key=lambda x: -x[1]):
        print(f"  {sector}: {count}건")

    print("\n=== 복잡도 분포 ===")
    for c, count in sorted(complexity_dist.items()):
        pct = count / len(unique_queries) * 100
        print(f"  {c}: {count}건 ({pct:.1f}%)")

    print("\n=== 기업규모 분포 ===")
    for s, count in sorted(size_dist.items()):
        print(f"  {s}: {count}건")

    # Save to JSON
    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_queries": len(unique_queries),
            "stage": "Stage 1: 증강 (260 → 550)",
            "sources": {
                "seed_designed": 50,
                "linkedin_reverse": 40,
                "augmented": len(unique_queries) - 90,
            },
            "distribution": {
                "uc": uc_dist,
                "sector": sector_dist,
                "complexity": complexity_dist,
                "size": size_dist,
            },
        },
        "queries": unique_queries,
    }

    output_path = "/Users/seungohnam/Desktop/git/personal/kr-acc/etl/data/finetuning_queries_stage1.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 저장 완료: {output_path}")
    return unique_queries


if __name__ == "__main__":
    main()
