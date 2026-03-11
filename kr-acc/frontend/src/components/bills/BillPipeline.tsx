import { useBillPipeline } from "@/api/queries";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from "recharts";

/** Ordered bill lifecycle stages with colors. */
const STAGE_ORDER = [
  "발의",
  "위원회심사",
  "체계자구심사",
  "본회의부의",
  "원안가결",
  "수정가결",
  "공포",
  "대안반영",
  "폐기",
  "철회",
  "부결",
];

const STAGE_COLORS: Record<string, string> = {
  발의: "#6366F1",
  위원회심사: "#8B5CF6",
  체계자구심사: "#A78BFA",
  본회의부의: "#3B82F6",
  원안가결: "#22C55E",
  수정가결: "#16A34A",
  공포: "#059669",
  대안반영: "#F59E0B",
  폐기: "#9CA3AF",
  철회: "#D1D5DB",
  부결: "#EF4444",
};

const DEFAULT_COLOR = "#6B7280";

export default function BillPipeline() {
  const { data, isLoading } = useBillPipeline();

  if (isLoading) {
    return <p className="mt-4 text-center text-sm text-gray-500">불러오는 중...</p>;
  }

  if (!data || data.stages.length === 0) {
    return <p className="mt-4 text-center text-sm text-gray-400">파이프라인 데이터가 없습니다.</p>;
  }

  // Sort by predefined order, then alphabetically for unknowns
  const sorted = [...data.stages].sort((a, b) => {
    const ai = STAGE_ORDER.indexOf(a.status);
    const bi = STAGE_ORDER.indexOf(b.status);
    if (ai === -1 && bi === -1) return a.status.localeCompare(b.status);
    if (ai === -1) return 1;
    if (bi === -1) return 1;
    return ai - bi;
  });

  const total = sorted.reduce((sum, s) => sum + s.count, 0);

  return (
    <div>
      {/* Funnel bar chart */}
      <div className="rounded-lg border bg-white p-4">
        <h2 className="text-sm font-semibold text-gray-700">법안 파이프라인</h2>
        <p className="mt-1 text-xs text-gray-500">총 {total.toLocaleString("ko-KR")}건</p>
        <div className="mt-4 h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={sorted} layout="vertical" margin={{ left: 10, right: 20 }}>
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis
                type="category"
                dataKey="status"
                width={90}
                tick={{ fontSize: 12 }}
              />
              <Tooltip
                formatter={(value) => [(value as number).toLocaleString("ko-KR") + "건"]}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {sorted.map((s) => (
                  <Cell
                    key={s.status}
                    fill={STAGE_COLORS[s.status] ?? DEFAULT_COLOR}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stage cards */}
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {sorted.map((s) => (
          <div key={s.status} className="rounded-lg border bg-white p-3">
            <div className="flex items-center gap-2">
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: STAGE_COLORS[s.status] ?? DEFAULT_COLOR }}
              />
              <span className="text-sm text-gray-600">{s.status}</span>
            </div>
            <p className="mt-1 text-xl font-bold">{s.count.toLocaleString("ko-KR")}</p>
            <p className="text-xs text-gray-400">
              {total > 0 ? ((s.count / total) * 100).toFixed(1) : 0}%
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
