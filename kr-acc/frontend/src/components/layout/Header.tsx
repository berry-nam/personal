import { useState } from "react";
import { Link, useLocation } from "react-router";

const NAV_ITEMS = [
  { to: "/", label: "대시보드" },
  { to: "/politicians", label: "국회의원" },
  { to: "/bills", label: "법안" },
  { to: "/votes", label: "표결" },
  { to: "/graph", label: "네트워크" },
] as const;

export default function Header() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  function navLink(to: string, label: string) {
    const active =
      to === "/" ? location.pathname === "/" : location.pathname.startsWith(to);
    return (
      <Link
        key={to}
        to={to}
        onClick={() => setMobileOpen(false)}
        className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
          active
            ? "bg-gray-900 text-white"
            : "text-gray-600 hover:bg-gray-100"
        }`}
      >
        {label}
      </Link>
    );
  }

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        <Link to="/" className="text-xl font-bold tracking-tight">
          kr-acc
        </Link>

        {/* Desktop nav */}
        <nav className="hidden gap-1 sm:flex">
          {NAV_ITEMS.map(({ to, label }) => navLink(to, label))}
        </nav>

        {/* Mobile hamburger */}
        <button
          className="rounded-md p-1.5 text-gray-600 hover:bg-gray-100 sm:hidden"
          onClick={() => setMobileOpen((v) => !v)}
          aria-label="메뉴 열기"
        >
          <svg
            className="h-5 w-5"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            viewBox="0 0 24 24"
          >
            {mobileOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile dropdown */}
      {mobileOpen && (
        <nav className="flex flex-col gap-1 border-t border-gray-100 px-4 py-2 sm:hidden">
          {NAV_ITEMS.map(({ to, label }) => navLink(to, label))}
        </nav>
      )}
    </header>
  );
}
