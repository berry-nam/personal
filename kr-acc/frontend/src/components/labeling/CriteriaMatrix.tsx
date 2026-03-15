import type { RubricCriterion, TaskResult } from "@/types/labeling";

interface ResultLabels {
  resultId: number;
  rubricScores: { criterion_id: number; score: string }[];
}

interface Props {
  results: TaskResult[];
  criteria: RubricCriterion[];
  labelsMap: Record<number, ResultLabels>;
}

const SCORE_COLORS: Record<string, string> = {
  yes: "bg-emerald-600",
  partially: "bg-yellow-600",
  no: "bg-red-600",
  "": "bg-gray-700",
};

export default function CriteriaMatrix({ results, criteria, labelsMap }: Props) {
  if (results.length === 0 || criteria.length === 0) return null;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr>
            <th className="px-2 py-1.5 text-left font-medium text-gray-400">기업</th>
            {criteria.map((c) => (
              <th key={c.id} className="px-2 py-1.5 text-center font-medium text-gray-400">
                {c.name}
                <span className="ml-1 text-gray-600">({c.weight})</span>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {results.map((r) => {
            const labels = labelsMap[r.id];
            return (
              <tr key={r.id} className="border-t border-gray-800">
                <td className="max-w-[120px] truncate px-2 py-1.5 text-gray-300">
                  {r.company_name}
                </td>
                {criteria.map((c) => {
                  const rs = labels?.rubricScores.find(
                    (s) => s.criterion_id === c.id,
                  );
                  const score = rs?.score ?? "";
                  return (
                    <td key={c.id} className="px-2 py-1.5 text-center">
                      <span
                        className={`inline-block h-4 w-4 rounded-sm ${SCORE_COLORS[score]}`}
                        title={score || "미평가"}
                      />
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
