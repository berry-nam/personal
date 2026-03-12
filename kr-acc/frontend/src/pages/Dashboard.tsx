import { useMemo } from "react";
import { Link, useNavigate } from "react-router";
import useDocumentTitle from "@/lib/useDocumentTitle";
import {
  useCoSponsorshipGraph,
  useBillPipeline,
  useTopSponsors,
  useVotes,
  usePartySeats,
  useDemographics,
  useVoteParticipation,
  useBillTrend,
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
  const graphData = useCoSponsorshipGraph({ min_weight: 5, limit: 300 });
  const partySeats = usePartySeats(22);
  const pipeline = useBillPipeline();
  const topSponsors = useTopSponsors({ assembly_term: 22, limit: 10 });
  const votesQuery = useVotes({ page: 1, size: 8 });
  const demographics = useDemographics(22);
  const voteParticipation = useVoteParticipation(22);
  const billTrend = useBillTrend(22);

  // Compute pipeline donut segments
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

  // Proposer type breakdown from pipeline? We'll approximate with passed/pending
  const proposerSegments = useMemo(() => {
    if (!pipeline.data) return [];
    const passed = pipeline.data
      .filter((d) => d.result === "원안가결" || d.result === "수정가결")
      .reduce((s, d) => s + d.count, 0);
    const pending = pipeline.data
      .filter((d) => d.result === "계류중")
      .reduce((s, d) => s + d.count, 0);
    const other = pipelineTotal - passed - pending;
    return [
      { label: "가결", value: passed, color: "#10B981" },
      { label: "계류", value: pending, color: "#3B82F6" },
      { label: "기타", value: other, color: "#9CA3AF" },
    ];
  }, [pipeline.data, pipelineTotal]);

  // Bill trend sparkline data
  const sparkData = useMemo(() => {
    if (!billTrend.data) return [];
    return billTrend.data.map((d) => ({
      label: d.week ? d.week.slice(5, 10) : "",
      value: d.count,
    }));
  }, [billTrend.data]);

  // Top sponsor max for proportional bars
  const maxBillCount = topSponsors.data?.[0]?.bill_count ?? 1;

  return (
    <div>
      {/* ── A. Hero: Co-sponsorship Network ─────────────────────── */}
      <section className="relative overflow-hidden bg-gray-950">
        <div className="pointer-events-none absolute inset-x-0 top-0 z-10 bg-gradient-to-b from-gray-950/80 to-transparent px-6 pb-16 pt-5">
          <div className="pointer-events-auto mx-auto max-w-7xl">
            <h1 className="text-lg font-bold text-white sm:text-xl">
              22대 국회 306인의 입법 관계도
            </h1>
            <p className="mt-1 text-xs text-gray-400">
              공동발의 기반 네트워크 · 노드 클릭으로 의원 프로필 이동
            </p>
          </div>
        </div>

        {/* "네트워크 전체보기" link */}
        <div className="pointer-events-none absolute bottom-4 right-4 z-10">
          <Link
            to="/graph"
            className="pointer-events-auto text-xs text-gray-400 transition-colors hover:text-white"
          >
            네트워크 전체보기 &rarr;
          </Link>
        </div>

        <div className="h-[250px] w-full sm:h-[400px]">
          {graphData.isLoading ? (
            <div className="flex h-full items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-700 border-t-gray-400" />
            </div>
          ) : graphData.data && graphData.data.nodes.length > 0 ? (
            <HeroGraph
              data={graphData.data}
              selectedNodeId={null}
              onNodeClick={(id) => {
                // Find politician and navigate
                const node = graphData.data?.nodes.find((n) => n.id === id);
                if (node) {
                  // Navigate via search — we'll use assembly_id
                  navigate(`/politicians?name=${encodeURIComponent(node.name)}`);
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

      <div className="mx-auto max-w-7xl px-4 py-6 space-y-8">
        {/* ── B. Party Seat Waffle Chart ────────────────────────── */}
        {partySeats.data && partySeats.data.length > 0 && (
          <section>
            <h2 className="text-lg font-semibold">22대 국회 의석 분포</h2>
            <div className="mt-3 rounded-lg border border-gray-200 bg-white p-5">
              <PartyWaffleChart data={partySeats.data} />
            </div>
          </section>
        )}

        {/* ── C. Key Metrics Row ───────────────────────────────── */}
        <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {/* 법안 처리율 */}
          <div className="flex flex-col items-center rounded-lg border border-gray-200 bg-white p-4">
            <p className="text-xs font-medium text-gray-500">법안 처리율</p>
            {pipelineSegments.length > 0 ? (
              <MiniDonut
                segments={pipelineSegments}
                centerLabel={`${passRate}%`}
                centerSub="가결"
                size={100}
              />
            ) : (
              <div className="flex h-[100px] items-center justify-center text-sm text-gray-300">
                —
              </div>
            )}
          </div>

          {/* 평균 표결 참여율 */}
          <div className="flex flex-col items-center rounded-lg border border-gray-200 bg-white p-4">
            <p className="text-xs font-medium text-gray-500">평균 표결 참여율</p>
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
                size={100}
              />
            ) : (
              <div className="flex h-[100px] items-center justify-center text-sm text-gray-300">
                —
              </div>
            )}
          </div>

          {/* 법안 현황 */}
          <div className="flex flex-col justify-center rounded-lg border border-gray-200 bg-white p-4">
            <p className="mb-2 text-xs font-medium text-gray-500">법안 현황</p>
            <StackedBar segments={proposerSegments} height={20} />
          </div>

          {/* 최근 발의 추이 */}
          <div className="flex flex-col rounded-lg border border-gray-200 bg-white p-4">
            <p className="mb-2 text-xs font-medium text-gray-500">
              최근 발의 추이 (12주)
            </p>
            {sparkData.length > 0 ? (
              <MiniSparkline data={sparkData} height={56} />
            ) : (
              <div className="flex h-14 items-center justify-center text-sm text-gray-300">
                —
              </div>
            )}
          </div>
        </section>

        {/* ── D. Top Sponsors ──────────────────────────────────── */}
        {topSponsors.data && topSponsors.data.length > 0 && (
          <section>
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">22대 대표발의 TOP 10</h2>
              <Link
                to="/politicians"
                className="text-sm text-gray-400 hover:text-gray-600"
              >
                전체 보기 &rarr;
              </Link>
            </div>
            <div className="mt-3 flex gap-3 overflow-x-auto pb-2">
              {topSponsors.data.map((pol, i) => (
                <Link
                  key={pol.id}
                  to={`/politicians/${pol.id}`}
                  className="flex shrink-0 items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-3 transition-all hover:border-gray-300 hover:shadow-md"
                >
                  <span className="text-lg font-bold text-gray-300">
                    {i + 1}
                  </span>
                  {pol.photo_url ? (
                    <img
                      src={pol.photo_url}
                      alt={pol.name}
                      className="h-8 w-8 shrink-0 rounded-full object-cover"
                    />
                  ) : (
                    <div
                      className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
                      style={{ backgroundColor: getPartyColor(pol.party) }}
                    >
                      {pol.name.charAt(0)}
                    </div>
                  )}
                  <div className="min-w-0">
                    <p className="text-sm font-medium">{pol.name}</p>
                    <p className="text-[11px] text-gray-400">
                      {pol.party} · {formatNumber(pol.bill_count)}건
                    </p>
                    {/* Proportional bar */}
                    <div className="mt-1 h-1 w-24 overflow-hidden rounded-full bg-gray-100">
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${(pol.bill_count / maxBillCount) * 100}%`,
                          backgroundColor: getPartyColor(pol.party),
                        }}
                      />
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* ── E. Recent Votes + Bill Pipeline ──────────────────── */}
        <section className="grid grid-cols-1 gap-6 lg:grid-cols-5">
          {/* Recent votes — left 3 cols */}
          <div className="lg:col-span-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">최근 표결</h2>
              <Link
                to="/legislation?tab=votes"
                className="text-sm text-gray-400 hover:text-gray-600"
              >
                전체 보기 &rarr;
              </Link>
            </div>
            <div className="mt-3 space-y-2">
              {votesQuery.data?.items.map((vote) => {
                const total = vote.total_members ?? 0;
                const yes = vote.yes_count ?? 0;
                const no = vote.no_count ?? 0;
                const abstain = vote.abstain_count ?? 0;
                const absent = vote.absent_count ?? 0;
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
                        {controversial && (
                          <span className="mr-1" title="반대 30% 이상">
                            🔥
                          </span>
                        )}
                        {vote.bill_name ?? vote.bill_id}
                      </p>
                      <p className="mt-0.5 text-[11px] text-gray-400">
                        {formatDate(vote.vote_date)}
                      </p>
                    </div>
                    {/* 4-segment CSS stacked bar */}
                    <div className="hidden w-32 sm:block">
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
                        {absent > 0 && (
                          <div
                            className="bg-gray-300"
                            style={{ width: `${pct(absent, total)}%` }}
                          />
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-base font-bold text-emerald-600">
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
          </div>

          {/* Bill pipeline — right 2 cols */}
          <div className="lg:col-span-2">
            <h2 className="text-lg font-semibold">법안 처리 현황</h2>
            {pipeline.data && pipeline.data.length > 0 ? (
              <div className="mt-3 rounded-lg border border-gray-200 bg-white p-4">
                <div className="h-80">
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
                      <Tooltip
                        formatter={(v) => formatNumber(Number(v))}
                      />
                      <Bar
                        dataKey="count"
                        radius={[0, 4, 4, 0]}
                        label={{
                          position: "right",
                          fontSize: 10,
                          fill: "#6B7280",
                          formatter: (v: number) => {
                            const p =
                              pipelineTotal > 0
                                ? ((v / pipelineTotal) * 100).toFixed(1)
                                : "0";
                            return `${p}%`;
                          },
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
              </div>
            ) : (
              <div className="mt-3 flex h-80 items-center justify-center rounded-lg border border-gray-200 bg-white text-sm text-gray-400">
                불러오는 중...
              </div>
            )}
          </div>
        </section>

        {/* ── F. Gender & Age Demographics ─────────────────────── */}
        {demographics.data && (
          <section className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="mb-4 text-lg font-semibold">22대 국회 인구통계</h2>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {/* Gender ratio */}
              <div>
                <p className="mb-2 text-sm font-medium text-gray-600">
                  성별 비율
                </p>
                {demographics.data.gender.length > 0 && (
                  <StackedBar
                    segments={demographics.data.gender.map((g) => ({
                      label: g.gender,
                      value: g.count,
                      color: g.gender === "남" ? "#3B82F6" : "#EC4899",
                    }))}
                    height={28}
                  />
                )}
              </div>

              {/* Age distribution — horizontal bars */}
              <div>
                <p className="mb-2 text-sm font-medium text-gray-600">
                  연령대 분포
                </p>
                <div className="space-y-1.5">
                  {demographics.data.age_brackets.map((ab) => {
                    const maxCount = Math.max(
                      ...demographics.data!.age_brackets.map((x) => x.count),
                    );
                    const width =
                      maxCount > 0
                        ? ((ab.count / maxCount) * 100).toFixed(0)
                        : "0";
                    return (
                      <div key={ab.bracket} className="flex items-center gap-2">
                        <span className="w-10 text-right text-xs text-gray-500">
                          {ab.bracket}
                        </span>
                        <div className="flex-1">
                          <div
                            className="h-4 rounded bg-indigo-400 transition-all"
                            style={{ width: `${width}%` }}
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
          </section>
        )}
      </div>
    </div>
  );
}
