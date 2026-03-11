import { useState } from "react";
import { useParams, Link } from "react-router";
import { useVote } from "@/api/queries";
import { formatDate, formatNumber } from "@/lib/format";
import { getPartyColor } from "@/lib/partyColors";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Cell,
  Tooltip,
} from "recharts";

const VOTE_COLORS: Record<string, string> = {
  찬성: "#22C55E",
  반대: "#EF4444",
  기권: "#F59E0B",
  불참: "#9CA3AF",
};

type VoteFilter = "all" | "찬성" | "반대" | "기권" | "불참";

export default function VoteDetail() {
  const { voteId } = useParams<{ voteId: string }>();
  const { data: vote, isLoading } = useVote(voteId ?? "");
  const [filter, setFilter] = useState<VoteFilter>("all");

  if (isLoading) {
    return <p className="mt-8 text-center text-gray-500">불러오는 중...</p>;
  }
  if (!vote) {
    return <p className="mt-8 text-center text-gray-500">표결 정보를 찾을 수 없습니다.</p>;
  }

  const chartData = [
    { name: "찬성", value: vote.yes_count ?? 0 },
    { name: "반대", value: vote.no_count ?? 0 },
    { name: "기권", value: vote.abstain_count ?? 0 },
    { name: "불참", value: vote.absent_count ?? 0 },
  ];

  const filteredRecords =
    filter === "all"
      ? vote.records
      : vote.records.filter((r) => r.vote_result === filter);

  // Group by party for summary
  const partyBreakdown = new Map<string, Record<string, number>>();
  for (const r of vote.records) {
    const party = r.politician_party ?? "무소속";
    if (!partyBreakdown.has(party)) {
      partyBreakdown.set(party, { 찬성: 0, 반대: 0, 기권: 0, 불참: 0 });
    }
    const counts = partyBreakdown.get(party)!;
    const result = r.vote_result ?? "불참";
    counts[result] = (counts[result] ?? 0) + 1;
  }

  return (
    <div>
      {/* Back link */}
      <Link to="/votes" className="text-sm text-gray-500 hover:text-gray-700">
        &larr; 표결 목록
      </Link>

      {/* Header */}
      <h1 className="mt-3 text-2xl font-bold">{vote.bill_name ?? vote.bill_id}</h1>
      <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-gray-500">
        <span>{formatDate(vote.vote_date)}</span>
        {vote.result && (
          <span
            className={`rounded px-2 py-0.5 text-xs font-medium ${
              vote.result === "가결"
                ? "bg-green-100 text-green-700"
                : "bg-red-100 text-red-700"
            }`}
          >
            {vote.result}
          </span>
        )}
        {vote.total_members && (
          <span>재적 {formatNumber(vote.total_members)}명</span>
        )}
      </div>

      {/* Vote summary chart */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {/* Bar chart */}
        <div className="rounded-lg border bg-white p-4">
          <h2 className="text-sm font-medium text-gray-500">투표 결과</h2>
          <div className="mt-2 h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical">
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" width={40} tick={{ fontSize: 13 }} />
                <Tooltip formatter={(value) => formatNumber(value as number)} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {chartData.map((d) => (
                    <Cell key={d.name} fill={VOTE_COLORS[d.name] ?? "#9CA3AF"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Summary cards */}
        <div className="grid grid-cols-2 gap-3">
          {chartData.map((d) => (
            <div key={d.name} className="rounded-lg border bg-white p-4">
              <p className="text-xs text-gray-500">{d.name}</p>
              <p
                className="mt-1 text-2xl font-bold"
                style={{ color: VOTE_COLORS[d.name] }}
              >
                {formatNumber(d.value)}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Party breakdown */}
      {partyBreakdown.size > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-700">정당별 투표 현황</h2>
          <div className="mt-2 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="pb-2 font-medium">정당</th>
                  <th className="pb-2 text-right font-medium text-green-600">찬성</th>
                  <th className="pb-2 text-right font-medium text-red-600">반대</th>
                  <th className="pb-2 text-right font-medium text-yellow-600">기권</th>
                  <th className="pb-2 text-right font-medium text-gray-400">불참</th>
                </tr>
              </thead>
              <tbody>
                {[...partyBreakdown.entries()]
                  .sort((a, b) => {
                    const totalA = Object.values(a[1]).reduce((s, v) => s + v, 0);
                    const totalB = Object.values(b[1]).reduce((s, v) => s + v, 0);
                    return totalB - totalA;
                  })
                  .map(([party, counts]) => (
                    <tr key={party} className="border-b last:border-0">
                      <td className="py-2">
                        <span className="flex items-center gap-1.5">
                          <span
                            className="inline-block h-2.5 w-2.5 rounded-full"
                            style={{ backgroundColor: getPartyColor(party) }}
                          />
                          {party}
                        </span>
                      </td>
                      <td className="py-2 text-right">{counts["찬성"] ?? 0}</td>
                      <td className="py-2 text-right">{counts["반대"] ?? 0}</td>
                      <td className="py-2 text-right">{counts["기권"] ?? 0}</td>
                      <td className="py-2 text-right">{counts["불참"] ?? 0}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Individual vote records */}
      <div className="mt-6">
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="text-sm font-semibold text-gray-700">
            개별 투표 기록 ({filteredRecords.length}명)
          </h2>
          <div className="flex gap-1">
            {(["all", "찬성", "반대", "기권", "불참"] as VoteFilter[]).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`rounded-full px-3 py-1 text-xs ${
                  filter === f
                    ? "bg-gray-900 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {f === "all" ? "전체" : f}
              </button>
            ))}
          </div>
        </div>
        <div className="mt-3 grid grid-cols-1 gap-1 sm:grid-cols-2 lg:grid-cols-3">
          {filteredRecords.map((r) => (
            <Link
              key={r.politician_id}
              to={`/politicians/${r.politician_id}`}
              className="flex items-center justify-between rounded border bg-white px-3 py-2 text-sm transition-shadow hover:shadow-sm"
            >
              <span className="flex items-center gap-2">
                <span
                  className="inline-block h-2 w-2 rounded-full"
                  style={{ backgroundColor: getPartyColor(r.politician_party) }}
                />
                {r.politician_name ?? "—"}
              </span>
              <span
                className={`rounded px-1.5 py-0.5 text-xs font-medium ${
                  r.vote_result === "찬성"
                    ? "bg-green-100 text-green-700"
                    : r.vote_result === "반대"
                      ? "bg-red-100 text-red-700"
                      : r.vote_result === "기권"
                        ? "bg-yellow-100 text-yellow-700"
                        : "bg-gray-100 text-gray-500"
                }`}
              >
                {r.vote_result ?? "불참"}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
