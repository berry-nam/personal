import { useState } from "react";
import { Link } from "react-router";
import { useVotes } from "@/api/queries";
import Pagination from "@/components/layout/Pagination";
import { formatDate, formatNumber } from "@/lib/format";

export default function VoteList() {
  const [result, setResult] = useState<string | undefined>();
  const [page, setPage] = useState(1);

  const { data, isLoading } = useVotes({ result, page, size: 20 });

  const RESULT_OPTIONS = ["가결", "부결"];

  return (
    <div>
      <h1 className="text-2xl font-bold">본회의 표결</h1>

      {/* Filters */}
      <div className="mt-4 flex gap-1">
        <button
          onClick={() => {
            setResult(undefined);
            setPage(1);
          }}
          className={`rounded-full px-3 py-1 text-xs ${
            !result
              ? "bg-gray-900 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          전체
        </button>
        {RESULT_OPTIONS.map((r) => (
          <button
            key={r}
            onClick={() => {
              setResult(r);
              setPage(1);
            }}
            className={`rounded-full px-3 py-1 text-xs ${
              result === r
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {r}
          </button>
        ))}
      </div>

      {/* Results */}
      {isLoading ? (
        <p className="mt-8 text-center text-gray-500">불러오는 중...</p>
      ) : (
        <>
          <p className="mt-4 text-sm text-gray-500">
            총 {data?.total ?? 0}건
          </p>
          <div className="mt-3 space-y-2">
            {data?.items.map((vote) => (
              <Link
                key={vote.vote_id}
                to={`/votes/${vote.vote_id}`}
                className="block rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-medium">
                      {vote.bill_name ?? vote.bill_id}
                    </p>
                    <p className="mt-1 text-xs text-gray-500">
                      {formatDate(vote.vote_date)}
                    </p>
                  </div>
                  {vote.result && (
                    <span
                      className={`shrink-0 rounded px-2 py-0.5 text-xs font-medium ${
                        vote.result === "가결"
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {vote.result}
                    </span>
                  )}
                </div>

                {/* Vote breakdown bar */}
                {vote.total_members && (
                  <div className="mt-3">
                    <div className="flex h-2 overflow-hidden rounded-full bg-gray-100">
                      {vote.yes_count && vote.yes_count > 0 && (
                        <div
                          className="bg-green-500"
                          style={{
                            width: `${(vote.yes_count / vote.total_members) * 100}%`,
                          }}
                        />
                      )}
                      {vote.no_count && vote.no_count > 0 && (
                        <div
                          className="bg-red-500"
                          style={{
                            width: `${(vote.no_count / vote.total_members) * 100}%`,
                          }}
                        />
                      )}
                      {vote.abstain_count && vote.abstain_count > 0 && (
                        <div
                          className="bg-yellow-500"
                          style={{
                            width: `${(vote.abstain_count / vote.total_members) * 100}%`,
                          }}
                        />
                      )}
                    </div>
                    <div className="mt-1 flex gap-3 text-xs text-gray-500">
                      <span>찬성 {formatNumber(vote.yes_count)}</span>
                      <span>반대 {formatNumber(vote.no_count)}</span>
                      <span>기권 {formatNumber(vote.abstain_count)}</span>
                      <span>불참 {formatNumber(vote.absent_count)}</span>
                    </div>
                  </div>
                )}
              </Link>
            ))}
          </div>
          {data && (
            <Pagination page={page} pages={data.pages} onPageChange={setPage} />
          )}
        </>
      )}
    </div>
  );
}
