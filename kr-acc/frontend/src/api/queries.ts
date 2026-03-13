/** TanStack Query hooks for all API endpoints. */

import { useQuery } from "@tanstack/react-query";
import api from "./client";
import type {
  AbsenteeRanking,
  AssetAggregate,
  AssetRanking,
  BillDetail,
  BillSummary,
  BillTrendPoint,
  CommitteeOut,
  ControversialVote,
  Demographics,
  GraphData,
  NeighborOut,
  PaginatedResponse,
  PartySeat,
  PartyOut,
  PoliticianDetail,
  PoliticianSummary,
  PoliticianVoteRecord,
  RegionSeat,
  VoteDetail,
  VoteParticipation,
  VoteSummary,
  AssetSummary,
  PoliticianCompanyOut,
  PoliticalFundSummary,
} from "@/types/api";

// ── Politicians ──────────────────────────────────────────────────────────────

export function usePoliticians(params: {
  party?: string;
  name?: string;
  assembly_term?: number;
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: ["politicians", params],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<PoliticianSummary>>(
        "/politicians",
        { params },
      );
      return data;
    },
  });
}

export function usePolitician(id: number) {
  return useQuery({
    queryKey: ["politician", id],
    queryFn: async () => {
      const { data } = await api.get<PoliticianDetail>(`/politicians/${id}`);
      return data;
    },
    enabled: id > 0,
  });
}

export function usePoliticianBills(
  id: number,
  params: { sponsor_type?: string; page?: number; size?: number },
) {
  return useQuery({
    queryKey: ["politician-bills", id, params],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<BillSummary>>(
        `/politicians/${id}/bills`,
        { params },
      );
      return data;
    },
    enabled: id > 0,
  });
}

export function usePoliticianVotes(
  id: number,
  params: { vote_result?: string; page?: number; size?: number },
) {
  return useQuery({
    queryKey: ["politician-votes", id, params],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<PoliticianVoteRecord>>(
        `/politicians/${id}/votes`,
        { params },
      );
      return data;
    },
    enabled: id > 0,
  });
}

// ── Bills ────────────────────────────────────────────────────────────────────

export function useBills(params: {
  keyword?: string;
  proposer_type?: string;
  committee_name?: string;
  result?: string;
  date_from?: string;
  date_to?: string;
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: ["bills", params],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<BillSummary>>(
        "/bills",
        { params },
      );
      return data;
    },
  });
}

export function useBillPipeline(assemblyTerm?: number) {
  return useQuery({
    queryKey: ["bill-pipeline", assemblyTerm],
    queryFn: async () => {
      const { data } = await api.get<{ result: string; count: number }[]>(
        "/bills/pipeline",
        { params: assemblyTerm ? { assembly_term: assemblyTerm } : {} },
      );
      return data;
    },
  });
}

export function useBill(billId: string) {
  return useQuery({
    queryKey: ["bill", billId],
    queryFn: async () => {
      const { data } = await api.get<BillDetail>(`/bills/${billId}`);
      return data;
    },
    enabled: !!billId,
  });
}

// ── Votes ────────────────────────────────────────────────────────────────────

export function useVotes(params: {
  bill_id?: string;
  result?: string;
  assembly_term?: number;
  date_from?: string;
  date_to?: string;
  page?: number;
  size?: number;
}) {
  return useQuery({
    queryKey: ["votes", params],
    queryFn: async () => {
      const { data } = await api.get<PaginatedResponse<VoteSummary>>(
        "/votes",
        { params },
      );
      return data;
    },
  });
}

export function useVote(voteId: string) {
  return useQuery({
    queryKey: ["vote", voteId],
    queryFn: async () => {
      const { data } = await api.get<VoteDetail>(`/votes/${voteId}`);
      return data;
    },
    enabled: !!voteId,
  });
}

// ── Graph ────────────────────────────────────────────────────────────────────

export function useCoSponsorshipGraph(params: {
  party?: string;
  min_weight?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["graph-co-sponsorship", params],
    queryFn: async () => {
      const { data } = await api.get<GraphData>("/graph/co-sponsorship", {
        params,
      });
      return data;
    },
  });
}

export function useNeighbors(
  assemblyId: string,
  params: { min_weight?: number; limit?: number },
) {
  return useQuery({
    queryKey: ["graph-neighbors", assemblyId, params],
    queryFn: async () => {
      const { data } = await api.get<NeighborOut[]>(
        `/graph/neighbors/${assemblyId}`,
        { params },
      );
      return data;
    },
    enabled: !!assemblyId,
  });
}

// ── Reference ────────────────────────────────────────────────────────────────

export function useParties() {
  return useQuery({
    queryKey: ["parties"],
    queryFn: async () => {
      const { data } = await api.get<PartyOut[]>("/parties");
      return data;
    },
    staleTime: 30 * 60 * 1000, // 30 min — rarely changes
  });
}

// ── Assets & Companies & Funds ───────────────────────────────────────────────

export function usePoliticianAssets(id: number) {
  return useQuery({
    queryKey: ["politician-assets", id],
    queryFn: async () => {
      const { data } = await api.get<AssetSummary[]>(
        `/politicians/${id}/assets`,
      );
      return data;
    },
    enabled: id > 0,
  });
}

export function usePoliticianCompanies(id: number) {
  return useQuery({
    queryKey: ["politician-companies", id],
    queryFn: async () => {
      const { data } = await api.get<PoliticianCompanyOut[]>(
        `/politicians/${id}/companies`,
      );
      return data;
    },
    enabled: id > 0,
  });
}

export function usePoliticianFunds(id: number) {
  return useQuery({
    queryKey: ["politician-funds", id],
    queryFn: async () => {
      const { data } = await api.get<PoliticalFundSummary[]>(
        `/politicians/${id}/funds`,
      );
      return data;
    },
    enabled: id > 0,
  });
}

export function useCommittees() {
  return useQuery({
    queryKey: ["committees"],
    queryFn: async () => {
      const { data } = await api.get<CommitteeOut[]>("/committees");
      return data;
    },
    staleTime: 30 * 60 * 1000,
  });
}

// ── Rankings & Stats ────────────────────────────────────────────────────────

export interface TopSponsor {
  id: number;
  name: string;
  party: string | null;
  photo_url: string | null;
  bill_count: number;
}

export function useTopSponsors(params: {
  assembly_term?: number;
  limit?: number;
}) {
  return useQuery({
    queryKey: ["top-sponsors", params],
    queryFn: async () => {
      const { data } = await api.get<TopSponsor[]>(
        "/politicians/top-sponsors",
        { params },
      );
      return data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function usePartySeats(term: number = 22) {
  return useQuery({
    queryKey: ["party-seats", term],
    queryFn: async () => {
      const { data } = await api.get<PartySeat[]>("/stats/party-seats", {
        params: { assembly_term: term },
      });
      return data;
    },
    staleTime: 30 * 60 * 1000,
  });
}

export function useDemographics(term: number = 22) {
  return useQuery({
    queryKey: ["demographics", term],
    queryFn: async () => {
      const { data } = await api.get<Demographics>("/stats/demographics", {
        params: { assembly_term: term },
      });
      return data;
    },
    staleTime: 30 * 60 * 1000,
  });
}

export function useVoteParticipation(term: number = 22) {
  return useQuery({
    queryKey: ["vote-participation", term],
    queryFn: async () => {
      const { data } = await api.get<VoteParticipation>(
        "/stats/vote-participation",
        { params: { assembly_term: term } },
      );
      return data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useBillTrend(term: number = 22) {
  return useQuery({
    queryKey: ["bill-trend", term],
    queryFn: async () => {
      const { data } = await api.get<BillTrendPoint[]>("/stats/bill-trend", {
        params: { assembly_term: term },
      });
      return data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useAssetRankings(limit: number = 20, category?: string) {
  return useQuery({
    queryKey: ["asset-rankings", limit, category],
    queryFn: async () => {
      const { data } = await api.get<AssetRanking[]>("/assets/rankings", {
        params: { limit, category: category || undefined },
      });
      return data;
    },
    staleTime: 30 * 60 * 1000,
  });
}

export function useRegionSeats(term: number = 22) {
  return useQuery({
    queryKey: ["region-seats", term],
    queryFn: async () => {
      const { data } = await api.get<RegionSeat[]>("/stats/region-seats", {
        params: { assembly_term: term },
      });
      return data;
    },
    staleTime: 30 * 60 * 1000,
  });
}

export function useControversialVotes(term: number = 22, limit: number = 10) {
  return useQuery({
    queryKey: ["controversial-votes", term, limit],
    queryFn: async () => {
      const { data } = await api.get<ControversialVote[]>(
        "/stats/controversial-votes",
        { params: { assembly_term: term, limit } },
      );
      return data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useAbsenteeRanking(term: number = 22, limit: number = 20) {
  return useQuery({
    queryKey: ["absentee-ranking", term, limit],
    queryFn: async () => {
      const { data } = await api.get<AbsenteeRanking[]>(
        "/stats/absentee-ranking",
        { params: { assembly_term: term, limit } },
      );
      return data;
    },
    staleTime: 10 * 60 * 1000,
  });
}

export function useAssetAggregate() {
  return useQuery({
    queryKey: ["asset-aggregate"],
    queryFn: async () => {
      const { data } = await api.get<AssetAggregate[]>("/assets/aggregate");
      return data;
    },
    staleTime: 30 * 60 * 1000,
  });
}

export function usePlatformStats() {
  return useQuery({
    queryKey: ["platform-stats"],
    queryFn: async () => {
      const { data } = await api.get<{
        politicians: number;
        bills: number;
        votes: number;
      }>("/stats");
      return data;
    },
    staleTime: 10 * 60 * 1000,
  });
}
