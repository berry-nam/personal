import { useMemo } from "react";
import { Link, useNavigate } from "react-router";
import useDocumentTitle from "@/lib/useDocumentTitle";
import {
  useUnifiedGraph,
  useBillPipeline,
  useTopSponsors,
  useVotes,
  usePartySeats,
  useDemographics,
  useVoteParticipation,
  useBillTrend,
  useAssetRankings,
  useAssetAggregate,
  useControversialVotes,
  useAbsenteeRanking,
  usePlatformStats,
  useFundRankings,
  useAssetItemStocks,
  useAllCompanyHoldings,
} from "@/api/queries";
import HeroGraph from "@/components/graph/HeroGraph";
import PartyWaffleChart from "@/components/charts/PartyWaffleChart";
import MiniDonut from "@/components/charts/MiniDonut";
import MiniSparkline from "@/components/charts/MiniSparkline";
import StackedBar from "@/components/charts/StackedBar";
import { getPartyColor } from "@/lib/partyColors";
import { formatNumber, formatDate, formatKrw } from "@/lib/format";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from "recharts";

const RESULT_COLORS: Record<string, string> = {
  원안가결: "#10B981",
  수정가결: "#059669",
  부결: "#EF4444",
  폐기: "#9CA3AF",
  철회: "#D1D5DB",
  대안반영폐기: "#F59E0B",
  임기만료폐기: "#6B7280",
  계류중: "#3B82F6",
};

function pct(n: number | null, total: number | null): number {
  if (!n || !total || total === 0) return 0;
  return Math.round((n / total) * 100);
}

export default function Dashboard() {
  useDocumentTitle();
  const navigate = useNavigate();

  // Data queries
  const graphData = useUnifiedGraph({ assembly_term: 22, min_cosponsorship: 2, cosponsorship_limit: 500 });
  const partySeats = usePartySeats(22);
  const pipeline = useBillPipeline();
  const topSponsors = useTopSponsors({ assembly_term: 22, limit: 10 });
  const votesQuery = useVotes({ page: 1, size: 8 });
  const demographics = useDemographics(22);
  const voteParticipation = useVoteParticipation(22);
  const billTrend = useBillTrend(22);
  const platformStats = usePlatformStats();

  // Asset data
  const assetRankingsTotal = useAssetRankings(10);
  const assetRankingsRealEstate = useAssetRankings(5, "real_estate");
  const assetRankingsSecurities = useAssetRankings(5, "securities");
  const assetRankingsCrypto = useAssetRankings(5, "crypto");
  const assetAggregate = useAssetAggregate();

  // Vote data
  const controversialVotes = useControversialVotes(22, 5);
  const absentees = useAbsenteeRanking(22, 10);

  // Fund & company data for dashboard
  const fundRankings = useFundRankings(undefined, 5);
  const topStocks = useAssetItemStocks(5);
  const companyHoldings = useAllCompanyHoldings();

  // Derived data
  const pipelineSegments = useMemo(() => {
    if (!pipeline.data) return [];
    return pipeline.data.map((d) => ({
      name: d.result,
      value: d.count,
      color: RESULT_COLORS[d.result] ?? "#6B7280",
    }));
  }, [pipeline.data]);

  const pipelineTotal = pipelineSegments.reduce((s, d) => s + d.value, 0);
  const passedCount =
    pipeline.data?.reduce(
      (s, d) =>
        d.result === "원안가결" || d.result === "수정가결" ? s + d.count : s,
      0,
    ) ?? 0;
  const passRate =
    pipelineTotal > 0 ? ((passedCount / pipelineTotal) * 100).toFixed(1) : "0";
  const pendingCount =
    pipeline.data?.find((d) => d.result === "계류중")?.count ?? 0;
  const rejectedCount =
    pipeline.data?.find((d) => d.result === "부결")?.count ?? 0;

  const sparkData = useMemo(() => {
    if (!billTrend.data) return [];
    return billTrend.data.map((d) => ({
      label: d.week ? d.week.slice(5, 10) : "",
      value: d.count,
    }));
  }, [billTrend.data]);

  const maxBillCount = topSponsors.data?.[0]?.bill_count ?? 1;
  const maxAsset = assetRankingsTotal.data?.[0]?.total_assets ?? 1;

  // Asset summary for dashboard
  const assetSummary = useMemo(() => {
    if (!assetRankingsTotal.data || assetRankingsTotal.data.length === 0) return null;
    const d = assetRankingsTotal.data;
    const total = d.reduce((s, r) => s + r.total_assets, 0);
    const avg = Math.round(total / d.length);
    return { total, avg, top: d[0] };
  }, [assetRankingsTotal.data]);

  // Per-capita party data
  const partyPerCapita = useMemo(() => {
    if (!assetAggregate.data) return [];
    return assetAggregate.data
      .filter((a) => a.count > 0 && a.total_assets > 0)
      .map((a) => ({
        party: a.party,
        avg: Math.round(a.total_assets / a.count),
        count: a.count,
      }))
      .sort((a, b) => b.avg - a.avg);
  }, [assetAggregate.data]);

  return (
    <div>
      {/* ════════════════════════════════════════════════════
          HERO: Network Graph
         ════════════════════════════════════════════════════ */}
      <section className="relative overflow-hidden bg-gray-950">
        <div className="pointer-events-none absolute inset-x-0 top-0 z-10 bg-gradient-to-b from-gray-950/80 to-transparent px-6 pb-16 pt-5">
          <div className="pointer-events-auto mx-auto max-w-7xl">
            <h1 className="text-lg font-bold text-white sm:text-xl">
              22대 국회 통합 관계도
            </h1>
            <p className="mt-1 text-xs text-gray-400">
              의원 · 기업 · 표결 · 재산이 연결된 인물 중심 네트워크
            </p>
          </div>
        </div>

        <div className="pointer-events-none absolute bottom-4 right-4 z-10">
          <Link
            to="/graph"
            className="pointer-events-auto text-xs text-gray-400 transition-colors hover:text-white"
          >
            전체화면으로 보기 &rarr;
          </Link>
        </div>

        {graphData.data && (
          <div className="pointer-events-none absolute bottom-4 left-4 z-10">
            <div className="pointer-events-auto space-y-1">
              {/* Node type legend */}
              <div className="flex gap-2">
                {[
                  { label: "의원", color: "#9CA3AF" },
                  { label: "기업", color: "#F97316" },
                  { label: "표결", color: "#EF4444" },
                  { label: "재산", color: "#8B5CF6" },
                ].map((t) => (
                  <span
                    key={t.label}
                    className="flex items-center gap-1 rounded bg-gray-900/80 px-2 py-0.5 text-[9px] text-gray-300 backdrop-blur-sm"
                  >
                    <span
                      className="h-1.5 w-1.5 rounded-full"
                      style={{ backgroundColor: t.color }}
                    />
                    {t.label}
                  </span>
                ))}
              </div>
              {/* Party counts */}
              <div className="flex flex-wrap gap-1">
                {(() => {
                  const counts = new Map<string, number>();
                  for (const n of graphData.data.nodes) {
                    if (n.node_type !== "politician" && n.group !== "politician") continue;
                    const p = n.party ?? "무소속";
                    counts.set(p, (counts.get(p) ?? 0) + 1);
                  }
                  return [...counts.entries()]
                    .sort((a, b) => b[1] - a[1])
                    .slice(0, 6)
                    .map(([party, count]) => (
                      <span
                        key={party}
                        className="flex items-center gap-1 rounded bg-gray-900/80 px-1.5 py-0.5 text-[8px] text-gray-400 backdrop-blur-sm"
                      >
                        <span
                          className="h-1 w-1 rounded-full"
                          style={{ backgroundColor: getPartyColor(party) }}
                        />
                        {party} {count}
                      </span>
                    ));
                })()}
              </div>
            </div>
          </div>
        )}

        <div className="h-[250px] w-full sm:h-[420px]">
          {graphData.isLoading ? (
            <div className="flex h-full items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-700 border-t-gray-400" />
            </div>
          ) : graphData.data && graphData.data.nodes.length > 0 ? (
            <HeroGraph
              data={graphData.data}
              selectedNodeId={null}
              onNodeClick={(id) => {
                const node = graphData.data?.nodes.find((n) => n.id === id);
                if (node) {
                  navigate(
                    `/politicians?name=${encodeURIComponent(node.name)}`,
                  );
                }
              }}
            />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-gray-600">
              그래프 데이터를 불러올 수 없습니다
            </div>
          )}
        </div>
      </section>

      <div className="mx-auto max-w-7xl space-y-8 px-4 py-6">
        {/* ════════════════════════════════════════════════════
            SECTION 1: 국회 현황 (Parliament Overview)
           ════════════════════════════════════════════════════ */}
        <div>
          <h2 className="mb-4 text-xl font-bold">국회 현황</h2>
          {/* Platform stats + demographics summary */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
              <p className="text-xs font-medium text-gray-500">전체 의원</p>
              <p className="mt-1 text-3xl font-bold">
                {platformStats.data?.politicians ?? "–"}
              </p>
              <p className="text-[10px] text-gray-400">22대 국회</p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
              <p className="text-xs font-medium text-gray-500">총 발의 법안</p>
              <p className="mt-1 text-3xl font-bold">
                {formatNumber(pipelineTotal)}
              </p>
              <p className="text-[10px] text-gray-400">
                가결 {formatNumber(passedCount)}
              </p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
              <p className="text-xs font-medium text-gray-500">총 표결</p>
              <p className="mt-1 text-3xl font-bold">
                {voteParticipation.data
                  ? formatNumber(voteParticipation.data.total_votes)
                  : "–"}
              </p>
              <p className="text-[10px] text-gray-400">
                참여율{" "}
                {voteParticipation.data?.avg_participation ?? "–"}%
              </p>
            </div>
            {demographics.data && (
              <>
                <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
                  <p className="text-xs font-medium text-gray-500">성별 비율</p>
                  {(() => {
                    const male = demographics.data.gender.find(
                      (g) => g.gender === "남",
                    );
                    const female = demographics.data.gender.find(
                      (g) => g.gender === "여",
                    );
                    const total = (male?.count ?? 0) + (female?.count ?? 0);
                    return (
                      <>
                        <p className="mt-1 text-lg font-bold">
                          <span className="text-blue-500">남 {male?.count ?? 0}</span>
                          {" · "}
                          <span className="text-pink-500">여 {female?.count ?? 0}</span>
                        </p>
                        <p className="text-[10px] text-gray-400">
                          여성{" "}
                          {total > 0
                            ? (((female?.count ?? 0) / total) * 100).toFixed(1)
                            : 0}
                          %
                        </p>
                      </>
                    );
                  })()}
                </div>
                <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
                  <p className="text-xs font-medium text-gray-500">최다 연령대</p>
                  {(() => {
                    const top = [...demographics.data.age_brackets].sort(
                      (a, b) => b.count - a.count,
                    )[0];
                    return top ? (
                      <>
                        <p className="mt-1 text-3xl font-bold">{top.bracket}</p>
                        <p className="text-[10px] text-gray-400">{top.count}명</p>
                      </>
                    ) : (
                      <p className="mt-2 text-gray-300">–</p>
                    );
                  })()}
                </div>
                <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
                  <p className="text-xs font-medium text-gray-500">법안 가결률</p>
                  <p className="mt-1 text-3xl font-bold text-emerald-600">
                    {passRate}%
                  </p>
                  <p className="text-[10px] text-gray-400">
                    부결 {formatNumber(rejectedCount)}
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Waffle + Demographics detail */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
          {partySeats.data && partySeats.data.length > 0 && (
            <div className="lg:col-span-3">
              <div className="rounded-lg border border-gray-200 bg-white p-5">
                <h3 className="mb-3 text-base font-semibold">의석 분포</h3>
                <PartyWaffleChart data={partySeats.data} />
              </div>
            </div>
          )}
          {demographics.data && (
            <div className="lg:col-span-2">
              <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-5">
                <div>
                  <p className="mb-2 text-sm font-medium text-gray-600">
                    성별 비율
                  </p>
                  <StackedBar
                    segments={demographics.data.gender.map((g) => ({
                      label: g.gender,
                      value: g.count,
                      color: g.gender === "남" ? "#3B82F6" : "#EC4899",
                    }))}
                    height={24}
                  />
                </div>
                <div>
                  <p className="mb-2 text-sm font-medium text-gray-600">
                    연령대 분포
                  </p>
                  <div className="space-y-1">
                    {demographics.data.age_brackets.map((ab) => {
                      const max = Math.max(
                        ...demographics.data!.age_brackets.map((x) => x.count),
                      );
                      return (
                        <div
                          key={ab.bracket}
                          className="flex items-center gap-2"
                        >
                          <span className="w-10 text-right text-xs text-gray-500">
                            {ab.bracket}
                          </span>
                          <div className="flex-1">
                            <div
                              className="h-3.5 rounded bg-indigo-400"
                              style={{
                                width: `${max > 0 ? (ab.count / max) * 100 : 0}%`,
                              }}
                            />
                          </div>
                          <span className="w-8 text-xs text-gray-500">
                            {ab.count}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ════════════════════════════════════════════════════
            SECTION 2: 입법활동 (Legislation)
           ════════════════════════════════════════════════════ */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-bold">입법활동</h2>
            <Link
              to="/legislation"
              className="text-sm text-gray-400 hover:text-gray-600"
            >
              상세 보기 &rarr;
            </Link>
          </div>

          {/* Legislation metric cards */}
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div className="flex flex-col items-center rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-xs font-medium text-gray-500">법안 가결률</p>
              {pipelineSegments.length > 0 ? (
                <MiniDonut
                  segments={pipelineSegments}
                  centerLabel={`${passRate}%`}
                  centerSub="가결"
                  size={90}
                />
              ) : (
                <div className="flex h-[90px] items-center text-gray-300">-</div>
              )}
            </div>

            <div className="flex flex-col items-center rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-xs font-medium text-gray-500">표결 참여율</p>
              {voteParticipation.data ? (
                <MiniDonut
                  segments={[
                    {
                      name: "참여",
                      value: voteParticipation.data.avg_participation,
                      color: "#3B82F6",
                    },
                    {
                      name: "불참",
                      value: 100 - voteParticipation.data.avg_participation,
                      color: "#E5E7EB",
                    },
                  ]}
                  centerLabel={`${voteParticipation.data.avg_participation}%`}
                  centerSub={`${formatNumber(voteParticipation.data.total_votes)}건`}
                  size={90}
                />
              ) : (
                <div className="flex h-[90px] items-center text-gray-300">-</div>
              )}
            </div>

            <div className="flex flex-col rounded-lg border border-gray-200 bg-white p-4">
              <p className="mb-2 text-xs font-medium text-gray-500">
                주간 발의 추이
              </p>
              {sparkData.length > 0 ? (
                <MiniSparkline data={sparkData} height={56} />
              ) : (
                <div className="flex h-14 items-center text-gray-300">-</div>
              )}
            </div>

            <div className="flex flex-col rounded-lg border border-gray-200 bg-white p-4">
              <p className="mb-1 text-xs font-medium text-gray-500">계류 법안</p>
              <p className="text-3xl font-bold text-amber-500">
                {formatNumber(pendingCount)}
              </p>
              <p className="mt-auto text-[10px] text-gray-400">
                전체의{" "}
                {pipelineTotal > 0
                  ? ((pendingCount / pipelineTotal) * 100).toFixed(1)
                  : 0}
                %
              </p>
            </div>
          </div>
        </div>

        {/* Top Sponsors + Pipeline side by side */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Top Sponsors */}
          {topSponsors.data && topSponsors.data.length > 0 && (
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold">대표발의 TOP 10</h3>
                <Link
                  to="/politicians"
                  className="text-xs text-gray-400 hover:text-gray-600"
                >
                  전체 &rarr;
                </Link>
              </div>
              <div className="mt-3 space-y-1">
                {topSponsors.data.map((pol, i) => (
                  <Link
                    key={pol.id}
                    to={`/politicians/${pol.id}`}
                    className="group flex items-center gap-2.5 rounded-lg px-2 py-1.5 transition-colors hover:bg-gray-50"
                  >
                    <span className="w-5 text-right text-xs font-bold text-gray-300">
                      {i + 1}
                    </span>
                    {pol.photo_url ? (
                      <img
                        src={pol.photo_url}
                        alt={pol.name}
                        className="h-7 w-7 shrink-0 rounded-full object-cover"
                      />
                    ) : (
                      <div
                        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white"
                        style={{ backgroundColor: getPartyColor(pol.party) }}
                      >
                        {pol.name.charAt(0)}
                      </div>
                    )}
                    <span className="w-14 text-sm font-medium group-hover:text-blue-600">
                      {pol.name}
                    </span>
                    <div className="flex-1">
                      <div className="h-3 overflow-hidden rounded-full bg-gray-100">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${(pol.bill_count / maxBillCount) * 100}%`,
                            backgroundColor: getPartyColor(pol.party),
                          }}
                        />
                      </div>
                    </div>
                    <span className="w-12 text-right text-xs font-semibold tabular-nums text-gray-600">
                      {formatNumber(pol.bill_count)}건
                    </span>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* Bill Pipeline */}
          {pipeline.data && pipeline.data.length > 0 && (
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h3 className="mb-3 text-base font-semibold">법안 처리 현황</h3>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={pipeline.data}
                    layout="vertical"
                    margin={{ left: 80, right: 40 }}
                  >
                    <XAxis
                      type="number"
                      tickFormatter={(v: number) => formatNumber(v)}
                      tick={{ fontSize: 11 }}
                    />
                    <YAxis
                      type="category"
                      dataKey="result"
                      width={80}
                      tick={{ fontSize: 11 }}
                    />
                    <Tooltip formatter={(v) => formatNumber(Number(v))} />
                    <Bar
                      dataKey="count"
                      radius={[0, 4, 4, 0]}
                      label={{
                        position: "right",
                        fontSize: 10,
                        fill: "#6B7280",
                        formatter: (v: number) =>
                          pipelineTotal > 0
                            ? `${((v / pipelineTotal) * 100).toFixed(1)}%`
                            : "0%",
                      }}
                    >
                      {pipeline.data.map((d) => (
                        <Cell
                          key={d.result}
                          fill={RESULT_COLORS[d.result] ?? "#6B7280"}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          )}
        </div>

        {/* Controversial Votes + Absentee Ranking */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {controversialVotes.data && controversialVotes.data.length > 0 && (
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold">논쟁 법안 TOP 5</h3>
                <Link
                  to="/legislation"
                  className="text-xs text-gray-400 hover:text-gray-600"
                >
                  더보기 &rarr;
                </Link>
              </div>
              <p className="mt-0.5 text-xs text-gray-400">
                반대율이 가장 높았던 표결
              </p>
              <div className="mt-3 space-y-2">
                {controversialVotes.data.map((v) => {
                  const total = v.total_members;
                  return (
                    <Link
                      key={v.vote_id}
                      to={`/legislation/votes/${v.vote_id}`}
                      className="group block rounded-lg border border-gray-100 p-3 transition-all hover:border-gray-300"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-medium group-hover:text-blue-600 line-clamp-1">
                          {v.bill_name}
                        </p>
                        <span className="shrink-0 rounded bg-red-50 px-1.5 py-0.5 text-[10px] font-bold text-red-500">
                          반대 {v.opposition_rate}%
                        </span>
                      </div>
                      <div className="mt-1.5 flex h-2 overflow-hidden rounded-full bg-gray-100">
                        <div
                          className="bg-emerald-500"
                          style={{ width: `${pct(v.yes_count, total)}%` }}
                        />
                        <div
                          className="bg-red-500"
                          style={{ width: `${pct(v.no_count, total)}%` }}
                        />
                        <div
                          className="bg-yellow-400"
                          style={{ width: `${pct(v.abstain_count, total)}%` }}
                        />
                      </div>
                      <p className="mt-1 text-[10px] text-gray-400">
                        {formatDate(v.vote_date)} · 찬성 {v.yes_count} 반대{" "}
                        {v.no_count}
                      </p>
                    </Link>
                  );
                })}
              </div>
            </section>
          )}

          {absentees.data && absentees.data.length > 0 && (
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h3 className="text-base font-semibold">표결 불참률 TOP 10</h3>
              <p className="mt-0.5 text-xs text-gray-400">
                국민의 대리인이 자리를 비운 횟수
              </p>
              <div className="mt-3 space-y-1.5">
                {absentees.data.map((a, i) => (
                  <Link
                    key={a.politician_id}
                    to={`/politicians/${a.politician_id}`}
                    className="group flex items-center gap-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-gray-50"
                  >
                    <span className="w-5 text-right text-xs font-bold text-gray-300">
                      {i + 1}
                    </span>
                    {a.photo_url ? (
                      <img
                        src={a.photo_url}
                        alt={a.name}
                        className="h-6 w-6 shrink-0 rounded-full object-cover"
                      />
                    ) : (
                      <div
                        className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white"
                        style={{ backgroundColor: getPartyColor(a.party) }}
                      >
                        {a.name.charAt(0)}
                      </div>
                    )}
                    <span className="w-14 text-sm font-medium group-hover:text-blue-600">
                      {a.name}
                    </span>
                    <span className="text-[10px] text-gray-400">
                      {a.party}
                    </span>
                    <div className="flex-1">
                      <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                        <div
                          className="h-full rounded-full bg-red-400"
                          style={{ width: `${a.absence_rate}%` }}
                        />
                      </div>
                    </div>
                    <span className="w-12 text-right text-sm font-bold text-red-500">
                      {a.absence_rate}%
                    </span>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Recent Votes */}
        <section>
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold">최근 표결</h3>
            <Link
              to="/legislation?tab=votes"
              className="text-xs text-gray-400 hover:text-gray-600"
            >
              전체 보기 &rarr;
            </Link>
          </div>
          <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
            {votesQuery.data?.items.map((vote) => {
              const total = vote.total_members ?? 0;
              const yes = vote.yes_count ?? 0;
              const no = vote.no_count ?? 0;
              const abstain = vote.abstain_count ?? 0;
              const passed =
                vote.result === "원안가결" || vote.result === "수정가결";
              const controversial = total > 0 && no / total > 0.3;

              return (
                <Link
                  key={vote.vote_id}
                  to={`/legislation/votes/${vote.vote_id}`}
                  className="group flex items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-2.5 transition-all hover:border-gray-300 hover:shadow-md"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-gray-900 group-hover:text-blue-600">
                      {controversial && <span className="mr-1">🔥</span>}
                      {vote.bill_name ?? vote.bill_id}
                    </p>
                    <p className="mt-0.5 text-[11px] text-gray-400">
                      {formatDate(vote.vote_date)}
                    </p>
                  </div>
                  <div className="hidden w-24 sm:block">
                    <div className="flex h-2 overflow-hidden rounded-full bg-gray-100">
                      {yes > 0 && (
                        <div
                          className="bg-emerald-500"
                          style={{ width: `${pct(yes, total)}%` }}
                        />
                      )}
                      {no > 0 && (
                        <div
                          className="bg-red-500"
                          style={{ width: `${pct(no, total)}%` }}
                        />
                      )}
                      {abstain > 0 && (
                        <div
                          className="bg-yellow-400"
                          style={{ width: `${pct(abstain, total)}%` }}
                        />
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-bold text-emerald-600">
                      {pct(yes, total)}%
                    </span>
                    {vote.result && (
                      <span
                        className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold ${
                          passed
                            ? "bg-emerald-50 text-emerald-600"
                            : "bg-red-50 text-red-500"
                        }`}
                      >
                        {vote.result}
                      </span>
                    )}
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* ════════════════════════════════════════════════════
            SECTION 3: 재산·자금 (Assets & Finance)
           ════════════════════════════════════════════════════ */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-xl font-bold">재산·자금</h2>
            <Link
              to="/assets"
              className="text-sm text-gray-400 hover:text-gray-600"
            >
              상세 보기 &rarr;
            </Link>
          </div>

          {/* Asset summary cards */}
          {assetSummary && (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
                <p className="text-xs font-medium text-gray-500">재산 1위</p>
                <p className="mt-1 text-lg font-bold">{assetSummary.top.name}</p>
                <p className="text-sm font-semibold text-blue-600">
                  {formatKrw(assetSummary.top.total_assets)}
                </p>
                <p className="text-[10px] text-gray-400">{assetSummary.top.party}</p>
              </div>
              <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
                <p className="text-xs font-medium text-gray-500">의원 평균 재산</p>
                <p className="mt-2 text-2xl font-bold">{formatKrw(assetSummary.avg)}</p>
              </div>
              <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
                <p className="text-xs font-medium text-gray-500">부동산 1위</p>
                {assetRankingsRealEstate.data?.[0] && (
                  <>
                    <p className="mt-1 text-lg font-bold">
                      {assetRankingsRealEstate.data[0].name}
                    </p>
                    <p className="text-sm font-semibold text-blue-500">
                      {formatKrw(assetRankingsRealEstate.data[0].total_real_estate ?? 0)}
                    </p>
                  </>
                )}
              </div>
              <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
                <p className="text-xs font-medium text-gray-500">유가증권 1위</p>
                {assetRankingsSecurities.data?.[0] && (
                  <>
                    <p className="mt-1 text-lg font-bold">
                      {assetRankingsSecurities.data[0].name}
                    </p>
                    <p className="text-sm font-semibold text-amber-500">
                      {formatKrw(
                        assetRankingsSecurities.data[0].total_securities ?? 0,
                      )}
                    </p>
                  </>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Asset rankings + Party per-capita side by side */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Total asset ranking */}
          {assetRankingsTotal.data && assetRankingsTotal.data.length > 0 && (
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h3 className="text-base font-semibold">재산 상위 10인</h3>
              <p className="text-xs text-gray-400">최신 재산공개 기준</p>
              <div className="mt-3 space-y-1">
                {assetRankingsTotal.data.map((r, i) => (
                  <Link
                    key={r.politician_id}
                    to={`/politicians/${r.politician_id}`}
                    className="group flex items-center gap-2.5 rounded-lg px-2 py-1.5 transition-colors hover:bg-gray-50"
                  >
                    <span className="w-5 text-right text-xs font-bold text-gray-300">
                      {i + 1}
                    </span>
                    {r.photo_url ? (
                      <img
                        src={r.photo_url}
                        alt={r.name}
                        className="h-7 w-7 shrink-0 rounded-full object-cover"
                      />
                    ) : (
                      <div
                        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[10px] font-bold text-white"
                        style={{ backgroundColor: getPartyColor(r.party) }}
                      >
                        {r.name.charAt(0)}
                      </div>
                    )}
                    <div className="w-16 shrink-0">
                      <p className="text-sm font-medium group-hover:text-blue-600">
                        {r.name}
                      </p>
                      <p className="text-[10px] text-gray-400">{r.party}</p>
                    </div>
                    <div className="flex-1">
                      <div className="h-4 overflow-hidden rounded bg-gray-100">
                        <div
                          className="h-full rounded"
                          style={{
                            width: `${(r.total_assets / maxAsset) * 100}%`,
                            backgroundColor: getPartyColor(r.party),
                            opacity: 0.7,
                          }}
                        />
                      </div>
                    </div>
                    <span className="w-20 text-right text-sm font-semibold tabular-nums">
                      {formatKrw(r.total_assets)}
                    </span>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* Party per-capita */}
          {partyPerCapita.length > 0 && (
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h3 className="text-base font-semibold">
                정당별 1인당 평균 재산
              </h3>
              <p className="text-xs text-gray-400">
                어떤 정당의 의원이 가장 부유한가?
              </p>
              <div className="mt-4 space-y-2">
                {(() => {
                  const maxAvg = partyPerCapita[0]?.avg || 1;
                  return partyPerCapita.map((a) => (
                    <div key={a.party} className="flex items-center gap-3">
                      <span className="w-20 text-right text-xs font-medium text-gray-600">
                        {a.party}
                      </span>
                      <div className="flex-1">
                        <div className="h-6 overflow-hidden rounded bg-gray-100">
                          <div
                            className="flex h-full items-center rounded pl-2 text-[10px] font-bold text-white"
                            style={{
                              width: `${(a.avg / maxAvg) * 100}%`,
                              backgroundColor: getPartyColor(a.party),
                              minWidth: "30px",
                            }}
                          >
                            {formatKrw(a.avg)}
                          </div>
                        </div>
                      </div>
                      <span className="w-10 text-right text-[10px] text-gray-400">
                        {a.count}명
                      </span>
                    </div>
                  ));
                })()}
              </div>
            </section>
          )}
        </div>

        {/* Category-specific mini rankings (부동산, 유가증권, 가상자산) */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
          {assetRankingsRealEstate.data &&
            assetRankingsRealEstate.data.length > 0 && (
              <section className="rounded-lg border border-gray-200 bg-white p-5">
                <h3 className="text-base font-semibold">
                  <span
                    className="mr-1.5 inline-block h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: "#3B82F6" }}
                  />
                  부동산 TOP 5
                </h3>
                <div className="mt-3 space-y-1.5">
                  {assetRankingsRealEstate.data.slice(0, 5).map((r, i) => (
                    <Link
                      key={r.politician_id}
                      to={`/politicians/${r.politician_id}`}
                      className="group flex items-center gap-2 rounded px-1 py-1 hover:bg-gray-50"
                    >
                      <span className="w-4 text-right text-xs font-bold text-gray-300">
                        {i + 1}
                      </span>
                      <span className="text-sm font-medium group-hover:text-blue-600">
                        {r.name}
                      </span>
                      <span className="ml-auto text-xs font-semibold text-blue-500">
                        {formatKrw(r.total_real_estate ?? 0)}
                      </span>
                    </Link>
                  ))}
                </div>
              </section>
            )}

          {assetRankingsSecurities.data &&
            assetRankingsSecurities.data.length > 0 && (
              <section className="rounded-lg border border-gray-200 bg-white p-5">
                <h3 className="text-base font-semibold">
                  <span
                    className="mr-1.5 inline-block h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: "#F59E0B" }}
                  />
                  유가증권 TOP 5
                </h3>
                <div className="mt-3 space-y-1.5">
                  {assetRankingsSecurities.data.slice(0, 5).map((r, i) => (
                    <Link
                      key={r.politician_id}
                      to={`/politicians/${r.politician_id}`}
                      className="group flex items-center gap-2 rounded px-1 py-1 hover:bg-gray-50"
                    >
                      <span className="w-4 text-right text-xs font-bold text-gray-300">
                        {i + 1}
                      </span>
                      <span className="text-sm font-medium group-hover:text-blue-600">
                        {r.name}
                      </span>
                      <span className="ml-auto text-xs font-semibold text-amber-500">
                        {formatKrw(r.total_securities ?? 0)}
                      </span>
                    </Link>
                  ))}
                </div>
              </section>
            )}

          {assetRankingsCrypto.data &&
            assetRankingsCrypto.data.length > 0 && (
              <section className="rounded-lg border border-gray-200 bg-white p-5">
                <h3 className="text-base font-semibold">
                  <span
                    className="mr-1.5 inline-block h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: "#8B5CF6" }}
                  />
                  가상자산 TOP 5
                </h3>
                <div className="mt-3 space-y-1.5">
                  {assetRankingsCrypto.data.slice(0, 5).map((r, i) => (
                    <Link
                      key={r.politician_id}
                      to={`/politicians/${r.politician_id}`}
                      className="group flex items-center gap-2 rounded px-1 py-1 hover:bg-gray-50"
                    >
                      <span className="w-4 text-right text-xs font-bold text-gray-300">
                        {i + 1}
                      </span>
                      <span className="text-sm font-medium group-hover:text-blue-600">
                        {r.name}
                      </span>
                      <span className="ml-auto text-xs font-semibold text-purple-500">
                        {formatKrw(r.total_crypto ?? 0)}
                      </span>
                    </Link>
                  ))}
                </div>
              </section>
            )}
        </div>

        {/* Fund rankings + Stock holdings + Company relationships */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Political fund TOP 5 */}
          {fundRankings.data && fundRankings.data.length > 0 && (
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h3 className="text-base font-semibold">정치자금 수입 TOP 5</h3>
              <p className="text-xs text-gray-400">후원회 기준</p>
              <div className="mt-3 space-y-1.5">
                {fundRankings.data.map((f, i) => (
                  <Link
                    key={f.politician_id}
                    to={`/politicians/${f.politician_id}`}
                    className="group flex items-center gap-2 rounded px-1 py-1 hover:bg-gray-50"
                  >
                    <span className="w-4 text-right text-xs font-bold text-gray-300">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <span className="text-sm font-medium group-hover:text-blue-600">
                        {f.name}
                      </span>
                      <span className="ml-1 text-[10px] text-gray-400">{f.party}</span>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-semibold text-green-600">{formatKrw(f.income_total ?? 0)}</p>
                      <p className="text-[10px] text-gray-400">지출 {formatKrw(f.expense_total ?? 0)}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* Stock holdings TOP 5 */}
          {topStocks.data && topStocks.data.length > 0 && (
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h3 className="text-base font-semibold">주식 보유 TOP 5</h3>
              <p className="text-xs text-gray-400">종목별 최대 보유액</p>
              <div className="mt-3 space-y-1.5">
                {topStocks.data.map((s, i) => (
                  <Link
                    key={`${s.politician_id}-${s.description}-${i}`}
                    to={`/politicians/${s.politician_id}`}
                    className="group flex items-center gap-2 rounded px-1 py-1 hover:bg-gray-50"
                  >
                    <span className="w-4 text-right text-xs font-bold text-gray-300">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium group-hover:text-blue-600 truncate">
                        {s.description}
                      </p>
                      <p className="text-[10px] text-gray-400">{s.name} · {s.relation}</p>
                    </div>
                    <span className="text-xs font-semibold text-amber-600">
                      {formatKrw(s.value_krw ?? 0)}
                    </span>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* Company holdings summary */}
          {companyHoldings.data && companyHoldings.data.length > 0 && (
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h3 className="text-base font-semibold">의원-기업 관계</h3>
              <p className="text-xs text-gray-400">주식 보유·임원 겸직 등</p>
              <div className="mt-3 space-y-1.5">
                {companyHoldings.data.slice(0, 5).map((c, i) => (
                  <Link
                    key={`${c.politician_id}-${c.corp_name}-${i}`}
                    to={`/politicians/${c.politician_id}`}
                    className="group flex items-center gap-2 rounded px-1 py-1 hover:bg-gray-50"
                  >
                    <span className="w-4 text-right text-xs font-bold text-gray-300">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium group-hover:text-blue-600 truncate">
                        {c.corp_name}
                        {c.stock_code && (
                          <span className="ml-1 font-mono text-[10px] text-gray-400">
                            ({c.stock_code})
                          </span>
                        )}
                      </p>
                      <p className="text-[10px] text-gray-400">
                        {c.name} · {c.relation_type}
                      </p>
                    </div>
                    <span className="text-xs font-semibold text-orange-600">
                      {c.value_krw ? formatKrw(c.value_krw) : "-"}
                    </span>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
