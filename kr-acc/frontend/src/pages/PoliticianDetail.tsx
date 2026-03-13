import { useState } from "react";
import { useParams, Link } from "react-router";
import {
  usePolitician,
  usePoliticianBills,
  usePoliticianVotes,
  useNeighbors,
  usePoliticianAssets,
  usePoliticianCompanies,
  usePoliticianFunds,
  usePoliticianAssetDetail,
} from "@/api/queries";
import useDocumentTitle from "@/lib/useDocumentTitle";
import PartyBadge from "@/components/layout/PartyBadge";
import ForceGraph from "@/components/graph/ForceGraph";
import { formatDate, formatNumber, formatKrw } from "@/lib/format";
import { getPartyColor } from "@/lib/partyColors";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  LineChart,
  Line,
  CartesianGrid,
} from "recharts";

const VOTE_COLORS: Record<string, string> = {
  찬성: "#22C55E",
  반대: "#EF4444",
  기권: "#F59E0B",
  불참: "#9CA3AF",
};

const CATEGORY_LABELS: Record<string, string> = {
  real_estate: "부동산",
  deposit: "예금",
  securities: "유가증권",
  crypto: "가상자산",
  vehicle: "차량",
};

const CATEGORY_COLORS: Record<string, string> = {
  real_estate: "#3B82F6",
  deposit: "#22C55E",
  securities: "#F59E0B",
  crypto: "#8B5CF6",
  vehicle: "#6B7280",
};

export default function PoliticianDetail() {
  const { id } = useParams<{ id: string }>();
  const politicianId = Number(id);
  const { data: pol, isLoading } = usePolitician(politicianId);
  useDocumentTitle(pol ? `${pol.name} (${pol.party ?? "무소속"})` : "정치인");
  const bills = usePoliticianBills(politicianId, { page: 1, size: 5 });
  const votes = usePoliticianVotes(politicianId, { page: 1, size: 5 });
  const neighbors = useNeighbors(pol?.assembly_id ?? "", {
    min_weight: 1,
    limit: 10,
  });
  const assets = usePoliticianAssets(politicianId);
  const companies = usePoliticianCompanies(politicianId);
  const funds = usePoliticianFunds(politicianId);

  // Expandable detail year
  const [detailYear, setDetailYear] = useState<number | null>(null);
  const latestYear = assets.data?.[0]?.report_year ?? 0;
  const activeDetailYear = detailYear ?? latestYear;
  const assetDetail = usePoliticianAssetDetail(
    politicianId,
    activeDetailYear,
  );

  if (isLoading) {
    return <p className="mt-8 text-center text-gray-500">불러오는 중...</p>;
  }
  if (!pol) {
    return (
      <p className="mt-8 text-center text-gray-500">
        의원 정보를 찾을 수 없습니다.
      </p>
    );
  }

  const stats = pol.stats;
  const voteChartData = stats
    ? [
        { name: "찬성", value: stats.yes_count },
        { name: "반대", value: stats.no_count },
        { name: "기권", value: stats.abstain_count },
        { name: "불참", value: stats.absent_count },
      ].filter((d) => d.value > 0)
    : [];

  // Group asset items by category
  const itemsByCategory = new Map<string, typeof assetDetail.data extends { items: infer I } ? (I extends (infer T)[] ? T[] : never) : never>();
  if (assetDetail.data?.items) {
    for (const item of assetDetail.data.items) {
      const list = itemsByCategory.get(item.category) ?? [];
      list.push(item);
      itemsByCategory.set(item.category, list);
    }
  }

  return (
    <div className="space-y-6">
      {/* Back */}
      <Link
        to="/politicians"
        className="text-sm text-gray-500 hover:text-gray-700"
      >
        &larr; 정치인 목록
      </Link>

      {/* Profile header */}
      <div className="flex items-start gap-4">
        {pol.photo_url ? (
          <img
            src={pol.photo_url}
            alt={pol.name}
            className="h-16 w-16 shrink-0 rounded-full object-cover"
          />
        ) : (
          <div
            className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full text-2xl font-bold text-white"
            style={{ backgroundColor: getPartyColor(pol.party) }}
          >
            {pol.name.charAt(0)}
          </div>
        )}
        <div>
          <h1 className="text-2xl font-bold">
            {pol.name}
            {pol.name_hanja && (
              <span className="ml-2 text-base font-normal text-gray-400">
                {pol.name_hanja}
              </span>
            )}
          </h1>
          <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-gray-500">
            <PartyBadge party={pol.party} />
            <span>제{pol.assembly_term}대</span>
            {pol.constituency && <span>{pol.constituency}</span>}
            {pol.elected_count && <span>{pol.elected_count}선</span>}
            {pol.gender && <span>{pol.gender}</span>}
            {pol.birth_date && <span>{formatDate(pol.birth_date)}</span>}
            {pol.eng_name && (
              <span className="text-gray-400">{pol.eng_name}</span>
            )}
          </div>
          {pol.committees && pol.committees.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {pol.committees.map((c) => (
                <span
                  key={c}
                  className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                >
                  {c}
                </span>
              ))}
            </div>
          )}
          <div className="mt-2 flex flex-wrap gap-3 text-xs text-gray-500">
            {pol.email && (
              <a
                href={`mailto:${pol.email}`}
                className="hover:text-gray-700 hover:underline"
              >
                {pol.email}
              </a>
            )}
            {pol.office_address && <span>{pol.office_address}</span>}
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {pol.homepage && (
              <a
                href={pol.homepage}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded bg-blue-50 px-2 py-0.5 text-xs text-blue-600 hover:bg-blue-100"
              >
                홈페이지
              </a>
            )}
            {pol.profile_url && (
              <a
                href={pol.profile_url}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded bg-blue-50 px-2 py-0.5 text-xs text-blue-600 hover:bg-blue-100"
              >
                국회 프로필
              </a>
            )}
            <a
              href={`https://ko.wikipedia.org/wiki/${encodeURIComponent(pol.name)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-600 hover:bg-gray-200"
            >
              위키백과
            </a>
            <a
              href={`https://namu.wiki/w/${encodeURIComponent(pol.name)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded bg-green-50 px-2 py-0.5 text-xs text-green-700 hover:bg-green-100"
            >
              나무위키
            </a>
          </div>
        </div>
      </div>

      {/* Bio */}
      {pol.bio && (
        <div className="rounded-lg border bg-white p-4">
          <h2 className="text-sm font-medium text-gray-500">주요 이력</h2>
          <div className="mt-2 space-y-1 text-sm text-gray-700">
            {pol.bio
              .split(/\r?\n/)
              .filter((line) => line.trim())
              .map((line, i) => (
                <p key={i}>{line.trim()}</p>
              ))}
          </div>
        </div>
      )}

      {/* Stats cards */}
      {stats && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div className="rounded-lg border bg-white p-4">
            <p className="text-xs text-gray-500">표결 참여율</p>
            <p className="mt-1 text-2xl font-bold">
              {stats.participation_rate}%
            </p>
          </div>
          <div className="rounded-lg border bg-white p-4">
            <p className="text-xs text-gray-500">총 표결</p>
            <p className="mt-1 text-2xl font-bold">
              {formatNumber(stats.total_votes)}
            </p>
          </div>
          <div className="rounded-lg border bg-white p-4">
            <p className="text-xs text-gray-500">발의 법안</p>
            <p className="mt-1 text-2xl font-bold">
              {formatNumber(stats.bills_sponsored)}
            </p>
          </div>
          <div className="rounded-lg border bg-white p-4">
            <p className="text-xs text-gray-500">대표발의</p>
            <p className="mt-1 text-2xl font-bold">
              {formatNumber(stats.bills_primary_sponsored)}
            </p>
          </div>
        </div>
      )}

      {/* Charts row */}
      <div className="grid gap-4 md:grid-cols-2">
        {voteChartData.length > 0 && (
          <div className="rounded-lg border bg-white p-4">
            <h2 className="text-sm font-medium text-gray-500">표결 분포</h2>
            <div className="mx-auto mt-2 h-48 w-48">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={voteChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={70}
                  >
                    {voteChartData.map((d) => (
                      <Cell key={d.name} fill={VOTE_COLORS[d.name]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 flex justify-center gap-4 text-xs">
              {voteChartData.map((d) => (
                <span key={d.name} className="flex items-center gap-1">
                  <span
                    className="inline-block h-2 w-2 rounded-full"
                    style={{ backgroundColor: VOTE_COLORS[d.name] }}
                  />
                  {d.name} {d.value}
                </span>
              ))}
            </div>
          </div>
        )}

        {neighbors.data && neighbors.data.length > 0 && (
          <div className="rounded-lg border bg-white p-4">
            <h2 className="text-sm font-medium text-gray-500">
              주요 공동발의 의원
            </h2>
            <div className="mt-3 space-y-2">
              {neighbors.data.map((n) => (
                <Link
                  key={n.assembly_id}
                  to={`/politicians/${n.assembly_id}`}
                  className="flex items-center justify-between rounded-lg px-2 py-1.5 transition-colors hover:bg-gray-50"
                >
                  <div className="flex items-center gap-2">
                    <span
                      className="h-2.5 w-2.5 rounded-full"
                      style={{ backgroundColor: getPartyColor(n.party) }}
                    />
                    <span className="text-sm font-medium">{n.name}</span>
                    {n.party && (
                      <span className="text-xs text-gray-400">{n.party}</span>
                    )}
                  </div>
                  <span className="text-xs text-gray-500">
                    {n.weight}건 공동발의
                  </span>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Co-sponsorship network graph */}
      {neighbors.data && neighbors.data.length > 0 && pol && (
        <div className="rounded-lg border bg-white p-4">
          <h2 className="text-sm font-medium text-gray-500">
            공동발의 네트워크
          </h2>
          <div className="mt-3">
            <ForceGraph
              data={{
                nodes: [
                  { id: pol.assembly_id, name: pol.name, party: pol.party, group: "center" },
                  ...neighbors.data.map((n) => ({
                    id: n.assembly_id,
                    name: n.name,
                    party: n.party,
                    group: n.party,
                  })),
                ],
                edges: neighbors.data.map((n) => ({
                  source: pol.assembly_id,
                  target: n.assembly_id,
                  weight: n.weight,
                })),
              }}
              width={700}
              height={350}
            />
          </div>
        </div>
      )}

      {/* ═══════════════════════════════════════════════════
          ASSET DECLARATIONS — Trend + Detail Items
         ═══════════════════════════════════════════════════ */}
      {assets.data && assets.data.length > 0 && (
        <div className="space-y-4">
          <div className="rounded-lg border bg-white p-4">
            <h2 className="text-sm font-medium text-gray-500">재산 변동 추이</h2>
            <div className="mt-3 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={[...assets.data].reverse()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="report_year" />
                  <YAxis tickFormatter={(v: number) => formatKrw(v)} />
                  <Tooltip formatter={(v) => formatKrw(Number(v))} />
                  <Line type="monotone" dataKey="total_assets" name="총 재산" stroke="#111827" strokeWidth={2} />
                  <Line type="monotone" dataKey="total_real_estate" name="부동산" stroke="#3B82F6" />
                  <Line type="monotone" dataKey="total_securities" name="유가증권" stroke="#F59E0B" />
                  <Line type="monotone" dataKey="total_deposits" name="예금" stroke="#22C55E" />
                  {assets.data.some((a) => a.total_crypto && a.total_crypto > 0) && (
                    <Line type="monotone" dataKey="total_crypto" name="가상자산" stroke="#8B5CF6" />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
            {/* Year summary table */}
            <div className="mt-3 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-xs text-gray-400">
                    <th className="pb-2 font-medium">연도</th>
                    <th className="pb-2 font-medium text-right">총 재산</th>
                    <th className="pb-2 font-medium text-right">부동산</th>
                    <th className="pb-2 font-medium text-right">유가증권</th>
                    <th className="pb-2 font-medium text-right">예금</th>
                    <th className="pb-2 font-medium text-right">가상자산</th>
                    <th className="pb-2 font-medium text-center">상세</th>
                  </tr>
                </thead>
                <tbody>
                  {assets.data.map((a) => (
                    <tr
                      key={a.report_year}
                      className={`border-b last:border-0 ${activeDetailYear === a.report_year ? "bg-blue-50" : ""}`}
                    >
                      <td className="py-2 font-medium">{a.report_year}</td>
                      <td className="py-2 text-right font-semibold">{formatKrw(a.total_assets)}</td>
                      <td className="py-2 text-right">{formatKrw(a.total_real_estate)}</td>
                      <td className="py-2 text-right">{formatKrw(a.total_securities)}</td>
                      <td className="py-2 text-right">{formatKrw(a.total_deposits)}</td>
                      <td className="py-2 text-right">{formatKrw(a.total_crypto)}</td>
                      <td className="py-2 text-center">
                        <button
                          onClick={() =>
                            setDetailYear(
                              activeDetailYear === a.report_year ? null : a.report_year,
                            )
                          }
                          className="rounded bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600 hover:bg-gray-200"
                        >
                          {activeDetailYear === a.report_year ? "접기" : "보기"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Detailed asset items for selected year */}
          {assetDetail.data && assetDetail.data.items.length > 0 && (
            <div className="rounded-lg border bg-white p-4">
              <h2 className="text-sm font-medium text-gray-500">
                {activeDetailYear}년 재산 상세 내역
              </h2>
              <p className="mt-0.5 text-xs text-gray-400">
                항목별 상세 — 부동산 주소지, 보유 주식, 가상자산, 예금, 차량 등
              </p>

              <div className="mt-4 space-y-5">
                {[...itemsByCategory.entries()].map(([cat, items]) => (
                  <div key={cat}>
                    <h3 className="flex items-center gap-2 text-sm font-semibold">
                      <span
                        className="h-2.5 w-2.5 rounded-full"
                        style={{ backgroundColor: CATEGORY_COLORS[cat] ?? "#6B7280" }}
                      />
                      {CATEGORY_LABELS[cat] ?? cat}
                      <span className="text-xs font-normal text-gray-400">
                        {items.length}건
                      </span>
                    </h3>
                    <div className="mt-2 overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b text-left text-xs text-gray-400">
                            <th className="pb-1.5 font-medium">유형</th>
                            <th className="pb-1.5 font-medium">상세</th>
                            <th className="pb-1.5 font-medium">관계</th>
                            <th className="pb-1.5 font-medium text-right">금액</th>
                          </tr>
                        </thead>
                        <tbody>
                          {items
                            .sort((a, b) => (b.value_krw ?? 0) - (a.value_krw ?? 0))
                            .map((item, idx) => (
                              <tr key={idx} className="border-b last:border-0">
                                <td className="py-1.5 text-gray-600">
                                  {item.subcategory ?? "–"}
                                </td>
                                <td className="py-1.5 font-medium">
                                  {item.description ?? "–"}
                                </td>
                                <td className="py-1.5">
                                  {item.relation && (
                                    <span className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-500">
                                      {item.relation}
                                    </span>
                                  )}
                                </td>
                                <td className="py-1.5 text-right font-semibold tabular-nums">
                                  {item.value_krw ? formatKrw(item.value_krw) : "–"}
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Company affiliations */}
      {companies.data && companies.data.length > 0 && (
        <div className="rounded-lg border bg-white p-4">
          <h2 className="text-sm font-medium text-gray-500">기업 관계</h2>
          <p className="mt-0.5 text-xs text-gray-400">
            이 의원이 지분을 보유하고 있거나 관련된 기업
          </p>
          <div className="mt-3 space-y-2">
            {companies.data.map((pc, i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-3">
                <div>
                  <p className="font-medium">{pc.company.corp_name}</p>
                  <div className="mt-0.5 flex flex-wrap gap-2 text-xs text-gray-500">
                    <span className="rounded bg-orange-50 px-1.5 py-0.5 text-orange-600">
                      {pc.relation_type}
                    </span>
                    {pc.company.industry && <span>{pc.company.industry}</span>}
                    {pc.company.stock_code && (
                      <span className="text-gray-400">
                        ({pc.company.stock_code})
                      </span>
                    )}
                    {pc.source_year && <span>{pc.source_year}년</span>}
                  </div>
                  {pc.detail && (
                    <p className="mt-1 text-xs text-gray-500">{pc.detail}</p>
                  )}
                </div>
                {pc.value_krw && (
                  <span className="shrink-0 text-sm font-semibold">
                    {formatKrw(pc.value_krw)}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Political funds */}
      {funds.data && funds.data.length > 0 && (
        <div className="rounded-lg border bg-white p-4">
          <h2 className="text-sm font-medium text-gray-500">정치자금</h2>
          <p className="mt-0.5 text-xs text-gray-400">
            후원회 수입·지출 내역 (연도별)
          </p>
          <div className="mt-3 h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[...funds.data].reverse()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="fund_year" />
                <YAxis tickFormatter={(v: number) => formatKrw(v)} />
                <Tooltip formatter={(v) => formatKrw(Number(v))} />
                <Bar dataKey="income_total" name="수입" fill="#22C55E" />
                <Bar dataKey="expense_total" name="지출" fill="#EF4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          {/* Fund details table */}
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-gray-400">
                  <th className="pb-2 font-medium">연도</th>
                  <th className="pb-2 font-medium text-right">수입</th>
                  <th className="pb-2 font-medium text-right">지출</th>
                  <th className="pb-2 font-medium text-right">잔액</th>
                </tr>
              </thead>
              <tbody>
                {funds.data.map((f) => (
                  <tr key={f.fund_year} className="border-b last:border-0">
                    <td className="py-2 font-medium">{f.fund_year}</td>
                    <td className="py-2 text-right text-emerald-600">
                      {formatKrw(f.income_total)}
                    </td>
                    <td className="py-2 text-right text-red-500">
                      {formatKrw(f.expense_total)}
                    </td>
                    <td className="py-2 text-right font-semibold">
                      {formatKrw(
                        (f.income_total ?? 0) - (f.expense_total ?? 0),
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent votes */}
      {votes.data && votes.data.items.length > 0 && (
        <div className="rounded-lg border bg-white p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium text-gray-500">최근 표결</h2>
            <span className="text-xs text-gray-400">
              전체 {votes.data.total}건
            </span>
          </div>
          <table className="mt-3 w-full text-sm">
            <thead>
              <tr className="border-b text-left text-xs text-gray-400">
                <th className="pb-2 font-medium">법안명</th>
                <th className="pb-2 font-medium">일자</th>
                <th className="pb-2 font-medium">투표</th>
                <th className="pb-2 font-medium">결과</th>
              </tr>
            </thead>
            <tbody>
              {votes.data.items.map((v) => (
                <tr key={v.vote_id} className="border-b last:border-0">
                  <td className="max-w-xs truncate py-2">{v.bill_name}</td>
                  <td className="py-2 text-gray-500">
                    {formatDate(v.vote_date)}
                  </td>
                  <td className="py-2">
                    <span
                      className={`rounded px-1.5 py-0.5 text-xs font-medium ${
                        v.vote_result === "찬성"
                          ? "bg-green-100 text-green-700"
                          : v.vote_result === "반대"
                            ? "bg-red-100 text-red-700"
                            : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {v.vote_result ?? "—"}
                    </span>
                  </td>
                  <td className="py-2 text-gray-500">{v.overall_result}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Recent bills */}
      {bills.data && bills.data.items.length > 0 && (
        <div className="rounded-lg border bg-white p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium text-gray-500">발의 법안</h2>
            <span className="text-xs text-gray-400">
              전체 {bills.data.total}건
            </span>
          </div>
          <div className="mt-3 space-y-2">
            {bills.data.items.map((b) => (
              <Link
                key={b.bill_id}
                to={`/legislation/bills/${b.bill_id}`}
                className="block rounded-lg border p-3 transition-shadow hover:shadow-sm"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium">{b.bill_name}</p>
                    <div className="mt-1 flex gap-3 text-xs text-gray-500">
                      <span>{formatDate(b.propose_date)}</span>
                      {b.committee_name && <span>{b.committee_name}</span>}
                    </div>
                  </div>
                  {b.result && (
                    <span
                      className={`shrink-0 rounded px-2 py-0.5 text-xs font-medium ${
                        b.result === "원안가결" || b.result === "수정가결"
                          ? "bg-green-100 text-green-700"
                          : b.result === "부결"
                            ? "bg-red-100 text-red-700"
                            : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {b.result}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
