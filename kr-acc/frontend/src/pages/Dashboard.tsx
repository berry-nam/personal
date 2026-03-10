import { Link } from "react-router";
import {
  usePoliticians,
  useBills,
  useVotes,
  useParties,
  useBillPipeline,
} from "@/api/queries";
import { getPartyColor } from "@/lib/partyColors";
import { formatNumber, formatDate } from "@/lib/format";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from "recharts";

const RESULT_COLORS: Record<string, string> = {
  원안가결: "#10B981",
  수정가결: "#059669",
  부결: "#EF4444",
  폐기: "#9CA3AF",
  철회: "#D1D5DB",
  대안반영폐기: "#F59E0B",
  임기만료폐기: "#6B7280",
  계류중: "#3B82F6",
};

function StatCard({
  label,
  value,
  to,
  accent,
}: {
  label: string;
  value: string | number;
  to: string;
  accent?: string;
}) {
  return (
    <Link
      to={to}
      className="group rounded-2xl border border-gray-200 bg-white p-6 transition-all hover:border-gray-300 hover:shadow-lg"
    >
      <p className="text-sm font-medium text-gray-400">{label}</p>
      <p
        className="mt-2 text-4xl font-bold tracking-tight"
        style={accent ? { color: accent } : undefined}
      >
        {value}
      </p>
    </Link>
  );
}

function pct(n: number | null, total: number | null): number {
  if (!n || !total || total === 0) return 0;
  return Math.round((n / total) * 100);
}

export default function Dashboard() {
  const politicians = usePoliticians({ page: 1, size: 1 });
  const bills = useBills({ page: 1, size: 1 });
  const votes = useVotes({ page: 1, size: 5 });
  const parties = useParties();
  const pipeline = useBillPipeline();

  return (
    <div>
      <h1 className="text-2xl font-bold">대시보드</h1>
      <p className="mt-1 text-sm text-gray-500">
        대한민국 국회 활동 현황 (17~22대)
      </p>

      {/* Summary stats */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="정치인"
          value={politicians.data ? formatNumber(politicians.data.total) : "—"}
          to="/politicians"
        />
        <StatCard
          label="발의 법안"
          value={bills.data ? formatNumber(bills.data.total) : "—"}
          to="/bills"
        />
        <StatCard
          label="본회의 표결"
          value={votes.data ? formatNumber(votes.data.total) : "—"}
          to="/votes"
          accent="#3B82F6"
        />
      </div>

      {/* Recent votes — Polymarket-style mini cards */}
      {votes.data && votes.data.items.length > 0 && (
        <div className="mt-8">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">최근 표결</h2>
            <Link
              to="/votes"
              className="text-sm text-gray-400 hover:text-gray-600"
            >
              전체 보기 &rarr;
            </Link>
          </div>
          <div className="mt-3 space-y-2">
            {votes.data.items.map((vote) => {
              const total = vote.total_members ?? 0;
              const yesPct = pct(vote.yes_count, total);
              const noPct = pct(vote.no_count, total);
              const passed =
                vote.result === "원안가결" || vote.result === "수정가결";

              return (
                <Link
                  key={vote.vote_id}
                  to={`/votes/${vote.vote_id}`}
                  className="group flex items-center gap-4 rounded-xl border border-gray-200 bg-white px-5 py-3.5 transition-all hover:border-gray-300 hover:shadow-md"
                >
                  {/* Bill name */}
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-gray-900 group-hover:text-blue-600">
                      {vote.bill_name ?? vote.bill_id}
                    </p>
                    <p className="mt-0.5 text-xs text-gray-400">
                      {formatDate(vote.vote_date)}
                    </p>
                  </div>

                  {/* Mini outcome bar */}
                  <div className="hidden w-32 sm:block">
                    <div className="flex h-1.5 overflow-hidden rounded-full bg-gray-100">
                      {(vote.yes_count ?? 0) > 0 && (
                        <div
                          className="bg-emerald-500"
                          style={{ width: `${yesPct}%` }}
                        />
                      )}
                      {(vote.no_count ?? 0) > 0 && (
                        <div
                          className="bg-red-500"
                          style={{ width: `${noPct}%` }}
                        />
                      )}
                    </div>
                  </div>

                  {/* Percentage + result */}
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-bold text-emerald-600">
                      {yesPct}%
                    </span>
                    {vote.result && (
                      <span
                        className={`shrink-0 rounded-md px-2 py-0.5 text-xs font-bold ${
                          passed
                            ? "bg-emerald-50 text-emerald-600"
                            : "bg-red-50 text-red-500"
                        }`}
                      >
                        {vote.result}
                      </span>
                    )}
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}

      {/* Bill pipeline funnel */}
      {pipeline.data && pipeline.data.length > 0 && (
        <div className="mt-8 rounded-2xl border border-gray-200 bg-white p-6">
          <h2 className="text-lg font-semibold">법안 처리 현황</h2>
          <p className="mt-1 text-xs text-gray-400">전체 대수 합산</p>
          <div className="mt-4 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={pipeline.data}
                layout="vertical"
                margin={{ left: 90 }}
              >
                <XAxis
                  type="number"
                  tickFormatter={(v: number) => formatNumber(v)}
                />
                <YAxis
                  type="category"
                  dataKey="result"
                  width={90}
                  tick={{ fontSize: 12 }}
                />
                <Tooltip formatter={(v) => formatNumber(Number(v))} />
                <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                  {pipeline.data.map((d) => (
                    <Cell
                      key={d.result}
                      fill={RESULT_COLORS[d.result] ?? "#6B7280"}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Party breakdown */}
      {parties.data && parties.data.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold">정당</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {parties.data.map((p) => (
              <Link
                key={p.id}
                to={`/politicians?party=${encodeURIComponent(p.name)}`}
                className="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm transition-all hover:border-gray-300 hover:shadow-md"
              >
                <span
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: getPartyColor(p.name) }}
                />
                {p.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
