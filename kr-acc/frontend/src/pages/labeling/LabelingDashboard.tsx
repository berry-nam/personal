import { useState } from "react";
import { useNavigate, useSearchParams } from "react-router";
import {
  useBulkAssign,
  useImportQueries,
  useLabelers,
  useMyCurrentTask,
  useNextTask,
  useProgress,
  useReopenTask,
  useTasks,
  useUcStats,
} from "@/api/labelingQueries";
import type { LabelingUser, LabelerStats } from "@/types/labeling";

const UC_LABELS: Record<string, string> = {
  "UC-1": "M&A 타겟 발굴",
  "UC-2": "경쟁사 탐색",
  "UC-3": "투자 대상 탐색",
  "UC-4": "매수자 탐색",
  "UC-5": "시장 탐색",
};

const PREFIX_LABELS: Record<string, string> = {
  A: "실제 고객 쿼리 + 증강",
  B: "검색 로그 기반",
  C: "경쟁사 탐색 특화",
  D: "실제 고객 (매도자)",
  E: "엣지 케이스",
  I: "투자대상 추가",
  L: "LinkedIn/프로젝트",
  M: "시장 탐색 특화",
  S: "페르소나/매트릭스 생성",
};

export default function LabelingDashboard() {
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab") ?? "";

  const user: LabelingUser | null = (() => {
    try {
      return JSON.parse(localStorage.getItem("labeling_user") ?? "null");
    } catch {
      return null;
    }
  })();

  const isAdmin = user?.role === "admin";

  const TABS = isAdmin
    ? (["대시보드", "작업큐", "히스토리"] as const)
    : (["내 작업", "작업큐", "히스토리"] as const);

  type Tab = (typeof TABS)[number];

  const TAB_MAP: Record<string, Tab> = { queue: "작업큐", history: "히스토리" };
  const activeTab: Tab = (TAB_MAP[tabParam] as Tab) ?? TABS[0];

  const setTab = (tab: Tab) => {
    if (tab === TABS[0]) setSearchParams({});
    else if (tab === "작업큐") setSearchParams({ tab: "queue" });
    else setSearchParams({ tab: "history" });
  };

  return (
    <main className="mx-auto max-w-6xl px-4 py-6">
      {/* Tab bar */}
      <div className="mb-6 flex gap-1 rounded-lg bg-gray-100 p-1">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setTab(tab)}
            className={`flex-1 rounded-md py-2 text-sm font-medium transition-all ${
              activeTab === tab
                ? "bg-white text-brand-600 shadow-sm"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {isAdmin && activeTab === "대시보드" && <AdminDashboardTab />}
      {!isAdmin && activeTab === "내 작업" && <LabelerDashboardTab userId={user?.id ?? 0} />}
      {activeTab === "작업큐" && <QueueTab isAdmin={isAdmin} />}
      {activeTab === "히스토리" && <HistoryTab />}
    </main>
  );
}

// ── Bulk Assign Panel ───────────────────────────────────────────────────────

function BulkAssignPanel({ pendingCount }: { pendingCount: number }) {
  const { data: labelers } = useLabelers();
  const bulkAssign = useBulkAssign();
  const [userId, setUserId] = useState<number | "">("");
  const [start, setStart] = useState("1");
  const [end, setEnd] = useState("100");
  const [result, setResult] = useState<string>("");

  const handleAssign = () => {
    if (!userId || !start || !end) return;
    const s = parseInt(start);
    const e = parseInt(end);
    if (isNaN(s) || isNaN(e) || s < 1 || e < s) return;

    const labeler = labelers?.find((l) => l.id === userId);
    bulkAssign.mutate(
      { userId: userId as number, start: s, end: e },
      {
        onSuccess: (data) => {
          setResult(`${labeler?.display_name}에게 ${data.count}건 배정 완료`);
          setTimeout(() => setResult(""), 4000);
        },
      },
    );
  };

  return (
    <div className="rounded-xl border border-brand-100 bg-brand-50 p-4">
      <h3 className="mb-3 text-sm font-semibold text-brand-800">작업 일괄 배정</h3>
      <p className="mb-3 text-xs text-brand-600">
        대기 중인 작업 {pendingCount.toLocaleString()}건 중, 범위를 지정하여 팀원에게 일괄 배정합니다.
        (쿼리 ID 순서 기준, 1번 = 첫 번째 대기 작업)
      </p>
      <div className="flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-brand-700">배정 대상</label>
          <select
            value={userId}
            onChange={(e) => setUserId(e.target.value ? parseInt(e.target.value) : "")}
            className="rounded-lg border border-brand-200 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none"
          >
            <option value="">팀원 선택</option>
            {labelers?.map((l) => (
              <option key={l.id} value={l.id}>{l.display_name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-brand-700">시작 번호</label>
          <input
            type="number"
            min={1}
            max={pendingCount}
            value={start}
            onChange={(e) => setStart(e.target.value)}
            className="w-24 rounded-lg border border-brand-200 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-brand-700">끝 번호</label>
          <input
            type="number"
            min={1}
            max={pendingCount}
            value={end}
            onChange={(e) => setEnd(e.target.value)}
            className="w-24 rounded-lg border border-brand-200 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none"
          />
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleAssign}
            disabled={!userId || bulkAssign.isPending}
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50"
          >
            {bulkAssign.isPending
              ? "배정 중..."
              : `${Math.max(0, (parseInt(end) || 0) - (parseInt(start) || 0) + 1)}건 배정`}
          </button>
          {start && end && parseInt(end) >= parseInt(start) && (
            <span className="text-xs text-brand-500">
              ({parseInt(start)}~{parseInt(end)}번째 대기 작업)
            </span>
          )}
        </div>
      </div>
      {result && (
        <div className="mt-3 rounded-lg bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700">
          {result}
        </div>
      )}
      {bulkAssign.isError && (
        <div className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
          배정 실패. 다시 시도해주세요.
        </div>
      )}
    </div>
  );
}

// ── Admin Dashboard ─────────────────────────────────────────────────────────

function AdminDashboardTab() {
  const { data: progress, isLoading } = useProgress();
  const importMutation = useImportQueries();

  if (isLoading) return <LoadingState />;
  if (!progress) return null;

  const completionPct =
    progress.total_tasks > 0
      ? Math.round(((progress.completed + progress.reviewed) / progress.total_tasks) * 100)
      : 0;

  return (
    <div className="flex flex-col gap-6">
      {/* Top row: progress ring + admin tools */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">전체 진행률</h2>
          <div className="flex items-center gap-6">
            <div className="relative h-28 w-28 shrink-0">
              <svg viewBox="0 0 36 36" className="h-full w-full -rotate-90">
                <circle cx="18" cy="18" r="15.5" fill="none" stroke="#e5e7eb" strokeWidth="3" />
                <circle
                  cx="18" cy="18" r="15.5"
                  fill="none" stroke="#0549cc" strokeWidth="3"
                  strokeDasharray={`${completionPct} ${100 - completionPct}`}
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl font-bold text-gray-900">{completionPct}%</span>
              </div>
            </div>
            <div className="flex flex-col gap-1.5 text-sm">
              <StatRow label="전체" value={progress.total_tasks} color="text-gray-900" />
              <StatRow label="대기" value={progress.pending} color="text-gray-500" />
              <StatRow label="진행중" value={progress.assigned} color="text-brand-500" />
              <StatRow label="완료" value={progress.completed} color="text-emerald-600" />
              <StatRow label="검토완료" value={progress.reviewed} color="text-purple-600" />
            </div>
          </div>
        </div>

        {/* Admin tools */}
        <div className="rounded-xl bg-white p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="mb-3 text-lg font-semibold text-gray-900">관리자 도구</h2>
            <div className="flex gap-3">
              <button
                onClick={() => importMutation.mutate()}
                disabled={importMutation.isPending}
                className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
              >
                {importMutation.isPending ? "임포트 중..." : "쿼리 임포트 (2,000건)"}
              </button>
              {importMutation.isSuccess && (
                <span className="self-center text-sm text-emerald-600">
                  {(importMutation.data as { imported: number }).imported > 0
                    ? `${(importMutation.data as { imported: number }).imported}건 임포트 완료`
                    : "이미 임포트됨"}
                </span>
              )}
            </div>
          </div>
          <div className="mt-4 rounded-lg bg-gray-50 px-3 py-2 text-xs text-gray-400">
            초대코드: <code className="rounded bg-gray-200 px-1 py-0.5 font-mono text-gray-600">cookiedeal2026</code>
          </div>
        </div>
      </div>

      {/* Bulk assign */}
      <BulkAssignPanel pendingCount={progress.pending} />

      {/* Team member table */}
      <div className="rounded-xl bg-white shadow-sm overflow-hidden">
        <div className="px-6 pt-5 pb-3">
          <h2 className="text-lg font-semibold text-gray-900">팀원별 현황</h2>
        </div>
        {progress.per_labeler.length === 0 ? (
          <div className="px-6 pb-5 text-sm text-gray-400">아직 등록된 팀원이 없습니다.</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-t bg-gray-50 text-left text-xs text-gray-500">
                <th className="px-6 py-2.5 font-medium">이름</th>
                <th className="px-6 py-2.5 font-medium">역할</th>
                <th className="px-6 py-2.5 font-medium text-center">완료</th>
                <th className="px-6 py-2.5 font-medium text-center">진행중</th>
                <th className="px-6 py-2.5 font-medium">현재 작업</th>
                <th className="px-6 py-2.5 font-medium">진행률</th>
              </tr>
            </thead>
            <tbody>
              {progress.per_labeler.map((p) => (
                <tr key={p.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="px-6 py-3">
                    <div className="font-medium text-gray-900">{p.name}</div>
                    <div className="text-xs text-gray-400">{p.email}</div>
                  </td>
                  <td className="px-6 py-3">
                    <span
                      className={`rounded px-1.5 py-0.5 text-xs font-medium ${
                        p.role === "admin"
                          ? "bg-brand-100 text-brand-700"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {p.role === "admin" ? "관리자" : "라벨러"}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-center">
                    <span className="text-lg font-bold text-emerald-600">{p.completed}</span>
                  </td>
                  <td className="px-6 py-3 text-center">
                    <span className={`text-lg font-bold ${p.assigned > 0 ? "text-brand-500" : "text-gray-300"}`}>
                      {p.assigned}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    {p.current_task ? (
                      <span className="rounded bg-brand-50 px-1.5 py-0.5 font-mono text-xs text-brand-600">
                        {p.current_task}
                      </span>
                    ) : (
                      <span className="text-xs text-gray-300">-</span>
                    )}
                  </td>
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-24 rounded-full bg-gray-100">
                        <div
                          className="h-2 rounded-full bg-brand-500 transition-all"
                          style={{
                            width: `${Math.min(100, (p.completed / Math.max(progress.total_tasks, 1)) * 100)}%`,
                            minWidth: p.completed > 0 ? "4px" : "0",
                          }}
                        />
                      </div>
                      <span className="text-[11px] text-gray-400">
                        {((p.completed / Math.max(progress.total_tasks, 1)) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

// ── Labeler Dashboard (non-admin) ───────────────────────────────────────────

function LabelerDashboardTab({ userId }: { userId: number }) {
  const navigate = useNavigate();
  const { data: currentTask } = useMyCurrentTask();
  const { data: progress, isLoading } = useProgress();
  const nextTask = useNextTask();

  const handleStartNext = async () => {
    try {
      const task = await nextTask.mutateAsync();
      navigate(`/labeling/tasks/${task.id}`);
    } catch {
      // No tasks available
    }
  };

  if (isLoading) return <LoadingState />;

  const myStats = progress?.per_labeler.find((p) => p.id === userId);
  const myCompleted = myStats?.completed ?? 0;
  const myAssigned = myStats?.assigned ?? 0;

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Current task */}
      <div className="rounded-xl bg-white p-6 shadow-sm md:col-span-2">
        {currentTask ? (
          <div className="flex items-center justify-between">
            <div>
              <h2 className="mb-2 text-lg font-semibold text-gray-900">현재 진행 중인 작업</h2>
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-brand-100 px-2 py-0.5 text-xs font-semibold text-brand-700">
                  진행 중
                </span>
                <span className="font-mono text-sm font-semibold text-gray-900">
                  {currentTask.query_id}
                </span>
              </div>
              <p className="mt-1 text-sm text-gray-600 truncate max-w-lg">
                {currentTask.query_text}
              </p>
              {currentTask.result_count > 0 && (
                <p className="mt-1 text-xs text-gray-500">
                  {currentTask.label_count} / {currentTask.result_count} 평가 완료
                </p>
              )}
            </div>
            <button
              onClick={() => navigate(`/labeling/tasks/${currentTask.id}`)}
              className="rounded-lg bg-brand-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-600"
            >
              계속하기
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <div>
              <h2 className="mb-1 text-lg font-semibold text-gray-900">새 작업 시작</h2>
              <p className="text-sm text-gray-500">현재 진행 중인 작업이 없습니다. 새 작업을 시작해보세요.</p>
            </div>
            <button
              onClick={handleStartNext}
              disabled={nextTask.isPending}
              className="rounded-lg bg-brand-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-brand-600 disabled:opacity-50"
            >
              {nextTask.isPending ? "할당 중..." : "다음 작업 시작"}
            </button>
          </div>
        )}
        {nextTask.isError && (
          <div className="mt-3 rounded-lg bg-yellow-50 px-3 py-2 text-sm text-yellow-700">
            현재 배정 가능한 작업이 없습니다.
          </div>
        )}
      </div>

      {/* My progress */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">내 진행 현황</h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-lg bg-emerald-50 p-4 text-center">
            <div className="text-3xl font-bold text-emerald-600">{myCompleted}</div>
            <div className="mt-1 text-xs text-emerald-700">완료한 작업</div>
          </div>
          <div className="rounded-lg bg-brand-50 p-4 text-center">
            <div className="text-3xl font-bold text-brand-500">{myAssigned}</div>
            <div className="mt-1 text-xs text-brand-700">진행 중</div>
          </div>
        </div>
      </div>

      {/* Overall progress */}
      {progress && (
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">전체 진행률</h2>
          <div className="flex flex-col gap-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-500">전체 작업</span>
              <span className="font-semibold">{progress.total_tasks.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-500">완료</span>
              <span className="font-semibold text-emerald-600">
                {(progress.completed + progress.reviewed).toLocaleString()}
              </span>
            </div>
            <div className="mt-2 h-3 w-full rounded-full bg-gray-100">
              <div
                className="h-3 rounded-full bg-brand-500"
                style={{
                  width: `${Math.round(((progress.completed + progress.reviewed) / Math.max(progress.total_tasks, 1)) * 100)}%`,
                }}
              />
            </div>
            <div className="text-right text-xs text-gray-400">
              {Math.round(((progress.completed + progress.reviewed) / Math.max(progress.total_tasks, 1)) * 100)}%
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Queue Tab ────────────────────────────────────────────────────────────────

function QueueTab({ isAdmin }: { isAdmin: boolean }) {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const { data, isLoading } = useTasks(page, 20, "pending");
  const { data: currentTask } = useMyCurrentTask();
  const { data: ucStats } = useUcStats();
  const nextTask = useNextTask();

  const handleStartNext = async () => {
    try {
      const task = await nextTask.mutateAsync();
      navigate(`/labeling/tasks/${task.id}`);
    } catch {
      // No tasks available
    }
  };

  if (isLoading) return <LoadingState />;

  const totalPending = data?.total ?? 0;
  const ucStatsMap = new Map(ucStats?.map((u) => [u.uc, u.count]) ?? []);

  return (
    <div>
      {/* Resume in-progress task */}
      {currentTask && (
        <div className="mb-4 rounded-xl border-2 border-brand-200 bg-brand-50 p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="rounded-full bg-brand-100 px-2 py-0.5 text-xs font-semibold text-brand-700">
                  진행 중
                </span>
                <span className="font-mono text-sm font-semibold text-gray-900">
                  {currentTask.query_id}
                </span>
              </div>
              <p className="mt-1 text-sm text-gray-600 truncate max-w-lg">
                {currentTask.query_text}
              </p>
              {currentTask.result_count > 0 && (
                <p className="mt-1 text-xs text-gray-500">
                  {currentTask.label_count} / {currentTask.result_count} 평가 완료
                </p>
              )}
            </div>
            <button
              onClick={() => navigate(`/labeling/tasks/${currentTask.id}`)}
              className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-600"
            >
              계속하기
            </button>
          </div>
        </div>
      )}

      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">
          대기 중인 작업 ({totalPending.toLocaleString()}건)
        </h2>
        {!currentTask && (
          <button
            onClick={handleStartNext}
            disabled={nextTask.isPending}
            className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-50"
          >
            {nextTask.isPending ? "할당 중..." : "다음 작업 시작"}
          </button>
        )}
      </div>

      {nextTask.isError && (
        <div className="mb-4 rounded-lg bg-yellow-50 px-3 py-2 text-sm text-yellow-700">
          현재 라벨링 가능한 작업이 없습니다.
        </div>
      )}

      {/* Bulk assign (admin only) */}
      {isAdmin && (
        <div className="mb-4">
          <BulkAssignPanel pendingCount={totalPending} />
        </div>
      )}

      {/* Legend: UC codes with stats + Prefixes */}
      <div className="mb-4 rounded-xl border border-brand-200 bg-brand-50 p-4">
        <div className="grid grid-cols-2 gap-6 text-xs">
          <div>
            <div className="mb-2 flex items-center gap-2">
              <span className="font-bold text-brand-700">UC (Use Case)</span>
              <span className="rounded bg-brand-100 px-1.5 py-0.5 text-[10px] font-medium text-brand-600">{totalPending.toLocaleString()}건</span>
            </div>
            <div className="flex flex-col gap-1">
              {Object.entries(UC_LABELS).map(([k, v]) => {
                const cnt = ucStatsMap.get(k) ?? 0;
                const pct = totalPending > 0 ? ((cnt / totalPending) * 100).toFixed(1) : "0";
                return (
                  <div key={k} className="flex items-center gap-1.5">
                    <span className="w-5 rounded bg-brand-100 py-0.5 text-center font-mono font-semibold text-brand-700">{k.replace("UC-", "")}</span>
                    <span className="w-[5.5rem] text-brand-800">{v}</span>
                    <span className="font-semibold tabular-nums text-brand-600">{cnt.toLocaleString()}</span>
                    <span className="text-brand-400 tabular-nums">({pct}%)</span>
                  </div>
                );
              })}
            </div>
          </div>
          <div>
            <div className="mb-2 font-bold text-brand-700">쿼리 ID 접두사</div>
            <div className="flex flex-col gap-1">
              {Object.entries(PREFIX_LABELS).map(([k, v]) => (
                <div key={k} className="flex items-center gap-2">
                  <span className="w-5 rounded bg-brand-100 text-center font-mono font-bold text-brand-700">{k}</span>
                  <span className="text-brand-800">{v}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Column header */}
      <div className="mb-1 flex items-center gap-3 px-4 text-[11px] font-medium text-gray-400">
        <span className="w-12">ID</span>
        <span className="flex-1">쿼리</span>
        <span className="w-16 text-center">UC</span>
        <span className="w-20 text-center">섹터</span>
        <span className="w-16 text-center">복잡도</span>
      </div>

      <div className="grid gap-2">
        {data?.items.map((task) => (
          <div
            key={task.id}
            className="flex items-center gap-3 rounded-lg bg-white px-4 py-3 shadow-sm"
          >
            <span className="w-12 shrink-0 font-mono text-sm text-gray-400">{task.query_id}</span>
            <span className="flex-1 truncate text-sm text-gray-700">{task.query_text}</span>
            <span className="w-16 shrink-0 text-center rounded bg-brand-50 px-1.5 py-0.5 text-xs text-brand-600">
              {task.query_metadata.uc ?? "-"}
            </span>
            <span className="w-20 shrink-0 text-center rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-500">
              {task.query_metadata.sector}
            </span>
            <span className="w-16 shrink-0 text-center rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-500">
              {task.query_metadata.complexity}
            </span>
          </div>
        ))}
      </div>

      {data && data.pages > 1 && (
        <Pagination page={page} pages={data.pages} onPage={setPage} />
      )}
    </div>
  );
}

// ── History Tab ──────────────────────────────────────────────────────────────

function HistoryTab() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const { data, isLoading } = useTasks(page, 20, "completed");
  const reopenMutation = useReopenTask();

  const handleEdit = async (taskId: number) => {
    await reopenMutation.mutateAsync(taskId);
    navigate(`/labeling/tasks/${taskId}`);
  };

  if (isLoading) return <LoadingState />;

  return (
    <div>
      <h2 className="mb-4 text-lg font-semibold text-gray-900">
        완료된 작업 ({data?.total ?? 0}건)
      </h2>
      <div className="grid gap-2">
        {data?.items.map((task) => (
          <div
            key={task.id}
            className="flex items-center gap-3 rounded-lg bg-white px-4 py-3 shadow-sm"
          >
            <span className="font-mono text-sm text-gray-400">{task.query_id}</span>
            <span className="flex-1 truncate text-sm text-gray-700">{task.query_text}</span>
            <span className="rounded bg-emerald-100 px-2 py-0.5 text-xs text-emerald-700">
              완료
            </span>
            {task.completed_at && (
              <span className="text-xs text-gray-400">
                {new Date(task.completed_at).toLocaleDateString("ko-KR")}
              </span>
            )}
            <button
              onClick={() => handleEdit(task.id)}
              disabled={reopenMutation.isPending}
              className="rounded border border-brand-200 px-2.5 py-1 text-xs font-medium text-brand-600 hover:bg-brand-50"
            >
              수정
            </button>
          </div>
        ))}
      </div>

      {data && data.pages > 1 && (
        <Pagination page={page} pages={data.pages} onPage={setPage} />
      )}
    </div>
  );
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function StatRow({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-16 text-gray-500">{label}</span>
      <span className={`font-semibold ${color}`}>{value.toLocaleString()}</span>
    </div>
  );
}

function Pagination({ page, pages, onPage }: { page: number; pages: number; onPage: (p: number) => void }) {
  return (
    <div className="mt-4 flex justify-center gap-2">
      <button
        onClick={() => onPage(Math.max(1, page - 1))}
        disabled={page <= 1}
        className="rounded px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-50"
      >
        이전
      </button>
      <span className="self-center text-sm text-gray-500">
        {page} / {pages}
      </span>
      <button
        onClick={() => onPage(Math.min(pages, page + 1))}
        disabled={page >= pages}
        className="rounded px-3 py-1 text-sm text-gray-600 hover:bg-gray-100 disabled:opacity-50"
      >
        다음
      </button>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="flex h-48 items-center justify-center">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-brand-500" />
    </div>
  );
}
