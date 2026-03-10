/** TanStack Query hooks for all API endpoints. */

import { useQuery } from "@tanstack/react-query";
import api from "./client";
import type {
  BillDetail,
  BillSummary,
  CommitteeOut,
  GraphData,
  NeighborOut,
  PaginatedResponse,
  PartyOut,
  PoliticianDetail,
  PoliticianSummary,
  PoliticianVoteRecord,
  VoteDetail,
  VoteSummary,
} from "@/types/api";

// ── Politicians ──────────────────────────────────────────────────────────────

export function usePoliticians(params: {
  party?: string;
  name?: string;
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
