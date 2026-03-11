import { Link } from "react-router";
import { usePoliticians, useBills, useVotes, useParties } from "@/api/queries";
import { getPartyColor } from "@/lib/partyColors";
import { formatDate } from "@/lib/format";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

function StatCard({
  label,
  value,
  to,
}: {
  label: string;
  value: string | number;
  to: string;
}) {
  return (
    <Link
      to={to}
      className="rounded-lg border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md"
    >
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 text-3xl font-bold">{value}</p>
    </Link>
  );
}

export default function Dashboard() {
  const politicians = usePoliticians({ page: 1, size: 1 });
  const bills = useBills({ page: 1, size: 5 });
  const votes = useVotes({ page: 1, size: 5 });
  const parties = useParties();

  // Build party distribution data for pie chart
  const partyData =
    parties.data?.map((p) => ({
      name: p.name,
      value: 1, // placeholder — no member count from parties endpoint
      color: getPartyColor(p.name),
    })) ?? [];

  return (
    <div>
      <h1 className="text-2xl font-bold">대시보드</h1>
      <p className="mt-1 text-gray-500">제22대 국회 활동 현황</p>

      {/* Summary stats */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="국회의원"
          value={politicians.data?.total ?? "—"}
          to="/politicians"
        />
        <StatCard
          label="발의 법안"
          value={bills.data?.total ?? "—"}
          to="/bills"
        />
        <StatCard
          label="본회의 표결"
          value={votes.data?.total ?? "—"}
          to="/votes"
        />
      </div>

      {/* Party breakdown with chart */}
      {parties.data && parties.data.length > 0 && (
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
          {/* Party pie chart */}
          <div className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-gray-700">정당 구성</h2>
            {partyData.length > 0 && (
              <div className="mt-3 h-52">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={partyData}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={80}
                      paddingAngle={2}
                    >
                      {partyData.map((d) => (
                        <Cell key={d.name} fill={d.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Party list */}
          <div className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-gray-700">정당</h2>
            <div className="mt-3 space-y-2">
              {parties.data.map((p) => (
                <Link
                  key={p.id}
                  to={`/politicians?party=${encodeURIComponent(p.name)}`}
                  className="flex items-center gap-3 rounded-md px-2 py-1.5 transition-colors hover:bg-gray-50"
                >
                  <span
                    className="h-3 w-3 shrink-0 rounded-full"
                    style={{ backgroundColor: getPartyColor(p.name) }}
                  />
                  <span className="text-sm">{p.name}</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Recent activity: bills + votes side by side */}
      <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
        {/* Recent bills */}
        <div>
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-700">최근 법안</h2>
            <Link to="/bills" className="text-xs text-gray-500 hover:text-gray-700">
              전체보기 &rarr;
            </Link>
          </div>
          <div className="mt-2 space-y-2">
            {bills.data?.items.map((b) => (
              <Link
                key={b.bill_id}
                to={`/bills/${b.bill_id}`}
                className="block rounded-lg border bg-white p-3 transition-shadow hover:shadow-sm"
              >
                <p className="text-sm font-medium leading-snug">{b.bill_name}</p>
                <div className="mt-1 flex gap-3 text-xs text-gray-500">
                  <span>{formatDate(b.propose_date)}</span>
                  {b.result && (
                    <span
                      className={`rounded px-1.5 py-0.5 text-xs font-medium ${
                        b.result === "원안가결" || b.result === "수정가결"
                          ? "bg-green-100 text-green-700"
                          : b.result === "부결"
                            ? "bg-red-100 text-red-700"
                            : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {b.result}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Recent votes */}
        <div>
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-700">최근 표결</h2>
            <Link to="/votes" className="text-xs text-gray-500 hover:text-gray-700">
              전체보기 &rarr;
            </Link>
          </div>
          <div className="mt-2 space-y-2">
            {votes.data?.items.map((v) => (
              <Link
                key={v.vote_id}
                to={`/votes/${v.vote_id}`}
                className="block rounded-lg border bg-white p-3 transition-shadow hover:shadow-sm"
              >
                <p className="text-sm font-medium leading-snug">
                  {v.bill_name ?? v.bill_id}
                </p>
                <div className="mt-1 flex gap-3 text-xs text-gray-500">
                  <span>{formatDate(v.vote_date)}</span>
                  {v.result && (
                    <span
                      className={`rounded px-1.5 py-0.5 text-xs font-medium ${
                        v.result === "가결"
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {v.result}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Quick links */}
      <div className="mt-8">
        <h2 className="text-sm font-semibold text-gray-700">탐색</h2>
        <div className="mt-2 grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Link
            to="/graph"
            className="rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
          >
            <p className="font-medium">공동발의 네트워크</p>
            <p className="mt-1 text-sm text-gray-500">
              의원 간 공동발의 관계를 시각화합니다
            </p>
          </Link>
          <Link
            to="/bills"
            className="rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
          >
            <p className="font-medium">법안 검색</p>
            <p className="mt-1 text-sm text-gray-500">
              키워드, 위원회, 처리 결과로 법안을 검색합니다
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}
