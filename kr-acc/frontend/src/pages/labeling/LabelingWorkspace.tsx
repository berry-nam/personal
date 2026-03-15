import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router";
import {
  useAddCompany,
  useDeleteResult,
  useRubric,
  useSaveDraft,
  useSkipTask,
  useSubmitLabels,
  useTask,
} from "@/api/labelingQueries";
import type { LabelInput, RubricCriterion, TaskResult } from "@/types/labeling";

/* ─── Constants ──────────────────────────────────────────────────────────── */

const RATINGS = [
  { value: 1, label: "무관", bg: "bg-red-50", border: "border-red-200", text: "text-red-700", activeBg: "bg-red-500" },
  { value: 2, label: "약함", bg: "bg-orange-50", border: "border-orange-200", text: "text-orange-700", activeBg: "bg-orange-500" },
  { value: 3, label: "보통", bg: "bg-yellow-50", border: "border-yellow-200", text: "text-yellow-700", activeBg: "bg-yellow-500" },
  { value: 4, label: "우수", bg: "bg-blue-50", border: "border-blue-200", text: "text-blue-700", activeBg: "bg-blue-500" },
  { value: 5, label: "완벽", bg: "bg-emerald-50", border: "border-emerald-200", text: "text-emerald-700", activeBg: "bg-emerald-500" },
] as const;

const RUBRIC_OPTIONS = [
  { value: "yes", label: "충족", active: "bg-emerald-500 text-white", inactive: "bg-white text-emerald-700 border-emerald-200 hover:bg-emerald-50" },
  { value: "partially", label: "부분충족", active: "bg-yellow-500 text-white", inactive: "bg-white text-yellow-700 border-yellow-200 hover:bg-yellow-50" },
  { value: "no", label: "미충족", active: "bg-red-500 text-white", inactive: "bg-white text-red-700 border-red-200 hover:bg-red-50" },
  { value: "na", label: "N/A", active: "bg-gray-500 text-white", inactive: "bg-white text-gray-500 border-gray-200 hover:bg-gray-50" },
] as const;

const UC_LABELS: Record<string, string> = {
  "UC-1": "M&A 타겟 발굴",
  "UC-2": "경쟁사 탐색",
  "UC-3": "투자 대상 탐색",
  "UC-4": "매수자 탐색",
  "UC-5": "시장 탐색",
};

/* ─── Paste parser ────────────────────────────────────────────────────────── */

/** Parse CookieDeal company detail text (copy-pasted) into structured fields. */
/** Parse Korean currency text (e.g. "55.7조원", "125.1억원", "3,500만원") → 천원 단위 */
function parseKrwToCheonwon(text: string): number | null {
  const s = text.replace(/,/g, "").trim();
  let m = s.match(/([\d.]+)\s*조/);
  if (m) return Math.round(parseFloat(m[1]) * 10000000000 / 1000); // 조 → 천원
  m = s.match(/([\d.]+)\s*억/);
  if (m) return Math.round(parseFloat(m[1]) * 100000); // 억 → 천원
  m = s.match(/([\d.]+)\s*만/);
  if (m) return Math.round(parseFloat(m[1]) * 10); // 만원 → 천원
  return null;
}

function parseCookieDealPaste(text: string): Record<string, string> {
  const result: Record<string, string> = {};
  const lines = text.split("\n").map((l) => l.trim()).filter(Boolean);
  if (lines.length === 0) return result;

  // First non-empty line is company name (if not a known label)
  const LABELS = ["법인 형태 표기", "직원수", "대표", "주소", "설립일", "홈페이지", "업종", "사업자 번호", "주요 생산품", "기업 유형", "사업 주체", "매출액", "영업이익", "자산총계", "자본총계", "부채총계", "기업 정보"];
  if (!LABELS.some((l) => lines[0].startsWith(l))) {
    result.company_name = lines[0];
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const nextLine = i + 1 < lines.length ? lines[i + 1] : "";
    if (line === "대표" || line === "대표자") result.ceo = nextLine;
    else if (line === "업종") result.industry = nextLine;
    else if (line === "주요 생산품" || line === "생산품") result.products = nextLine;
    else if (line === "사업자 번호" || line === "사업자등록번호") result.brn = nextLine.replace(/-/g, "").replace(/\s/g, "");
    else if (line === "홈페이지") result.homepage = nextLine;
    else if (line === "기업 유형" || line === "기업유형") result.company_type = nextLine;
    else if (line === "법인 형태 표기") result.legal_name = nextLine;
    else if (line === "직원수") result.employees = nextLine;
    else if (line === "주소") result.address = nextLine;
    else if (line === "설립일") result.founded = nextLine;
    else if (line === "매출액") {
      const v = parseKrwToCheonwon(nextLine);
      if (v != null) result.revenue = String(v);
      else result.revenue_text = nextLine;
    } else if (line === "영업이익") {
      const v = parseKrwToCheonwon(nextLine);
      if (v != null) result.operating_profit = String(v);
      else result.op_text = nextLine;
    } else if (line === "자산총계") {
      const v = parseKrwToCheonwon(nextLine);
      if (v != null) result.total_assets = String(v);
    } else if (line === "자본총계") {
      const v = parseKrwToCheonwon(nextLine);
      if (v != null) result.equity = String(v);
    } else if (line === "부채총계") {
      const v = parseKrwToCheonwon(nextLine);
      if (v != null) result.debt = String(v);
    }
  }

  // Use legal_name as company_name fallback
  if (!result.company_name && result.legal_name) {
    result.company_name = result.legal_name;
  }

  return result;
}

/* ─── Types ──────────────────────────────────────────────────────────────── */

interface CompanyLabelState {
  resultId: number;
  rating: number | null;
  justification: string;
  rubricScores: { criterion_id: number; score: "" | "yes" | "partially" | "no" | "na" }[];
}

/* ─── Main Component ─────────────────────────────────────────────────────── */

export default function LabelingWorkspace() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const id = taskId ? parseInt(taskId) : null;

  const { data: task, isLoading } = useTask(id);
  const { data: criteria } = useRubric();
  const submitMutation = useSubmitLabels();
  const skipMutation = useSkipTask();
  const draftMutation = useSaveDraft();

  const [phase, setPhase] = useState<"intro" | "work">("intro");
  const [labels, setLabels] = useState<Map<number, CompanyLabelState>>(new Map());
  const [draftStatus, setDraftStatus] = useState<"" | "saving" | "saved">("");
  const labelsRef = useRef(labels);
  labelsRef.current = labels;

  // Initialize labels when task loads — restore from existing labels if present
  useEffect(() => {
    if (!task?.results || !criteria) return;
    const init = new Map<number, CompanyLabelState>();
    for (const r of task.results) {
      // Check if there are existing labels (draft restore)
      const existingLabel = task.labels?.find((l) => l.result_id === r.id);
      if (existingLabel) {
        init.set(r.id, {
          resultId: r.id,
          rating: existingLabel.overall_rating,
          justification: existingLabel.justification ?? "",
          rubricScores: criteria.map((c) => {
            const rs = existingLabel.rubric_scores?.find((s) => s.criterion_id === c.id);
            return { criterion_id: c.id, score: (rs?.score as "" | "yes" | "partially" | "no") ?? "" };
          }),
        });
      } else {
        init.set(r.id, {
          resultId: r.id,
          rating: null,
          justification: "",
          rubricScores: criteria.map((c) => ({ criterion_id: c.id, score: "" })),
        });
      }
    }
    setLabels(init);
    // If existing labels found, skip intro
    if (task.labels && task.labels.length > 0) {
      setPhase("work");
    }
  }, [task, criteria]);

  // Autosave with debounce (5 seconds)
  useEffect(() => {
    if (phase !== "work" || !task) return;
    const timer = setTimeout(() => {
      const currentLabels = labelsRef.current;
      const rated = [...currentLabels.values()].filter((l) => l.rating !== null);
      if (rated.length === 0) return;

      const inputs: LabelInput[] = rated.map((l, idx) => ({
        result_id: l.resultId,
        overall_rating: l.rating!,
        rank_position: idx + 1,
        justification: l.justification || null,
        rubric_scores: l.rubricScores
          .filter((s) => s.score !== "")
          .map((s) => ({ criterion_id: s.criterion_id, score: s.score })),
      }));

      setDraftStatus("saving");
      draftMutation.mutate(
        { taskId: task.id, labels: inputs },
        {
          onSuccess: () => {
            setDraftStatus("saved");
            setTimeout(() => setDraftStatus(""), 2000);
          },
          onError: () => setDraftStatus(""),
        },
      );
    }, 5000);
    return () => clearTimeout(timer);
  }, [labels, phase, task]);

  const updateLabel = useCallback(
    (resultId: number, update: Partial<CompanyLabelState>) => {
      setLabels((prev) => {
        const next = new Map(prev);
        const existing = next.get(resultId);
        if (existing) next.set(resultId, { ...existing, ...update });
        return next;
      });
    },
    [],
  );

  const ratedCount = useMemo(() => {
    if (!task?.results) return 0;
    return task.results.filter((r) => labels.get(r.id)?.rating != null).length;
  }, [task, labels]);

  const missingJustification = useMemo(() => {
    if (!task?.results) return 0;
    return task.results.filter((r) => {
      const l = labels.get(r.id);
      return l?.rating != null && (!l.justification || l.justification.trim().length < 20);
    }).length;
  }, [task, labels]);

  const isComplete = useMemo(() => {
    if (!task?.results || task.results.length === 0) return false;
    return ratedCount === task.results.length && missingJustification === 0;
  }, [task, ratedCount, missingJustification]);

  const handleSubmit = async () => {
    if (!task || !isComplete) return;
    const sorted = [...labels.entries()].sort((a, b) => (b[1].rating ?? 0) - (a[1].rating ?? 0));
    let rank = 1;
    const inputs: LabelInput[] = [];
    for (const [, l] of sorted) {
      if (l.rating === null) continue;
      inputs.push({
        result_id: l.resultId,
        overall_rating: l.rating,
        rank_position: rank++,
        justification: l.justification || null,
        rubric_scores: l.rubricScores
          .filter((s) => s.score !== "")
          .map((s) => ({ criterion_id: s.criterion_id, score: s.score })),
      });
    }
    await submitMutation.mutateAsync({ taskId: task.id, labels: inputs });
    navigate("/labeling?tab=queue");
  };

  const handleSkip = async () => {
    if (!task) return;
    await skipMutation.mutateAsync(task.id);
    navigate("/labeling?tab=queue");
  };

  if (isLoading || !task) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-gray-300 border-t-gray-900" />
      </div>
    );
  }

  const hasExistingLabels = (task?.labels?.length ?? 0) > 0;

  if (phase === "intro") {
    return (
      <IntroPhase
        task={task}
        isResume={hasExistingLabels}
        onStart={() => setPhase("work")}
        onBack={() => navigate("/labeling?tab=queue")}
      />
    );
  }

  return (
    <WorkPhase
      task={task}
      criteria={criteria ?? []}
      labels={labels}
      ratedCount={ratedCount}
      isComplete={isComplete}
      updateLabel={updateLabel}
      onSubmit={handleSubmit}
      onSkip={handleSkip}
      onBack={() => navigate("/labeling?tab=queue")}
      submitPending={submitMutation.isPending}
      skipPending={skipMutation.isPending}
      draftStatus={draftStatus}
      missingJustification={missingJustification}
    />
  );
}

/* ─── Intro Phase ────────────────────────────────────────────────────────── */

function IntroPhase({
  task,
  isResume,
  onStart,
  onBack,
}: {
  task: { query_id: string; query_text: string; query_metadata: Record<string, string>; results: TaskResult[] };
  isResume: boolean;
  onStart: () => void;
  onBack: () => void;
}) {
  const meta = task.query_metadata;
  const hasResults = task.results.length > 0;

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <button onClick={onBack} className="mb-6 flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
        <span>←</span> 대시보드로 돌아가기
      </button>
      <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
        <div className="mb-6 text-center">
          <span className="inline-block rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold text-brand-700">{task.query_id}</span>
          <h1 className="mt-3 text-xl font-bold text-gray-900">기업탐색 라벨링 작업</h1>
          <p className="mt-1 text-sm text-gray-500">아래 쿼리를 읽고, 조건에 맞는 기업을 평가하거나 직접 추가합니다.</p>
        </div>
        <div className="mb-6 rounded-xl bg-gray-50 p-5">
          <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-400">쿼리</div>
          <p className="text-base leading-relaxed text-gray-800">{task.query_text}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {meta.uc && <MetaBadge label={UC_LABELS[meta.uc] ?? meta.uc} color="bg-brand-100 text-brand-700" />}
            {meta.sector && <MetaBadge label={meta.sector} color="bg-brand-100 text-brand-700" />}
            {meta.size && <MetaBadge label={meta.size} color="bg-green-100 text-green-700" />}
            {meta.complexity && <MetaBadge label={`복잡도: ${meta.complexity}`} color="bg-orange-100 text-orange-700" />}
            {meta.audit && <MetaBadge label={`외감: ${meta.audit}`} color="bg-gray-200 text-gray-700" />}
          </div>
        </div>
        <div className="mb-6 rounded-xl border border-brand-100 bg-brand-50 p-4">
          {hasResults ? (
            <p className="text-sm text-brand-800">
              이 쿼리에 <strong>{task.results.length}개</strong>의 기업 결과가 등록되어 있습니다. 각 기업을 평가하고, 추가로 기업을 찾아 추가할 수도 있습니다.
            </p>
          ) : (
            <p className="text-sm text-brand-800">이 쿼리에 아직 등록된 기업이 없습니다. <strong>직접 기업을 찾아 추가</strong>해 주세요.</p>
          )}
        </div>
        <div className="mb-8">
          <h3 className="mb-3 text-sm font-semibold text-gray-700">작업 방법</h3>
          <div className="flex flex-col gap-2">
            <InstructionStep num={1} title="쿼리 확인" desc="위 쿼리의 조건(업종, 매출, 규모 등)을 꼼꼼히 읽으세요." />
            <InstructionStep num={2} title="기업 평가" desc="등록된 기업 결과가 있으면, 각 기업이 쿼리 조건에 얼마나 부합하는지 1~5점으로 평가하세요." />
            <InstructionStep num={3} title="기업 추가" desc="쿠키딜 기업탐색으로 쿼리에 맞는 기업을 찾고, 근거와 함께 추가하세요." />
            <InstructionStep num={4} title="제출" desc="모든 기업을 평가한 후 제출하세요. (자동 저장됩니다)" />
          </div>
        </div>
        <button onClick={onStart} className="w-full rounded-xl bg-gray-900 py-3 text-sm font-semibold text-white transition-colors hover:bg-gray-800">
          {isResume ? "계속하기" : "작업 시작하기"}
        </button>
      </div>
    </div>
  );
}

/* ─── Work Phase ─────────────────────────────────────────────────────────── */

function WorkPhase({
  task,
  criteria,
  labels,
  ratedCount,
  isComplete,
  updateLabel,
  onSubmit,
  onSkip,
  onBack,
  submitPending,
  skipPending,
  draftStatus,
  missingJustification,
}: {
  task: { id: number; query_id: string; query_text: string; query_metadata: Record<string, string>; results: TaskResult[] };
  criteria: RubricCriterion[];
  labels: Map<number, CompanyLabelState>;
  ratedCount: number;
  isComplete: boolean;
  updateLabel: (resultId: number, update: Partial<CompanyLabelState>) => void;
  onSubmit: () => void;
  onSkip: () => void;
  onBack: () => void;
  submitPending: boolean;
  skipPending: boolean;
  draftStatus: string;
  missingJustification: number;
}) {
  const meta = task.query_metadata;
  const addCompanyMutation = useAddCompany();
  const deleteResultMutation = useDeleteResult();
  const [addMode, setAddMode] = useState<"" | "paste" | "form">("");
  const [pasteText, setPasteText] = useState("");
  const [newCompany, setNewCompany] = useState({
    company_name: "", brn: "", ceo: "", industry: "", products: "",
    revenue: "", operating_profit: "", total_assets: "", equity: "",
    debt: "", company_type: "", homepage: "", fiscal_year: "2024",
  });

  const handleParsePaste = () => {
    const parsed = parseCookieDealPaste(pasteText);
    setNewCompany({
      company_name: parsed.company_name ?? "",
      brn: parsed.brn ?? "",
      ceo: parsed.ceo ?? "",
      industry: parsed.industry ?? "",
      products: parsed.products ?? "",
      revenue: parsed.revenue ?? "",
      operating_profit: parsed.operating_profit ?? "",
      total_assets: parsed.total_assets ?? "",
      equity: parsed.equity ?? "",
      debt: parsed.debt ?? "",
      company_type: parsed.company_type ?? "",
      homepage: parsed.homepage ?? "",
      fiscal_year: parsed.fiscal_year ?? "2024",
    });
    setPasteText("");
    setAddMode("form");
  };

  const buildMetadata = () => {
    const metadata: Record<string, unknown> = {};
    if (newCompany.brn) metadata.brn = newCompany.brn;
    if (newCompany.ceo) metadata.ceo = newCompany.ceo;
    if (newCompany.industry) metadata.industry = newCompany.industry;
    if (newCompany.products) metadata.products = newCompany.products;
    if (newCompany.revenue) metadata.revenue = parseInt(newCompany.revenue) || 0;
    if (newCompany.operating_profit) metadata.operating_profit = parseInt(newCompany.operating_profit) || 0;
    if (newCompany.total_assets) metadata.total_assets = parseInt(newCompany.total_assets) || 0;
    if (newCompany.equity) metadata.equity = parseInt(newCompany.equity) || 0;
    if (newCompany.debt) metadata.debt = parseInt(newCompany.debt) || 0;
    if (newCompany.company_type) metadata.company_type = newCompany.company_type;
    if (newCompany.homepage) metadata.homepage = newCompany.homepage;
    if (newCompany.fiscal_year) metadata.fiscal_year = newCompany.fiscal_year;
    if (newCompany.revenue && newCompany.operating_profit) {
      const rev = parseInt(newCompany.revenue);
      const op = parseInt(newCompany.operating_profit);
      if (rev > 0) metadata.op_margin = ((op / rev) * 100).toFixed(1) + "%";
    }
    return metadata;
  };

  const handleAddCompany = async () => {
    if (!newCompany.company_name.trim()) return;
    const name = newCompany.company_name.trim();

    // Check if company already exists in this task
    const existing = task.results.find(
      (r) => r.company_name.trim() === name,
    );
    if (existing) {
      const ok = window.confirm(
        `"${name}"은(는) 이미 존재합니다. 메타데이터를 업데이트할까요?`,
      );
      if (!ok) return;
    }

    const metadata = buildMetadata();
    await addCompanyMutation.mutateAsync({
      taskId: task.id,
      companyName: name,
      companyMetadata: Object.keys(metadata).length > 0 ? metadata : undefined,
    });
    setNewCompany({ company_name: "", brn: "", ceo: "", industry: "", products: "", revenue: "", operating_profit: "", total_assets: "", equity: "", debt: "", company_type: "", homepage: "", fiscal_year: "2024" });
    setAddMode("");
  };

  const handleDeleteResult = async (resultId: number) => {
    if (!confirm("이 기업을 삭제하시겠습니까?")) return;
    await deleteResultMutation.mutateAsync({ taskId: task.id, resultId });
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-6">
      {/* Top bar */}
      <div className="mb-4 flex items-center justify-between">
        <button onClick={onBack} className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700">
          <span>←</span> 대시보드
        </button>
        <div className="flex items-center gap-2">
          {draftStatus === "saving" && <span className="text-xs text-gray-400">저장 중...</span>}
          {draftStatus === "saved" && <span className="text-xs text-emerald-500">자동 저장됨</span>}
          <button onClick={onSkip} disabled={skipPending} className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-500 hover:bg-gray-50">
            건너뛰기
          </button>
          <button onClick={onSubmit} disabled={!isComplete || submitPending} className="rounded-lg bg-gray-900 px-4 py-1.5 text-sm font-semibold text-white hover:bg-gray-800 disabled:opacity-40">
            {submitPending ? "제출 중..." : "제출하기"}
          </button>
        </div>
      </div>
      {missingJustification > 0 && ratedCount > 0 && (
        <div className="mx-auto max-w-5xl px-4 -mt-1 mb-2">
          <p className="text-xs text-red-500">판단근거 미작성 {missingJustification}건 (20자 이상 필수)</p>
        </div>
      )}

      {/* Query bar */}
      <div className="mb-6 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <div className="flex items-start gap-3">
          <span className="shrink-0 rounded-full bg-brand-100 px-2.5 py-0.5 text-xs font-semibold text-brand-700">{task.query_id}</span>
          <div className="min-w-0 flex-1">
            <p className="text-sm leading-relaxed text-gray-800">{task.query_text}</p>
            <div className="mt-2 flex flex-wrap gap-1.5">
              {meta.uc && <MetaBadge label={UC_LABELS[meta.uc] ?? meta.uc} color="bg-brand-50 text-brand-600" />}
              {meta.sector && <MetaBadge label={meta.sector} color="bg-brand-50 text-brand-600" />}
              {meta.size && <MetaBadge label={meta.size} color="bg-green-50 text-green-600" />}
            </div>
          </div>
        </div>
      </div>

      {/* Progress */}
      {task.results.length > 0 && (
        <div className="mb-4 flex items-center gap-3">
          <div className="flex-1 rounded-full bg-gray-100">
            <div className="h-1.5 rounded-full bg-emerald-500 transition-all" style={{ width: `${(ratedCount / task.results.length) * 100}%` }} />
          </div>
          <span className="shrink-0 text-xs text-gray-500">{ratedCount} / {task.results.length} 평가 완료</span>
        </div>
      )}

      {/* Company cards */}
      {task.results.length > 0 && (
        <div className="mb-6">
          <h3 className="mb-3 text-sm font-semibold text-gray-700">기업 결과 ({task.results.length}건)</h3>
          <div className="flex flex-col gap-4">
            {[...task.results].sort((a, b) => (a.rank_position ?? 9999) - (b.rank_position ?? 9999)).map((r, idx) => (
              <CompanyEvalCard key={r.id} index={idx + 1} result={r} label={labels.get(r.id) ?? null} criteria={criteria} onUpdate={(update) => updateLabel(r.id, update)} onDelete={() => handleDeleteResult(r.id)} />
            ))}
          </div>
        </div>
      )}

      {/* Add company section */}
      <div className="mb-8 rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 p-5">
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-sm font-semibold text-gray-700">기업 직접 추가</h3>
          <a href="https://cookiedeal.io/company-search" target="_blank" rel="noopener noreferrer" className="text-xs text-brand-500 hover:text-brand-700 hover:underline">
            쿠키딜에서 검색 →
          </a>
        </div>
        <p className="mb-3 text-xs text-gray-500">쿠키딜 기업탐색에서 기업 상세 정보를 복사하여 붙여넣거나, 직접 입력하세요.</p>

        {addMode === "" && (
          <div className="flex gap-2">
            <button onClick={() => setAddMode("paste")} className="flex-1 rounded-lg border border-brand-200 bg-brand-50 py-2.5 text-sm font-medium text-brand-700 hover:bg-brand-100">
              붙여넣기로 추가
            </button>
            <button onClick={() => setAddMode("form")} className="flex-1 rounded-lg border border-gray-300 bg-white py-2.5 text-sm text-gray-600 hover:bg-gray-50">
              직접 입력
            </button>
          </div>
        )}

        {addMode === "paste" && (
          <div className="rounded-lg border border-gray-200 bg-white p-4">
            <p className="mb-2 text-xs text-gray-500">쿠키딜 기업 상세 페이지에서 텍스트를 전체 선택(Ctrl+A) 후 복사 붙여넣기 하세요.</p>
            <textarea
              value={pasteText}
              onChange={(e) => setPasteText(e.target.value)}
              placeholder={"큐브리펀드\n기업 정보\n법인 형태 표기\n(주)큐브리펀드\n직원수\n27명\n대표\n좌정훈\n...\n매출액\n125.1억원\n영업이익\n21.2억원"}
              rows={8}
              className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-700 font-mono placeholder-gray-300 focus:border-brand-500 focus:outline-none"
            />
            <div className="mt-3 flex gap-2">
              <button onClick={handleParsePaste} disabled={!pasteText.trim()} className="rounded-lg bg-brand-500 px-4 py-2 text-sm font-medium text-white hover:bg-brand-600 disabled:opacity-40">
                자동 분류
              </button>
              <button onClick={() => { setAddMode(""); setPasteText(""); }} className="rounded-lg border border-gray-200 px-4 py-2 text-sm text-gray-500 hover:bg-gray-50">
                취소
              </button>
            </div>
          </div>
        )}

        {addMode === "form" && (
          <div className="rounded-lg border border-gray-200 bg-white p-4">
            <div className="grid grid-cols-2 gap-3">
              <FormField label="기업명 *" value={newCompany.company_name} onChange={(v) => setNewCompany((p) => ({ ...p, company_name: v }))} placeholder="(주)쿠키딜" />
              <FormField label="사업자등록번호 *" value={newCompany.brn} onChange={(v) => setNewCompany((p) => ({ ...p, brn: v }))} placeholder="000-00-00000" />
              <FormField label="대표자명 *" value={newCompany.ceo} onChange={(v) => setNewCompany((p) => ({ ...p, ceo: v }))} placeholder="홍길동" />
              <FormField label="업종 *" value={newCompany.industry} onChange={(v) => setNewCompany((p) => ({ ...p, industry: v }))} placeholder="소프트웨어 개발" />
              <FormField label="생산품/주요사업 *" value={newCompany.products} onChange={(v) => setNewCompany((p) => ({ ...p, products: v }))} placeholder="기업정보 플랫폼" colSpan />
              <FormField label="매출액 (천원) *" value={newCompany.revenue} onChange={(v) => setNewCompany((p) => ({ ...p, revenue: v }))} placeholder="10000000" type="number" />
              <FormField label="영업이익 (천원) *" value={newCompany.operating_profit} onChange={(v) => setNewCompany((p) => ({ ...p, operating_profit: v }))} placeholder="1000000" type="number" />
              <FormField label="자산총계 (천원)" value={newCompany.total_assets} onChange={(v) => setNewCompany((p) => ({ ...p, total_assets: v }))} placeholder="선택" type="number" />
              <FormField label="자본총계 (천원)" value={newCompany.equity} onChange={(v) => setNewCompany((p) => ({ ...p, equity: v }))} placeholder="선택" type="number" />
              <FormField label="부채총계 (천원)" value={newCompany.debt} onChange={(v) => setNewCompany((p) => ({ ...p, debt: v }))} placeholder="선택" type="number" />
              <FormField label="기준년도 *" value={newCompany.fiscal_year} onChange={(v) => setNewCompany((p) => ({ ...p, fiscal_year: v }))} placeholder="2024" />
              <FormField label="기업유형" value={newCompany.company_type} onChange={(v) => setNewCompany((p) => ({ ...p, company_type: v }))} placeholder="중소기업" />
              <FormField label="홈페이지" value={newCompany.homepage} onChange={(v) => setNewCompany((p) => ({ ...p, homepage: v }))} placeholder="https://" />
            </div>
            {newCompany.revenue && newCompany.operating_profit && parseInt(newCompany.revenue) > 0 && (
              <p className="mt-2 text-xs text-gray-500">
                영업이익률: {((parseInt(newCompany.operating_profit) / parseInt(newCompany.revenue)) * 100).toFixed(1)}%
              </p>
            )}
            <div className="mt-4 flex gap-2">
              <button onClick={handleAddCompany} disabled={!newCompany.company_name.trim() || !newCompany.brn.trim() || addCompanyMutation.isPending} className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-40">
                {addCompanyMutation.isPending ? "추가 중..." : "추가"}
              </button>
              <button onClick={() => { setAddMode(""); setNewCompany({ company_name: "", brn: "", ceo: "", industry: "", products: "", revenue: "", operating_profit: "", total_assets: "", equity: "", debt: "", company_type: "", homepage: "", fiscal_year: "2024" }); }} className="rounded-lg border border-gray-200 px-4 py-2 text-sm text-gray-500 hover:bg-gray-50">
                취소
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Bottom submit */}
      {task.results.length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-white p-5 text-center shadow-sm">
          {isComplete ? (
            <>
              <p className="mb-3 text-sm text-emerald-600 font-medium">모든 기업 평가를 완료했습니다!</p>
              <button onClick={onSubmit} disabled={submitPending} className="rounded-xl bg-gray-900 px-8 py-3 text-sm font-semibold text-white hover:bg-gray-800 disabled:opacity-50">
                {submitPending ? "제출 중..." : "제출하기"}
              </button>
            </>
          ) : (
            <p className="text-sm text-gray-400">모든 기업을 평가하면 제출할 수 있습니다. ({ratedCount}/{task.results.length})</p>
          )}
        </div>
      )}
    </div>
  );
}

/* ─── Company Evaluation Card ────────────────────────────────────────────── */

function CompanyEvalCard({
  index,
  result,
  label,
  criteria,
  onUpdate,
  onDelete,
}: {
  index: number;
  result: TaskResult;
  label: CompanyLabelState | null;
  criteria: RubricCriterion[];
  onUpdate: (update: Partial<CompanyLabelState>) => void;
  onDelete?: () => void;
}) {
  const meta = result.company_metadata ?? {};
  const isRated = label?.rating != null;
  const isManual = meta.source === "manual";
  const brn = meta.brn ? String(meta.brn).replace(/-/g, "") : null;
  const cookiedealUrl = brn ? `https://cookiedeal.io/company-search/${brn}` : null;

  return (
    <div className={`rounded-xl border p-5 shadow-sm transition-all ${isManual ? "border-amber-300 bg-amber-50/40" : isRated ? "border-emerald-200 bg-white" : "border-gray-200 bg-white"}`}>
      {/* Company header */}
      <div className="mb-3 flex items-start justify-between">
        <div className="flex items-start gap-2.5">
          <span className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold ${isManual ? "bg-amber-200 text-amber-700" : "bg-gray-100 text-gray-500"}`}>{index}</span>
          <div>
            <div className="flex items-center gap-2">
              <h4 className="text-base font-semibold text-gray-900">{result.company_name}</h4>
              {isManual && (
                <span className="rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-700">수동 추가</span>
              )}
              {cookiedealUrl && (
                <a href={cookiedealUrl} target="_blank" rel="noopener noreferrer" className="rounded bg-brand-50 px-1.5 py-0.5 text-[10px] font-medium text-brand-600 hover:bg-brand-100">
                  쿠키딜
                </a>
              )}
            </div>
            {meta.brn && <p className="text-xs text-gray-400">BRN: {String(meta.brn)}</p>}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isRated && (
            <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-600">평가 완료</span>
          )}
          {onDelete && (
            <button onClick={onDelete} className="rounded p-1 text-gray-300 hover:bg-red-50 hover:text-red-500 transition-colors" title="삭제">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
            </button>
          )}
        </div>
      </div>

      {/* Company info grid */}
      {Object.keys(meta).length > 0 && (
        <div className="mb-4 grid grid-cols-2 gap-x-6 gap-y-1 rounded-lg bg-gray-50 p-3 text-xs">
          {meta.ceo && <InfoRow label="대표자" value={String(meta.ceo)} />}
          {meta.industry && <InfoRow label="업종" value={String(meta.industry)} />}
          {meta.products && <InfoRow label="생산품" value={String(meta.products)} />}
          {meta.company_type && <InfoRow label="기업유형" value={String(meta.company_type)} />}
          {(meta.revenue || meta.revenue_text) && (
            <InfoRow label={meta.fiscal_year ? `매출 (${meta.fiscal_year})` : "매출"} value={meta.revenue_text ? String(meta.revenue_text) : fmtKrw(Number(meta.revenue))} />
          )}
          {(meta.operating_profit || meta.op_text) && (
            <InfoRow label={meta.fiscal_year ? `영업이익 (${meta.fiscal_year})` : "영업이익"} value={meta.op_text ? String(meta.op_text) : fmtKrw(Number(meta.operating_profit))} />
          )}
          {meta.total_assets && <InfoRow label={meta.fiscal_year ? `자산총계 (${meta.fiscal_year})` : "자산총계"} value={fmtKrw(Number(meta.total_assets))} />}
          {meta.equity && <InfoRow label={meta.fiscal_year ? `자본총계 (${meta.fiscal_year})` : "자본총계"} value={fmtKrw(Number(meta.equity))} />}
          {meta.op_margin && <InfoRow label="영업이익률" value={String(meta.op_margin)} />}
          {meta.homepage && (
            <div className="col-span-2 flex gap-2">
              <span className="w-16 shrink-0 text-gray-400">홈페이지</span>
              <a href={String(meta.homepage).startsWith("http") ? String(meta.homepage) : `https://${meta.homepage}`} target="_blank" rel="noopener noreferrer" className="truncate text-brand-600 hover:underline">
                {String(meta.homepage)}
              </a>
            </div>
          )}
          {meta.recommendation && (
            <div className="col-span-2 flex gap-2">
              <span className="w-16 shrink-0 text-gray-400">추천사유</span>
              <span className="text-gray-700">{String(meta.recommendation)}</span>
            </div>
          )}
        </div>
      )}

      {/* Rating */}
      <div className="mb-4">
        <div className="mb-1.5 text-xs font-medium text-gray-500">평점</div>
        <div className="flex gap-1.5">
          {RATINGS.map((r) => {
            const active = label?.rating === r.value;
            return (
              <button key={r.value} onClick={() => onUpdate({ rating: r.value })} className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${active ? `${r.activeBg} border-transparent text-white shadow-sm` : `${r.bg} ${r.border} ${r.text} hover:shadow-sm`}`}>
                {r.value} {r.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Rubric */}
      {criteria.length > 0 && (
        <div className="mb-4">
          <div className="mb-1.5 text-xs font-medium text-gray-500">조건별 평가</div>
          <div className="rounded-lg border border-gray-100 bg-gray-50 p-3">
            <div className="flex flex-col gap-2">
              {criteria.map((c) => {
                const scoreEntry = label?.rubricScores.find((s) => s.criterion_id === c.id);
                const currentScore = scoreEntry?.score ?? "";
                return (
                  <div key={c.id} className="flex items-center gap-3">
                    <span className="w-24 shrink-0 text-xs font-medium text-gray-700" title={c.description}>{c.name}</span>
                    <div className="flex gap-1">
                      {(RUBRIC_OPTIONS as readonly { value: string; label: string; active: string; inactive: string }[]).map((opt) => {
                        const active = currentScore === opt.value;
                        return (
                          <button key={opt.value} onClick={() => {
                            if (!label) return;
                            const scores = label.rubricScores.map((s) => s.criterion_id === c.id ? { ...s, score: opt.value as "" | "yes" | "partially" | "no" } : s);
                            onUpdate({ rubricScores: scores });
                          }} className={`rounded border px-2 py-0.5 text-[11px] font-medium transition-all ${active ? opt.active : opt.inactive}`}>
                            {opt.label}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Justification (required) with persistent guideline */}
      <div>
        <div className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-gray-500">
          판단근거 <span className="text-red-400">*필수 (20자 이상)</span>
        </div>
        <div className="mb-2 rounded-lg border border-brand-100 bg-brand-50 px-3 py-2 text-[11px] leading-relaxed text-brand-800">
          <p className="font-semibold mb-0.5">작성 가이드</p>
          <p className="mb-1">이 기업이 쿼리 조건에 <strong>왜 적합하거나 부적합한지</strong> 구체적으로 서술하세요. AI 모델이 이 텍스트로 추천 이유를 생성하는 법을 학습합니다.</p>
          <ul className="list-none flex flex-col gap-0.5">
            <li><span className="text-brand-500 mr-1">1.</span><strong>수치를 인용</strong>하세요 &mdash; 매출 XX억, 영업이익률 XX% 등 카드에 표시된 데이터를 근거로 사용</li>
            <li><span className="text-brand-500 mr-1">2.</span>쿼리의 <strong>각 조건별로 부합 여부</strong>를 명시하세요 &mdash; 업종, 매출 범위, 규모, 지역 등</li>
            <li><span className="text-brand-500 mr-1">3.</span><strong>불일치 사유</strong>도 구체적으로 &mdash; "매출 미달"이 아니라 "매출 30억으로 50억 하한 미달"</li>
            <li><span className="text-brand-500 mr-1">4.</span>카드에 없는 <strong>추가 판단 근거</strong>가 있으면 함께 기재 (업계 지식, 쿠키딜 검색 결과 등)</li>
          </ul>
          <p className="mt-1 text-brand-600 italic">예: "매출 85억(조건 50~200억 내), VAN 대리점 업종으로 TRS 사업과 직결. 영업이익률 17%로 수익성 양호. 단, 수도권 외 지역 소재로 지역 조건 부분 충족."</p>
        </div>
        <textarea
          value={label?.justification ?? ""}
          onChange={(e) => onUpdate({ justification: e.target.value })}
          placeholder="위 가이드를 참고하여 구체적 수치와 함께 판단 근거를 작성하세요."
          rows={3}
          className={`w-full rounded-lg border px-3 py-2 text-sm text-gray-700 placeholder-gray-400 focus:border-brand-500 focus:outline-none ${
            label?.rating != null && (!label.justification || label.justification.trim().length < 20)
              ? "border-red-300 bg-red-50"
              : "border-gray-200"
          }`}
        />
      </div>
    </div>
  );
}

/* ─── Small helpers ──────────────────────────────────────────────────────── */

function MetaBadge({ label, color }: { label: string; color: string }) {
  return <span className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${color}`}>{label}</span>;
}

function InstructionStep({ num, title, desc }: { num: number; title: string; desc: string }) {
  return (
    <div className="flex gap-3">
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-900 text-xs font-bold text-white">{num}</span>
      <div>
        <div className="text-sm font-medium text-gray-800">{title}</div>
        <div className="text-xs text-gray-500">{desc}</div>
      </div>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-2">
      <span className="w-16 shrink-0 text-gray-400">{label}</span>
      <span className="text-gray-700 truncate">{value}</span>
    </div>
  );
}

function FormField({ label, value, onChange, placeholder, type = "text", colSpan }: {
  label: string; value: string; onChange: (v: string) => void; placeholder?: string; type?: string; colSpan?: boolean;
}) {
  return (
    <div className={colSpan ? "col-span-2" : ""}>
      <label className="mb-1 block text-xs font-medium text-gray-600">{label}</label>
      <input type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} className="w-full rounded-lg border border-gray-200 px-2.5 py-1.5 text-sm focus:border-brand-500 focus:outline-none" />
    </div>
  );
}

/** Format a number (assumed 천원 unit) to Korean 억/만 display. */
function fmtKrw(val: number): string {
  if (!val || isNaN(val)) return "-";
  // val is in 천원 (thousands of KRW)
  const billions = val / 100000; // 억 = 100,000천원
  if (Math.abs(billions) >= 1) return `${billions.toFixed(0)}억`;
  const tenThousands = val / 10; // 만 = 10천원
  if (Math.abs(tenThousands) >= 1) return `${tenThousands.toFixed(0)}만`;
  return `${val.toLocaleString()}천원`;
}
