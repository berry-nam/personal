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

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        <Link to="/" className="text-xl font-bold tracking-tight">
          kr-acc
        </Link>
        <nav className="flex gap-1">
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
