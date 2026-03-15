/** TanStack Query hooks for the labeling tool. */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import labelingApi from "./labelingClient";
import type {
  LabelInput,
  LabelerInfo,
  ProgressStats,
  RubricCriterion,
  TaskDetail,
  TaskListResponse,
  TokenResponse,
} from "@/types/labeling";

// ── Auth ──────────────────────────────────────────────────────────────────────

export function useRegister() {
  return useMutation({
    mutationFn: async (data: {
      email: string;
      display_name: string;
      password: string;
      invite_code: string;
    }) => {
      const res = await labelingApi.post<TokenResponse>("/auth/register", data);
      return res.data;
    },
  });
}

export function useLogin() {
  return useMutation({
    mutationFn: async (data: { email: string; password: string }) => {
      const res = await labelingApi.post<TokenResponse>("/auth/login", data);
      return res.data;
    },
  });
}

export function useMe() {
  return useQuery({
    queryKey: ["labeling", "me"],
    queryFn: async () => {
      const res = await labelingApi.get("/auth/me");
      return res.data;
    },
    retry: false,
  });
}

// ── Tasks ─────────────────────────────────────────────────────────────────────

export function useMyCurrentTask() {
  return useQuery({
    queryKey: ["labeling", "tasks", "current"],
    queryFn: async () => {
      const res = await labelingApi.get<{
        id: number;
        query_id: string;
        query_text: string;
        result_count: number;
        label_count: number;
      } | null>("/tasks/current");
      return res.data;
    },
  });
}

export function useTasks(page = 1, size = 20, status?: string) {
  return useQuery({
    queryKey: ["labeling", "tasks", page, size, status],
    queryFn: async () => {
      const params: Record<string, unknown> = { page, size };
      if (status) params.status = status;
      const res = await labelingApi.get<TaskListResponse>("/tasks", { params });
      return res.data;
    },
  });
}

export function useNextTask() {
  return useMutation({
    mutationFn: async () => {
      const res = await labelingApi.get<TaskDetail>("/tasks/next");
      return res.data;
    },
  });
}

export function useTask(taskId: number | null) {
  return useQuery({
    queryKey: ["labeling", "task", taskId],
    queryFn: async () => {
      const res = await labelingApi.get<TaskDetail>(`/tasks/${taskId}`);
      return res.data;
    },
    enabled: taskId != null,
  });
}

export function useReopenTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (taskId: number) => {
      const res = await labelingApi.post(`/tasks/${taskId}/reopen`);
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["labeling"] });
    },
  });
}

export function useSkipTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (taskId: number) => {
      const res = await labelingApi.post(`/tasks/${taskId}/skip`);
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["labeling", "tasks"] });
    },
  });
}

// ── Labels ────────────────────────────────────────────────────────────────────

export function useSubmitLabels() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      taskId,
      labels,
    }: {
      taskId: number;
      labels: LabelInput[];
    }) => {
      const res = await labelingApi.post(`/tasks/${taskId}/labels`, { labels });
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["labeling"] });
    },
  });
}

// ── Draft save ───────────────────────────────────────────────────────────────

export function useSaveDraft() {
  return useMutation({
    mutationFn: async ({
      taskId,
      labels,
    }: {
      taskId: number;
      labels: LabelInput[];
    }) => {
      const res = await labelingApi.post(`/tasks/${taskId}/labels/draft`, { labels });
      return res.data as { status: string; count: number };
    },
  });
}

// ── Add company ──────────────────────────────────────────────────────────────

export function useAddCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      taskId,
      companyName,
      companyMetadata,
    }: {
      taskId: number;
      companyName: string;
      companyMetadata?: Record<string, unknown>;
    }) => {
      const res = await labelingApi.post(`/tasks/${taskId}/add-company`, {
        company_name: companyName,
        company_metadata: companyMetadata ?? null,
      });
      return res.data as { id: number; company_name: string };
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ["labeling", "task", vars.taskId] });
    },
  });
}

// ── Delete company ───────────────────────────────────────────────────────────

export function useDeleteResult() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ taskId, resultId }: { taskId: number; resultId: number }) => {
      const res = await labelingApi.delete(`/tasks/${taskId}/results/${resultId}`);
      return res.data;
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ["labeling", "task", vars.taskId] });
    },
  });
}

// ── Rubric ────────────────────────────────────────────────────────────────────

export function useRubric() {
  return useQuery({
    queryKey: ["labeling", "rubric"],
    queryFn: async () => {
      const res = await labelingApi.get<RubricCriterion[]>("/rubric");
      return res.data;
    },
  });
}

// ── Admin ─────────────────────────────────────────────────────────────────────

export function useProgress() {
  return useQuery({
    queryKey: ["labeling", "progress"],
    queryFn: async () => {
      const res = await labelingApi.get<ProgressStats>("/admin/progress");
      return res.data;
    },
    refetchInterval: 30_000,
  });
}

export function useUcStats() {
  return useQuery({
    queryKey: ["labeling", "uc-stats"],
    queryFn: async () => {
      const res = await labelingApi.get<{ uc: string; count: number }[]>("/admin/uc-stats");
      return res.data;
    },
  });
}

export function useImportQueries() {
  return useMutation({
    mutationFn: async () => {
      const res = await labelingApi.post("/admin/import-queries");
      return res.data;
    },
  });
}

export function useLabelers() {
  return useQuery({
    queryKey: ["labeling", "labelers"],
    queryFn: async () => {
      const res = await labelingApi.get<LabelerInfo[]>("/admin/labelers");
      return res.data;
    },
  });
}

export function useAssignTask() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ taskId, userId }: { taskId: number; userId: number }) => {
      const res = await labelingApi.post(`/admin/tasks/${taskId}/assign`, { user_id: userId });
      return res.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["labeling"] });
    },
  });
}

export function useBulkAssign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      userId,
      start,
      end,
    }: {
      userId: number;
      start: number;
      end: number;
    }) => {
      const res = await labelingApi.post("/admin/tasks/bulk-assign", {
        user_id: userId,
        start,
        end,
      });
      return res.data as { status: string; count: number; assigned_to: number };
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["labeling"] });
    },
  });
}

export function useBulkUnassign() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      userId,
      start,
      end,
    }: {
      userId: number;
      start?: number;
      end?: number;
    }) => {
      const res = await labelingApi.post("/admin/tasks/bulk-unassign", {
        user_id: userId,
        start,
        end,
      });
      return res.data as { status: string; count: number };
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["labeling"] });
    },
  });
}
