"""Pydantic models for raw API responses from 열린국회정보.

Each model maps to a specific API endpoint's row fields.
All fields default to empty string since the API may omit fields.
"""

from pydantic import BaseModel


class RawLegislator(BaseModel):
    """국회의원 인적사항 — legislator bio (nwvrqwxyaytdsfvhu)."""

    HG_NM: str = ""          # 한글 이름
    HJ_NM: str = ""          # 한자 이름
    POLY_NM: str = ""        # 정당명
    ORIG_NM: str = ""        # 선거구
    REELE_GBN_NM: str = ""   # 당선 횟수 (초선, 재선, etc.)
    CMITS: str = ""          # 소속 위원회
    MONA_CD: str = ""        # 의원 코드 (assembly_id)
    LINK_URL: str = ""       # 프로필 URL
    BTH_DATE: str = ""       # 생년월일
    SEX_GBN_NM: str = ""     # 성별
    E_MAIL: str = ""         # 이메일
    TEL_NO: str = ""         # 전화번호
    ASSEM_ADDR: str = ""     # 사무실 주소
    UNITS: str = ""          # 약력
    SEC_CD: str = ""         # 비서관 코드
    JOB_RES_NM: str = ""     # 직책


class RawBill(BaseModel):
    """의안 정보 — bill info (nzmimeepazxkubdpn)."""

    BILL_ID: str = ""        # 의안 ID
    BILL_NO: str = ""        # 의안 번호
    BILL_NAME: str = ""      # 의안명
    PROPOSER: str = ""       # 제안자 (e.g. "김철수의원 외 10인")
    PROPOSER_KIND: str = ""  # 제안자 구분 (의원, 위원장, 정부)
    PROPOSE_DT: str = ""     # 제안일
    COMMITTEE_ID: str = ""   # 소관위원회 ID
    COMMITTEE: str = ""      # 소관위원회명
    PROC_RESULT: str = ""    # 처리결과
    DETAIL_LINK: str = ""    # 상세 링크
    LAW_PROC_DT: str = ""    # 법사위 처리일
    RST_PROPOSER: str = ""   # 대표발의자


class RawBillReview(BaseModel):
    """법률안 심사정보 — bill review details (nojepdqqaweusdfbi)."""

    BILL_ID: str = ""
    BILL_NO: str = ""
    BILL_NAME: str = ""
    COMMITTEE: str = ""
    COMMITTEE_DT: str = ""
    COMMITTEE_RESULT: str = ""
    LAW_SUBMIT_DT: str = ""
    LAW_PROC_DT: str = ""
    LAW_PROC_RESULT: str = ""
    PLENARY_PROC_DT: str = ""
    PLENARY_PROC_RESULT: str = ""


class RawVoteSummary(BaseModel):
    """본회의 표결 정보 — plenary vote summary (ncocpbgebiallbyeq)."""

    BILL_ID: str = ""
    BILL_NO: str = ""
    BILL_NAME: str = ""
    VOTE_DATE: str = ""
    MEMBER_TCNT: str = ""
    YES_TCNT: str = ""
    NO_TCNT: str = ""
    BLANK_TCNT: str = ""
    ABSENT_TCNT: str = ""
    RESULT: str = ""


class RawVotePerMember(BaseModel):
    """본회의 표결결과 의원별 — per-member vote (nwbpacrgavhjryiph)."""

    BILL_ID: str = ""
    HG_NM: str = ""
    POLY_NM: str = ""
    ORIG_NM: str = ""
    RESULT_VOTE_MOD: str = ""
    VOTE_DATE: str = ""


class RawCommittee(BaseModel):
    """위원회 현황 — committee info (nknaocmjlgzmoutew)."""

    CURR_COMMITTEE_ID: str = ""
    CURR_COMMITTEE: str = ""
    COMMITTEE_TYPE: str = ""
    HG_NM: str = ""
    POLY_NM: str = ""
    ORIG_NM: str = ""
