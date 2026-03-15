import { useEffect, useState } from "react";
import { Link, Outlet, useNavigate } from "react-router";
import { useMe } from "@/api/labelingQueries";
import type { LabelingUser } from "@/types/labeling";

export default function LabelingLayout() {
  const navigate = useNavigate();
  const [user, setUser] = useState<LabelingUser | null>(null);
  const { data: freshUser } = useMe();

  useEffect(() => {
    document.title = "CookieDeal Labeler";
    const stored = localStorage.getItem("labeling_user");
    if (!stored) {
      navigate("/labeling/login");
      return;
    }
    setUser(JSON.parse(stored));
  }, [navigate]);

  // Sync localStorage with fresh user data from server
  useEffect(() => {
    if (freshUser) {
      localStorage.setItem("labeling_user", JSON.stringify(freshUser));
      setUser(freshUser as LabelingUser);
    }
  }, [freshUser]);

  const handleLogout = () => {
    localStorage.removeItem("labeling_token");
    localStorage.removeItem("labeling_user");
    navigate("/labeling/login");
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-brand-100 bg-white">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
          <Link to="/labeling" className="flex items-center gap-2 text-lg font-bold text-brand-600">
            <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-500 text-xs font-black text-white">CD</span>
            Labeler
          </Link>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">{user.display_name}</span>
            {user.role === "admin" && (
              <span className="rounded bg-brand-100 px-1.5 py-0.5 text-xs font-medium text-brand-700">
                Admin
              </span>
            )}
            <button
              onClick={handleLogout}
              className="rounded-md px-2 py-1 text-sm text-gray-500 hover:bg-gray-100 hover:text-gray-700"
            >
              로그아웃
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <Outlet />
    </div>
  );
}
