import type { RubricCriterion } from "@/types/labeling";

const WEIGHT_LABELS: Record<number, { label: string; color: string }> = {
  5: { label: "Crucial", color: "bg-red-900/50 text-red-300" },
  3: { label: "Important", color: "bg-yellow-900/50 text-yellow-300" },
  1: { label: "Less", color: "bg-gray-700 text-gray-400" },
};

interface RubricScoreState {
  criterion_id: number;
  score: "yes" | "partially" | "no" | "";
  note: string;
}

interface Props {
  criteria: RubricCriterion[];
  scores: RubricScoreState[];
  onChange: (scores: RubricScoreState[]) => void;
  selectedCompanyName: string | null;
}

export default function RubricPanel({
  criteria,
  scores,
  onChange,
  selectedCompanyName,
}: Props) {
  const handleScoreChange = (criterionId: number, score: "yes" | "partially" | "no") => {
    const updated = scores.map((s) =>
      s.criterion_id === criterionId ? { ...s, score } : s,
    );
    onChange(updated);
  };

  const weight = (w: number) => WEIGHT_LABELS[w] ?? WEIGHT_LABELS[1]!;

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-300">루브릭 평가</h3>
        {selectedCompanyName && (
          <span className="truncate text-xs text-gray-500">
            {selectedCompanyName}
          </span>
        )}
      </div>

      {!selectedCompanyName && (
        <p className="text-xs text-gray-500">기업을 선택하면 루브릭을 평가할 수 있습니다.</p>
      )}

      {selectedCompanyName &&
        criteria.map((c) => {
          const s = scores.find((sc) => sc.criterion_id === c.id);
          const wt = weight(c.weight);
          return (
            <div key={c.id} className="rounded-lg bg-gray-800/50 p-3">
              <div className="mb-2 flex items-center gap-2">
                <span className="text-sm font-medium text-gray-200">{c.name}</span>
                <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${wt?.color ?? ""}`}>
                  {c.weight}pt · {wt?.label ?? ""}
                </span>
              </div>
              {c.description && (
                <p className="mb-2 text-xs text-gray-500">{c.description}</p>
              )}
              <div className="flex gap-1.5">
                {(["yes", "partially", "no"] as const).map((opt) => {
                  const active = s?.score === opt;
                  const optStyles: Record<string, string> = {
                    yes: active
                      ? "bg-emerald-600 text-white"
                      : "bg-gray-700 text-gray-400 hover:bg-emerald-900/50 hover:text-emerald-300",
                    partially: active
                      ? "bg-yellow-600 text-white"
                      : "bg-gray-700 text-gray-400 hover:bg-yellow-900/50 hover:text-yellow-300",
                    no: active
                      ? "bg-red-600 text-white"
                      : "bg-gray-700 text-gray-400 hover:bg-red-900/50 hover:text-red-300",
                  };
                  const optLabels: Record<string, string> = {
                    yes: "Yes",
                    partially: "Partially",
                    no: "No",
                  };
                  return (
                    <button
                      key={opt}
                      onClick={() => handleScoreChange(c.id, opt)}
                      className={`flex-1 rounded px-2 py-1.5 text-xs font-medium transition-all ${optStyles[opt]}`}
                    >
                      {optLabels[opt]}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
    </div>
  );
}
