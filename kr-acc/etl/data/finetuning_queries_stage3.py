"""
기업탐색 Fine-tuning 데이터셋 — Stage 3: 페르소나 기반 (1,200 → 2,000)

Stage 2의 1,200건을 기반으로, 5개 매수자 페르소나별 화법/톤 변형을 적용하여 2,000건으로 확장.

페르소나:
1. PE 심사역 — 재무 중심, 건조한 톤, EBITDA/멀티플/LBO 용어
2. 전략적 매수자(대기업 M&A팀) — 시너지 중심, "당사" 표현, 기술/채널 확보
3. 개인 매수자 — 실용적, 구어체, 소자본, "살 수 있는", "월 순이익"
4. VC/CVC — 성장 지표 중심, 시리즈/MRR/MAU, 영어 혼용
5. 회계법인/M&A자문사 — 고객사 대리, 객관적, "의뢰:", "롱리스트"

+ 보너스 페르소나:
6. 오픈채팅방 화법 — 캐주얼, "~있나요?", "~구합니다", 약어 사용
7. 은행/금융기관 — 여신 심사, "거래처", "재무안정성", 보수적

출력: finetuning_queries_stage3.json (최종 2,000건)
"""

import json
from datetime import datetime
from collections import defaultdict

# ============================================================
# Load Stage 2
# ============================================================
with open("etl/data/finetuning_queries_stage2.json", encoding="utf-8") as f:
    stage2 = json.load(f)

stage2_queries = stage2["queries"]

UC_CATEGORIES = {
    "UC-1": {"name": "M&A 타겟 발굴", "weight": 0.30},
    "UC-2": {"name": "경쟁사 탐색", "weight": 0.25},
    "UC-3": {"name": "투자 대상 탐색", "weight": 0.15},
    "UC-4": {"name": "매수자 탐색 (매도자)", "weight": 0.05},
    "UC-5": {"name": "시장 탐색", "weight": 0.25},
}

# Current distribution
uc_current = defaultdict(int)
for q in stage2_queries:
    uc_current[q["uc"]] += 1

TARGET_TOTAL = 2000
# How many more per UC?
uc_need = {}
for uc, info in UC_CATEGORIES.items():
    target = int(TARGET_TOTAL * info["weight"])
    uc_need[uc] = max(0, target - uc_current[uc])

print("=== 추가 필요 건수 ===")
for uc in sorted(uc_need):
    print(f"  {uc}: 현재 {uc_current[uc]}건 → 목표 {int(TARGET_TOTAL * UC_CATEGORIES[uc]['weight'])}건, 추가 {uc_need[uc]}건")

# ============================================================
# Stage 3 쿼리 생성
# ============================================================
new_queries = []
qid = 0


def make_id():
    global qid
    qid += 1
    return f"S3-{qid:04d}"


def audit_for_size(size):
    if size in ("중기업", "중견기업", "준대기업", "대기업"):
        return "외감"
    return "비외감"


# ===========================================================
# 페르소나 1: PE 심사역 (~120건)
# 화법: 건조, 재무 용어, "EBITDA", "멀티플", "LBO", "인수금융"
# ===========================================================
pe_queries = [
    # UC-1 M&A 타겟
    {"uc": "UC-1", "text": "EBITDA 30~100억, 제조업, 캡엑스 낮은 경상적 비즈니스. LBO 구조 가능. 비상장.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "EBITDA 50~200억, 식품, 원재료 가격 변동 리스크 낮은 가공식품 위주. 바이아웃.", "sector": "식품/F&B", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "EV/EBITDA 5~8x, 반도체 소부장, 삼성/SK 다변화 납품. 경영권 100%.", "sector": "반도체/소부장", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "FCF Yield 10%+, 유통/물류, 자산경량 모델. 딜사이즈 500~2,000억.", "sector": "유통/물류", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "EBITDA 마진 20%+, IT서비스/SaaS, 반복매출(Recurring) 비중 70%+. 그로스 바이아웃.", "sector": "IT/SaaS", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "EBITDA 100~500억, 화장품/뷰티, K뷰티 수출 비중 40%+. 인수 후 글로벌 확장.", "sector": "화장품/뷰티", "size": "중견기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "넷 부채/EBITDA 2x 이하, 자동차 부품, EV 전환 수혜. 딜사이즈 1,000~5,000억.", "sector": "자동차/부품", "size": "중견기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "EBITDA 20~80억, 건설 특수 시공(방수/단열/소방), 안정적 수주잔고. 바이아웃.", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "EBITDA 30~150억, 교육, 법정의무교육 또는 자격증 B2B. 반복매출 구조.", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "EBITDA 50~300억, 에너지 서비스(EPC/O&M), 장기 계약 비중 높은 곳.", "sector": "에너지/기후", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "EBITDA 100억+, 방산, 수출 매출 비중 30%+, K-방산 성장 수혜.", "sector": "방위산업", "size": "중견기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "EBITDA 20~100억, 금융(캐피탈/리스), ROE 10%+, 부실채권 비율 3% 이하.", "sector": "금융/보험", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "EBITDA 10~50억, 철강 가공, 고부가가치(STS/특수강), 안정적 거래처.", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "EBITDA 50~200억, 게임, 라이브서비스 운영 중인 타이틀 보유, 해외 매출 50%+.", "sector": "게임/콘텐츠", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "EBITDA 마진 15%+, 바이오(CDMO/CMO), GMP 시설 캐파 여유, 해외 수주.", "sector": "바이오/헬스케어", "size": "중견기업", "complexity": "Complex"},
    # 볼트온/플랫폼 빌딩
    {"uc": "UC-1", "text": "볼트온 대상: 기존 포트코(식품 유통) 대비 카테고리 확장 가능한 식자재 가공사, 매출 50~200억.", "sector": "식품/F&B", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "볼트온: 기존 포트코(IT서비스) 연동 가능한 보안/인프라 업체, ARR 30억+.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "플랫폼 빌딩 1호: 치과/안과/피부과 체인, 10개+ 지점, 매출 100~300억, 경영 시스템화.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "플랫폼 빌딩: 물류 3PL 기업 인수 후 역량 통합, EBITDA 30억+ 기업.", "sector": "유통/물류", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "세컨더리 바이아웃: 기존 PE 보유 포트코, 식품/제조, EBITDA 개선 추가 여지.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    # 다양한 규모
    {"uc": "UC-1", "text": "딜사이즈 5,000억~1조, 중견 제조업, 글로벌 #1~3 포지션, 바이아웃.", "sector": "제조업(일반)", "size": "중견기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "딜사이즈 100~500억, 소형 바이아웃, 제조/서비스, 오너 은퇴 매각.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "딜사이즈 1~3조, 대형 바이아웃, 코스피/코스닥 상장사 포함. 공개매수 가능.", "sector": "제조업(일반)", "size": "준대기업", "complexity": "Complex"},
    # UC-3 투자
    {"uc": "UC-3", "text": "그로스 에쿼티: EBITDA 흑자 전환, 매출 200~500억, IT/SaaS, 소수지분 20~30%.", "sector": "IT/SaaS", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "메자닌 투자: CB 500~1,000억, 제조업, 2년 내 IPO 계획, 전환 프리미엄 확보.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "코인베스트: 바이아웃 딜 공동 참여, LP 직접투자, 딜사이즈 3,000억+.", "sector": "식품/F&B", "size": "중견기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "디스트레스드: 영업이익 적자이나 구조조정 시 EBITDA 50억+ 가능, 제조업.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "인프라 투자: 물류센터/데이터센터, 완공 후 장기 임대 확정, Cap Rate 6%+.", "sector": "건설", "size": "중기업", "complexity": "Complex"},
    # UC-2
    {"uc": "UC-2", "text": "밸류에이션 벤치마크: 화장품 ODM 동종 기업 EV/EBITDA 멀티플 비교.", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "피어 그룹 분석: 반도체 장비 국내 상장사, 매출/EBITDA/멀티플 비교 테이블.", "sector": "반도체/소부장", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "Comp 분석: 국내 게임사 EV/Sales 멀티플, 장르(RPG/캐주얼/FPS)별 차이.", "sector": "게임/콘텐츠", "size": "중기업", "complexity": "Complex"},
]

for q in pe_queries:
    q["id"] = make_id()
    q["source"] = "페르소나-PE심사역"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(pe_queries)

# ===========================================================
# 페르소나 2: 전략적 매수자 (대기업 M&A팀) (~120건)
# 화법: "당사", "시너지", "기술 확보", "유통망", "수직계열화"
# ===========================================================
strategic_queries = [
    # UC-1 전략적 인수
    {"uc": "UC-1", "text": "당사 배터리 사업부와 시너지 가능한 양극재/음극재 소재 업체, 자체 기술 필수, 매출 100~500억.", "sector": "반도체/소부장", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "당사 식품 포트폴리오 보완 — 프리미엄 간편식/밀키트 전문사, 매출 50~200억, 자체 생산라인.", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "당사 동남아 진출 교두보 — 현지 유통망 보유 화장품 유통사, 인도네시아/베트남 거점.", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "당사 제약 파이프라인 보강 — 항암제/면역질환 파이프라인 Phase 2+ 보유 바이오텍.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "당사 물류 역량 내재화 — 수도권 풀필먼트 센터 보유 3PL 기업, 일 처리량 10만건+.", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "당사 반도체 공정 국산화 — 세정/에칭 장비 자체 기술 보유 업체, 삼성/SK 레퍼런스.", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "당사 건설 밸류체인 확장 — 전기/소방 설비 시공 전문사, 면허 보유, 매출 100억+.", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "당사 AI 역량 강화 — 제조 AI(불량검출/예측정비) 스타트업, 기술 인력 확보 목적.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "당사 방산 수출 라인업 강화 — 전자전/C4I 기술 기업, 해외 수출 실적 보유.", "sector": "방위산업", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "당사 에너지 신사업 진출 — ESS/마이크로그리드 솔루션 기업, 매출 50~200억.", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "당사 자동차 전장 사업 수직계열화 — 차량용 커넥터/센서 업체, 현대/기아 납품.", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "당사 교육 사업 디지털 전환 — 에듀테크 플랫폼, MAU 50만+, 콘텐츠 라이브러리.", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "당사 철강 고부가가치화 — 특수강/합금 기술 보유 업체, 항공/에너지 적용.", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "당사 게임 IP 확보 — 자체 IP(웹툰/게임) 보유 기업, 미디어믹스 확장 가능.", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "당사 금융 디지털 채널 강화 — 핀테크/로보어드바이저 기업, MAU 30만+.", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    # 카브아웃/사업부 인수
    {"uc": "UC-1", "text": "경쟁사 비핵심 사업부 카브아웃 기회 — 당사 포트폴리오 보완 가능한 제조 라인.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "대기업 계열사 매각 건 중 당사 사업과 시너지 — 화학/소재 분야.", "sector": "제조업(일반)", "size": "준대기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "외국계 기업 한국 법인 철수 건 — 당사 제품 라인 보완 가능한 의료기기.", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Complex"},
    # UC-2
    {"uc": "UC-2", "text": "당사 주요 경쟁사 최근 M&A 동향 분석 — 어디를 인수했고, 왜, 얼마에.", "sector": "제조업(일반)", "size": "중견기업", "complexity": "Complex"},
    {"uc": "UC-2", "text": "당사 vs 경쟁사 기술 역량 비교 — 특허 건수, R&D 투자, 핵심 인력 규모.", "sector": "반도체/소부장", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-2", "text": "당사 해외 시장 경쟁 구도 — 일본/중국 로컬 기업 vs 한국 기업 비교.", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Complex"},
    # UC-5
    {"uc": "UC-5", "text": "당사 신사업 후보 시장 조사 — 국내 수소 경제 전체 밸류체인 플레이어.", "sector": "에너지/기후", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-5", "text": "당사 인수 타겟 풀 — 국내 CDMO 시장 전체 기업 규모/캐파/인증 맵핑.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-5", "text": "당사 협력사 확대 — 국내 반도체 소재(가스/케미칼/타겟) 전체 공급사 맵핑.", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "당사 유통 채널 분석 — 국내 편의점/마트/온라인 식품 유통 구조 맵핑.", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
]

for q in strategic_queries:
    q["id"] = make_id()
    q["source"] = "페르소나-전략적매수자"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(strategic_queries)

# ===========================================================
# 페르소나 3: 개인 매수자 (~130건)
# 화법: 구어체, "~살 수 있는", "월 순이익", "인수가", "자기자본"
# ===========================================================
individual_queries = [
    # UC-1 소자본 인수
    {"uc": "UC-1", "text": "1~3억으로 인수할 수 있는 사업체 추천. 월 순이익 300만원 이상 나오면 됨.", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-1", "text": "자기자본 5억으로 인수 가능한 제조업체. 직원 10명 이내, 수도권, 흑자.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-1", "text": "10억 이내로 살 수 있는 카페/음식점. 강남역 근처, 월세 합리적, 매출 월 3천만원+.", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-1", "text": "퇴직금 2억으로 시작할 수 있는 온라인 쇼핑몰 인수. 자체 브랜드 있으면 좋겠음.", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-1", "text": "학원 인수하고 싶은데 매출 5억+ 수학학원, 분당/판교 지역.", "sector": "교육", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-1", "text": "동물병원 인수, 서울 또는 경기, 월 매출 5천만원+, 수의사 2명+ 근무 중.", "sector": "바이오/헬스케어", "size": "소상공인", "complexity": "Medium"},
    {"uc": "UC-1", "text": "네이버 스마트스토어 인수. 건기식이나 뷰티 카테고리, 월 매출 2천만원+, 리뷰 5천개+.", "sector": "화장품/뷰티", "size": "소상공인", "complexity": "Medium"},
    {"uc": "UC-1", "text": "코인세탁소 3~5개 운영 중인 곳 일괄 인수, 서울/경기, 월 순이익 합계 500만원+.", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-1", "text": "인수가 5~10억, 식자재 납품, 거래처 안정적, 수도권. 배송차량 포함.", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "셀프 스튜디오/사진관 인수, 서울, 인테리어 깔끔한 곳, 예약 시스템 구축된 곳.", "sector": "게임/콘텐츠", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-1", "text": "자동세차장 인수, 수도권, 월 매출 1,500만원+, 토지 포함이면 더 좋음.", "sector": "자동차/부품", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-1", "text": "미용실/헤어샵 인수, 강남 또는 홍대, 직원 5명+, 단골 고객 확보된 곳.", "sector": "화장품/뷰티", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-1", "text": "무인 아이스크림 할인점 5개+ 운영 일괄 인수, 인수가 1~2억.", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-1", "text": "필라테스/요가 스튜디오 인수, 회원 200명+, 강남/판교, 강사 확보된 곳.", "sector": "교육", "size": "소상공인", "complexity": "Medium"},
    {"uc": "UC-1", "text": "IT 외주 개발사 인수, 직원 5~10명, 매출 5~10억, 안정적 고정 고객.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    # 중간 규모 개인 매수자
    {"uc": "UC-1", "text": "인수가 20~50억, 제조업, 공장 보유, 직원 30명 이내, 3년 흑자, 수도권.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "인수가 10~30억, 프랜차이즈 본사, 가맹점 30개+, 로열티 수입 안정적.", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "인수가 30~100억, 건설 면허 법인, 시공실적 보유, 수주잔고 있는 곳.", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "인수가 10~30억, 물류 창고, 수도권, 임대 수익 월 500만원+, 부지 포함.", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "인수가 5~15억, 여행사/투어 업체, 인바운드(외국인 한국 관광) 특화.", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    # UC-2
    {"uc": "UC-2", "text": "무인빨래방 프랜차이즈 어디가 좋은지 비교해줘. 초기 비용, 월 수익, 본사 지원.", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-2", "text": "배달 전문 치킨집 브랜드 비교. 가맹비, 인테리어비, 월 평균 매출, 폐점률.", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-2", "text": "키즈카페 프랜차이즈 비교해줘. 투자비 대비 수익률, 평수별.", "sector": "교육", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-2", "text": "스터디카페 vs 독서실 vs 코워킹스페이스, 투자 대비 수익 비교.", "sector": "교육", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-2", "text": "반려동물 유치원/호텔 프랜차이즈, 어디가 괜찮은지 비교.", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    # UC-3
    {"uc": "UC-3", "text": "월 50만원씩 투자할 수 있는 비상장 기업 직접 투자. 배당 나오면 좋겠음.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-3", "text": "1~2억 투자해서 지분 10~20% 갖고 싶어. IT 스타트업, 매출 발생 중인 곳.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-3", "text": "코스닥 소형주 중에 저평가된 거 찾아줘. PER 5배 이하, 매출 100억+.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    # UC-5
    {"uc": "UC-5", "text": "요즘 뜨는 무인 매장 종류별로 정리해줘. 어떤 게 수익성 좋은지.", "sector": "유통/물류", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-5", "text": "소자본으로 시작할 수 있는 프랜차이즈 전체 리스트. 1억 이내.", "sector": "식품/F&B", "size": "소상공인", "complexity": "Simple"},
    {"uc": "UC-5", "text": "온라인에서 잘 팔리는 건기식/뷰티 브랜드 리스트. 인수 검토용.", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple"},
]

for q in individual_queries:
    q["id"] = make_id()
    q["source"] = "페르소나-개인매수자"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(individual_queries)

# ===========================================================
# 페르소나 4: VC/CVC (~120건)
# 화법: 성장 지표, 시리즈, MRR/ARR, MAU, NRR, Rule of 40, 영어 혼용
# ===========================================================
vc_queries = [
    # UC-3 투자
    {"uc": "UC-3", "text": "Series A, B2B SaaS, MRR 3억+, NRR 120%+, 고객 이탈률 5% 이하. 제조/물류 vertical.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series B, D2C 뷰티 브랜드, 매출 50~150억, YoY 50%+ 성장, 글로벌 확장 준비 중.", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Pre-Series A, 딥테크(로봇/반도체), 대기업 PoC 2건+, 팀 대기업 R&D 출신.", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series A, 헬스케어 AI, FDA/MFDS 인허가 진행 중, MAU 10만+, 의료 데이터 확보.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series B, 핀테크, 월 거래액 500억+, Take Rate 1%+, 금융 라이선스 보유.", "sector": "금융/보험", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series A, 에듀테크, MAU 30만+, 유료 전환율 5%+, B2C+B2B 하이브리드.", "sector": "교육", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Pre-IPO, 게임사, 매출 300억+, 글로벌 DAU 100만+, 코스닥 상장 준비.", "sector": "게임/콘텐츠", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series A, 클라이밋테크, 탄소 측정/감축 SaaS, ARR 10억+, 글로벌 고객.", "sector": "에너지/기후", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series B, 물류테크, 자체 WMS/TMS, 월 처리 물동량 100만건+, 대형 이커머스 고객.", "sector": "유통/물류", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series A, 푸드테크, 대체식품/배양육, R&D 단계이나 글로벌 파트너십 확보.", "sector": "식품/F&B", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series C, 프롭테크, 부동산 중개/관리 플랫폼, 월 거래건수 1만+, 흑자 전환.", "sector": "건설", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series A, 자율주행/로보틱스, 물류 라스트마일, 시범사업 3건+, 기술 특허 10건+.", "sector": "자동차/부품", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Seed, 방산 스타트업, AI 기반 ISR(정보/감시/정찰), 군 과제 수주.", "sector": "방위산업", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series B, 건설테크, 스마트 시공/안전 AI, ARR 20억+, 대형 건설사 고객 5사+.", "sector": "건설", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "Series A, HR테크, 채용/평가/보상 SaaS, ARR 15억+, 기업 고객 100사+.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "CVC: 당사 반도체 사업 시너지 — 검사/계측 기술 스타트업, PoC 가능.", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "CVC: 당사 자동차 사업 시너지 — 배터리 리사이클링/진단 기술.", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-3", "text": "CVC: 당사 리테일 사업 시너지 — 리테일 AI(수요예측/가격최적화).", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    # UC-2
    {"uc": "UC-2", "text": "투자 검토 중인 타겟의 경쟁사 맵핑. B2B SaaS, 한국 시장, TAM/SAM 분석용.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "바이오 포트폴리오사 경쟁 분석. 동일 적응증(NASH) 파이프라인 기업 비교.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-2", "text": "핀테크 landscape — 한국 시장 카테고리별(결제/대출/보험/투자) 주요 플레이어.", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    # UC-5
    {"uc": "UC-5", "text": "한국 SaaS 시장 전체 맵핑. 카테고리별(HR/회계/CRM/마케팅/물류) ARR 기준.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-5", "text": "한국 바이오 스타트업 전체 맵핑. 적응증별/Stage별/투자 규모별.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-5", "text": "한국 모빌리티 스타트업 landscape. 자율주행/EV/충전/공유 카테고리별.", "sector": "자동차/부품", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-5", "text": "한국 에듀테크 시장 맵핑. K-12/직무교육/어학/코딩 카테고리별 주요 기업.", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "한국 클라이밋테크/그린테크 스타트업 전체 맵핑.", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
]

for q in vc_queries:
    q["id"] = make_id()
    q["source"] = "페르소나-VC"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(vc_queries)

# ===========================================================
# 페르소나 5: 회계법인/M&A자문사 (~80건)
# 화법: "의뢰:", "고객사", "롱리스트", "숏리스트", "DD", 객관적
# ===========================================================
advisor_queries = [
    # UC-1
    {"uc": "UC-1", "text": "의뢰: PE 고객사 — 매출 200~500억, 제조업(자동화설비), 비상장, 오너 매각 의향. 롱리스트 20사.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "의뢰: 대기업 고객사 — 식품 소재/원료 기업 인수 후보, 매출 100~500억, 기술 특허 보유.", "sector": "식품/F&B", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "의뢰: 중견기업 고객사 — 화장품 ODM 인수 대상, 매출 200~1,000억, 수출 비중 높은 곳.", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "의뢰: PE 고객사 — 의료기기(체외진단/영상) 바이아웃, EBITDA 30억+, CE/FDA.", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "의뢰: 해외 PE — 한국 IT서비스 기업 인수, 매출 500~2,000억, 영문 IM 작성 필요.", "sector": "IT/SaaS", "size": "중견기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "의뢰: 일본 기업 — 한국 반도체 소부장 지분 투자/인수, 기술 제휴 겸.", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "의뢰: 중동 SWF — 한국 에너지/인프라 투자, 딜사이즈 5,000억+.", "sector": "에너지/기후", "size": "준대기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "의뢰: 개인 고객사 — 매출 30~100억, 제조업, 수도권, 경영권 100%, 인수 후 직접 경영.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    # UC-4 (자문사 전문)
    {"uc": "UC-4", "text": "매도 자문 의뢰: 바이오 CDMO, 매출 500억, GMP 시설 2개. 전략적/재무적 매수자 숏리스트.", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-4", "text": "매도 자문 의뢰: 반도체 장비사, 매출 300억, 삼성/SK 납품. 해외 전략적 매수자 포함.", "sector": "반도체/소부장", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-4", "text": "매도 자문 의뢰: 게임 개발사, 매출 200억, 자체 IP 3개. 대형 퍼블리셔 매칭.", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-4", "text": "매도 자문 의뢰: 건설 장비 렌탈사, 매출 100억. 건설 대기업 또는 PE 매칭.", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-4", "text": "매도 자문 의뢰: 프랜차이즈 본사(외식), 가맹점 100개+. 대기업 또는 PE.", "sector": "식품/F&B", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-4", "text": "매도 자문 의뢰: 물류센터 운영사, 수도권 3개 거점. 인프라 펀드 매칭.", "sector": "유통/물류", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-4", "text": "매도 자문 의뢰: 보험 GA, 설계사 300명. 금융지주 또는 대형 GA 통합.", "sector": "금융/보험", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-4", "text": "매도 자문 의뢰: 교육 플랫폼, MAU 50만. 에듀테크 대기업 매칭.", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    # UC-2 (DD/밸류에이션 지원)
    {"uc": "UC-2", "text": "DD 지원: 타겟(식품 제조사) 동종 기업 재무 비교. 매출/EBITDA/마진/성장률 벤치마크.", "sector": "식품/F&B", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "밸류에이션: 타겟(IT서비스) Comparable Company 분석용 피어 그룹 선정.", "sector": "IT/SaaS", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "공정의견서: 타겟(제조업) 주식 가치 산정을 위한 유사 기업 거래 사례(Precedent).", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-2", "text": "시장분석: 타겟(화장품) 산업 내 경쟁 포지션, 시장점유율, 성장 전망.", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
    # UC-5
    {"uc": "UC-5", "text": "산업 리서치: 클라이언트 보고서용 국내 방산 시장 전체 플레이어/매출/수출 맵핑.", "sector": "방위산업", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-5", "text": "마켓 스터디: 국내 CDMO 시장 규모/성장률/경쟁 구도, PE 투자 보고서용.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-5", "text": "IM 작성용: 타겟 기업이 속한 산업(반도체 장비) 시장 맵핑, 경쟁 환경 분석.", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "딜 소싱: 국내 매출 100~500억, 오너 고령(60세+), 비상장 제조업 전수 조사.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Complex"},
]

for q in advisor_queries:
    q["id"] = make_id()
    q["source"] = "페르소나-자문사"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(advisor_queries)

# ===========================================================
# 페르소나 6: 오픈채팅방 화법 (~100건)
# 화법: 캐주얼, "~있나요?", "~구합니다", 약어, 이모지 없음
# ===========================================================
chat_queries = [
    # UC-1
    {"uc": "UC-1", "text": "수도권 제조업체 매물 있으면 연락주세요. 매출 50~200억, 흑자, 공장 포함.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "화장품 OEM/ODM 업체 매물 구합니다. 매출 300~1,000억, 수출 비중 높은 곳 선호.", "sector": "화장품/뷰티", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "식품 제조사 매물 있나요? 매출 100억+, HACCP, 대형마트 납품 실적. 바이아웃 희망.", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "반도체 장비/소재 회사 매물 찾습니다. 딜사이즈 500~2,000억. PE입니다.", "sector": "반도체/소부장", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "의료기기 회사 인수 관심. 매출 50~200억, CE인증, 수출 비중 30%+.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "IT서비스/SI 회사 매물 구합니다. 매출 100~500억, 공공 사업 비중 낮은 곳.", "sector": "IT/SaaS", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "물류회사 매물 있으면 알려주세요. 3PL, 수도권, 매출 100억+.", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-1", "text": "건기식 브랜드 매물 찾습니다. 온라인 매출 50억+, 자체 브랜드.", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-1", "text": "자동차 부품사 매물 구합니다. EV 관련, 매출 200~500억, 현대기아 납품.", "sector": "자동차/부품", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "에너지(태양광/풍력) 관련 회사 매물 있나요? 발전사업 허가 포함.", "sector": "에너지/기후", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "방산 부품사 매물 정보 구합니다. 매출 100억+, 방사청 납품 실적.", "sector": "방위산업", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "교육회사 매물 있으면 연결부탁드립니다. 법정의무교육 또는 온라인교육 플랫폼.", "sector": "교육", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-1", "text": "게임회사 인수 관심. 매출 100억+, 자체 IP, 모바일 위주.", "sector": "게임/콘텐츠", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-1", "text": "건설회사 매물 구합니다. 시공능력 100위권, 아파트/주거 실적.", "sector": "건설", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "철강/금속 가공업체 매물 있나요? 매출 50~200억, 자동차/전자 납품.", "sector": "철강/금속", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "캐피탈/리스회사 인수 관심. 자산 3,000억+, 건전성 양호.", "sector": "금융/보험", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "상속/승계 이슈로 급매 나오는 매물 있으면 알려주세요. 업종 무관, 흑자.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "카브아웃 매물 찾습니다. 대기업 비핵심 사업부, 매출 500억+.", "sector": "제조업(일반)", "size": "중견기업", "complexity": "Complex"},
    # UC-2
    {"uc": "UC-2", "text": "지금 검토 중인 식품회사랑 비슷한 규모 경쟁사 알려주세요. 매출 300~500억, HMR 위주.", "sector": "식품/F&B", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "화장품 ODM 업체 비교 자료 필요합니다. 코스맥스/콜마 제외 중소규모.", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "이 반도체 장비회사랑 비슷한 곳 어디 있나요? 세정장비 전문, 매출 100~300억.", "sector": "반도체/소부장", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "3PL 물류회사 비교해주세요. 이커머스 풀필먼트 특화, 수도권.", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    # UC-3
    {"uc": "UC-3", "text": "좋은 투자 딜 있으면 공유해주세요. 기업가치 300~1,000억, 제조업, 흑자.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Simple"},
    {"uc": "UC-3", "text": "코인베스트 기회 있나요? 바이아웃 딜, 딜사이즈 2,000억+, LP 직접투자 가능.", "sector": "제조업(일반)", "size": "중견기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "프리IPO 투자 기회 찾습니다. 2년 내 상장 계획, 기업가치 500~2,000억.", "sector": "IT/SaaS", "size": "중기업", "complexity": "Medium"},
    # UC-4
    {"uc": "UC-4", "text": "저희 회사 매각 고려 중입니다. 제조업, 매출 100억, 영업이익 15억. 어디에 매칭하면 좋을까요?", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-4", "text": "IT회사 매각합니다. 매출 50억, 직원 30명, 공공 SI 위주. 매수자 찾아주세요.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-4", "text": "식품 프랜차이즈 본사 매각 의향. 가맹점 80개, 매출 150억. 대기업 인수 선호.", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    # UC-5
    {"uc": "UC-5", "text": "요즘 M&A 시장에서 핫한 업종이 뭔가요? 딜 많이 나오는 섹터 알려주세요.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-5", "text": "K-뷰티 관련 회사 전체 리스트 있나요? ODM/브랜드/유통 포함.", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 바이오 CDMO 시장 플레이어 정리해주실 수 있나요? 매출/캐파 기준.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
]

for q in chat_queries:
    q["id"] = make_id()
    q["source"] = "페르소나-오픈채팅"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(chat_queries)

# ===========================================================
# 페르소나 7: 은행/금융기관 (~60건)
# 화법: "여신", "거래처", "재무안정성", "담보", 보수적 톤
# ===========================================================
bank_queries = [
    {"uc": "UC-2", "text": "여신 심사 참고용: 거래처(제조업, 매출 200억)와 동종 기업 재무 비교. 부채비율/유동비율/이자보상배율.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "거래처 산업 분석: 반도체 장비 업종 평균 영업이익률/부채비율 벤치마크.", "sector": "반도체/소부장", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "여신 심사: 거래처(식품, 매출 500억) 동종 기업 대비 재무 건전성 비교.", "sector": "식품/F&B", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "거래처 신용평가: 건설업 동종 기업 PF 노출도/부채비율 비교.", "sector": "건설", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-2", "text": "인수금융 심사: 타겟(유통업, 매출 1,000억) 피어 그룹 현금흐름 비교.", "sector": "유통/물류", "size": "중견기업", "complexity": "Complex"},
    {"uc": "UC-5", "text": "산업 리서치: IB 보고서용 국내 자동차 부품 산업 주요 기업 맵핑.", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "여신 포트폴리오 분석: 당행 건설업 여신 거래처 동종 기업 리스트.", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "PF 심사: 국내 물류센터 개발/운영 주요 기업 맵핑, 재무 현황.", "sector": "유통/물류", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "IPO 심사: 코스닥 상장 추진 바이오 기업 동종 기업 상장 사례 분석.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "은행 PI 투자: 기업가치 500~2,000억, 안정적 현금흐름, 제조/유통. 담보 가치 충분.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-3", "text": "인수금융 대상: EBITDA 100억+, 제조업, 담보 자산(공장/토지) 가치 LTV 50% 이하.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-1", "text": "은행 NPL 매각 대상 기업 중 정상화 가능한 곳. 자산 가치 > 부채, 제조업.", "sector": "제조업(일반)", "size": "소기업", "complexity": "Edge"},
]

for q in bank_queries:
    q["id"] = make_id()
    q["source"] = "페르소나-은행"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(bank_queries)

# ===========================================================
# 추가 균형 조정 (~70건, UC별 부족분 보충)
# ===========================================================
balance_queries = [
    # UC-5 추가 (가장 많이 필요)
    {"uc": "UC-5", "text": "국내 프리랜서/긱이코노미 플랫폼 전수 조사", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 명품/럭셔리 유통 기업 맵핑(백화점/온라인/면세점별)", "sector": "유통/물류", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 반도체 FAB 설비 시공/클린룸 전문사 맵핑", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 식품 첨가물(향료/색소/보존제) 제조사 전수 조사", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 의약품 도매/유통(종합의약품 도매상) 맵핑", "sector": "바이오/헬스케어", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 자동차 해체/재활용 업체 맵핑", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 도시가스 공급사 맵핑, 지역별", "sector": "에너지/기후", "size": "중기업", "complexity": "Simple"},
    {"uc": "UC-5", "text": "국내 상조(장례) 서비스 기업 맵핑", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-5", "text": "국내 해운/선박관리 기업 맵핑", "sector": "유통/물류", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 중고차 매매/경매 플랫폼 맵핑", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 AI 칩 설계(NPU/가속기) 기업 전수 조사", "sector": "반도체/소부장", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-5", "text": "국내 스마트 빌딩/빌딩 자동화(BAS) 기업 맵핑", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 식물성 화장품/비건 뷰티 브랜드 맵핑", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-5", "text": "국내 레이저 장비(산업용/의료용/반도체용) 기업 맵핑", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-5", "text": "국내 철도/도시철도 관련 기업(차량/신호/궤도) 맵핑", "sector": "제조업(일반)", "size": "중기업", "complexity": "Complex"},
    # UC-2 추가
    {"uc": "UC-2", "text": "국내 라면 제조사 비교(농심/삼양/오뚜기 외 중소)", "sector": "식품/F&B", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "국내 생수/미네랄워터 브랜드 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-2", "text": "국내 전자칠판/스마트보드 업체 비교(교육용)", "sector": "교육", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "국내 치약/칫솔 브랜드 비교", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-2", "text": "국내 도시락/급식 납품 업체 비교", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "국내 청소/위생 서비스 업체 비교(B2B)", "sector": "유통/물류", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-2", "text": "국내 실내 공기질 관리/환기 장비 업체 비교", "sector": "제조업(일반)", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "국내 전기차 충전 서비스 업체 비교(충전요금/네트워크)", "sector": "자동차/부품", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-2", "text": "국내 반려동물 보험 상품/업체 비교", "sector": "금융/보험", "size": "소기업", "complexity": "Simple"},
    {"uc": "UC-2", "text": "국내 인테리어 플랫폼(오늘의집 vs 집닥 등) 비교", "sector": "건설", "size": "소기업", "complexity": "Medium"},
    # UC-1 추가 (소규모 빈곳)
    {"uc": "UC-1", "text": "인허가 업종(폐기물/의약품/위험물) 기업 인수, 면허 가치 위주, 매출 무관.", "sector": "에너지/기후", "size": "소기업", "complexity": "Edge"},
    {"uc": "UC-1", "text": "대학교 앞 상가 건물 + 임대 사업 일괄 인수, 수도권 주요 대학가.", "sector": "건설", "size": "소기업", "complexity": "Edge"},
    {"uc": "UC-1", "text": "노인요양시설/요양병원 인수, 수도권, 100병상+, 건물 포함.", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "중고 명품 매입/판매 사업 인수, 온라인+오프라인, 월 거래액 3억+.", "sector": "유통/물류", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-1", "text": "축산 농장(양돈/양계) 인수, 사육두수 1만+, 계열화 업체.", "sector": "식품/F&B", "size": "소기업", "complexity": "Medium"},
    # UC-3 추가
    {"uc": "UC-3", "text": "NPL(부실채권) 전문 투자, 담보 부동산, 서울/수도권, 회수율 150%+ 기대.", "sector": "금융/보험", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "비상장 우량 기업 장외 주식 투자, 매출 500억+, 배당 수익 4%+.", "sector": "제조업(일반)", "size": "중기업", "complexity": "Medium"},
    {"uc": "UC-3", "text": "컨버터블 노트 투자, 초기 단계, AI/로봇, 밸류캡 50~100억.", "sector": "IT/SaaS", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-3", "text": "부동산 개발 PF 참여, 수도권 물류센터, 사전 임차 확보, 수익률 10%+.", "sector": "건설", "size": "중기업", "complexity": "Complex"},
    {"uc": "UC-3", "text": "재생에너지 프로젝트 투자, 태양광 100MW급, 장기 PPA 확보.", "sector": "에너지/기후", "size": "중기업", "complexity": "Complex"},
    # UC-4 추가
    {"uc": "UC-4", "text": "당사(화장품 제조) 매각 시 가장 높은 밸류에이션 받을 수 있는 매수자 유형?", "sector": "화장품/뷰티", "size": "소기업", "complexity": "Medium"},
    {"uc": "UC-4", "text": "바이오 스타트업 매각, 파이프라인 라이선싱 vs 회사 통째 매각, 어떤 매수자?", "sector": "바이오/헬스케어", "size": "소기업", "complexity": "Complex"},
    {"uc": "UC-4", "text": "은퇴 준비 중, 30년 운영한 공장 매각하려면 어떤 매수자가 적합?", "sector": "제조업(일반)", "size": "소기업", "complexity": "Simple"},
]

for q in balance_queries:
    q["id"] = make_id()
    q["source"] = "균형조정-최종"
    q["audit"] = audit_for_size(q["size"])
new_queries.extend(balance_queries)

# ===========================================================
# Round 2: 대량 보충 (~580건) — UC-2, UC-5 중심 + UC-1 감축 대신 UC-2/5 확대
# ===========================================================

# ---- UC-2 대량 보충 (~170건) ----
uc2_bulk = []
# 전 업종 세분화된 경쟁사 탐색
_uc2_items = [
    ("복사기/프린터 렌탈 업체 비교", "제조업(일반)", "소기업", "Simple"),
    ("소형 가전(믹서/에어프라이어) 브랜드 비교", "제조업(일반)", "소기업", "Simple"),
    ("건축용 페인트/도료 업체 비교", "제조업(일반)", "소기업", "Simple"),
    ("자동문/셔터 제조/시공 업체 비교", "제조업(일반)", "소기업", "Simple"),
    ("계량기/유량계 업체 비교", "제조업(일반)", "소기업", "Medium"),
    ("산업용 히터/보일러 업체 비교", "제조업(일반)", "소기업", "Medium"),
    ("용기(캔/유리병/PET) 제조사 비교, 음료/식품용", "제조업(일반)", "중기업", "Medium"),
    ("산업용 접착제/실란트 업체 비교", "제조업(일반)", "소기업", "Medium"),
    ("비닐/필름 제조사 비교, 포장재용", "제조업(일반)", "소기업", "Medium"),
    ("승강기/엘리베이터 업체 비교, 국산 vs 수입", "제조업(일반)", "중기업", "Medium"),
    ("식품 첨가물(유화제/증점제) 업체 비교", "식품/F&B", "소기업", "Medium"),
    ("소스/드레싱 전문 제조사 비교", "식품/F&B", "소기업", "Medium"),
    ("두부/콩나물 제조사 비교", "식품/F&B", "소기업", "Simple"),
    ("떡볶이/분식 프랜차이즈 비교", "식품/F&B", "소기업", "Simple"),
    ("영양제/비타민 브랜드 비교(국내산)", "식품/F&B", "소기업", "Medium"),
    ("전통주(막걸리/소주/청주) 제조사 비교", "식품/F&B", "소기업", "Medium"),
    ("유아식/이유식 배달 서비스 비교", "식품/F&B", "소기업", "Simple"),
    ("마스크팩/시트마스크 브랜드 비교", "화장품/뷰티", "소기업", "Simple"),
    ("한방 화장품 브랜드 비교", "화장품/뷰티", "소기업", "Medium"),
    ("클렌징/세안 제품 브랜드 비교", "화장품/뷰티", "소기업", "Simple"),
    ("향초/디퓨저/홈프래그런스 브랜드 비교", "화장품/뷰티", "소기업", "Simple"),
    ("택시 호출 앱/플랫폼 비교", "IT/SaaS", "소기업", "Simple"),
    ("음식 배달 플랫폼(배민/쿠팡이츠/요기요) 수수료 비교", "IT/SaaS", "중기업", "Simple"),
    ("인사/급여 관리 솔루션 비교(더존/삼성SDS 등)", "IT/SaaS", "소기업", "Medium"),
    ("비대면 본인확인(eKYC) 솔루션 업체 비교", "IT/SaaS", "소기업", "Medium"),
    ("로그 관리/모니터링 SaaS 비교", "IT/SaaS", "소기업", "Medium"),
    ("위치기반서비스(LBS) 솔루션 업체 비교", "IT/SaaS", "소기업", "Medium"),
    ("블루투스/WiFi 모듈 업체 비교", "반도체/소부장", "소기업", "Medium"),
    ("반도체 이온주입 장비 업체 비교", "반도체/소부장", "소기업", "Complex"),
    ("실리콘 웨이퍼 재생/폴리싱 업체 비교", "반도체/소부장", "소기업", "Medium"),
    ("보청기/청각 기기 업체 비교", "바이오/헬스케어", "소기업", "Medium"),
    ("약국 자동화(자동조제기) 장비 업체 비교", "바이오/헬스케어", "소기업", "Medium"),
    ("골밀도 측정/정형외과 기기 업체 비교", "바이오/헬스케어", "소기업", "Medium"),
    ("안과 진단/수술 장비 업체 비교", "바이오/헬스케어", "소기업", "Medium"),
    ("요양원/실버타운 운영사 비교", "바이오/헬스케어", "소기업", "Medium"),
    ("택배 앱/스마트 로커 서비스 비교", "유통/물류", "소기업", "Medium"),
    ("식품 원자재 도매(쌀/밀가루/설탕) 업체 비교", "유통/물류", "중기업", "Medium"),
    ("꽃 배달/구독 서비스 비교", "유통/물류", "소기업", "Simple"),
    ("사무용 가구/의자 브랜드 비교", "유통/물류", "소기업", "Simple"),
    ("전기차 충전소 운영사 비교, 충전요금/커버리지별", "에너지/기후", "소기업", "Medium"),
    ("태양광 패널 설치(가정용) 업체 비교", "에너지/기후", "소기업", "Simple"),
    ("산업폐수 처리 업체 비교", "에너지/기후", "소기업", "Medium"),
    ("탄소 크레딧 거래 플랫폼 비교", "에너지/기후", "소기업", "Medium"),
    ("자동차 PPF/틴팅 전문점 프랜차이즈 비교", "자동차/부품", "소기업", "Simple"),
    ("중고차 플랫폼(KCar/SK엔카/헤이딜러) 비교", "자동차/부품", "소기업", "Simple"),
    ("타이어/배터리 교체 서비스(오프라인) 비교", "자동차/부품", "소기업", "Simple"),
    ("온라인 자격증 교육 플랫폼 비교", "교육", "소기업", "Simple"),
    ("미술/음악 학원 프랜차이즈 비교", "교육", "소기업", "Simple"),
    ("외국어(일본어/중국어) 학원/앱 비교", "교육", "소기업", "Simple"),
    ("건축물 에너지 진단 업체 비교", "건설", "소기업", "Medium"),
    ("리모델링/인테리어 플랫폼 비교", "건설", "소기업", "Medium"),
    ("AR/VR 콘텐츠 제작사 비교", "게임/콘텐츠", "소기업", "Medium"),
    ("음원 유통(디지털 어그리게이터) 업체 비교", "게임/콘텐츠", "소기업", "Medium"),
    ("글로벌 진출한 K-웹소설 플랫폼 비교", "게임/콘텐츠", "소기업", "Medium"),
    ("크라우드 펀딩 플랫폼(와디즈/텀블벅 등) 비교", "금융/보험", "소기업", "Medium"),
    ("PG(전자결제) 대행사 수수료 비교", "금융/보험", "소기업", "Medium"),
    ("해외 송금 서비스(핀테크) 비교", "금융/보험", "소기업", "Medium"),
    ("국내 볼트/너트/패스너 전문 업체 비교", "철강/금속", "소기업", "Simple"),
    ("파이프/배관 자재(STS/PE) 업체 비교", "철강/금속", "소기업", "Medium"),
    ("방산 광학/야시 장비 업체 비교", "방위산업", "소기업", "Medium"),
    ("군용 피복/장구류 업체 비교", "방위산업", "소기업", "Simple"),
    # Complex/Edge
    ("자동차 부품 Tier 1 중 전장 전환 성공사 vs 실패사 비교", "자동차/부품", "중기업", "Complex"),
    ("식품 리콜 이력 있는 기업 vs 없는 기업, 주가/매출 영향 비교", "식품/F&B", "중기업", "Edge"),
    ("ESG 등급 A+ vs C 기업, 동일 업종 내 밸류에이션 갭 분석", "제조업(일반)", "중기업", "Edge"),
    ("코스닥 스팩 합병 성공 vs 실패 사례, 업종별 비교", "금융/보험", "소기업", "Edge"),
    ("대기업 출자 스타트업 vs 순수 스타트업, 동종 기업 성장률 비교", "IT/SaaS", "소기업", "Edge"),
]

for i, (text, sector, size, complexity) in enumerate(_uc2_items):
    uc2_bulk.append({
        "id": make_id(), "uc": "UC-2", "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "페르소나-대량보충",
        "audit": audit_for_size(size),
    })
new_queries.extend(uc2_bulk)

# ---- UC-5 대량 보충 (~170건) ----
uc5_bulk = []
_uc5_items = [
    ("국내 엘리베이터/에스컬레이터 유지보수 업체 맵핑", "건설", "소기업", "Medium"),
    ("국내 바이오매스/바이오에너지 기업 맵핑", "에너지/기후", "소기업", "Medium"),
    ("국내 수소차(FCEV) 부품 업체 맵핑", "자동차/부품", "소기업", "Medium"),
    ("국내 초전도체 관련 기업 맵핑", "반도체/소부장", "소기업", "Complex"),
    ("국내 로봇 수술 기업(다빈치 외) 맵핑", "바이오/헬스케어", "소기업", "Complex"),
    ("국내 보험사 자회사/계열사 전수 조사", "금융/보험", "중기업", "Medium"),
    ("국내 특수교육/장애인 교육 기업 맵핑", "교육", "소기업", "Medium"),
    ("국내 K-콘텐츠 해외 유통사 맵핑", "게임/콘텐츠", "소기업", "Medium"),
    ("국내 밸러스트워터 처리 장비 업체 맵핑", "에너지/기후", "소기업", "Medium"),
    ("국내 양식장/수산양식 기업 맵핑, 지역별", "식품/F&B", "소기업", "Medium"),
    ("국내 가스 터빈/엔진 부품 기업 맵핑", "제조업(일반)", "소기업", "Medium"),
    ("국내 의약품 패키징/포장재 기업 맵핑", "바이오/헬스케어", "소기업", "Medium"),
    ("국내 웨딩/브라이덜 관련 기업 맵핑", "유통/물류", "소기업", "Simple"),
    ("국내 영화관/극장 체인 맵핑", "게임/콘텐츠", "중기업", "Simple"),
    ("국내 렌터카/장기렌탈 업체 맵핑", "자동차/부품", "소기업", "Medium"),
    ("국내 보일러/난방 기기 제조사 맵핑", "제조업(일반)", "소기업", "Medium"),
    ("국내 산업용 로봇(다관절/SCARA/협동) 기업 맵핑", "제조업(일반)", "소기업", "Medium"),
    ("국내 바이오플라스틱/PLA 기업 맵핑", "에너지/기후", "소기업", "Medium"),
    ("국내 카시트/주니어 시트 브랜드 맵핑", "자동차/부품", "소기업", "Simple"),
    ("국내 원격진료/비대면 의료 서비스 맵핑", "바이오/헬스케어", "소기업", "Medium"),
    ("국내 고속도로 휴게소 운영 기업 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 컨테이너/모듈러 건축 기업 맵핑", "건설", "소기업", "Medium"),
    ("국내 전동 스쿠터/이륜차 업체 맵핑", "자동차/부품", "소기업", "Medium"),
    ("국내 미세먼지/공기 관련 기업(측정/정화) 맵핑", "에너지/기후", "소기업", "Medium"),
    ("국내 영양주사/수액클리닉 체인 맵핑", "바이오/헬스케어", "소기업", "Simple"),
    ("국내 캠핑카/모터홈 제조/렌탈 업체 맵핑", "자동차/부품", "소기업", "Simple"),
    ("국내 떡/한과/전통 디저트 전문점 맵핑", "식품/F&B", "소상공인", "Simple"),
    ("국내 AI 음성/대화 스타트업 맵핑", "IT/SaaS", "소기업", "Medium"),
    ("국내 마케팅 에이전시 맵핑(디지털/퍼포먼스)", "IT/SaaS", "소기업", "Medium"),
    ("국내 번역/통역 서비스 기업 맵핑", "IT/SaaS", "소기업", "Simple"),
    ("국내 자동차 경매/도매 기업 맵핑", "자동차/부품", "소기업", "Medium"),
    ("국내 산업용 드론 서비스(농업/측량/배송) 맵핑", "제조업(일반)", "소기업", "Medium"),
    ("국내 공유 주방/공유 부엌 운영사 맵핑", "식품/F&B", "소상공인", "Simple"),
    ("국내 네일/뷰티 프랜차이즈 맵핑", "화장품/뷰티", "소기업", "Simple"),
    ("국내 중고 의류/빈티지 매장 맵핑", "유통/물류", "소기업", "Simple"),
    ("국내 벌크/화물 선사 맵핑", "유통/물류", "중기업", "Medium"),
    ("국내 반려동물 장묘/화장 서비스 맵핑", "유통/물류", "소상공인", "Simple"),
    ("국내 스마트 홈/IoT 기업 맵핑", "IT/SaaS", "소기업", "Medium"),
    ("국내 캡슐/정제 위탁생산(CMO) 기업 맵핑", "바이오/헬스케어", "소기업", "Medium"),
    ("국내 기상/날씨 관련 기술 기업 맵핑", "IT/SaaS", "소기업", "Medium"),
    ("국내 화재 감지/소방 설비 기업 맵핑", "건설", "소기업", "Medium"),
    ("국내 노인 돌봄/방문 요양 기업 맵핑", "바이오/헬스케어", "소기업", "Medium"),
    ("국내 전기 자전거 제조/유통 맵핑", "자동차/부품", "소기업", "Simple"),
    ("국내 사진/영상 장비 렌탈 기업 맵핑", "게임/콘텐츠", "소기업", "Simple"),
    ("국내 세무/회계 법인 맵핑(4대 법인 외)", "금융/보험", "소기업", "Simple"),
    ("국내 학생 유니폼/교복 업체 맵핑", "제조업(일반)", "소기업", "Simple"),
    ("국내 피부 관리 전문(에스테틱) 체인 맵핑", "화장품/뷰티", "소기업", "Medium"),
    ("국내 산업가스(질소/산소/아르곤) 기업 맵핑", "제조업(일반)", "중기업", "Medium"),
    ("국내 전기/전자 폐기물 재활용 기업 맵핑", "에너지/기후", "소기업", "Medium"),
    ("국내 축제/이벤트 기획사 맵핑", "게임/콘텐츠", "소기업", "Simple"),
    ("국내 창업 보육(인큐베이터/액셀러레이터) 맵핑", "금융/보험", "소기업", "Medium"),
    ("국내 실험동물/실험 기자재 기업 맵핑", "바이오/헬스케어", "소기업", "Medium"),
    ("국내 과수원/과일 농장 법인 맵핑, 매출 10억+", "식품/F&B", "소기업", "Simple"),
    ("국내 소프트웨어 테스트(QA) 전문 기업 맵핑", "IT/SaaS", "소기업", "Medium"),
    ("국내 디지털 간판(디지털 사이니지) 기업 맵핑", "IT/SaaS", "소기업", "Medium"),
    ("국내 전기차 폐배터리 진단/등급분류 기업 맵핑", "에너지/기후", "소기업", "Medium"),
    ("국내 전력선 지중화/전선 공사 기업 맵핑", "건설", "소기업", "Medium"),
    ("국내 피클볼/스쿼시 등 신규 스포츠 시설 맵핑", "게임/콘텐츠", "소상공인", "Simple"),
    ("국내 에어컨/냉방 설비 업체 맵핑", "제조업(일반)", "소기업", "Simple"),
    ("국내 수중/해저 작업(잠수) 전문 기업 맵핑", "건설", "소기업", "Medium"),
    ("국내 펫시터/반려동물 돌봄 플랫폼 맵핑", "IT/SaaS", "소기업", "Simple"),
    ("국내 중고 산업기계/장비 거래 플랫폼 맵핑", "제조업(일반)", "소기업", "Medium"),
    ("국내 대체 투자(미술품/와인/운동화) 플랫폼 맵핑", "금융/보험", "소기업", "Medium"),
    ("국내 스마트 팜 장비(센서/제어/양액) 기업 맵핑", "제조업(일반)", "소기업", "Medium"),
    ("국내 장애인 보조기기 제조/유통 기업 맵핑", "바이오/헬스케어", "소기업", "Medium"),
    ("국내 고무/타이어 재활용 기업 맵핑", "에너지/기후", "소기업", "Medium"),
]

for i, (text, sector, size, complexity) in enumerate(_uc5_items):
    uc5_bulk.append({
        "id": make_id(), "uc": "UC-5", "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "페르소나-대량보충",
        "audit": audit_for_size(size),
    })
new_queries.extend(uc5_bulk)

# ---- UC-1 페르소나 다양화 (~100건) ----
uc1_persona_diverse = []
_uc1_items = [
    # 개인매수자 톤
    ("중국집/짜장면 프랜차이즈 인수, 서울, 월 매출 3천만+", "식품/F&B", "소상공인", "Simple"),
    ("세무사 사무소 인수, 고정 고객 100건+, 서울 강남", "금융/보험", "소상공인", "Simple"),
    ("스크린 골프장 인수, 수도권, 월 매출 2천만+", "게임/콘텐츠", "소상공인", "Simple"),
    ("유기농 농장+직판장 인수, 경기 근교", "식품/F&B", "소상공인", "Simple"),
    ("그릴/바베큐 레스토랑 인수, 서울, 인스타 인기", "식품/F&B", "소상공인", "Simple"),
    ("코인 빨래방 10개 일괄 인수, 서울/경기", "유통/물류", "소기업", "Simple"),
    ("자동차 정비소 인수, 인증 정비, 월 매출 3천만+", "자동차/부품", "소상공인", "Simple"),
    ("키즈 수영장/수영 교실 인수, 수도권", "교육", "소상공인", "Simple"),
    ("반려동물 용품 온라인몰 인수, 월 매출 5천만+", "유통/물류", "소기업", "Medium"),
    ("빵집(베이커리카페) 인수, 강남/판교, 일 매출 100만+", "식품/F&B", "소상공인", "Simple"),
    # PE 톤
    ("EBITDA 200~500억, 화학/소재, 고객 집중도 낮은(상위 20% 미만) 기업. 바이아웃.", "제조업(일반)", "중견기업", "Complex"),
    ("EBITDA 50~150억, 포장재, 식품/반도체 이중 고객. 경기방어적.", "제조업(일반)", "중기업", "Complex"),
    ("FCF 안정적, 네트워크 효과 있는 플랫폼 비즈니스, 기업가치 1,000~5,000억", "IT/SaaS", "중기업", "Complex"),
    ("Roll-up 전략: 건축 설비 시공사 다수 인수 통합, 1호 대상 EBITDA 20억+", "건설", "소기업", "Complex"),
    ("Carve-out: 대기업 비핵심 사업부 중 독립 운영 가능, EBITDA 100억+", "제조업(일반)", "준대기업", "Complex"),
    # 전략적매수자 톤
    ("당사 수출 채널 활용 가능한 K-뷰티 브랜드, 일본/동남아 인지도", "화장품/뷰티", "소기업", "Medium"),
    ("당사 기존 고객(병원) 대상 크로스셀 가능한 의료 소모품 업체", "바이오/헬스케어", "소기업", "Medium"),
    ("당사 배송 네트워크 활용 가능한 라스트마일 물류 기술 기업", "유통/물류", "소기업", "Medium"),
    ("당사 공장 유휴 라인 활용 가능한 위탁생산(CMO) 고객사 보유 기업", "제조업(일반)", "소기업", "Medium"),
    ("당사 IP(캐릭터) 활용 가능한 굿즈/MD 기획사", "게임/콘텐츠", "소기업", "Medium"),
    # 자문사 톤
    ("의뢰: 해외 PE — 한국 방산 부품사, 수출형, 딜사이즈 2,000~5,000억. 숏리스트 10사.", "방위산업", "중기업", "Complex"),
    ("의뢰: 일본 종합상사 — 한국 식품 원료(아미노산/발효) 기업 인수, 기술 확보 목적.", "식품/F&B", "소기업", "Complex"),
    ("의뢰: 싱가포르 PE — 한국 교육 플랫폼, 매출 100~500억, 아시아 확장 잠재력.", "교육", "중기업", "Complex"),
    ("의뢰: 독일 화학기업 — 한국 특수 화학/코팅 업체, 기술 제휴 겸 인수.", "제조업(일반)", "소기업", "Complex"),
    # 오픈채팅 톤
    ("ESG 관련 컨설팅 회사 매물 있나요? 매출 30억+", "IT/SaaS", "소기업", "Simple"),
    ("인테리어 시공 업체 매물 구합니다. 서울, 매출 50억+, 시공팀 보유.", "건설", "소기업", "Simple"),
    ("헬스장/피트니스 매물 정보 부탁합니다. 서울 강남, 회원 1,000명+.", "유통/물류", "소기업", "Simple"),
    ("약국 인수 관심. 서울 역세권, 처방전 일 100건+.", "바이오/헬스케어", "소상공인", "Simple"),
    ("치킨/피자 프랜차이즈 다점포(3개+) 인수 원합니다.", "식품/F&B", "소상공인", "Simple"),
    ("PC방 인수 관심. 서울/경기, 좌석 80석+, 월 매출 2천만+.", "게임/콘텐츠", "소상공인", "Simple"),
]

for i, (text, sector, size, complexity) in enumerate(_uc1_items):
    uc1_persona_diverse.append({
        "id": make_id(), "uc": "UC-1", "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "페르소나-UC1다양화",
        "audit": audit_for_size(size),
    })
new_queries.extend(uc1_persona_diverse)

# ---- UC-3 보충 (~55건) ----
uc3_bulk = []
_uc3_items = [
    ("K-팝 엔터 기획사 투자, 시리즈A, 소속 아티스트 팬덤 확보", "게임/콘텐츠", "소기업", "Medium"),
    ("위성 통신/지상국 장비 스타트업, Seed~A, 정부 과제", "방위산업", "소기업", "Complex"),
    ("반려동물 헬스케어(진단키트/보험) 투자", "바이오/헬스케어", "소기업", "Medium"),
    ("전기차 충전 인프라 운영, 시리즈B, 충전기 1,000기+", "에너지/기후", "소기업", "Medium"),
    ("양자암호통신 기업, Seed, 정부 과제 수주, 기술 특허", "IT/SaaS", "소기업", "Complex"),
    ("마이크로바이옴 식품(프로바이오틱스), 매출 20억+", "식품/F&B", "소기업", "Medium"),
    ("3D 프린팅 금속/세라믹, 항공/의료 적용, 시리즈A", "제조업(일반)", "소기업", "Complex"),
    ("레그테크(규제준수 자동화) SaaS, ARR 10억+, 금융권 고객", "IT/SaaS", "소기업", "Medium"),
    ("산업 메타버스(디지털트윈) 플랫폼, 매출 30억+", "IT/SaaS", "소기업", "Medium"),
    ("식물공장/수직농업, 매출 10억+, 기술 특허, 글로벌 확장", "식품/F&B", "소기업", "Complex"),
    ("배터리 진단(BMS/SOH) 기술 스타트업, EV/ESS 적용", "에너지/기후", "소기업", "Complex"),
    ("국내 신약 개발(First-in-class), 파이프라인 Phase 1, 글로벌 라이선싱 가능", "바이오/헬스케어", "소기업", "Complex"),
    ("건설 안전 AI(CCTV 분석/IoT 센서), 매출 10억+", "건설", "소기업", "Medium"),
    ("K-뷰티 성분 기술(펩타이드/레티놀) 스타트업, 특허 보유", "화장품/뷰티", "소기업", "Complex"),
    ("에너지 하베스팅(진동/열/광) 기술, IoT 적용, 시리즈A", "에너지/기후", "소기업", "Complex"),
    ("자동차 사이버보안 솔루션, UNECE 인증, OEM 납품", "자동차/부품", "소기업", "Complex"),
    ("그린수소 생산(수전해) 기업, 파일럿 단계, 정부 지원", "에너지/기후", "소기업", "Complex"),
    ("시니어 케어테크(돌봄 로봇/AI 모니터링), 매출 5억+", "바이오/헬스케어", "소기업", "Medium"),
    ("식품 트레이서빌리티(블록체인/IoT) 솔루션, B2B", "IT/SaaS", "소기업", "Medium"),
    ("비건 패션/지속가능 패션 브랜드, 매출 20억+, D2C", "유통/물류", "소기업", "Medium"),
    # 소상공인/대규모
    ("동네 세탁소 여러 개 사서 체인화, 인수가 개당 3천만원대", "유통/물류", "소상공인", "Simple"),
    ("무인매장(아이스크림/편의점) 10개 일괄 투자, 인수가 2~3억", "유통/물류", "소상공인", "Simple"),
    ("중견 제약사 PEF 투자, 기업가치 3,000~1조, 제네릭→바이오 전환", "바이오/헬스케어", "중견기업", "Complex"),
    ("대형 데이터센터 인프라 투자, 준공 후 리츠 편입, 수익률 8%+", "건설", "대기업", "Complex"),
    ("비상장 중견 제조사, 코스닥 상장 2년 내, Pre-IPO 투자", "제조업(일반)", "중견기업", "Medium"),
]

for i, (text, sector, size, complexity) in enumerate(_uc3_items):
    uc3_bulk.append({
        "id": make_id(), "uc": "UC-3", "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "페르소나-UC3보충",
        "audit": audit_for_size(size),
    })
new_queries.extend(uc3_bulk)

# ---- UC-4 보충 (~25건) ----
uc4_bulk = []
_uc4_items = [
    ("약국 체인 매도 — 대형 약국 체인 또는 유통사 매칭", "바이오/헬스케어", "소기업", "Medium"),
    ("코스닥 바이오 기업 경영권 양도 — 적합한 PE 또는 전략적 매수자", "바이오/헬스케어", "중기업", "Complex"),
    ("여행사 매도 — OTA(온라인여행사) 또는 대형 여행사 매칭", "유통/물류", "소기업", "Simple"),
    ("인쇄 회사 매도 — 디지털 인쇄 기업 또는 마케팅 기업 매칭", "제조업(일반)", "소기업", "Simple"),
    ("네일샵 프랜차이즈 본사 매도 — 뷰티 대기업 또는 프랜차이즈 전문 PE", "화장품/뷰티", "소기업", "Medium"),
    ("태양광 발전소 매도(20MW) — 인프라 펀드 또는 에너지 대기업", "에너지/기후", "소기업", "Medium"),
    ("코딩 교육 스타트업 매도 — 에듀테크 대기업 매칭", "교육", "소기업", "Medium"),
    ("PC방 다점포 매도 — 게임 관련 기업 또는 개인 투자자", "게임/콘텐츠", "소기업", "Simple"),
    ("철강 도매상 매도 — 대형 유통사 또는 철강 제조사 매칭", "철강/금속", "소기업", "Medium"),
    ("물류 창고(수도권) 매도 — 리츠/인프라 펀드 또는 이커머스 기업", "유통/물류", "소기업", "Medium"),
    ("헬스장/피트니스 매도 — 프랜차이즈 본사 또는 부동산 투자자", "유통/물류", "소기업", "Simple"),
    ("중고차 딜러십(다점포) 매도 — 중고차 플랫폼 또는 자동차 딜러 그룹", "자동차/부품", "소기업", "Medium"),
    ("자문사 의뢰: 반도체 소재사 매도, 매출 200억, 해외 매수자 우선", "반도체/소부장", "소기업", "Complex"),
    ("자문사 의뢰: 게임 개발사 매도, 자체 IP 5개, 글로벌 퍼블리셔 매칭", "게임/콘텐츠", "소기업", "Medium"),
    ("PE 엑시트: 포트코(식품 제조) 매각, 보유 5년, 세컨더리 바이아웃 또는 전략적", "식품/F&B", "중기업", "Complex"),
    ("창업자 은퇴: 30년 운영 제조업체, 기술 인력 잔류 조건, 적합한 매수자 유형", "제조업(일반)", "소기업", "Medium"),
    ("이혼 분쟁: 공동 명의 레스토랑 매도, 빠른 매각 가능 매수자", "식품/F&B", "소상공인", "Edge"),
    ("워크아웃 졸업 기업: 정상화 완료, 신규 투자자/매수자 매칭", "제조업(일반)", "소기업", "Edge"),
    ("스타트업 시리즈C 기업: 기존 주주 지분 매각(세컨더리), 적합 매수자", "IT/SaaS", "소기업", "Medium"),
    ("대기업 자회사 MBO: 경영진이 매수 주체, 인수금융 파트너 매칭", "제조업(일반)", "중기업", "Complex"),
]

for i, (text, sector, size, complexity) in enumerate(_uc4_items):
    uc4_bulk.append({
        "id": make_id(), "uc": "UC-4", "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "페르소나-UC4보충",
        "audit": audit_for_size(size),
    })
new_queries.extend(uc4_bulk)

# ===========================================================
# Round 3: 최종 보충 (~375건) — 2,000건 달성
# ===========================================================

# UC-2 최종 보충 (~100건)
_uc2_final = [
    ("국내 냉동 피자/냉동 식품 브랜드 비교", "식품/F&B", "소기업", "Simple"),
    ("국내 참치캔/통조림 브랜드 비교", "식품/F&B", "소기업", "Simple"),
    ("국내 유아복/아동복 브랜드 비교", "유통/물류", "소기업", "Simple"),
    ("국내 스낵/과자 브랜드(중소) 비교", "식품/F&B", "소기업", "Simple"),
    ("국내 두유/식물성 음료 브랜드 비교", "식품/F&B", "소기업", "Simple"),
    ("국내 다이어트 식품/쉐이크 브랜드 비교", "식품/F&B", "소기업", "Simple"),
    ("국내 반창고/1회용 의료소모품 업체 비교", "바이오/헬스케어", "소기업", "Simple"),
    ("국내 혈압계/체온계 브랜드 비교", "바이오/헬스케어", "소기업", "Simple"),
    ("국내 치실/구강관리 용품 업체 비교", "바이오/헬스케어", "소기업", "Simple"),
    ("국내 매트리스/침구 브랜드 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 운동화/스포츠 신발 브랜드(국산) 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 캐리어/여행가방 브랜드 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 공기청정기 브랜드 비교(LG/삼성 외 중소)", "제조업(일반)", "소기업", "Medium"),
    ("국내 로봇 청소기 브랜드 비교", "제조업(일반)", "소기업", "Medium"),
    ("국내 식기세척기 브랜드 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 비데 업체 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 정수기 업체 비교(코웨이/청호 등)", "제조업(일반)", "중기업", "Medium"),
    ("국내 에어컨/냉방 가전 비교", "제조업(일반)", "중기업", "Medium"),
    ("국내 건조기 브랜드 비교", "제조업(일반)", "중기업", "Simple"),
    ("국내 전기레인지/인덕션 브랜드 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 연수기/수처리 가전 비교", "제조업(일반)", "소기업", "Medium"),
    ("국내 블랙박스/대시캠 브랜드 비교", "자동차/부품", "소기업", "Simple"),
    ("국내 내비게이션/차량 인포테인먼트 비교", "자동차/부품", "소기업", "Medium"),
    ("국내 보조배터리/충전기 브랜드 비교", "반도체/소부장", "소기업", "Simple"),
    ("국내 이어폰/헤드폰 브랜드(국산) 비교", "반도체/소부장", "소기업", "Simple"),
    ("국내 스마트워치/밴드 브랜드 비교", "IT/SaaS", "소기업", "Simple"),
    ("국내 선풍기/공기순환기 브랜드 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 제습기 브랜드 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 홈 CCTV/스마트 도어락 비교", "IT/SaaS", "소기업", "Medium"),
    ("국내 스마트팜 솔루션 비교", "제조업(일반)", "소기업", "Medium"),
    ("국내 프로젝터(가정용) 브랜드 비교", "반도체/소부장", "소기업", "Simple"),
    ("국내 노트북/태블릿(국산) 브랜드 비교", "반도체/소부장", "중기업", "Medium"),
    ("국내 아웃도어/등산 브랜드 비교", "유통/물류", "소기업", "Medium"),
    ("국내 수면 보조(베개/매트리스토퍼) 브랜드 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 홈트레이닝 기구(러닝머신/자전거) 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 캐주얼 의류 브랜드(SPA) 비교", "유통/물류", "소기업", "Medium"),
    ("국내 신선식품 새벽배송 vs 로켓프레시 vs 마켓컬리 비교", "유통/물류", "중기업", "Medium"),
    ("국내 구독 커머스(정기배송) 서비스 비교", "유통/물류", "소기업", "Medium"),
    ("국내 중고 전자제품 거래 플랫폼 비교", "유통/물류", "소기업", "Simple"),
    ("국내 셀프인테리어/DIY 자재 플랫폼 비교", "건설", "소기업", "Medium"),
    ("국내 화환/꽃 배달 서비스 비교", "유통/물류", "소기업", "Simple"),
    ("국내 세차용품 브랜드 비교", "자동차/부품", "소기업", "Simple"),
    ("국내 전동 킥보드 서비스(빔/라임/킥고잉 등) 비교", "자동차/부품", "소기업", "Simple"),
    ("국내 주차관제/주차앱 업체 비교", "IT/SaaS", "소기업", "Medium"),
    ("국내 반려동물 사료(건식/습식) 브랜드 비교", "식품/F&B", "소기업", "Medium"),
    ("국내 반려동물 간식 브랜드 비교", "식품/F&B", "소기업", "Simple"),
    ("국내 가습기 브랜드 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 다리미/의류관리기 브랜드 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 식기/도자기(한식기) 업체 비교", "제조업(일반)", "소기업", "Simple"),
    ("국내 화훼/원예 자재 업체 비교", "유통/물류", "소기업", "Simple"),
    # Complex/Edge
    ("코로나 이후 비대면 서비스 기업 중 성장 지속 vs 회귀 기업 비교", "IT/SaaS", "소기업", "Edge"),
    ("해외 직구 플랫폼 vs 국내 이커머스, 카테고리별 경쟁 분석", "유통/물류", "소기업", "Complex"),
    ("가맹점 만족도 기준 프랜차이즈 비교(공정위 정보공개서 활용)", "식품/F&B", "소기업", "Complex"),
    ("특허 출원 건수 기준 바이오텍 경쟁력 비교", "바이오/헬스케어", "소기업", "Complex"),
    ("정부 R&D 수주 기준 IT 기업 비교", "IT/SaaS", "소기업", "Complex"),
]

for text, sector, size, complexity in _uc2_final:
    new_queries.append({
        "id": make_id(), "uc": "UC-2", "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "최종보충-UC2",
        "audit": audit_for_size(size),
    })

# UC-5 최종 보충 (~100건)
_uc5_final = [
    ("국내 빨래방/세탁편의점 프랜차이즈 전수 맵핑", "유통/물류", "소상공인", "Simple"),
    ("국내 떡집/한과 전문점 맵핑", "식품/F&B", "소상공인", "Simple"),
    ("국내 주스/스무디 전문점 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 요가/명상 앱 맵핑", "IT/SaaS", "소기업", "Simple"),
    ("국내 가정용 태양광 설치 업체 맵핑", "에너지/기후", "소기업", "Simple"),
    ("국내 중고 명품 온라인 플랫폼 맵핑", "유통/물류", "소기업", "Simple"),
    ("국내 사진 인화/포토북 서비스 맵핑", "게임/콘텐츠", "소기업", "Simple"),
    ("국내 이삿짐 보관/미니창고 맵핑", "유통/물류", "소기업", "Simple"),
    ("국내 소주/맥주 크래프트 양조장 맵핑", "식품/F&B", "소기업", "Medium"),
    ("국내 토스트/샌드위치 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 셀프빨래방(무인) 프랜차이즈 맵핑", "유통/물류", "소상공인", "Simple"),
    ("국내 반려동물 미용(그루밍) 프랜차이즈 맵핑", "유통/물류", "소상공인", "Simple"),
    ("국내 횟집/초밥 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 중식/짜장면 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 족발/보쌈 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 이탈리안/파스타 레스토랑 체인 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 뷔페/한정식 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 꼬치/이자카야 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 마라탕/훠궈 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 타코야키/일본 간식 프랜차이즈 맵핑", "식품/F&B", "소상공인", "Simple"),
    ("국내 삼겹살/고기 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 국밥/설렁탕 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 찜닭/닭볶음탕 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 칼국수/수제비 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 떡볶이 전문 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 샐러드/건강식 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 아사이볼/포케 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 타피오카/버블티 프랜차이즈 맵핑", "식품/F&B", "소기업", "Simple"),
    ("국내 한약재/한약 도매상 맵핑", "바이오/헬스케어", "소기업", "Medium"),
    ("국내 한의원 체인/프랜차이즈 맵핑", "바이오/헬스케어", "소기업", "Medium"),
    ("국내 성형외과 체인/네트워크 맵핑", "바이오/헬스케어", "소기업", "Medium"),
    ("국내 피부과 체인/프랜차이즈 맵핑", "바이오/헬스케어", "소기업", "Medium"),
    ("국내 안경/렌즈 프랜차이즈 맵핑", "바이오/헬스케어", "소기업", "Simple"),
    ("국내 스포츠 용품(골프/테니스/배드민턴) 전문점 맵핑", "유통/물류", "소기업", "Simple"),
    ("국내 악기(피아노/기타) 판매/렌탈 맵핑", "유통/물류", "소기업", "Simple"),
    ("국내 서점(독립서점 포함) 맵핑", "유통/물류", "소기업", "Simple"),
    ("국내 문구/사무용품 유통 맵핑", "유통/물류", "소기업", "Simple"),
    ("국내 피트니스 장비(상업용) 유통 맵핑", "제조업(일반)", "소기업", "Medium"),
    ("국내 미용기기(에스테틱/가정용) 유통 맵핑", "화장품/뷰티", "소기업", "Medium"),
    ("국내 기능성 원단/스포츠 원단 업체 맵핑", "제조업(일반)", "소기업", "Medium"),
    ("국내 목재/합판 유통 맵핑", "제조업(일반)", "소기업", "Medium"),
    ("국내 석재/대리석 가공 맵핑", "건설", "소기업", "Simple"),
    ("국내 간판/사인물 제작 업체 맵핑", "제조업(일반)", "소기업", "Simple"),
    ("국내 렌탈(정수기/안마의자/공기청정기) 시장 맵핑", "제조업(일반)", "중기업", "Medium"),
    ("국내 보안(경비/시설경비) 업체 맵핑", "유통/물류", "소기업", "Medium"),
    ("국내 방역/소독 서비스 업체 맵핑", "유통/물류", "소기업", "Simple"),
    ("국내 택배/특송 업체(우체국/CJ 외) 맵핑", "유통/물류", "소기업", "Medium"),
    ("국내 이사/포장이사 업체 맵핑", "유통/물류", "소기업", "Simple"),
    ("국내 화물 운송 플랫폼 맵핑", "유통/물류", "소기업", "Medium"),
    ("국내 자동차 폐차장/고철 처리 맵핑", "에너지/기후", "소기업", "Simple"),
    ("국내 고물상/재활용 수집 업체 맵핑", "에너지/기후", "소기업", "Simple"),
    ("국내 소방 설비(스프링클러/소화기) 제조사 맵핑", "건설", "소기업", "Medium"),
    ("국내 엘리베이터/에스컬레이터 제조사 맵핑", "제조업(일반)", "중기업", "Medium"),
    ("국내 산업용 가구(실험실/병원/학교) 제조 맵핑", "제조업(일반)", "소기업", "Medium"),
    ("국내 유니폼/작업복 제조 맵핑", "제조업(일반)", "소기업", "Simple"),
    ("국내 주방기구/조리도구 업체 맵핑", "제조업(일반)", "소기업", "Simple"),
    ("국내 카펫/바닥재 업체 맵핑", "건설", "소기업", "Simple"),
    ("국내 방충망/방범창 업체 맵핑", "건설", "소기업", "Simple"),
    ("국내 기부/CSR 플랫폼 맵핑", "IT/SaaS", "소기업", "Simple"),
    ("국내 임대관리/프롭테크(부동산 관리) 맵핑", "IT/SaaS", "소기업", "Medium"),
    # Complex
    ("국내 DARPA 스타일 방산 R&D 프로그램 참여 기업 맵핑", "방위산업", "소기업", "Complex"),
    ("국내 mRNA 기술 보유 기업 전수 조사(코로나 이후)", "바이오/헬스케어", "소기업", "Complex"),
    ("국내 차세대 디스플레이(마이크로LED/투명디스플레이) 기업 맵핑", "반도체/소부장", "소기업", "Complex"),
    ("국내 6G 통신 관련 기업 맵핑(연구 단계 포함)", "IT/SaaS", "소기업", "Complex"),
    ("국내 합성 데이터/생성AI 인프라 기업 맵핑", "IT/SaaS", "소기업", "Complex"),
]

for text, sector, size, complexity in _uc5_final:
    new_queries.append({
        "id": make_id(), "uc": "UC-5", "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "최종보충-UC5",
        "audit": audit_for_size(size),
    })

# UC-1 최종 보충 (~100건 — 개인매수자+오픈채팅 톤 위주)
_uc1_final = [
    ("떡볶이 프랜차이즈 인수, 가맹점 20개+, 매출 30억+", "식품/F&B", "소기업", "Simple"),
    ("양꼬치 전문점 인수, 서울 대학가, 월 매출 2천만+", "식품/F&B", "소상공인", "Simple"),
    ("횟집/초밥 가게 인수, 역세권, 월 매출 5천만+", "식품/F&B", "소상공인", "Simple"),
    ("고깃집(삼겹살) 인수, 서울, 일 매출 100만+", "식품/F&B", "소상공인", "Simple"),
    ("와인바/칵테일바 인수, 강남/이태원", "식품/F&B", "소상공인", "Simple"),
    ("수영장/수영 교실 인수, 수도권, 회원 500명+", "교육", "소기업", "Medium"),
    ("태권도장 인수, 수도권, 관원 200명+", "교육", "소상공인", "Simple"),
    ("영어유치원/어린이집 인수, 강남/분당, 원아 50명+", "교육", "소기업", "Medium"),
    ("꽃 도매시장 점포 인수, 양재/남대문", "유통/물류", "소상공인", "Simple"),
    ("과일 도매 사업 인수, 가락시장/농협 경로", "식품/F&B", "소상공인", "Simple"),
    ("인테리어 업체 인수, 수도권, 매출 10~30억, 시공팀 보유", "건설", "소기업", "Medium"),
    ("세무사 사무실 인수(또는 인계), 고객 200건+", "금융/보험", "소상공인", "Simple"),
    ("부동산 중개 법인 인수, 서울, 매출 5억+", "금융/보험", "소상공인", "Simple"),
    ("스크린골프장 인수, 수도권, 타석 30개+", "게임/콘텐츠", "소상공인", "Simple"),
    ("노래방 인수, 서울 역세권, 50룸+", "게임/콘텐츠", "소상공인", "Simple"),
    ("당구장 인수, 서울/경기, 30대+", "게임/콘텐츠", "소상공인", "Simple"),
    ("찜질방/사우나 인수, 수도권, 면적 1,000평+", "유통/물류", "소기업", "Medium"),
    ("세차장(자동+수동) 인수, 수도권, 토지 포함", "자동차/부품", "소상공인", "Simple"),
    ("렌터카 영업소 인수, 제주/수도권, 차량 50대+", "자동차/부품", "소기업", "Medium"),
    ("네일/속눈썹 샵 인수, 강남/홍대", "화장품/뷰티", "소상공인", "Simple"),
    # PE/전략적 톤
    ("EBITDA 30~100억, 건기식/프로바이오틱스, 브랜드력 있는 곳. 인수 후 해외 확장.", "식품/F&B", "소기업", "Complex"),
    ("EBITDA 100~300억, 물류/풀필먼트, 수도권 거점 3개+. 이커머스 볼트온.", "유통/물류", "중기업", "Complex"),
    ("의뢰: 대기업 — 차량용 반도체 설계 기업, 자체 IP, 매출 50~200억, 기술 인수.", "반도체/소부장", "소기업", "Complex"),
    ("의뢰: 일본 PE — 한국 화장품 ODM/OEM, 매출 300~1,000억, 일본 시장 진출.", "화장품/뷰티", "중기업", "Complex"),
    ("당사 B2B SaaS 포트폴리오 확장 — 회계/HR/물류 중 하나, ARR 30억+.", "IT/SaaS", "소기업", "Complex"),
    # 오픈채팅 톤
    ("에스테틱/뷰티 디바이스 업체 매물 있나요? 매출 50~200억.", "화장품/뷰티", "소기업", "Simple"),
    ("요양병원/요양원 매물 구합니다. 수도권, 100병상+.", "바이오/헬스케어", "소기업", "Medium"),
    ("웨딩홀/예식장 매물 있으면 연락주세요.", "유통/물류", "소기업", "Simple"),
    ("주유소 매물 구합니다. 수도권, 토지 포함, 일 판매 5kL+.", "에너지/기후", "소기업", "Simple"),
    ("도시가스 대리점 인수 관심. 수도권.", "에너지/기후", "소기업", "Medium"),
    # Edge
    ("코스닥 상장폐지 직전 기업, 기술 자산 가치 있는 곳 인수", "IT/SaaS", "소기업", "Edge"),
    ("이민/비자 사업(E-9/E-7 대행) 인수, 고정 고객 보유", "유통/물류", "소상공인", "Edge"),
    ("원어민 강사 파견 사업 인수, 학교/기업 고정 거래처", "교육", "소기업", "Edge"),
    ("광산/채석장 운영권 인수, 자원 가치", "에너지/기후", "소기업", "Edge"),
    ("마사지숍 프랜차이즈 인수, 수도권 10개점+", "유통/물류", "소기업", "Edge"),
]

for text, sector, size, complexity in _uc1_final:
    new_queries.append({
        "id": make_id(), "uc": "UC-1", "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "최종보충-UC1",
        "audit": audit_for_size(size),
    })

# UC-3 최종 보충 (~50건)
_uc3_final = [
    ("토큰증권(STO) 관련 플랫폼 투자, 규제 샌드박스 참여", "금융/보험", "소기업", "Complex"),
    ("사이버보안 스타트업, 시리즈A, 공공/금융 레퍼런스, ARR 10억+", "IT/SaaS", "소기업", "Complex"),
    ("로봇 바리스타/무인 카페 기술 투자", "식품/F&B", "소기업", "Medium"),
    ("그래핀/CNT 소재 기업, 상용화 단계, 시리즈A~B", "반도체/소부장", "소기업", "Complex"),
    ("줄기세포 은행/보관 서비스, 매출 10억+", "바이오/헬스케어", "소기업", "Medium"),
    ("드론 배송/물류 스타트업, 규제 특구 사업", "유통/물류", "소기업", "Complex"),
    ("AI 의료영상 판독(피부/안저/유방), FDA 승인 추진", "바이오/헬스케어", "소기업", "Complex"),
    ("친환경 포장재(종이/PLA) 제조, 매출 30억+", "제조업(일반)", "소기업", "Medium"),
    ("K-컨텐츠(웹소설/웹툰) IP 투자 펀드, 글로벌 영상화 권리", "게임/콘텐츠", "소기업", "Medium"),
    ("합성생물학(SynBio) 식품/화장품 원료, Seed~A", "바이오/헬스케어", "소기업", "Complex"),
    ("해양풍력 하부구조(모노파일) 기업, 시리즈B, 수주잔고 확보", "에너지/기후", "소기업", "Complex"),
    ("실버케어 로봇/AI 모니터링, 요양시설 B2B, 매출 10억+", "바이오/헬스케어", "소기업", "Medium"),
    ("건물 외벽 청소 로봇, B2B, 매출 5억+", "제조업(일반)", "소기업", "Medium"),
    ("스마트 물류(AMR) 스타트업, 대기업 물류센터 납품 3건+", "유통/물류", "소기업", "Medium"),
    ("AI 기반 약물 설계(Drug Discovery) 플랫폼, 파트너십 확보", "바이오/헬스케어", "소기업", "Complex"),
    ("자동차 OTA(무선 업데이트) 기술, OEM 계약", "자동차/부품", "소기업", "Complex"),
    ("고체 전해질 기업, 파일럿 양산, 전고체 배터리", "에너지/기후", "소기업", "Complex"),
    ("크로스보더 결제/환전 핀테크, 시리즈A, 글로벌 라이선스", "금융/보험", "소기업", "Complex"),
    ("디지털 트윈/메타버스 플랫폼(산업용), ARR 15억+", "IT/SaaS", "소기업", "Medium"),
    ("AI 채용/인사 솔루션, B2B SaaS, 기업 고객 200사+", "IT/SaaS", "소기업", "Medium"),
    ("천연 화장품 원료(식물성/발효), 글로벌 수출, 매출 20억+", "화장품/뷰티", "소기업", "Medium"),
    ("수산물 양식 기술(RAS/IMTA), 스마트 양식, 시리즈A", "식품/F&B", "소기업", "Complex"),
    ("실내 공기질 IoT 기업, B2B(학교/사무실), 매출 10억+", "IT/SaaS", "소기업", "Medium"),
    ("재생에너지 인증서(REC) 거래 플랫폼", "에너지/기후", "소기업", "Medium"),
    ("코스닥 턴어라운드 기업, 적자→흑자, PER 10배 이하, 제조업", "제조업(일반)", "소기업", "Medium"),
]

for text, sector, size, complexity in _uc3_final:
    new_queries.append({
        "id": make_id(), "uc": "UC-3", "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "최종보충-UC3",
        "audit": audit_for_size(size),
    })

# UC-4 최종 보충 (~20건)
_uc4_final = [
    ("한의원 체인 매도 — 대형 병원 그룹 또는 헬스케어 PE", "바이오/헬스케어", "소기업", "Medium"),
    ("성형외과 매도 — 병원 체인/PE 매칭", "바이오/헬스케어", "소기업", "Medium"),
    ("대형 음식점(뷔페/한정식) 매도 — 외식 대기업 또는 부동산 투자자", "식품/F&B", "소기업", "Simple"),
    ("물놀이시설/워터파크 매도 — 레저 기업 또는 부동산 개발사", "게임/콘텐츠", "중기업", "Medium"),
    ("캠핑장 운영 매도 — 아웃도어 기업 또는 투자자", "게임/콘텐츠", "소기업", "Simple"),
    ("화훼 농장 매도 — 유통 기업 또는 농업법인", "식품/F&B", "소기업", "Simple"),
    ("세무/회계 사무소 매도 — 대형 법인 또는 개인 세무사", "금융/보험", "소상공인", "Simple"),
    ("스포츠 센터(GX/헬스) 매도 — 피트니스 프랜차이즈 본사", "유통/물류", "소기업", "Simple"),
    ("영어유치원 매도 — 교육 대기업 또는 투자자", "교육", "소기업", "Medium"),
    ("자동차 딜러십(수입차) 매도 — 딜러 그룹 또는 수입차 본사", "자동차/부품", "소기업", "Medium"),
    ("편의점 다점포 매도 — 동종 다점포 운영자 또는 투자자", "유통/물류", "소상공인", "Simple"),
    ("PC방 다점포 매도 — 게임/엔터 기업 또는 투자자", "게임/콘텐츠", "소기업", "Simple"),
    ("공유오피스 운영 매도 — 부동산 기업 또는 코워킹 대기업", "건설", "소기업", "Medium"),
    ("인력파견/아웃소싱 업체 매도 — HR 대기업 매칭", "유통/물류", "소기업", "Medium"),
    ("번역/통역 회사 매도 — AI 번역 기업 또는 글로벌 에이전시", "IT/SaaS", "소기업", "Medium"),
]

for text, sector, size, complexity in _uc4_final:
    new_queries.append({
        "id": make_id(), "uc": "UC-4", "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "최종보충-UC4",
        "audit": audit_for_size(size),
    })


# ===========================================================
# Round 4: 최종 2,000건 달성용 보충 (180건)
# ===========================================================

# --- Edge 복잡도 보충 (55건) ---
edge_final = [
    # UC-1 Edge (15건)
    ("UC-1", "매출 매달 20% 이상 변동하는 제조업체 — 계절성 때문인지, 구조적 문제인지 파악하고 싶음", "제조업(일반)", "중기업", "Edge"),
    ("UC-1", "대표이사가 70세 이상인 비상장 중견기업, 후계자 미정, 매출 500억+", "제조업(일반)", "중견기업", "Edge"),
    ("UC-1", "최근 3년간 R&D 비용이 매출의 20% 이상인 바이오 기업, 아직 매출 미발생 포함", "바이오/헬스케어", "소기업", "Edge"),
    ("UC-1", "법정관리 졸업 후 3년 이내, 실적 회복 중인 제조업체, 매출 100억+", "제조업(일반)", "중기업", "Edge"),
    ("UC-1", "수출 비중 90% 이상인데 원화 약세로 영업이익률이 갑자기 좋아진 중소기업", "반도체/소부장", "중기업", "Edge"),
    ("UC-1", "임직원 평균 근속연수 15년+ 장수기업, 기술력 검증됨, 매출 200~500억", "제조업(일반)", "중견기업", "Edge"),
    ("UC-1", "특허 100건 이상 보유한 중소 제조업체, 매출 50억 미만이지만 IP 가치 높은 곳", "IT/SaaS", "소기업", "Edge"),
    ("UC-1", "매출 1,000억 이상인데 임직원 50명 미만인 자산경량형 사업 모델", "유통/물류", "중견기업", "Edge"),
    ("UC-1", "가맹본부 등록 후 5년 이내, 가맹점 50개+, 본사 직영점 수익성 검증된 프랜차이즈", "식품/F&B", "소기업", "Edge"),
    ("UC-1", "지분 구조가 50:50 교착 상태인 기업, 어느 한쪽이 매도 의향 있는 경우", "제조업(일반)", "중기업", "Edge"),
    # UC-2 Edge (10건)
    ("UC-2", "한국에서 '키오스크' 하드웨어 자체 제조하는 업체 vs 해외 OEM 수입 후 소프트웨어만 하는 업체", "IT/SaaS", "소기업", "Edge"),
    ("UC-2", "네이버 스마트스토어 상위 1% 셀러 중 법인사업자인 곳 — 개인사업자 제외", "이커머스", "소기업", "Edge"),
    ("UC-2", "드론 관련 기업 비교 — 기체 제조 vs 소프트웨어(자율비행) vs 서비스(촬영/측량)", "제조업(일반)", "소기업", "Edge"),
    ("UC-2", "대체육/배양육 vs 식물성 단백질 vs 곤충 단백질 — 한국 시장 참여 기업 전체 비교", "식품/F&B", "소기업", "Edge"),
    ("UC-2", "반려동물 장례/추모 서비스 업체 — 시장 형성기라 경쟁사가 몇 개나 있는지부터 파악", "바이오/헬스케어", "소상공인", "Edge"),
    ("UC-2", "수소 밸류체인 전체: 생산(그린/그레이) vs 저장 vs 운송 vs 충전소 운영 업체 맵핑", "에너지/기후", "중기업", "Edge"),
    ("UC-2", "아이돌 매니지먼트 vs 버추얼 아이돌 vs AI 아이돌 — 한국 엔터 업체 비교", "게임/콘텐츠", "소기업", "Edge"),
    ("UC-2", "탄소배출권 거래 관련 기업 — 컨설팅 vs 거래 플랫폼 vs 측정/검증(MRV) 비교", "에너지/기후", "소기업", "Edge"),
    ("UC-2", "한국 우주산업 참여 기업 — 위성 제조 vs 발사체 vs 지상장비 vs 위성데이터 서비스", "방위산업", "소기업", "Edge"),
    ("UC-2", "메디컬 AI 진단 — 영상의학 vs 병리 vs 피부 vs 안과 분야별 한국 기업 비교", "바이오/헬스케어", "소기업", "Edge"),
    # UC-3 Edge (10건)
    ("UC-3", "토큰증권(STO) 발행 기업 중 실물자산(부동산/미술품) 기반, 매출 발생 시작한 곳", "금융/보험", "소기업", "Edge"),
    ("UC-3", "창업 2년 이내 딥테크, 아직 매출 없지만 정부과제 수주액 30억+", "IT/SaaS", "소기업", "Edge"),
    ("UC-3", "대학 연구실 스핀오프 바이오 기업, 창업 3년 이내, 기술이전 계약 있는 곳", "바이오/헬스케어", "소기업", "Edge"),
    ("UC-3", "북한 개성공단 경험 기업 중 현재 국내에서 비슷한 사업 영위 중인 제조업체", "제조업(일반)", "소기업", "Edge"),
    ("UC-3", "NFT/블록체인 게임 기업 중 실제 MAU 1만+ 유지하고 있는 곳", "게임/콘텐츠", "소기업", "Edge"),
    ("UC-3", "사회적기업 인증 받은 곳 중 매출 성장률 30%+, 소셜임팩트와 수익 둘 다 되는 곳", "교육", "소기업", "Edge"),
    ("UC-3", "폐배터리 리사이클링 기술 보유 기업, 파일럿 단계 포함, 한국 전체 맵핑", "에너지/기후", "소기업", "Edge"),
    ("UC-3", "K-뷰티 ODM 중 일본 수출 비중 50%+ — 엔화 강세 수혜 기업", "화장품/뷰티", "중기업", "Edge"),
    ("UC-3", "농업 기술(AgriTech) 스타트업 — 스마트팜, 종자, 유통 자동화 등", "식품/F&B", "소기업", "Edge"),
    ("UC-3", "군용 로봇/무인체계 기업 — 방산 지정업체 여부 무관, 기술 보유만으로 투자 검토", "방위산업", "소기업", "Edge"),
    # UC-5 Edge (15건)
    ("UC-5", "한국 내 '클린룸' 장비/시설/소모품 전체 밸류체인 맵핑", "반도체/소부장", "중기업", "Edge"),
    ("UC-5", "실버타운/시니어 주거 시장 참여 기업 전체 — 건설, 운영, 헬스케어 서비스 포함", "건설", "중기업", "Edge"),
    ("UC-5", "한국 데이터센터 밸류체인 — 시설(건설/임대) vs 냉각 vs 전력 vs 서버/네트워크 장비", "건설", "중견기업", "Edge"),
    ("UC-5", "한국 펫푸드 시장 전체 기업 맵핑 — 사료 제조, 간식, 영양제, 수입 유통 포함", "식품/F&B", "소기업", "Edge"),
    ("UC-5", "웨딩 산업 밸류체인: 스튜디오, 드레스, 메이크업, 플래닝, 허니문 여행사까지", "게임/콘텐츠", "소상공인", "Edge"),
    ("UC-5", "한국 치과 관련 기업 전체 — 임플란트, 교정장치, 디지털덴티스트리, 체어/장비", "바이오/헬스케어", "중기업", "Edge"),
    ("UC-5", "주류 시장 전체 — 소주/맥주 제조 vs 수입와인 유통 vs 크래프트 맥주 vs 전통주", "식품/F&B", "소기업", "Edge"),
    ("UC-5", "한국 법률 테크(LegalTech) 시장 참여 기업 — AI 계약 검토, 전자소송, 법률 SaaS", "IT/SaaS", "소기업", "Edge"),
    ("UC-5", "K-pop 굿즈/MD 제조·유통 업체 전체 맵핑 — 포토카드 인쇄부터 온라인 플랫폼까지", "게임/콘텐츠", "소기업", "Edge"),
    ("UC-5", "한국 원전 해체 관련 기업 — 아직 시장 초기지만 참여 예정 기업까지 포함", "에너지/기후", "중기업", "Edge"),
    ("UC-5", "전기차 충전 인프라 기업 — 충전기 제조 vs 설치/운영 vs CPO(충전사업자) vs 결제", "에너지/기후", "중기업", "Edge"),
    ("UC-5", "한국 인슈어테크(InsurTech) 기업 전체 — 보험 비교, 언더라이팅 AI, 보험 SaaS", "금융/보험", "소기업", "Edge"),
    ("UC-5", "산업용 3D프린팅 한국 밸류체인 — 장비, 소재(금속분말/레진), 서비스뷰로, SW", "제조업(일반)", "소기업", "Edge"),
    ("UC-5", "한국 프롭테크(PropTech) 전체 — 중개 플랫폼, 건물관리, 부동산 데이터, 인테리어", "건설", "소기업", "Edge"),
    ("UC-5", "수산 양식 밸류체인 — 종묘, 사료, 양식장비, 가공, 유통까지 한국 기업 전체", "식품/F&B", "소기업", "Edge"),
    # UC-4 Edge (5건)
    ("UC-4", "우리 회사가 특허 300건+인데, 특허 포트폴리오만 따로 매각할 수 있는 매수자 찾기", "IT/SaaS", "중기업", "Edge"),
    ("UC-4", "법정관리 졸업 예정 기업인데, M&A나 투자 유치 가능한 매수자/투자자 찾기", "제조업(일반)", "중기업", "Edge"),
    ("UC-4", "공동대표 체제에서 한쪽 지분(40%) 매각 — 기존 주주 우선매수 거절 시 외부 매수자", "식품/F&B", "소기업", "Edge"),
    ("UC-4", "해외(동남아) 현지법인만 매각하고 싶은데, 크로스보더 M&A 가능한 매수자", "제조업(일반)", "중기업", "Edge"),
    ("UC-4", "ESG 평가 A등급 받은 기업인데, ESG 투자 전문 PE나 임팩트 펀드 매수자 찾기", "에너지/기후", "중견기업", "Edge"),
]

for uc, text, sector, size, complexity in edge_final:
    new_queries.append({
        "id": make_id(), "uc": uc, "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "최종보충-Edge",
        "audit": audit_for_size(size),
    })

# --- Medium 복잡도 + 중기업/중견기업 보충 (65건) ---
medium_size_final = [
    # UC-1 중기업/중견기업 Medium (20건)
    ("UC-1", "연매출 300~500억, 영업이익률 10%+, 자동차 전장부품 제조, 중기업, 100% 경영권 인수", "자동차/부품", "중기업", "Medium"),
    ("UC-1", "매출 500~1,000억, EBITDA 마진 15%+, 식품 가공 중견기업, 수도권 공장", "식품/F&B", "중견기업", "Medium"),
    ("UC-1", "매출 200~400억, 건설 특수공법(터널/교량) 전문업체, 중기업, 공공 수주 실적 보유", "건설", "중기업", "Medium"),
    ("UC-1", "매출 300~600억, 산업용 로봇/자동화 장비 제조, 영업이익률 8%+, 중기업", "제조업(일반)", "중기업", "Medium"),
    ("UC-1", "매출 500~800억, 영업이익 50억+, 의료기기 제조 중견기업, FDA 인증 보유", "바이오/헬스케어", "중견기업", "Medium"),
    ("UC-1", "매출 200~500억, 화장품 ODM 중기업, 일본/동남아 수출 비중 30%+", "화장품/뷰티", "중기업", "Medium"),
    ("UC-1", "매출 300~700억, 반도체 검사장비, 영업이익률 12%+, 중기업, 대기업 납품 실적", "반도체/소부장", "중기업", "Medium"),
    ("UC-1", "매출 400~600억, 특수화학(전자재료) 중기업, 3년 연속 흑자, 기술진입장벽 높은 곳", "제조업(일반)", "중기업", "Medium"),
    ("UC-1", "매출 500~1,000억, 방산 중견기업, 방위사업청 등록업체, 수출 실적 있는 곳", "방위산업", "중견기업", "Medium"),
    ("UC-1", "매출 200~400억, 게임 개발사 중기업, 자체 IP 보유, 해외 퍼블리싱 경험", "게임/콘텐츠", "중기업", "Medium"),
    ("UC-1", "매출 300~500억, 태양광/풍력 EPC 중기업, 3년 연속 수주 성장", "에너지/기후", "중기업", "Medium"),
    ("UC-1", "매출 200~400억, 교육 콘텐츠 제작·운영, 중기업, B2B 매출 비중 60%+", "교육", "중기업", "Medium"),
    ("UC-1", "매출 500~800억, 철강 유통·가공 중견기업, 자체 물류센터 보유", "철강/금속", "중견기업", "Medium"),
    ("UC-1", "매출 300~600억, 클라우드/SaaS 중기업, ARR 기준 YoY 20%+ 성장", "IT/SaaS", "중기업", "Medium"),
    ("UC-1", "매출 400~700억, 식자재 유통 중기업, 급식/외식 채널, 콜드체인 인프라 보유", "유통/물류", "중기업", "Medium"),
    # UC-2 중기업 Medium (10건)
    ("UC-2", "매출 300억대 산업용 펌프 제조업체 비교 — 국내 3~4개사 기술력/납품처 비교", "제조업(일반)", "중기업", "Medium"),
    ("UC-2", "매출 200~500억 규모 물류 자동화(AGV/AMR) 기업 비교", "유통/물류", "중기업", "Medium"),
    ("UC-2", "중기업급 화장품 ODM 3사 비교: 생산 캐파, 주요 고객사, 수출 비중", "화장품/뷰티", "중기업", "Medium"),
    ("UC-2", "매출 300~500억 건설기계 부품 제조업체 경쟁 비교", "자동차/부품", "중기업", "Medium"),
    ("UC-2", "중견기업급 IT 인프라(서버/스토리지/네트워크) 유통업체 비교", "IT/SaaS", "중견기업", "Medium"),
    ("UC-2", "매출 200~400억 방산 전자장비 업체 비교 — 통신/레이더/전자전 분야별", "방위산업", "중기업", "Medium"),
    ("UC-2", "매출 500억대 교육 플랫폼 3사 비교 — B2B vs B2C 매출 구조", "교육", "중기업", "Medium"),
    ("UC-2", "중기업급 바이오 CDMO 3사 비교 — 생산 규모, GMP 인증, 주요 고객", "바이오/헬스케어", "중기업", "Medium"),
    ("UC-2", "매출 300~600억 식품 OEM 업체 비교 — 즉석식품/HMR 전문", "식품/F&B", "중기업", "Medium"),
    ("UC-2", "매출 200~500억 에너지 저장(ESS) 업체 경쟁 비교", "에너지/기후", "중기업", "Medium"),
    # UC-3 중기업/중견기업 Medium (10건)
    ("UC-3", "매출 200~500억, 영업이익률 10%+, 중기업, 제조업, Series C 이후 프리IPO 투자", "제조업(일반)", "중기업", "Medium"),
    ("UC-3", "매출 300~600억, EBITDA 50억+, 중견기업 전환 직전, 성장형 메자닌 투자 대상", "IT/SaaS", "중기업", "Medium"),
    ("UC-3", "매출 500억+, 중견기업, 바이오 CDMO, IPO 3년 이내 계획, 프리IPO 투자", "바이오/헬스케어", "중견기업", "Medium"),
    ("UC-3", "매출 200~400억, 영업이익률 8%+, 자동차 전장 중기업, 기술주도 그로스 투자", "자동차/부품", "중기업", "Medium"),
    ("UC-3", "매출 300~500억, 에너지 인프라(태양광/ESS), 중기업, 인프라 펀드 투자 적합", "에너지/기후", "중기업", "Medium"),
    ("UC-3", "매출 200~400억, 교육 에듀테크, 중기업, B2B ARR 100억+, 성장 투자", "교육", "중기업", "Medium"),
    ("UC-3", "매출 400~700억, 식품 제조 중기업, 해외 수출 YoY 30%+, 성장 자본 필요", "식품/F&B", "중기업", "Medium"),
    ("UC-3", "매출 300~500억, 반도체 소재 중기업, 국산화율 30% 미만 품목, 전략 투자", "반도체/소부장", "중기업", "Medium"),
    ("UC-3", "매출 500~800억, 게임 개발사, 자체 IP 흥행작 보유, 중기업, 해외 진출 투자", "게임/콘텐츠", "중기업", "Medium"),
    ("UC-3", "매출 200~500억, 건설 모듈러/PC 공법 전문, 중기업, ESG 테마 투자", "건설", "중기업", "Medium"),
    # UC-5 중기업 Medium (10건)
    ("UC-5", "매출 200억 이상 중기업급 한국 클린뷰티 브랜드 전체 리스트", "화장품/뷰티", "중기업", "Medium"),
    ("UC-5", "매출 300억+ 중기업급 방산 소프트웨어(C4I/지휘통제) 업체 맵핑", "방위산업", "중기업", "Medium"),
    ("UC-5", "중기업급 물류 자동화 장비 제조업체 한국 시장 전체 맵핑", "유통/물류", "중기업", "Medium"),
    ("UC-5", "매출 200~500억 규모 산업용 센서/계측기기 제조업체 전체", "제조업(일반)", "중기업", "Medium"),
    ("UC-5", "중기업급 한국 EdTech 기업 — AI 기반 학습, LMS, 콘텐츠 제작 도구", "교육", "중기업", "Medium"),
    ("UC-5", "매출 300억+ 금속 표면처리/도금 전문 중기업 리스트", "철강/금속", "중기업", "Medium"),
    ("UC-5", "중기업급 식품 콜드체인 물류업체 전체 — 저온창고, 냉장차량, 라스트마일", "유통/물류", "중기업", "Medium"),
    ("UC-5", "매출 200억+ 중기업급 한국 핀테크 기업 맵핑 — 결제, 송금, 대출, 자산관리", "금융/보험", "중기업", "Medium"),
    ("UC-5", "매출 300억+ 자동차 경량화 부품(알루미늄/탄소섬유) 중기업 전체 리스트", "자동차/부품", "중기업", "Medium"),
    ("UC-5", "매출 200억+ 바이오 원료의약품(API) 제조 중기업 전체 맵핑", "바이오/헬스케어", "중기업", "Medium"),
    # UC-4 중기업 Medium (5건)
    ("UC-4", "매출 400억, 산업용 밸브 중기업 매도 — 플랜트/에너지 분야 전략적 매수자 찾기", "제조업(일반)", "중기업", "Medium"),
    ("UC-4", "매출 300억, IT 보안 솔루션 중기업 매각 — 대기업 SI 또는 글로벌 보안업체 매수자", "IT/SaaS", "중기업", "Medium"),
    ("UC-4", "매출 500억, 식품 포장재 중기업 매도 — 식품 대기업 또는 패키징 그룹 매수자", "제조업(일반)", "중기업", "Medium"),
    ("UC-4", "매출 250억, 의료기기(진단) 중기업 매각 — 글로벌 IVD 기업 또는 헬스케어 PE", "바이오/헬스케어", "중기업", "Medium"),
    ("UC-4", "매출 350억, 화장품 용기 제조 중기업 매도 — 화장품 대기업 또는 패키징 전문 PE", "화장품/뷰티", "중기업", "Medium"),
]

for uc, text, sector, size, complexity in medium_size_final:
    new_queries.append({
        "id": make_id(), "uc": uc, "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "최종보충-중기업균형",
        "audit": audit_for_size(size),
    })

# --- 나머지 UC-1/UC-3/UC-5 Simple/Complex 보충 (60건) ---
remaining_final = [
    # UC-1 Complex (12건)
    ("UC-1", "매출 100~300억, 3년 연속 흑자, 영업이익률 10%+, IT/소프트웨어, 수도권, B2B 매출 비중 70%+, 외감, 바이아웃", "IT/SaaS", "중기업", "Complex"),
    ("UC-1", "매출 50~150억, 영업이익률 15%+, 화장품 원료(기능성 성분) 제조, 특허 10건+, 수출 비중 40%+, 소수지분 가능", "화장품/뷰티", "소기업", "Complex"),
    ("UC-1", "EBITDA 30~80억, EV/EBITDA 6x 이하, 식자재 유통, 자체 물류 인프라, 콜드체인, 수도권, 차입금의존도 30% 이하", "유통/물류", "중기업", "Complex"),
    ("UC-1", "매출 200~500억, 반도체 후공정 장비, 매출 성장률 YoY 15%+, 글로벌 고객사 3곳+, 수출 비중 50%+", "반도체/소부장", "중기업", "Complex"),
    ("UC-1", "매출 100~300억, 건설 특수자재(방수/단열/내화), 3년 흑자, 특허 보유, 아파트 시공사 납품 실적", "건설", "소기업", "Complex"),
    ("UC-1", "매출 300~600억, 게임 퍼블리싱, 자체 IP 3개+, 해외 매출 비중 50%+, EBITDA 마진 20%+, 상장 예정", "게임/콘텐츠", "중기업", "Complex"),
    ("UC-1", "매출 50~200억, 에듀테크, B2B 고객사 100곳+, 월간 리텐션 90%+, ARR 기준 YoY 30%+, VC 투자 이력", "교육", "소기업", "Complex"),
    ("UC-1", "매출 100~400억, 자동차 전장(ADAS 센서), Tier 1 납품, 영업이익률 10%+, 신규 수주 잔고 매출의 150%+", "자동차/부품", "중기업", "Complex"),
    ("UC-1", "매출 200~500억, 철강 2차 가공(절단/절곡/용접), 수도권+충청 공장, 3년 흑자, 자체 물류, 대기업 직납", "철강/금속", "중기업", "Complex"),
    ("UC-1", "매출 500~1,000억, 에너지 EPC(태양광/ESS), 수주잔고 매출의 200%+, 영업이익률 8%+, 중견기업", "에너지/기후", "중견기업", "Complex"),
    ("UC-1", "매출 100~300억, 금융 IT(코어뱅킹/보험 시스템), 은행/보험사 납품 3곳+, 유지보수 매출 비중 50%+", "금융/보험", "소기업", "Complex"),
    ("UC-1", "매출 50~200억, 방산 소프트웨어(시뮬레이션/훈련체계), 방사청 등록, 보안 인증, 3년 흑자", "방위산업", "소기업", "Complex"),
    # UC-3 Simple (8건)
    ("UC-3", "바이오 스타트업, 시리즈 A 투자 대상", "바이오/헬스케어", "소기업", "Simple"),
    ("UC-3", "프리IPO 투자 가능한 제조 중기업", "제조업(일반)", "중기업", "Simple"),
    ("UC-3", "에듀테크 시리즈 B 투자 대상 기업", "교육", "소기업", "Simple"),
    ("UC-3", "ESG 테마 그린에너지 투자 대상", "에너지/기후", "소기업", "Simple"),
    ("UC-3", "K뷰티 브랜드 성장 투자 대상", "화장품/뷰티", "소기업", "Simple"),
    ("UC-3", "방산 기업 전략적 투자 대상", "방위산업", "소기업", "Simple"),
    ("UC-3", "핀테크 스타트업 시드~시리즈A 투자", "금융/보험", "소기업", "Simple"),
    ("UC-3", "물류 자동화 기업 성장 투자", "유통/물류", "소기업", "Simple"),
    # UC-5 Simple (10건)
    ("UC-5", "한국 김치 제조업체 전체 리스트", "식품/F&B", "소기업", "Simple"),
    ("UC-5", "국내 드론 관련 기업 맵핑", "제조업(일반)", "소기업", "Simple"),
    ("UC-5", "한국 VR/AR 기업 전체 리스트", "IT/SaaS", "소기업", "Simple"),
    ("UC-5", "한국 치킨 프랜차이즈 본사 리스트", "식품/F&B", "소기업", "Simple"),
    ("UC-5", "국내 2차전지 소재 기업 맵핑", "에너지/기후", "소기업", "Simple"),
    ("UC-5", "한국 CCTV/보안장비 업체 리스트", "IT/SaaS", "소기업", "Simple"),
    ("UC-5", "국내 건강기능식품 OEM 업체", "식품/F&B", "소기업", "Simple"),
    ("UC-5", "한국 전자결제(PG) 업체 리스트", "금융/보험", "소기업", "Simple"),
    ("UC-5", "국내 수소차 부품 관련 기업", "자동차/부품", "소기업", "Simple"),
    ("UC-5", "한국 MICE(전시/컨벤션) 업체 리스트", "유통/물류", "소기업", "Simple"),
    # UC-1 Simple (10건)
    ("UC-1", "흑자 제조업체 인수 대상 찾기", "제조업(일반)", "소기업", "Simple"),
    ("UC-1", "수도권 식품 제조업체 인수", "식품/F&B", "소기업", "Simple"),
    ("UC-1", "물류 창고업 인수 대상", "유통/물류", "소기업", "Simple"),
    ("UC-1", "교육 기업 바이아웃 대상", "교육", "소기업", "Simple"),
    ("UC-1", "뷰티 브랜드 인수 대상", "화장품/뷰티", "소기업", "Simple"),
    ("UC-1", "IT 서비스 기업 인수 검토", "IT/SaaS", "소기업", "Simple"),
    ("UC-1", "건설 전문업체 인수 대상", "건설", "소기업", "Simple"),
    ("UC-1", "에너지 기업 바이아웃 대상", "에너지/기후", "소기업", "Simple"),
    ("UC-1", "게임 스튜디오 인수 검토", "게임/콘텐츠", "소기업", "Simple"),
    ("UC-1", "금융 IT 기업 인수 대상", "금융/보험", "소기업", "Simple"),
    # UC-2 Complex (10건)
    ("UC-2", "한국 CDMO 기업 5사 비교 — GMP 등급, 생산 캐파(L), API vs 완제 비중, 주요 고객사, 해외 인증 현황", "바이오/헬스케어", "중기업", "Complex"),
    ("UC-2", "국내 ESS 인테그레이터 3사 비교 — 배터리 소싱(삼성/LG/CATL), 시공 실적(MWh), A/S 체계, 인증", "에너지/기후", "중기업", "Complex"),
    ("UC-2", "반도체 CMP 슬러리 국산화 업체 비교 — 기술 수준(nm 대응), 대기업 채택 현황, 수율, 단가 경쟁력", "반도체/소부장", "중기업", "Complex"),
    ("UC-2", "교육 AI 튜터링 서비스 비교 — 과목 커버리지, B2B vs B2C, MAU, 학습 효과 데이터, 가격 모델", "교육", "소기업", "Complex"),
    ("UC-2", "국내 밀키트 제조업체 5사 비교 — 생산 캐파, SKU 수, 유통 채널(이커머스/오프라인), 매출 규모", "식품/F&B", "소기업", "Complex"),
    ("UC-2", "한국 자율주행 기술 기업 비교 — Level 3/4 기술 수준, 테스트 주행거리, OEM 파트너십, 인허가 현황", "자동차/부품", "중기업", "Complex"),
    ("UC-2", "국내 RPA(로봇프로세스자동화) 업체 비교 — 도입 기업 수, 산업별 특화, 기술 스택, 가격, 레퍼런스", "IT/SaaS", "소기업", "Complex"),
    ("UC-2", "한국 프리미엄 김/해태 스낵 제조업체 비교 — 수출 비중, 주요 수출국, OEM vs 자체브랜드, 매출 성장률", "식품/F&B", "중기업", "Complex"),
    ("UC-2", "국내 산업용 가스 공급업체 비교 — 가스 종류(질소/산소/아르곤/특수가스), 공급 방식, 반도체/철강 납품 비중", "제조업(일반)", "중기업", "Complex"),
    ("UC-2", "한국 보험 플랫폼 비교 — 보험 비교/추천, GA 채널, 보험금 청구 자동화, MAU, 제휴 보험사 수", "금융/보험", "소기업", "Complex"),
    # UC-4 Simple (5건)
    ("UC-4", "식품 제조업체 매도 — 매수자 찾기", "식품/F&B", "소기업", "Simple"),
    ("UC-4", "IT 기업 매각 — 잠재 매수자 탐색", "IT/SaaS", "소기업", "Simple"),
    ("UC-4", "제조업체 지분 매각 매수자 탐색", "제조업(일반)", "소기업", "Simple"),
    ("UC-4", "교육 기업 매도 — 매수자 리스트", "교육", "소기업", "Simple"),
    ("UC-4", "물류 기업 매각 매수자 찾기", "유통/물류", "소기업", "Simple"),
    # UC-3 Complex (5건)
    ("UC-3", "매출 100~300억, 영업이익률 12%+, SaaS, B2B 고객 200사+, NRR 120%+, 시리즈 C~프리IPO 투자", "IT/SaaS", "소기업", "Complex"),
    ("UC-3", "EBITDA 20~50억, EV/EBITDA 8x 이하, 제조업, 수도권, 3년 흑자, PE 바이아웃 동반 소수지분 투자", "제조업(일반)", "중기업", "Complex"),
    ("UC-3", "매출 50~200억, 바이오시밀러/CDMO, FDA/EMA 인증 보유, 시리즈 B~C, 해외 파트너 계약 보유", "바이오/헬스케어", "소기업", "Complex"),
    ("UC-3", "매출 200~500억, 방산 전자장비, 방사청 핵심기술 보유, 수출 확대 중, 전략적 투자(CVC)", "방위산업", "중기업", "Complex"),
    ("UC-3", "ARR 50억+, 매출 성장률 40%+, Rule of 40 충족, 에듀테크/HR테크, 시리즈 B~C 투자", "교육", "소기업", "Complex"),
]

for uc, text, sector, size, complexity in remaining_final:
    new_queries.append({
        "id": make_id(), "uc": uc, "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "최종보충-2000달성",
        "audit": audit_for_size(size),
    })

# --- Round 5: 최종 20건 (2,000 정확 달성) ---
final_20 = [
    ("UC-1", "가업승계 이슈 있는 중견기업, 매출 1,000억+, 제조업, 2세가 경영 의지 없는 경우", "제조업(일반)", "중견기업", "Edge"),
    ("UC-1", "군납 실적 있는 통신장비 업체, 매출 100~300억, 민수 전환 가능성 높은 곳", "방위산업", "소기업", "Medium"),
    ("UC-2", "한국 소형 모듈원전(SMR) 관련 기업 — 원자로 설계 vs 핵연료 vs 계측제어 비교", "에너지/기후", "중기업", "Edge"),
    ("UC-2", "국내 식물공장(vertical farming) 업체 비교 — 재배 기술, 작물 종류, 투자 규모", "식품/F&B", "소기업", "Edge"),
    ("UC-3", "사이버보안 스타트업, 제로트러스트/SASE 기술, 시리즈 A~B, MRR 3억+", "IT/SaaS", "소기업", "Medium"),
    ("UC-3", "헬스케어 AI(신약개발 AI, 진단 AI, 디지털치료제) 시리즈 B+ 투자 대상", "바이오/헬스케어", "소기업", "Medium"),
    ("UC-5", "한국 로봇 밸류체인 전체 — 산업용/서비스용/의료용/물류로봇, 핵심부품(감속기/모터) 포함", "제조업(일반)", "중기업", "Edge"),
    ("UC-5", "국내 우주항공 산업 참여 기업 전체 맵핑 — 위성, 발사체, 지상국, 우주 스타트업", "방위산업", "소기업", "Edge"),
    ("UC-1", "매출 200~500억, 식품 포장재(연포장/필름) 제조, 중기업, 대기업 납품, 흑자", "제조업(일반)", "중기업", "Medium"),
    ("UC-1", "매출 100~200억, 수의학/동물 의약품 제조, 3년 흑자, 수도권", "바이오/헬스케어", "소기업", "Medium"),
    ("UC-2", "국내 전기차 배터리 리사이클링 업체 3사 비교 — 기술(습식/건식), 처리 캐파, 원료 회수율", "에너지/기후", "소기업", "Complex"),
    ("UC-2", "한국 클라우드 MSP(매니지드서비스) 업체 비교 — AWS/Azure/GCP 파트너 등급, 매출, 고객수", "IT/SaaS", "소기업", "Medium"),
    ("UC-5", "한국 배달 플랫폼 생태계 전체 — 플랫폼, 라이더, 포장재, POS, 공유주방", "IT/SaaS", "소기업", "Edge"),
    ("UC-5", "국내 수소경제 밸류체인 기업 맵핑 — 생산, 저장, 운송, 충전, 활용(연료전지)", "에너지/기후", "중기업", "Edge"),
    ("UC-4", "AI 반도체 설계 기업 매도 — 글로벌 팹리스/파운드리 또는 테크 PE 매수자 탐색", "반도체/소부장", "소기업", "Medium"),
    ("UC-3", "국내 탄소 포집(CCUS) 기술 기업, 파일럿 단계 포함, 정부 과제 수주 실적", "에너지/기후", "소기업", "Edge"),
    ("UC-1", "매출 300~600억, 건설 자재(창호/유리/단열재) 제조 중기업, 수도권, 아파트 브랜드 납품", "건설", "중기업", "Medium"),
    ("UC-5", "한국 반려동물 산업 전체 맵핑 — 사료, 용품, 의료, 보험, 호텔/미용, 장례", "바이오/헬스케어", "소기업", "Edge"),
    ("UC-2", "국내 스마트팜 기업 비교 — 온실 자동화 vs 축산 자동화 vs 데이터 분석 플랫폼", "식품/F&B", "소기업", "Medium"),
    ("UC-3", "매출 50~150억, 국방 AI(자율무기체계/드론) 기업, 방산 전문 VC 투자 대상", "방위산업", "소기업", "Medium"),
]

for uc, text, sector, size, complexity in final_20:
    new_queries.append({
        "id": make_id(), "uc": uc, "text": text, "sector": sector,
        "size": size, "complexity": complexity, "source": "최종보충-final20",
        "audit": audit_for_size(size),
    })


# ============================================================
# 병합 및 출력
# ============================================================
all_queries = stage2_queries + new_queries

# Deduplicate by ID
seen_ids = set()
unique_queries = []
for q in all_queries:
    if q["id"] not in seen_ids:
        seen_ids.add(q["id"])
        unique_queries.append(q)

total = len(unique_queries)
print(f"\n총 생성 쿼리 수: {total}")

# Distribution analysis
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
    pct = count / total * 100
    print(f"  {sector}: {count}건 ({pct:.1f}%)")

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

print("\n=== 소스(페르소나) 분포 ===")
for src, count in sorted(source_dist.items(), key=lambda x: -x[1]):
    print(f"  {src}: {count}건")

# Save
output = {
    "metadata": {
        "generated_at": datetime.now().isoformat(),
        "total_queries": total,
        "stage": "Stage 3: 페르소나 기반 (1,200 → 2,000) — FINAL",
        "sources": {
            "stage1": len([q for q in unique_queries if q["id"].startswith(("A-", "B-", "C-", "D-", "E-", "L-"))]),
            "stage1_augmented": len([q for q in unique_queries if q["id"].startswith(("AUG", "COMP", "MKT", "INV", "SELL", "EDGE"))]),
            "stage2_matrix": len([q for q in unique_queries if q["id"].startswith("S2-")]),
            "stage3_persona": len([q for q in unique_queries if q["id"].startswith("S3-")]),
        },
        "distribution": {
            "uc": dict(uc_dist),
            "sector": dict(sector_dist),
            "complexity": dict(complexity_dist),
            "size": dict(size_dist),
        },
        "personas": {
            "PE심사역": len([q for q in unique_queries if "PE심사역" in q.get("source", "")]),
            "전략적매수자": len([q for q in unique_queries if "전략적매수자" in q.get("source", "")]),
            "개인매수자": len([q for q in unique_queries if "개인매수자" in q.get("source", "")]),
            "VC": len([q for q in unique_queries if q.get("source", "").startswith("페르소나-VC")]),
            "자문사": len([q for q in unique_queries if "자문사" in q.get("source", "")]),
            "오픈채팅": len([q for q in unique_queries if "오픈채팅" in q.get("source", "")]),
            "은행": len([q for q in unique_queries if "은행" in q.get("source", "")]),
        },
    },
    "queries": unique_queries,
}

output_path = "etl/data/finetuning_queries_final.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ 최종 저장: {output_path}")
