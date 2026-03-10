import { useParams, Link } from "react-router";
import { useBill, useVotes } from "@/api/queries";
import { formatDate, formatNumber } from "@/lib/format";
import PartyBadge from "@/components/layout/PartyBadge";
import { getPartyColor } from "@/lib/partyColors";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

export default function BillDetail() {
  const { billId } = useParams<{ billId: string }>();
  const { data: bill, isLoading } = useBill(billId ?? "");
  const votes = useVotes({ bill_id: billId ?? "", page: 1, size: 5 });

  if (isLoading) {
    return <p className="mt-8 text-center text-gray-500">불러오는 중...</p>;
  }
  if (!bill) {
    return (
      <p className="mt-8 text-center text-gray-500">
        법안 정보를 찾을 수 없습니다.
      </p>
    );
  }

  const primary = bill.sponsors.filter((s) => s.sponsor_type === "primary");
  const cosigners = bill.sponsors.filter((s) => s.sponsor_type !== "primary");

  // Party distribution among sponsors
  const partyCount = new Map<string, number>();
  for (const s of bill.sponsors) {
    const party = s.politician_party ?? "무소속";
    partyCount.set(party, (partyCount.get(party) ?? 0) + 1);
  }
  const partyData = [...partyCount.entries()]
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const vote = votes.data?.items?.[0]; // most relevant vote for this bill

  return (
    <div className="space-y-6">
      {/* Back */}
      <Link to="/bills" className="text-sm text-gray-500 hover:text-gray-700">
        &larr; 법안 목록
      </Link>

      {/* Title & badges */}
      <div>
        <h1 className="text-2xl font-bold leading-tight">{bill.bill_name}</h1>
        <div className="mt-3 flex flex-wrap gap-2">
          {bill.result && (
            <span
              className={`rounded-full px-3 py-1 text-xs font-medium ${
                bill.result === "원안가결" || bill.result === "수정가결"
                  ? "bg-green-100 text-green-700"
                  : bill.result === "부결"
                    ? "bg-red-100 text-red-700"
                    : "bg-gray-100 text-gray-600"
              }`}
            >
              {bill.result}
            </span>
          )}
          {bill.status && (
            <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium text-blue-700">
              {bill.status}
            </span>
          )}
          {bill.proposer_type && (
            <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600">
              {bill.proposer_type}
            </span>
          )}
        </div>
      </div>

      {/* Meta info grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {bill.bill_no && (
          <div className="rounded-lg border bg-white p-4">
            <p className="text-xs text-gray-500">의안번호</p>
            <p className="mt-1 text-lg font-bold">{bill.bill_no}</p>
          </div>
        )}
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">발의일</p>
          <p className="mt-1 text-lg font-bold">
            {bill.propose_date ? formatDate(bill.propose_date) : "—"}
          </p>
        </div>
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">대수</p>
          <p className="mt-1 text-lg font-bold">제{bill.assembly_term}대</p>
        </div>
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">발의자 수</p>
          <p className="mt-1 text-lg font-bold">{bill.sponsors.length}명</p>
        </div>
      </div>

      {/* Committee */}
      {bill.committee_name && (
        <div className="rounded-lg border bg-white p-4">
          <p className="text-xs text-gray-500">소관위원회</p>
          <p className="mt-1 font-medium">{bill.committee_name}</p>
        </div>
      )}

      {/* Vote result — Polymarket-style */}
      {vote && (() => {
        const total = vote.total_members ?? 0;
        const yp = total ? Math.round(((vote.yes_count ?? 0) / total) * 100) : 0;
        const np = total ? Math.round(((vote.no_count ?? 0) / total) * 100) : 0;
        const ap = total ? Math.round(((vote.abstain_count ?? 0) / total) * 100) : 0;
        const passed = vote.result === "가결" || vote.result === "원안가결" || vote.result === "수정가결";
        return (
          <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-500">본회의 표결</h2>
              {vote.result && (
                <span className={`rounded-md px-2.5 py-1 text-xs font-bold ${passed ? "bg-emerald-50 text-emerald-600" : "bg-red-50 text-red-500"}`}>
                  {vote.result}
                </span>
              )}
            </div>
            <div className="mt-4 space-y-2">
              {[
                { label: "찬성", count: vote.yes_count ?? 0, p: yp, bg: "bg-emerald-500/10", text: "text-emerald-600" },
                { label: "반대", count: vote.no_count ?? 0, p: np, bg: "bg-red-500/10", text: "text-red-500" },
                { label: "기권", count: vote.abstain_count ?? 0, p: ap, bg: "bg-amber-500/10", text: "text-amber-500" },
              ].filter((d) => d.count > 0 || d.label === "찬성" || d.label === "반대").map((d) => (
                <div key={d.label} className="relative overflow-hidden rounded-xl bg-gray-50 px-4 py-2.5">
                  <div className={`absolute inset-y-0 left-0 ${d.bg}`} style={{ width: `${d.p}%` }} />
                  <div className="relative flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">{d.label}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-gray-400">{formatNumber(d.count)}명</span>
                      <span className={`min-w-[3rem] text-right text-lg font-bold ${d.text}`}>{d.p}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {total > 0 && (
              <div className="mt-3 flex h-2 overflow-hidden rounded-full bg-gray-100">
                {(vote.yes_count ?? 0) > 0 && <div className="bg-emerald-500" style={{ width: `${yp}%` }} />}
                {(vote.no_count ?? 0) > 0 && <div className="bg-red-500" style={{ width: `${np}%` }} />}
                {(vote.abstain_count ?? 0) > 0 && <div className="bg-amber-400" style={{ width: `${ap}%` }} />}
              </div>
            )}
            <div className="mt-3 flex items-center justify-between text-xs text-gray-400">
              <span>{formatDate(vote.vote_date)}</span>
              <Link to={`/votes/${vote.vote_id}`} className="text-blue-500 hover:underline">
                의원별 표결 상세 &rarr;
              </Link>
            </div>
          </div>
        );
      })()}

      {/* Sponsors section */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Primary sponsor */}
        <div className="rounded-lg border bg-white p-4">
          <h2 className="text-sm font-medium text-gray-500">대표발의</h2>
          {primary.length > 0 ? (
            <div className="mt-3 space-y-2">
              {primary.map((s) => (
                <Link
                  key={s.politician_id}
                  to={`/politicians/${s.politician_id}`}
                  className="flex items-center gap-3 rounded-lg border p-3 transition-shadow hover:shadow-md"
                >
                  <div
                    className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
                    style={{
                      backgroundColor: getPartyColor(s.politician_party),
                    }}
                  >
                    {s.politician_name?.charAt(0) ?? "?"}
                  </div>
                  <div>
                    <p className="font-medium">{s.politician_name}</p>
                    {s.politician_party && (
                      <PartyBadge party={s.politician_party} />
                    )}
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <p className="mt-2 text-sm text-gray-400">정보 없음</p>
          )}
        </div>

        {/* Party distribution pie */}
        {partyData.length > 0 && (
          <div className="rounded-lg border bg-white p-4">
            <h2 className="text-sm font-medium text-gray-500">
              발의자 정당 분포
            </h2>
            <div className="mx-auto mt-2 h-48 w-48">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={partyData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={35}
                    outerRadius={65}
                  >
                    {partyData.map((d) => (
                      <Cell
                        key={d.name}
                        fill={getPartyColor(d.name)}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 flex flex-wrap justify-center gap-3 text-xs">
              {partyData.map((d) => (
                <span key={d.name} className="flex items-center gap-1">
                  <span
                    className="inline-block h-2 w-2 rounded-full"
                    style={{ backgroundColor: getPartyColor(d.name) }}
                  />
                  {d.name} {d.value}명
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Co-sponsors */}
      {cosigners.length > 0 && (
        <div className="rounded-lg border bg-white p-4">
          <h2 className="text-sm font-medium text-gray-500">
            공동발의 ({cosigners.length}명)
          </h2>
          <div className="mt-3 flex flex-wrap gap-1.5">
            {cosigners.map((s) => (
              <Link
                key={s.politician_id}
                to={`/politicians/${s.politician_id}`}
                className="inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs transition-colors hover:bg-gray-50"
              >
                <span
                  className="inline-block h-1.5 w-1.5 rounded-full"
                  style={{
                    backgroundColor: getPartyColor(s.politician_party),
                  }}
                />
                {s.politician_name}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* External links */}
      <div className="flex flex-wrap gap-3">
        {bill.detail_url && (
          <a
            href={bill.detail_url}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border bg-white px-4 py-2.5 text-sm text-blue-600 transition-shadow hover:shadow-md"
          >
            의안정보시스템에서 보기 &rarr;
          </a>
        )}
        {bill.bill_no && (
          <a
            href={`https://likms.assembly.go.kr/bill/billDetail.do?billId=${bill.bill_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border bg-white px-4 py-2.5 text-sm text-gray-600 transition-shadow hover:shadow-md"
          >
            국회 의안정보 &rarr;
          </a>
        )}
      </div>
    </div>
  );
}
