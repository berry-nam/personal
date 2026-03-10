import { useState } from "react";
import { Link } from "react-router";
import { useVotes } from "@/api/queries";
import Pagination from "@/components/layout/Pagination";
import { formatDate, formatNumber } from "@/lib/format";

const RESULT_FILTERS = [
  { value: undefined, label: "전체" },
  { value: "원안가결", label: "원안가결" },
  { value: "수정가결", label: "수정가결" },
  { value: "부결", label: "부결" },
];

function pct(n: number | null, total: number | null): number {
  if (!n || !total || total === 0) return 0;
  return Math.round((n / total) * 100);
}

const TERM_OPTIONS = [
  { value: undefined, label: "전체 대수" },
  { value: 22, label: "22대" },
  { value: 21, label: "21대" },
  { value: 20, label: "20대" },
];

export default function VoteList() {
  const [result, setResult] = useState<string | undefined>();
  const [term, setTerm] = useState<number | undefined>();
  const [page, setPage] = useState(1);
  const { data, isLoading } = useVotes({
    result,
    assembly_term: term,
    page,
    size: 20,
  });

  return (
    <div>
      <h1 className="text-2xl font-bold">본회의 표결</h1>
      <p className="mt-1 text-sm text-gray-500">
        국회 본회의 법안 처리 현황
      </p>

      {/* Filters — Polymarket style */}
      <div className="mt-5 flex flex-wrap items-center gap-4">
        {/* Term filter */}
        <div className="flex gap-1.5">
          {TERM_OPTIONS.map((t) => (
            <button
              key={t.label}
              onClick={() => {
                setTerm(t.value);
                setPage(1);
              }}
              className={`rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors ${
                term === t.value
                  ? "bg-blue-600 text-white"
                  : "border border-gray-200 bg-white text-gray-500 hover:border-gray-400"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="h-5 w-px bg-gray-200" />

        {/* Result filter */}
        <div className="flex gap-1.5">
          {RESULT_FILTERS.map((f) => (
            <button
              key={f.label}
              onClick={() => {
                setResult(f.value);
                setPage(1);
              }}
              className={`rounded-full px-3.5 py-1.5 text-sm font-medium transition-colors ${
                result === f.value
                  ? "bg-gray-900 text-white"
                  : "border border-gray-200 bg-white text-gray-500 hover:border-gray-400"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="mt-12 flex justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />
        </div>
      ) : (
        <>
          <p className="mt-6 text-sm text-gray-400">
            {formatNumber(data?.total ?? 0)}건
          </p>

          {/* Vote cards — Polymarket-inspired */}
          <div className="mt-3 space-y-3">
            {data?.items.map((vote) => {
              const yesPct = pct(vote.yes_count, vote.total_members);
              const noPct = pct(vote.no_count, vote.total_members);
              const absPct = pct(vote.abstain_count, vote.total_members);
              const voted = (vote.yes_count ?? 0) + (vote.no_count ?? 0) + (vote.abstain_count ?? 0);
              const turnout = pct(voted, vote.total_members);
              const passed =
                vote.result === "원안가결" ||
                vote.result === "수정가결";

              return (
                <Link
                  key={vote.vote_id}
                  to={`/votes/${vote.vote_id}`}
                  className="group block rounded-xl border border-gray-200 bg-white p-5 transition-all hover:border-gray-300 hover:shadow-lg"
                >
                  {/* Header row */}
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-[15px] font-semibold leading-snug text-gray-900 group-hover:text-blue-600">
                      {vote.bill_name ?? vote.bill_id}
                    </h3>
                    {vote.result && (
                      <span
                        className={`shrink-0 rounded-md px-2.5 py-1 text-xs font-bold ${
                          passed
                            ? "bg-emerald-50 text-emerald-600"
                            : "bg-red-50 text-red-500"
                        }`}
                      >
                        {vote.result}
                      </span>
                    )}
                  </div>

                  {/* Outcome rows — Polymarket style large percentages */}
                  <div className="mt-4 space-y-2">
                    {/* 찬성 */}
                    <div className="relative overflow-hidden rounded-lg bg-gray-50 px-4 py-2.5">
                      <div
                        className="absolute inset-y-0 left-0 bg-emerald-500/10"
                        style={{ width: `${yesPct}%` }}
                      />
                      <div className="relative flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">
                          찬성
                        </span>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-gray-400">
                            {formatNumber(vote.yes_count)}명
                          </span>
                          <span className="min-w-[3rem] text-right text-lg font-bold text-emerald-600">
                            {yesPct}%
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* 반대 */}
                    <div className="relative overflow-hidden rounded-lg bg-gray-50 px-4 py-2.5">
                      <div
                        className="absolute inset-y-0 left-0 bg-red-500/10"
                        style={{ width: `${noPct}%` }}
                      />
                      <div className="relative flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">
                          반대
                        </span>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-gray-400">
                            {formatNumber(vote.no_count)}명
                          </span>
                          <span className="min-w-[3rem] text-right text-lg font-bold text-red-500">
                            {noPct}%
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* 기권 (only show if > 0) */}
                    {(vote.abstain_count ?? 0) > 0 && (
                      <div className="relative overflow-hidden rounded-lg bg-gray-50 px-4 py-2.5">
                        <div
                          className="absolute inset-y-0 left-0 bg-amber-500/10"
                          style={{ width: `${absPct}%` }}
                        />
                        <div className="relative flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-700">
                            기권
                          </span>
                          <div className="flex items-center gap-3">
                            <span className="text-xs text-gray-400">
                              {formatNumber(vote.abstain_count)}명
                            </span>
                            <span className="min-w-[3rem] text-right text-lg font-bold text-amber-500">
                              {absPct}%
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Footer meta */}
                  <div className="mt-3 flex items-center justify-between text-xs text-gray-400">
                    <span>{formatDate(vote.vote_date)}</span>
                    <span>
                      투표율 {turnout}% · 재적 {formatNumber(vote.total_members)}명
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>

          {data && (
            <Pagination page={page} pages={data.pages} onPageChange={setPage} />
          )}
        </>
      )}
    </div>
  );
}
