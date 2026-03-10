"""Pydantic models for raw API responses from 열린국회정보."""

from pydantic import BaseModel


class RawLegislator(BaseModel):
    """Raw legislator record from the API."""

    HG_NM: str = ""
    HJ_NM: str = ""
    POLY_NM: str = ""
    ORIG_NM: str = ""
    REELE_GBN_NM: str = ""
    CMITS: str = ""
    MONA_CD: str = ""
    LINK_URL: str = ""
    BTH_DATE: str = ""
    SEX_GBN_NM: str = ""


class RawBill(BaseModel):
    """Raw bill record from the API."""

    BILL_ID: str = ""
    BILL_NO: str = ""
    BILL_NAME: str = ""
    PROPOSER: str = ""
    PROPOSER_KIND: str = ""
    PROPOSE_DT: str = ""
    COMMITTEE_ID: str = ""
    COMMITTEE: str = ""
    PROC_RESULT: str = ""
    DETAIL_LINK: str = ""


class RawVoteSummary(BaseModel):
    """Raw vote summary record from the API."""

    BILL_ID: str = ""
    VOTE_DATE: str = ""
    BILL_NAME: str = ""
    MEMBER_TCNT: str = ""
    YES_TCNT: str = ""
    NO_TCNT: str = ""
    BLANK_TCNT: str = ""
    ABSENT_TCNT: str = ""
    RESULT: str = ""
