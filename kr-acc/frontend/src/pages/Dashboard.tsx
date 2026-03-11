import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useStatsOverview, useBills, useVotes } from "@/api/queries";
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
  const stats = useStatsOverview();
  const bills = useBills({ page: 1, size: 5 });
  const votes = useVotes({ page: 1, size: 5 });
  const navigate = useNavigate();
  const [search, setSearch] = useState("");

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (search.trim()) {
      navigate(`/politicians?name=${encodeURIComponent(search.trim())}`);
    }
  }

  // Party distribution for pie chart (now with real member counts)
  const partyData =
    stats.data?.parties.map((p) => ({
      name: p.party,
      value: p.count,
      color: getPartyColor(p.party),
    })) ?? [];

  return (
    <div>
      <h1 className="text-2xl font-bold">대시보드</h1>
      <p className="mt-1 text-gray-500">제22대 국회 활동 현황</p>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="mt-4">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="의원명, 법안명, 위원회 검색..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 rounded-md border border-gray-300 px-4 py-2 text-sm focus:border-gray-500 focus:outline-none"
          />
          <button
            type="submit"
            className="rounded-md bg-gray-900 px-4 py-2 text-sm text-white hover:bg-gray-800"
          >
            검색
          </button>
        </div>
      </form>

      {/* Summary stats */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="국회의원"
          value={stats.data?.politicians ?? "—"}
          to="/politicians"
        />
        <StatCard
          label="발의 법안"
          value={stats.data?.bills ?? "—"}
          to="/bills"
        />
        <StatCard
          label="본회의 표결"
          value={stats.data?.votes ?? "—"}
          to="/votes"
        />
      </div>

      {/* Party breakdown with chart */}
      {partyData.length > 0 && (
        <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2">
          {/* Party pie chart */}
          <div className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-gray-700">정당 구성</h2>
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
                  <Tooltip formatter={(value) => `${value}명`} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Party list with counts */}
          <div className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="text-sm font-semibold text-gray-700">정당</h2>
            <div className="mt-3 space-y-2">
              {partyData.map((p) => (
                <Link
                  key={p.name}
                  to={`/politicians?party=${encodeURIComponent(p.name)}`}
                  className="flex items-center justify-between rounded-md px-2 py-1.5 transition-colors hover:bg-gray-50"
                >
                  <span className="flex items-center gap-3">
                    <span
                      className="h-3 w-3 shrink-0 rounded-full"
                      style={{ backgroundColor: p.color }}
                    />
                    <span className="text-sm">{p.name}</span>
                  </span>
                  <span className="text-sm font-medium text-gray-500">{p.value}명</span>
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
              전체보기 →
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
              전체보기 →
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
        <div className="mt-2 grid grid-cols-1 gap-3 sm:grid-cols-3">
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
            to="/bills?view=pipeline"
            className="rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
          >
            <p className="font-medium">법안 파이프라인</p>
            <p className="mt-1 text-sm text-gray-500">
              법안 진행 상태를 단계별로 확인합니다
            </p>
          </Link>
          <Link
            to="/about"
            className="rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
          >
            <p className="font-medium">프로젝트 소개</p>
            <p className="mt-1 text-sm text-gray-500">
              kr-acc 데이터 출처와 법적 근거
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}
