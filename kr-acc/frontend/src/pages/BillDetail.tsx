import { useParams, Link } from "react-router";
import { useBill, useVotes } from "@/api/queries";
import PartyBadge from "@/components/layout/PartyBadge";
import { formatDate, formatNumber } from "@/lib/format";

/** Ordered stages for the timeline — a bill progresses through these. */
const TIMELINE_STAGES = [
  { key: "발의", label: "발의" },
  { key: "위원회심사", label: "위원회 심사" },
  { key: "체계자구심사", label: "체계·자구 심사" },
  { key: "본회의부의", label: "본회의 부의" },
] as const;

/** Terminal/outcome stages. */
const OUTCOME_MAP: Record<string, { label: string; color: string }> = {
  원안가결: { label: "원안가결", color: "#22C55E" },
  수정가결: { label: "수정가결", color: "#16A34A" },
  공포: { label: "공포", color: "#059669" },
  대안반영: { label: "대안반영", color: "#F59E0B" },
  폐기: { label: "폐기", color: "#9CA3AF" },
  철회: { label: "철회", color: "#D1D5DB" },
  부결: { label: "부결", color: "#EF4444" },
};

function getTimelineProgress(status: string | null): number {
  if (!status) return 0;
  const idx = TIMELINE_STAGES.findIndex((s) => s.key === status);
  if (idx !== -1) return idx + 1;
  // If it's a terminal stage, the bill went through all process stages
  if (status in OUTCOME_MAP) return TIMELINE_STAGES.length + 1;
  return 0;
}

export default function BillDetail() {
  const { billId } = useParams<{ billId: string }>();
  const { data: bill, isLoading } = useBill(billId ?? "");
  // Fetch vote data for this bill
  const { data: voteData } = useVotes({ bill_id: billId ?? "", page: 1, size: 1 });

  if (isLoading) {
    return <p className="mt-8 text-center text-gray-500">불러오는 중...</p>;
  }
  if (!bill) {
    return <p className="mt-8 text-center text-gray-500">법안 정보를 찾을 수 없습니다.</p>;
  }

  const primarySponsors = bill.sponsors.filter((s) => s.sponsor_type === "대표발의");
  const jointSponsors = bill.sponsors.filter((s) => s.sponsor_type !== "대표발의");
  const progress = getTimelineProgress(bill.status);
  const outcome = bill.result ? OUTCOME_MAP[bill.result] : null;
  const vote = voteData?.items?.[0];

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

      {/* Timeline */}
      <div className="mt-6 rounded-lg border bg-white p-5">
        <h2 className="text-sm font-semibold text-gray-700">입법 진행 타임라인</h2>
        <div className="mt-4 flex items-center gap-0">
          {TIMELINE_STAGES.map((stage, idx) => {
            const reached = progress > idx;
            const isCurrent = progress === idx + 1 && !outcome;
            return (
              <div key={stage.key} className="flex flex-1 items-center">
                <div className="flex flex-col items-center">
                  <div
                    className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                      reached
                        ? isCurrent
                          ? "bg-blue-500 text-white ring-2 ring-blue-200"
                          : "bg-green-500 text-white"
                        : "bg-gray-200 text-gray-400"
                    }`}
                  >
                    {reached ? (isCurrent ? idx + 1 : "✓") : idx + 1}
                  </div>
                  <span
                    className={`mt-1.5 text-center text-xs ${
                      reached ? "font-medium text-gray-700" : "text-gray-400"
                    }`}
                  >
                    {stage.label}
                  </span>
                </div>
                {idx < TIMELINE_STAGES.length - 1 && (
                  <div
                    className={`mx-1 h-0.5 flex-1 ${
                      progress > idx + 1 ? "bg-green-400" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>
            );
          })}

          {/* Outcome node */}
          {outcome && (
            <>
              <div className="mx-1 h-0.5 flex-1 bg-green-400" />
              <div className="flex flex-col items-center">
                <div
                  className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold text-white"
                  style={{ backgroundColor: outcome.color }}
                >
                  ★
                </div>
                <span className="mt-1.5 text-center text-xs font-medium" style={{ color: outcome.color }}>
                  {outcome.label}
                </span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Status + Result + Committee */}
      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">현재 상태</p>
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

      {/* Vote result if exists */}
      {vote && (
        <div className="mt-4 rounded-lg border bg-white p-4">
          <h2 className="text-sm font-semibold text-gray-700">본회의 표결</h2>
          <div className="mt-3 flex flex-wrap items-center gap-4 text-sm">
            <span className="text-gray-500">{formatDate(vote.vote_date)}</span>
            {vote.result && (
              <span
                className={`rounded px-2 py-0.5 text-xs font-medium ${
                  vote.result === "가결"
                    ? "bg-green-100 text-green-700"
                    : "bg-red-100 text-red-700"
                }`}
              >
                {vote.result}
              </span>
            )}
            <span className="text-green-600">찬성 {formatNumber(vote.yes_count ?? 0)}</span>
            <span className="text-red-600">반대 {formatNumber(vote.no_count ?? 0)}</span>
            <span className="text-yellow-600">기권 {formatNumber(vote.abstain_count ?? 0)}</span>
            <span className="text-gray-400">불참 {formatNumber(vote.absent_count ?? 0)}</span>
            <Link
              to={`/votes/${vote.vote_id}`}
              className="text-blue-600 hover:underline"
            >
              표결 상세 →
            </Link>
          </div>
        </div>
      )}

      {/* External link */}
      {bill.detail_url && (
        <a
          href={bill.detail_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 inline-block text-sm text-blue-600 hover:underline"
        >
          국회 의안정보 바로가기 →
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
