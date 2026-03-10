"""Pydantic response/query schemas for the API."""

from datetime import date

from pydantic import BaseModel, ConfigDict


# ── Shared ────────────────────────────────────────────────────────────────────


class PaginatedResponse(BaseModel):
    """Wrapper for paginated list responses."""

    items: list
    total: int
    page: int
    size: int
    pages: int


# ── Parties ───────────────────────────────────────────────────────────────────


class PartyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color_hex: str | None
    assembly_term: int


# ── Committees ────────────────────────────────────────────────────────────────


class CommitteeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    committee_id: str
    name: str
    committee_type: str | None
    assembly_term: int


# ── Politicians ───────────────────────────────────────────────────────────────


class PoliticianSummary(BaseModel):
    """Lightweight politician for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    assembly_id: str
    name: str
    party: str | None
    constituency: str | None
    elected_count: int | None
    photo_url: str | None
    assembly_term: int


class PoliticianDetail(BaseModel):
    """Full politician detail."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    assembly_id: str
    name: str
    name_hanja: str | None
    party: str | None
    constituency: str | None
    elected_count: int | None
    committees: list[str] | None
    profile_url: str | None
    photo_url: str | None
    eng_name: str | None
    bio: str | None
    email: str | None
    homepage: str | None
    office_address: str | None
    birth_date: date | None
    gender: str | None
    assembly_term: int


class PoliticianStats(BaseModel):
    """Vote statistics for a politician."""

    total_votes: int
    yes_count: int
    no_count: int
    abstain_count: int
    absent_count: int
    participation_rate: float
    bills_sponsored: int
    bills_primary_sponsored: int


class PoliticianDetailWithStats(PoliticianDetail):
    stats: PoliticianStats | None = None


# ── Bills ─────────────────────────────────────────────────────────────────────


class BillSponsorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    politician_id: int
    politician_name: str | None = None
    politician_party: str | None = None
    sponsor_type: str | None


class BillSummary(BaseModel):
    """Lightweight bill for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    bill_id: str
    bill_no: str | None
    bill_name: str
    proposer_type: str | None
    propose_date: date | None
    committee_name: str | None
    result: str | None


class BillDetail(BillSummary):
    """Full bill detail with sponsors."""

    committee_id: str | None
    status: str | None
    assembly_term: int
    detail_url: str | None
    sponsors: list[BillSponsorOut] = []


# ── Votes ─────────────────────────────────────────────────────────────────────


class VoteRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    politician_id: int
    politician_name: str | None = None
    politician_party: str | None = None
    vote_result: str | None


class VoteSummary(BaseModel):
    """Vote summary for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vote_id: str
    bill_id: str
    bill_name: str | None = None
    vote_date: date
    total_members: int | None
    yes_count: int | None
    no_count: int | None
    abstain_count: int | None
    absent_count: int | None
    result: str | None


class VoteDetail(VoteSummary):
    """Full vote detail with per-member records."""

    records: list[VoteRecordOut] = []


# ── Graph ─────────────────────────────────────────────────────────────────────


class GraphNode(BaseModel):
    id: str
    name: str
    party: str | None = None
    group: str | None = None


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: int = 1


class GraphData(BaseModel):
    """Co-sponsorship network data for D3.js force graph."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]


class NeighborOut(BaseModel):
    """A neighbor in the co-sponsorship graph."""

    assembly_id: str
    name: str
    party: str | None = None
    weight: int


# ── Assets (재산공개) ────────────────────────────────────────────────────────


class AssetItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    subcategory: str | None
    description: str | None
    relation: str | None
    value_krw: int | None
    change_krw: int | None
    note: str | None


class AssetDeclarationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_year: int
    total_assets: int | None
    total_real_estate: int | None
    total_deposits: int | None
    total_securities: int | None
    total_crypto: int | None
    source: str | None
    items: list[AssetItemOut] = []


class AssetSummaryOut(BaseModel):
    """Lightweight asset declaration for list/chart views."""
    model_config = ConfigDict(from_attributes=True)

    report_year: int
    total_assets: int | None
    total_real_estate: int | None
    total_deposits: int | None
    total_securities: int | None
    total_crypto: int | None


# ── Companies (기업) ─────────────────────────────────────────────────────────


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    corp_code: str | None
    corp_name: str
    stock_code: str | None
    industry: str | None


class PoliticianCompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    company: CompanyOut
    relation_type: str
    detail: str | None
    value_krw: int | None
    source: str | None
    source_year: int | None


# ── Political Funds (정치자금) ───────────────────────────────────────────────


class PoliticalFundItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_type: str
    category: str | None
    counterpart: str | None
    amount: int
    item_date: date | None
    note: str | None


class PoliticalFundOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fund_year: int
    fund_type: str | None
    income_total: int | None
    expense_total: int | None
    balance: int | None
    source: str | None
    items: list[PoliticalFundItemOut] = []


class PoliticalFundSummaryOut(BaseModel):
    """Lightweight fund summary for charts."""
    model_config = ConfigDict(from_attributes=True)

    fund_year: int
    fund_type: str | None
    income_total: int | None
    expense_total: int | None
