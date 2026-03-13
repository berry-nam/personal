import { lazy, Suspense, useMemo } from "react";
import { Link, useSearchParams } from "react-router";
import useDocumentTitle from "@/lib/useDocumentTitle";
import {
  useBillPipeline,
  useVoteParticipation,
  useBillTrend,
  useControversialVotes,
} from "@/api/queries";
import { formatNumber, formatDate } from "@/lib/format";
import MiniDonut from "@/components/charts/MiniDonut";
import MiniSparkline from "@/components/charts/MiniSparkline";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from "recharts";

const BillList = lazy(() => import("@/pages/BillList"));
const VoteList = lazy(() => import("@/pages/VoteList"));

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

const TABS = [
  { key: "overview", label: "한눈에 보기" },
  { key: "bills", label: "법안 검색" },
  { key: "votes", label: "표결 검색" },
] as const;

type Tab = (typeof TABS)[number]["key"];

function pct(n: number, total: number): number {
  if (!total) return 0;
  return Math.round((n / total) * 100);
}

export default function LegislationPage() {
  useDocumentTitle("입법활동");
  const [searchParams, setSearchParams] = useSearchParams();
  const tab = (searchParams.get("tab") as Tab) ?? "overview";

  const pipeline = useBillPipeline();
  const participation = useVoteParticipation(22);
  const billTrend = useBillTrend(22);
  const controversial = useControversialVotes(22, 8);

  function switchTab(t: Tab) {
    setSearchParams(t === "overview" ? {} : { tab: t });
  }

  const pipelineTotal = useMemo(
    () => pipeline.data?.reduce((s, d) => s + d.count, 0) ?? 0,
    [pipeline.data],
  );
  const passedCount = useMemo(
    () =>
      pipeline.data?.reduce(
        (s, d) =>
          d.result === "원안가결" || d.result === "수정가결"
            ? s + d.count
            : s,
        0,
      ) ?? 0,
    [pipeline.data],
  );
  const passRate =
    pipelineTotal > 0 ? ((passedCount / pipelineTotal) * 100).toFixed(1) : "0";

  const pipelineSegments = useMemo(() => {
    if (!pipeline.data) return [];
    return pipeline.data.map((d) => ({
      name: d.result,
      value: d.count,
      color: RESULT_COLORS[d.result] ?? "#6B7280",
    }));
  }, [pipeline.data]);

  const sparkData = useMemo(() => {
    if (!billTrend.data) return [];
    return billTrend.data.map((d) => ({
      label: d.week ? d.week.slice(5, 10) : "",
      value: d.count,
    }));
  }, [billTrend.data]);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold">입법활동</h1>
        <div className="flex rounded-lg border border-gray-200 bg-gray-50 p-0.5">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => switchTab(t.key)}
              className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
                tab === t.key
                  ? "bg-white text-gray-900 shadow-sm"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {tab === "overview" && (
        <div className="space-y-6">
          {/* Key metrics row */}
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            {/* Bills processed */}
            <div className="flex flex-col items-center rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-xs font-medium text-gray-500">총 발의 법안</p>
              <p className="mt-2 text-3xl font-bold">
                {formatNumber(pipelineTotal)}
              </p>
              <p className="text-[10px] text-gray-400">22대 국회</p>
            </div>

            {/* Pass rate donut */}
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
                <div className="flex h-[90px] items-center text-gray-300">
                  -
                </div>
              )}
            </div>

            {/* Vote participation */}
            <div className="flex flex-col items-center rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-xs font-medium text-gray-500">
                평균 표결 참여율
              </p>
              {participation.data ? (
                <>
                  <p className="mt-2 text-3xl font-bold text-blue-600">
                    {participation.data.avg_participation}%
                  </p>
                  <p className="text-[10px] text-gray-400">
                    {formatNumber(participation.data.total_votes)}건 표결
                  </p>
                </>
              ) : (
                <div className="flex h-[50px] items-center text-gray-300">
                  -
                </div>
              )}
            </div>

            {/* Bill trend sparkline */}
            <div className="flex flex-col rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-xs font-medium text-gray-500">
                주간 발의 추이
              </p>
              {sparkData.length > 0 ? (
                <div className="mt-2 flex-1">
                  <MiniSparkline data={sparkData} height={56} />
                </div>
              ) : (
                <div className="flex h-14 items-center text-gray-300">-</div>
              )}
            </div>
          </div>

          {/* Pipeline chart + Controversial votes side by side */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Pipeline */}
            {pipeline.data && pipeline.data.length > 0 && (
              <div className="rounded-lg border border-gray-200 bg-white p-5">
                <h2 className="mb-3 text-lg font-semibold">
                  법안 처리 현황
                </h2>
                <div className="h-64">
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
              </div>
            )}

            {/* Controversial votes */}
            {controversial.data && controversial.data.length > 0 && (
              <div className="rounded-lg border border-gray-200 bg-white p-5">
                <h2 className="mb-3 text-lg font-semibold">
                  논쟁 법안 TOP 8
                </h2>
                <p className="mb-3 text-xs text-gray-400">
                  반대율이 가장 높았던 표결
                </p>
                <div className="space-y-2">
                  {controversial.data.map((v) => {
                    const total = v.total_members;
                    return (
                      <Link
                        key={v.vote_id}
                        to={`/legislation/votes/${v.vote_id}`}
                        className="group block rounded-lg border border-gray-100 p-3 transition-all hover:border-gray-300 hover:shadow-sm"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-sm font-medium group-hover:text-blue-600 line-clamp-1">
                            {v.bill_name}
                          </p>
                          <span className="shrink-0 rounded bg-red-50 px-1.5 py-0.5 text-[10px] font-bold text-red-500">
                            반대 {v.opposition_rate}%
                          </span>
                        </div>
                        {/* Mini stacked bar */}
                        <div className="mt-2 flex h-2 overflow-hidden rounded-full bg-gray-100">
                          <div
                            className="bg-emerald-500"
                            style={{
                              width: `${pct(v.yes_count, total)}%`,
                            }}
                          />
                          <div
                            className="bg-red-500"
                            style={{
                              width: `${pct(v.no_count, total)}%`,
                            }}
                          />
                          <div
                            className="bg-yellow-400"
                            style={{
                              width: `${pct(v.abstain_count, total)}%`,
                            }}
                          />
                        </div>
                        <div className="mt-1 flex justify-between text-[10px] text-gray-400">
                          <span>
                            찬성 {v.yes_count} · 반대 {v.no_count} · 기권{" "}
                            {v.abstain_count}
                          </span>
                          <span>{formatDate(v.vote_date)}</span>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "bills" && (
        <Suspense
          fallback={
            <div className="flex h-32 items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />
            </div>
          }
        >
          <BillList />
        </Suspense>
      )}

      {tab === "votes" && (
        <Suspense
          fallback={
            <div className="flex h-32 items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />
            </div>
          }
        >
          <VoteList />
        </Suspense>
      )}
    </div>
  );
}
