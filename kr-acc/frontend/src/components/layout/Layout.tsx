import { Outlet, useLocation } from "react-router";
import Header from "./Header";

export default function Layout() {
  const location = useLocation();
  const isDashboard = location.pathname === "/";

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      {isDashboard ? (
        <main>
          <Outlet />
        </main>
      ) : (
        <main className="mx-auto max-w-7xl px-4 py-6">
          <Outlet />
        </main>
      )}
    </div>
  );
}
