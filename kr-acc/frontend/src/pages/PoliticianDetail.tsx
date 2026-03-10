import { useState } from "react";
import { useParams, Link } from "react-router";
import { usePolitician, usePoliticianBills, usePoliticianVotes } from "@/api/queries";
import PartyBadge from "@/components/layout/PartyBadge";
import Pagination from "@/components/layout/Pagination";
import { formatDate, formatNumber } from "@/lib/format";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { getPartyColor } from "@/lib/partyColors";

const VOTE_COLORS = {
  찬성: "#22C55E",
  반대: "#EF4444",
  기권: "#F59E0B",
  불참: "#9CA3AF",
};

type Tab = "bills" | "votes";

export default function PoliticianDetail() {
  const { id } = useParams<{ id: string }>();
  const politicianId = Number(id);
  const { data: pol, isLoading } = usePolitician(politicianId);
  const [tab, setTab] = useState<Tab>("votes");
  const [billPage, setBillPage] = useState(1);
  const [votePage, setVotePage] = useState(1);

  const bills = usePoliticianBills(politicianId, { page: billPage, size: 10 });
  const votes = usePoliticianVotes(politicianId, { page: votePage, size: 10 });

  if (isLoading) {
    return <p className="mt-8 text-center text-gray-500">불러오는 중...</p>;
  }
  if (!pol) {
    return <p className="mt-8 text-center text-gray-500">의원 정보를 찾을 수 없습니다.</p>;
  }

  const stats = pol.stats;
  const voteChartData = stats
    ? [
        { name: "찬성", value: stats.yes_count },
        { name: "반대", value: stats.no_count },
        { name: "기권", value: stats.abstain_count },
        { name: "불참", value: stats.absent_count },
      ].filter((d) => d.value > 0)
    : [];

  return (
    <div>
      {/* Header */}
      <div className="flex items-start gap-4">
        <div
          className="flex h-16 w-16 items-center justify-center rounded-full text-2xl font-bold text-white"
          style={{ backgroundColor: getPartyColor(pol.party) }}
        >
          {pol.name.charAt(0)}
        </div>
        <div>
          <h1 className="text-2xl font-bold">
            {pol.name}
            {pol.name_hanja && (
              <span className="ml-2 text-base font-normal text-gray-400">
                {pol.name_hanja}
              </span>
            )}
          </h1>
          <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-gray-500">
            <PartyBadge party={pol.party} />
            {pol.constituency && <span>{pol.constituency}</span>}
            {pol.elected_count && <span>{pol.elected_count}선</span>}
            {pol.gender && <span>{pol.gender}</span>}
          </div>
          {pol.committees && pol.committees.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {pol.committees.map((c) => (
                <span
                  key={c}
                  className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                >
                  {c}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="rounded-lg border bg-white p-4">
            <p className="text-sm text-gray-500">표결 참여율</p>
            <p className="mt-1 text-2xl font-bold">{stats.participation_rate}%</p>
          </div>
          <div className="rounded-lg border bg-white p-4">
            <p className="text-sm text-gray-500">총 표결</p>
            <p className="mt-1 text-2xl font-bold">{formatNumber(stats.total_votes)}</p>
          </div>
          <div className="rounded-lg border bg-white p-4">
            <p className="text-sm text-gray-500">발의 법안</p>
            <p className="mt-1 text-2xl font-bold">{formatNumber(stats.bills_sponsored)}</p>
          </div>
          <div className="rounded-lg border bg-white p-4">
            <p className="text-sm text-gray-500">대표발의</p>
            <p className="mt-1 text-2xl font-bold">
              {formatNumber(stats.bills_primary_sponsored)}
            </p>
          </div>
        </div>
      )}

      {/* Vote pie chart */}
      {voteChartData.length > 0 && (
        <div className="mt-6 rounded-lg border bg-white p-4">
          <h2 className="text-sm font-medium text-gray-500">표결 분포</h2>
          <div className="mx-auto h-48 w-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={voteChartData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={70}
                >
                  {voteChartData.map((d) => (
                    <Cell
                      key={d.name}
                      fill={VOTE_COLORS[d.name as keyof typeof VOTE_COLORS]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-2 flex justify-center gap-4 text-xs">
            {voteChartData.map((d) => (
              <span key={d.name} className="flex items-center gap-1">
                <span
                  className="inline-block h-2 w-2 rounded-full"
                  style={{
                    backgroundColor:
                      VOTE_COLORS[d.name as keyof typeof VOTE_COLORS],
                  }}
                />
                {d.name} {d.value}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tabs: Bills / Votes */}
      <div className="mt-6 flex gap-1 border-b">
        {(["votes", "bills"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium ${
              tab === t
                ? "border-b-2 border-gray-900 text-gray-900"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {t === "votes" ? "표결 기록" : "발의 법안"}
          </button>
        ))}
      </div>

      {tab === "votes" && (
        <div className="mt-4">
          {votes.isLoading ? (
            <p className="text-center text-sm text-gray-500">불러오는 중...</p>
          ) : (
            <>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-gray-500">
                    <th className="pb-2 font-medium">법안명</th>
                    <th className="pb-2 font-medium">일자</th>
                    <th className="pb-2 font-medium">투표</th>
                    <th className="pb-2 font-medium">결과</th>
                  </tr>
                </thead>
                <tbody>
                  {votes.data?.items.map((v) => (
                    <tr key={v.vote_id} className="border-b last:border-0">
                      <td className="max-w-xs truncate py-2">{v.bill_name}</td>
                      <td className="py-2 text-gray-500">
                        {formatDate(v.vote_date)}
                      </td>
                      <td className="py-2">
                        <span
                          className={`rounded px-1.5 py-0.5 text-xs font-medium ${
                            v.vote_result === "찬성"
                              ? "bg-green-100 text-green-700"
                              : v.vote_result === "반대"
                                ? "bg-red-100 text-red-700"
                                : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {v.vote_result ?? "—"}
                        </span>
                      </td>
                      <td className="py-2 text-gray-500">
                        {v.overall_result}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {votes.data && (
                <Pagination
                  page={votePage}
                  pages={votes.data.pages}
                  onPageChange={setVotePage}
                />
              )}
            </>
          )}
        </div>
      )}

      {tab === "bills" && (
        <div className="mt-4">
          {bills.isLoading ? (
            <p className="text-center text-sm text-gray-500">불러오는 중...</p>
          ) : (
            <>
              <div className="space-y-2">
                {bills.data?.items.map((b) => (
                  <Link
                    key={b.bill_id}
                    to={`/bills/${b.bill_id}`}
                    className="block rounded-lg border bg-white p-3 transition-shadow hover:shadow-sm"
                  >
                    <p className="font-medium">{b.bill_name}</p>
                    <div className="mt-1 flex gap-3 text-xs text-gray-500">
                      <span>{formatDate(b.propose_date)}</span>
                      {b.committee_name && <span>{b.committee_name}</span>}
                      {b.result && <span>{b.result}</span>}
                    </div>
                  </Link>
                ))}
              </div>
              {bills.data && (
                <Pagination
                  page={billPage}
                  pages={bills.data.pages}
                  onPageChange={setBillPage}
                />
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
