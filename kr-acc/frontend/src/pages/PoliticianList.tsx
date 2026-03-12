import { useState } from "react";
import { Link, useSearchParams } from "react-router";
import useDocumentTitle from "@/lib/useDocumentTitle";
import { usePoliticians, useParties } from "@/api/queries";
import Pagination from "@/components/layout/Pagination";
import PartyBadge from "@/components/layout/PartyBadge";
import { getPartyColor } from "@/lib/partyColors";

const TERMS = [22, 21, 20, 19, 18, 17];

export default function PoliticianList() {
  useDocumentTitle("정치인");
  const [searchParams, setSearchParams] = useSearchParams();
  const partyFilter = searchParams.get("party") ?? undefined;
  const termFilter = searchParams.get("term")
    ? Number(searchParams.get("term"))
    : undefined;
  const [nameSearch, setNameSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = usePoliticians({
    party: partyFilter,
    name: nameSearch || undefined,
    assembly_term: termFilter,
    page,
    size: 24,
  });
  const parties = useParties();

  function updateFilter(key: string, value: string | undefined) {
    setPage(1);
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    setSearchParams(params);
  }

  return (
    <div>
      <h1 className="text-2xl font-bold">정치인</h1>

      {/* Filters */}
      <div className="mt-4 space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          <input
            type="text"
            placeholder="이름 검색..."
            value={nameSearch}
            onChange={(e) => {
              setNameSearch(e.target.value);
              setPage(1);
            }}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-gray-500 focus:outline-none"
          />
        </div>

        {/* Term filter */}
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => updateFilter("term", undefined)}
            className={`rounded-full px-3 py-1 text-xs ${
              !termFilter
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            전체 대수
          </button>
          {TERMS.map((t) => (
            <button
              key={t}
              onClick={() => updateFilter("term", String(t))}
              className={`rounded-full px-3 py-1 text-xs ${
                termFilter === t
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {t}대
            </button>
          ))}
        </div>

        {/* Party filter */}
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => updateFilter("party", undefined)}
            className={`rounded-full px-3 py-1 text-xs ${
              !partyFilter
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            전체 정당
          </button>
          {parties.data?.map((p) => (
            <button
              key={p.id}
              onClick={() => updateFilter("party", p.name)}
              className={`rounded-full px-3 py-1 text-xs ${
                partyFilter === p.name
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {p.name}
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
            총 {data?.total ?? 0}명
          </p>
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data?.items.map((pol) => (
              <Link
                key={pol.id}
                to={`/politicians/${pol.id}`}
                className="flex items-center gap-3 rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
              >
                <div
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
                  style={{ backgroundColor: getPartyColor(pol.party) }}
                >
                  {pol.name.charAt(0)}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-medium">{pol.name}</p>
                  <div className="mt-0.5 flex items-center gap-2">
                    <PartyBadge party={pol.party} />
                    {pol.constituency && (
                      <span className="truncate text-xs text-gray-400">
                        {pol.constituency}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-0.5">
                  <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] text-gray-500">
                    {pol.assembly_term}대
                  </span>
                  {pol.elected_count && (
                    <span className="text-xs text-gray-400">
                      {pol.elected_count}선
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
    </div>
  );
}
