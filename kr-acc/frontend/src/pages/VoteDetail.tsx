import { useParams, Link } from "react-router";
import { useVote } from "@/api/queries";
import { formatDate, formatNumber } from "@/lib/format";
import { getPartyColor } from "@/lib/partyColors";

const RESULT_COLORS: Record<string, string> = {
  찬성: "#10B981",
  반대: "#EF4444",
  기권: "#F59E0B",
  불참: "#9CA3AF",
};

function pct(n: number, total: number): number {
  if (!total) return 0;
  return Math.round((n / total) * 100);
}

export default function VoteDetail() {
  const { voteId } = useParams<{ voteId: string }>();
  const { data: vote, isLoading } = useVote(voteId ?? "");

  if (isLoading) {
    return (
      <div className="mt-12 flex justify-center">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />
      </div>
    );
  }
  if (!vote) {
    return (
      <p className="mt-8 text-center text-gray-500">
        표결 정보를 찾을 수 없습니다.
      </p>
    );
  }

  const total = vote.total_members ?? 0;
  const yes = vote.yes_count ?? 0;
  const no = vote.no_count ?? 0;
  const abstain = vote.abstain_count ?? 0;
  const absent = vote.absent_count ?? 0;
  const voted = yes + no + abstain;
  const passed = vote.result === "가결" || vote.result === "원안가결" || vote.result === "수정가결";

  // Party breakdown
  const partyMap = new Map<
    string,
    { yes: number; no: number; abstain: number; absent: number }
  >();
  for (const r of vote.records) {
    const party = r.politician_party ?? "무소속";
    if (!partyMap.has(party)) {
      partyMap.set(party, { yes: 0, no: 0, abstain: 0, absent: 0 });
    }
    const entry = partyMap.get(party)!;
    if (r.vote_result === "찬성") entry.yes++;
    else if (r.vote_result === "반대") entry.no++;
    else if (r.vote_result === "기권") entry.abstain++;
    else entry.absent++;
  }
  const partyBreakdown = [...partyMap.entries()]
    .map(([party, counts]) => ({
      party,
      ...counts,
      total: counts.yes + counts.no + counts.abstain + counts.absent,
    }))
    .sort((a, b) => b.total - a.total);

  // Group records by vote result
  const grouped = {
    찬성: vote.records.filter((r) => r.vote_result === "찬성"),
    반대: vote.records.filter((r) => r.vote_result === "반대"),
    기권: vote.records.filter((r) => r.vote_result === "기권"),
    불참: vote.records.filter(
      (r) =>
        r.vote_result !== "찬성" &&
        r.vote_result !== "반대" &&
        r.vote_result !== "기권",
    ),
  };

  return (
    <div className="mx-auto max-w-3xl">
      {/* Back */}
      <Link
        to="/votes"
        className="inline-flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600"
      >
        <span>&larr;</span> 표결 목록
      </Link>

      {/* Hero card — Polymarket style */}
      <div className="mt-4 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        {/* Result badge + title */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1">
            <h1 className="text-xl font-bold leading-tight text-gray-900">
              {vote.bill_name ?? "표결"}
            </h1>
            <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-gray-400">
              <span>{formatDate(vote.vote_date)}</span>
              {total > 0 && <span>재적 {total}명</span>}
              {voted > 0 && (
                <span>투표율 {pct(voted, total)}%</span>
              )}
            </div>
          </div>
          {vote.result && (
            <div
              className={`shrink-0 rounded-xl px-4 py-2 text-center ${
                passed ? "bg-emerald-50" : "bg-red-50"
              }`}
            >
              <p className="text-xs text-gray-400">결과</p>
              <p
                className={`text-lg font-bold ${
                  passed ? "text-emerald-600" : "text-red-500"
                }`}
              >
                {vote.result}
              </p>
            </div>
          )}
        </div>

        {/* Outcome bars — Polymarket-style large percentages */}
        <div className="mt-6 space-y-3">
          {[
            { label: "찬성", count: yes, color: "emerald", bgClass: "bg-emerald-500/10", textClass: "text-emerald-600" },
            { label: "반대", count: no, color: "red", bgClass: "bg-red-500/10", textClass: "text-red-500" },
            { label: "기권", count: abstain, color: "amber", bgClass: "bg-amber-500/10", textClass: "text-amber-500" },
            { label: "불참", count: absent, color: "gray", bgClass: "bg-gray-200/50", textClass: "text-gray-400" },
          ].map((item) => {
            const p = pct(item.count, total);
            return (
              <div
                key={item.label}
                className="relative overflow-hidden rounded-xl bg-gray-50 px-5 py-3.5"
              >
                <div
                  className={`absolute inset-y-0 left-0 transition-all ${item.bgClass}`}
                  style={{ width: `${p}%` }}
                />
                <div className="relative flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span
                      className="h-3 w-3 rounded-full"
                      style={{ backgroundColor: RESULT_COLORS[item.label] }}
                    />
                    <span className="text-sm font-semibold text-gray-700">
                      {item.label}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-gray-400">
                      {formatNumber(item.count)}명
                    </span>
                    <span
                      className={`min-w-[4rem] text-right text-2xl font-bold ${item.textClass}`}
                    >
                      {p}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Combined progress bar */}
        {total > 0 && (
          <div className="mt-4 flex h-2.5 overflow-hidden rounded-full bg-gray-100">
            {yes > 0 && (
              <div
                className="bg-emerald-500 transition-all"
                style={{ width: `${pct(yes, total)}%` }}
              />
            )}
            {no > 0 && (
              <div
                className="bg-red-500 transition-all"
                style={{ width: `${pct(no, total)}%` }}
              />
            )}
            {abstain > 0 && (
              <div
                className="bg-amber-400 transition-all"
                style={{ width: `${pct(abstain, total)}%` }}
              />
            )}
          </div>
        )}
      </div>

      {/* Party breakdown — Polymarket-style stacked bars */}
      {partyBreakdown.length > 0 && (
        <div className="mt-4 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-500">정당별 표결</h2>
          <div className="mt-4 space-y-3">
            {partyBreakdown.map((p) => (
              <div key={p.party}>
                <div className="mb-1.5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span
                      className="h-2.5 w-2.5 shrink-0 rounded-full"
                      style={{ backgroundColor: getPartyColor(p.party) }}
                    />
                    <span className="text-sm font-medium">{p.party}</span>
                  </div>
                  <span className="text-xs text-gray-400">{p.total}명</span>
                </div>
                <div className="flex h-6 overflow-hidden rounded-lg bg-gray-100">
                  {p.yes > 0 && (
                    <div
                      className="flex items-center justify-center bg-emerald-500 text-[10px] font-medium text-white"
                      style={{ width: `${(p.yes / p.total) * 100}%` }}
                    >
                      {p.yes > 2 && p.yes}
                    </div>
                  )}
                  {p.no > 0 && (
                    <div
                      className="flex items-center justify-center bg-red-500 text-[10px] font-medium text-white"
                      style={{ width: `${(p.no / p.total) * 100}%` }}
                    >
                      {p.no > 2 && p.no}
                    </div>
                  )}
                  {p.abstain > 0 && (
                    <div
                      className="flex items-center justify-center bg-amber-400 text-[10px] font-medium text-white"
                      style={{ width: `${(p.abstain / p.total) * 100}%` }}
                    >
                      {p.abstain > 2 && p.abstain}
                    </div>
                  )}
                  {p.absent > 0 && (
                    <div
                      className="flex items-center justify-center bg-gray-300 text-[10px] font-medium text-gray-600"
                      style={{ width: `${(p.absent / p.total) * 100}%` }}
                    >
                      {p.absent > 2 && p.absent}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
          {/* Legend */}
          <div className="mt-4 flex gap-5 text-xs text-gray-400">
            {Object.entries(RESULT_COLORS).map(([label, color]) => (
              <span key={label} className="flex items-center gap-1.5">
                <span
                  className="inline-block h-2 w-2 rounded-full"
                  style={{ backgroundColor: color }}
                />
                {label}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Per-member records */}
      {vote.records.length > 0 && (
        <div className="mt-4 space-y-3">
          {(["찬성", "반대", "기권", "불참"] as const).map((result) => {
            const records = grouped[result];
            if (records.length === 0) return null;
            return (
              <div
                key={result}
                className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm"
              >
                <div className="flex items-center gap-2.5">
                  <span
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: RESULT_COLORS[result] }}
                  />
                  <h3 className="text-sm font-semibold text-gray-700">
                    {result}
                  </h3>
                  <span className="text-sm text-gray-400">
                    {records.length}명
                  </span>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {records.map((r) => (
                    <Link
                      key={r.politician_id}
                      to={`/politicians/${r.politician_id}`}
                      className="inline-flex items-center gap-1.5 rounded-full border border-gray-100 bg-gray-50 px-3 py-1.5 text-xs font-medium transition-colors hover:border-gray-300 hover:bg-white"
                    >
                      <span
                        className="h-1.5 w-1.5 rounded-full"
                        style={{
                          backgroundColor: getPartyColor(
                            r.politician_party ?? "",
                          ),
                        }}
                      />
                      {r.politician_name}
                      {r.politician_party && (
                        <span className="text-gray-400">
                          {r.politician_party}
                        </span>
                      )}
                    </Link>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
