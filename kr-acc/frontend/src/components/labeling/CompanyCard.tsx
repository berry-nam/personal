import type { TaskResult } from "@/types/labeling";
import RatingSelector from "./RatingSelector";

interface Props {
  result: TaskResult;
  rating: number | null;
  justification: string;
  isSelected: boolean;
  onSelect: () => void;
  onRatingChange: (rating: number) => void;
  onJustificationChange: (text: string) => void;
  dragHandleProps?: Record<string, unknown>;
}

export default function CompanyCard({
  result,
  rating,
  justification,
  isSelected,
  onSelect,
  onRatingChange,
  onJustificationChange,
}: Props) {
  return (
    <div
      onClick={onSelect}
      className={`cursor-pointer rounded-lg border p-4 transition-all ${
        isSelected
          ? "border-blue-500 bg-gray-800/80 shadow-lg shadow-blue-500/10"
          : "border-gray-700 bg-gray-800/50 hover:border-gray-600"
      }`}
    >
      {/* Header */}
      <div className="mb-3 flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded bg-gray-700 text-xs font-mono text-gray-400">
            {result.rank_position ?? "–"}
          </span>
          <h4 className="font-medium text-gray-100">{result.company_name}</h4>
        </div>
        {rating && (
          <span
            className={`rounded px-2 py-0.5 text-xs font-bold ${
              rating >= 4
                ? "bg-emerald-900/50 text-emerald-300"
                : rating >= 3
                  ? "bg-yellow-900/50 text-yellow-300"
                  : "bg-red-900/50 text-red-300"
            }`}
          >
            {rating}/5
          </span>
        )}
      </div>

      {/* Metadata */}
      {result.company_metadata && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          {Object.entries(result.company_metadata).map(([k, v]) =>
            v ? (
              <span
                key={k}
                className="rounded bg-gray-700/80 px-1.5 py-0.5 text-[11px] text-gray-400"
              >
                {k}: {String(v)}
              </span>
            ) : null,
          )}
        </div>
      )}

      {/* Rating */}
      <div className="mb-3">
        <RatingSelector value={rating} onChange={onRatingChange} />
      </div>

      {/* Justification */}
      <textarea
        placeholder="평가 근거를 입력하세요..."
        value={justification}
        onChange={(e) => onJustificationChange(e.target.value)}
        onClick={(e) => e.stopPropagation()}
        rows={2}
        className="w-full resize-none rounded border border-gray-700 bg-gray-900/50 px-3 py-2 text-sm text-gray-300 placeholder-gray-600 focus:border-blue-500 focus:outline-none"
      />
    </div>
  );
}
