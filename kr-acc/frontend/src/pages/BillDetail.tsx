import { useParams, Link } from "react-router";
import { useBill } from "@/api/queries";
import PartyBadge from "@/components/layout/PartyBadge";
import { formatDate } from "@/lib/format";

export default function BillDetail() {
  const { billId } = useParams<{ billId: string }>();
  const { data: bill, isLoading } = useBill(billId ?? "");

  if (isLoading) {
    return <p className="mt-8 text-center text-gray-500">불러오는 중...</p>;
  }
  if (!bill) {
    return <p className="mt-8 text-center text-gray-500">법안 정보를 찾을 수 없습니다.</p>;
  }

  const primarySponsors = bill.sponsors.filter((s) => s.sponsor_type === "대표발의");
  const jointSponsors = bill.sponsors.filter((s) => s.sponsor_type !== "대표발의");

  return (
    <div>
      {/* Back link */}
      <Link to="/bills" className="text-sm text-gray-500 hover:text-gray-700">
        &larr; 법안 목록
      </Link>

      {/* Header */}
      <h1 className="mt-3 text-2xl font-bold">{bill.bill_name}</h1>
      <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-gray-500">
        {bill.bill_no && <span>의안번호 {bill.bill_no}</span>}
        <span>{formatDate(bill.propose_date)}</span>
        {bill.proposer_type && <span>{bill.proposer_type}</span>}
      </div>

      {/* Status + Result */}
      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">상태</p>
          <p className="mt-1 font-medium">{bill.status ?? "—"}</p>
        </div>
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">결과</p>
          <p className="mt-1 font-medium">
            {bill.result ? (
              <span
                className={`rounded px-2 py-0.5 text-sm font-medium ${
                  bill.result === "원안가결" || bill.result === "수정가결"
                    ? "bg-green-100 text-green-700"
                    : bill.result === "부결"
                      ? "bg-red-100 text-red-700"
                      : "bg-gray-100 text-gray-600"
                }`}
              >
                {bill.result}
              </span>
            ) : (
              "—"
            )}
          </p>
        </div>
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">소관위원회</p>
          <p className="mt-1 font-medium">{bill.committee_name ?? "—"}</p>
        </div>
      </div>

      {/* External link */}
      {bill.detail_url && (
        <a
          href={bill.detail_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 inline-block text-sm text-blue-600 hover:underline"
        >
          국회 의안정보 바로가기 &rarr;
        </a>
      )}

      {/* Primary sponsors */}
      {primarySponsors.length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold text-gray-700">
            대표발의 ({primarySponsors.length}명)
          </h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {primarySponsors.map((s) => (
              <Link
                key={s.politician_id}
                to={`/politicians/${s.politician_id}`}
                className="flex items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm transition-shadow hover:shadow-sm"
              >
                <span className="font-medium">{s.politician_name ?? "—"}</span>
                <PartyBadge party={s.politician_party} />
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Joint sponsors */}
      {jointSponsors.length > 0 && (
        <div className="mt-5">
          <h2 className="text-sm font-semibold text-gray-700">
            공동발의 ({jointSponsors.length}명)
          </h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {jointSponsors.map((s) => (
              <Link
                key={s.politician_id}
                to={`/politicians/${s.politician_id}`}
                className="rounded-lg border bg-white px-3 py-1.5 text-xs text-gray-700 transition-shadow hover:shadow-sm"
              >
                {s.politician_name ?? "—"}
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
