import { Link } from "react-router";
import { usePoliticians } from "@/api/queries";
import { useBills } from "@/api/queries";
import { useVotes } from "@/api/queries";
import { useParties } from "@/api/queries";
import { getPartyColor } from "@/lib/partyColors";

function StatCard({
  label,
  value,
  to,
}: {
  label: string;
  value: string | number;
  to: string;
}) {
  return (
    <Link
      to={to}
      className="rounded-lg border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md"
    >
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 text-3xl font-bold">{value}</p>
    </Link>
  );
}

export default function Dashboard() {
  const politicians = usePoliticians({ page: 1, size: 1 });
  const bills = useBills({ page: 1, size: 1 });
  const votes = useVotes({ page: 1, size: 1 });
  const parties = useParties();

  return (
    <div>
      <h1 className="text-2xl font-bold">대시보드</h1>
      <p className="mt-1 text-gray-500">제22대 국회 활동 현황</p>

      {/* Summary stats */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="국회의원"
          value={politicians.data?.total ?? "—"}
          to="/politicians"
        />
        <StatCard
          label="발의 법안"
          value={bills.data?.total ?? "—"}
          to="/bills"
        />
        <StatCard
          label="본회의 표결"
          value={votes.data?.total ?? "—"}
          to="/votes"
        />
      </div>

      {/* Party breakdown */}
      {parties.data && parties.data.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold">정당</h2>
          <div className="mt-3 flex flex-wrap gap-3">
            {parties.data.map((p) => (
              <Link
                key={p.id}
                to={`/politicians?party=${encodeURIComponent(p.name)}`}
                className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm transition-shadow hover:shadow-md"
              >
                <span
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: getPartyColor(p.name) }}
                />
                {p.name}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Quick links */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold">탐색</h2>
        <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Link
            to="/graph"
            className="rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
          >
            <p className="font-medium">공동발의 네트워크</p>
            <p className="mt-1 text-sm text-gray-500">
              의원 간 공동발의 관계를 시각화합니다
            </p>
          </Link>
          <Link
            to="/bills"
            className="rounded-lg border border-gray-200 bg-white p-4 transition-shadow hover:shadow-md"
          >
            <p className="font-medium">법안 검색</p>
            <p className="mt-1 text-sm text-gray-500">
              키워드, 위원회, 처리 결과로 법안을 검색합니다
            </p>
          </Link>
        </div>
      </div>
    </div>
  );
}
