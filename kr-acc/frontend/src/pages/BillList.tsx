import { useRef, useState } from "react";
import { Link } from "react-router";
import { useBills } from "@/api/queries";
import Pagination from "@/components/layout/Pagination";
import BillPipeline from "@/components/bills/BillPipeline";
import { formatDate } from "@/lib/format";

type ViewMode = "list" | "pipeline";

export default function BillList() {
  const [view, setView] = useState<ViewMode>("list");
  const [keyword, setKeyword] = useState("");
  const [debouncedKeyword, setDebouncedKeyword] = useState("");
  const [result, setResult] = useState<string | undefined>();
  const [page, setPage] = useState(1);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  const { data, isLoading } = useBills({
    keyword: debouncedKeyword || undefined,
    result,
    page,
    size: 20,
  });

  function handleKeywordChange(value: string) {
    setKeyword(value);
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      setDebouncedKeyword(value);
      setPage(1);
    }, 300);
  }

  const RESULT_OPTIONS = ["원안가결", "수정가결", "부결", "폐기", "철회"];

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">법안</h1>
        {/* View toggle */}
        <div className="flex rounded-md border border-gray-200">
          <button
            onClick={() => setView("list")}
            className={`px-3 py-1.5 text-xs font-medium ${
              view === "list"
                ? "bg-gray-900 text-white"
                : "text-gray-600 hover:bg-gray-50"
            } rounded-l-md`}
          >
            목록
          </button>
          <button
            onClick={() => setView("pipeline")}
            className={`px-3 py-1.5 text-xs font-medium ${
              view === "pipeline"
                ? "bg-gray-900 text-white"
                : "text-gray-600 hover:bg-gray-50"
            } rounded-r-md`}
          >
            파이프라인
          </button>
        </div>
      </div>

      {view === "pipeline" ? (
        <div className="mt-4">
          <BillPipeline />
        </div>
      ) : (
        <>
          {/* Filters */}
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <input
              type="text"
              placeholder="법안명 검색..."
              value={keyword}
              onChange={(e) => handleKeywordChange(e.target.value)}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-gray-500 focus:outline-none"
            />
            <div className="flex flex-wrap gap-1">
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
                {data?.items.map((bill) => (
                  <Link
                    key={bill.bill_id}
                    to={`/bills/${bill.bill_id}`}
                    className="block rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <p className="font-medium">{bill.bill_name}</p>
                        <div className="mt-1 flex flex-wrap gap-3 text-xs text-gray-500">
                          {bill.bill_no && <span>의안번호 {bill.bill_no}</span>}
                          <span>{formatDate(bill.propose_date)}</span>
                          {bill.proposer_type && <span>{bill.proposer_type}</span>}
                          {bill.committee_name && (
                            <span>{bill.committee_name}</span>
                          )}
                        </div>
                      </div>
                      {bill.result && (
                        <span
                          className={`shrink-0 rounded px-2 py-0.5 text-xs font-medium ${
                            bill.result === "원안가결" || bill.result === "수정가결"
                              ? "bg-green-100 text-green-700"
                              : bill.result === "부결"
                                ? "bg-red-100 text-red-700"
                                : "bg-gray-100 text-gray-600"
                          }`}
                        >
                          {bill.result}
                        </span>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
              {data && (
                <Pagination page={page} pages={data.pages} onPageChange={setPage} />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
