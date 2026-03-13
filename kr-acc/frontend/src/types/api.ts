/** API response types — synced with backend Pydantic schemas. */

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PartyOut {
  id: number;
  name: string;
  color_hex: string | null;
  assembly_term: number;
}

export interface CommitteeOut {
  id: number;
  committee_id: string;
  name: string;
  committee_type: string | null;
  assembly_term: number;
}

export interface PoliticianSummary {
  id: number;
  assembly_id: string;
  name: string;
  party: string | null;
  constituency: string | null;
  elected_count: number | null;
  photo_url: string | null;
  assembly_term: number;
}

export interface PoliticianStats {
  total_votes: number;
  yes_count: number;
  no_count: number;
  abstain_count: number;
  absent_count: number;
  participation_rate: number;
  bills_sponsored: number;
  bills_primary_sponsored: number;
}

export interface PoliticianDetail {
  id: number;
  assembly_id: string;
  name: string;
  name_hanja: string | null;
  party: string | null;
  constituency: string | null;
  elected_count: number | null;
  committees: string[] | null;
  profile_url: string | null;
  photo_url: string | null;
  eng_name: string | null;
  bio: string | null;
  email: string | null;
  homepage: string | null;
  office_address: string | null;
  birth_date: string | null;
  gender: string | null;
  assembly_term: number;
  stats: PoliticianStats | null;
}

export interface BillSponsorOut {
  politician_id: number;
  politician_name: string | null;
  politician_party: string | null;
  sponsor_type: string | null;
}

export interface BillSummary {
  id: number;
  bill_id: string;
  bill_no: string | null;
  bill_name: string;
  proposer_type: string | null;
  propose_date: string | null;
  committee_name: string | null;
  result: string | null;
}

export interface BillDetail extends BillSummary {
  committee_id: string | null;
  status: string | null;
  assembly_term: number;
  detail_url: string | null;
  sponsors: BillSponsorOut[];
}

export interface VoteSummary {
  id: number;
  vote_id: string;
  bill_id: string;
  bill_name: string | null;
  vote_date: string;
  total_members: number | null;
  yes_count: number | null;
  no_count: number | null;
  abstain_count: number | null;
  absent_count: number | null;
  result: string | null;
}

export interface VoteRecordOut {
  politician_id: number;
  politician_name: string | null;
  politician_party: string | null;
  vote_result: string | null;
}

export interface VoteDetail extends VoteSummary {
  records: VoteRecordOut[];
}

export interface GraphNode {
  id: string;
  name: string;
  party: string | null;
  group: string | null;
}

export interface GraphEdge {
  source: string;
  target: string;
  weight: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface NeighborOut {
  assembly_id: string;
  name: string;
  party: string | null;
  weight: number;
}

// ── Assets & Companies & Funds ───────────────────────────────────────────────

export interface AssetSummary {
  report_year: number;
  total_assets: number | null;
  total_real_estate: number | null;
  total_deposits: number | null;
  total_securities: number | null;
  total_crypto: number | null;
}

export interface CompanyOut {
  id: number;
  corp_code: string | null;
  corp_name: string;
  stock_code: string | null;
  industry: string | null;
}

export interface PoliticianCompanyOut {
  company: CompanyOut;
  relation_type: string;
  detail: string | null;
  value_krw: number | null;
  source: string | null;
  source_year: number | null;
}

export interface PoliticalFundSummary {
  fund_year: number;
  fund_type: string | null;
  income_total: number | null;
  expense_total: number | null;
}

// ── Stats & Dashboard ────────────────────────────────────────────────────────

export interface PartySeat {
  party: string;
  count: number;
  color_hex: string;
}

export interface Demographics {
  gender: { gender: string; count: number }[];
  age_brackets: { bracket: string; count: number }[];
}

export interface VoteParticipation {
  avg_participation: number;
  total_votes: number;
}

export interface BillTrendPoint {
  week: string;
  count: number;
}

export interface AssetRanking {
  politician_id: number;
  name: string;
  party: string | null;
  photo_url: string | null;
  total_assets: number;
  total_real_estate: number | null;
  total_deposits: number | null;
  total_securities: number | null;
  total_crypto: number | null;
  report_year: number;
}

export interface RegionSeat {
  region: string;
  total: number;
  parties: Record<string, number>;
}

export interface ControversialVote {
  vote_id: string;
  bill_name: string;
  vote_date: string | null;
  total_members: number;
  yes_count: number;
  no_count: number;
  abstain_count: number;
  absent_count: number;
  result: string | null;
  opposition_rate: number;
}

export interface AbsenteeRanking {
  politician_id: number;
  name: string;
  party: string | null;
  photo_url: string | null;
  total_votes: number;
  absent_count: number;
  absence_rate: number;
}

export interface AssetAggregate {
  party: string;
  total_assets: number;
  total_real_estate: number;
  total_deposits: number;
  total_securities: number;
  total_crypto: number;
  count: number;
}

export interface PoliticianVoteRecord {
  vote_id: string;
  bill_id: string;
  bill_name: string;
  vote_date: string;
  vote_result: string | null;
  overall_result: string | null;
}
