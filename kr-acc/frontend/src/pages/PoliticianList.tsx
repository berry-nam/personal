import { useState } from "react";
import { Link, useSearchParams } from "react-router";
import { usePoliticians, useParties } from "@/api/queries";
import Pagination from "@/components/layout/Pagination";
import PartyBadge from "@/components/layout/PartyBadge";

export default function PoliticianList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const partyFilter = searchParams.get("party") ?? undefined;
  const [nameSearch, setNameSearch] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = usePoliticians({
    party: partyFilter,
    name: nameSearch || undefined,
    page,
    size: 24,
  });
  const parties = useParties();

  function setParty(party: string | undefined) {
    setPage(1);
    if (party) {
      setSearchParams({ party });
    } else {
      setSearchParams({});
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold">국회의원</h1>

      {/* Filters */}
      <div className="mt-4 flex flex-wrap items-center gap-3">
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
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => setParty(undefined)}
            className={`rounded-full px-3 py-1 text-xs ${
              !partyFilter
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            전체
          </button>
          {parties.data?.map((p) => (
            <button
              key={p.id}
              onClick={() => setParty(p.name)}
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
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 text-sm font-bold text-gray-600">
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
                {pol.elected_count && (
                  <span className="text-xs text-gray-400">
                    {pol.elected_count}선
                  </span>
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
