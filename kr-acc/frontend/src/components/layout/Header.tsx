import { Link, useLocation, useNavigate } from "react-router";
import { useState, useRef, useEffect } from "react";
import { usePoliticians, useBills } from "@/api/queries";
import { getPartyColor } from "@/lib/partyColors";

const NAV_ITEMS = [
  { to: "/", label: "대시보드" },
  { to: "/politicians", label: "정치인" },
  { to: "/bills", label: "법안" },
  { to: "/votes", label: "표결" },
  { to: "/graph", label: "네트워크" },
] as const;

export default function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const trimmed = query.trim();
  const politicianResults = usePoliticians({
    name: trimmed || undefined,
    page: 1,
    size: 5,
  });
  const billResults = useBills({
    keyword: trimmed || undefined,
    page: 1,
    size: 5,
  });

  // Close dropdown on outside click
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  // Close on navigation
  useEffect(() => {
    setOpen(false);
    setQuery("");
  }, [location.pathname]);

  const hasResults =
    trimmed.length >= 1 &&
    ((politicianResults.data?.items.length ?? 0) > 0 ||
      (billResults.data?.items.length ?? 0) > 0);

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-2 px-4 sm:gap-4">
        <Link to="/" className="shrink-0 text-xl font-bold tracking-tight">
          kr-acc
        </Link>

        {/* Search bar */}
        <div ref={ref} className="relative mx-2 min-w-0 flex-1 sm:mx-4 sm:block">
          <input
            type="text"
            placeholder="정치인·법안 검색..."
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setOpen(true);
            }}
            onFocus={() => trimmed && setOpen(true)}
            onKeyDown={(e) => {
              if (e.key === "Escape") {
                setOpen(false);
              }
            }}
            className="w-full max-w-md rounded-xl border border-gray-200 bg-gray-50 px-4 py-1.5 text-sm placeholder-gray-400 transition-colors focus:border-gray-400 focus:bg-white focus:outline-none"
          />

          {/* Dropdown results */}
          {open && hasResults && (
            <div className="absolute left-0 top-full z-50 mt-1 w-full max-w-md overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl">
              {/* Politicians */}
              {(politicianResults.data?.items.length ?? 0) > 0 && (
                <div>
                  <p className="px-4 pt-3 text-xs font-medium text-gray-400">
                    정치인
                  </p>
                  {politicianResults.data!.items.map((pol) => (
                    <button
                      key={pol.id}
                      onClick={() => navigate(`/politicians/${pol.id}`)}
                      className="flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors hover:bg-gray-50"
                    >
                      <span
                        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
                        style={{
                          backgroundColor: getPartyColor(pol.party),
                        }}
                      >
                        {pol.name.charAt(0)}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium">{pol.name}</p>
                        <p className="truncate text-xs text-gray-400">
                          {pol.party} · {pol.constituency ?? "비례대표"}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {/* Bills */}
              {(billResults.data?.items.length ?? 0) > 0 && (
                <div>
                  <p className="px-4 pt-3 text-xs font-medium text-gray-400">
                    법안
                  </p>
                  {billResults.data!.items.map((bill) => (
                    <button
                      key={bill.bill_id}
                      onClick={() => navigate(`/bills/${bill.bill_id}`)}
                      className="flex w-full items-center gap-3 px-4 py-2.5 text-left transition-colors hover:bg-gray-50"
                    >
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium">
                          {bill.bill_name}
                        </p>
                        <p className="text-xs text-gray-400">
                          {bill.propose_date} · {bill.proposer_type ?? "의원"}
                        </p>
                      </div>
                      {bill.result && (
                        <span className="shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium text-gray-500 bg-gray-100">
                          {bill.result}
                        </span>
                      )}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        <nav className="flex shrink-0 gap-1 overflow-x-auto">
          {NAV_ITEMS.map(({ to, label }) => {
            const active =
              to === "/"
                ? location.pathname === "/"
                : location.pathname.startsWith(to);
            return (
              <Link
                key={to}
                to={to}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  active
                    ? "bg-gray-900 text-white"
                    : "text-gray-600 hover:bg-gray-100"
                }`}
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
