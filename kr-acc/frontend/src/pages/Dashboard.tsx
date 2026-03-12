import { useState, useMemo } from "react";
import { Link, useNavigate } from "react-router";
import useDocumentTitle from "@/lib/useDocumentTitle";
import {
  usePoliticians,
  useBills,
  useVotes,
  useParties,
  useCoSponsorshipGraph,
  useBillPipeline,
  useNeighbors,
  useTopSponsors,
} from "@/api/queries";
import HeroGraph from "@/components/graph/HeroGraph";
import { getPartyColor } from "@/lib/partyColors";
import { formatNumber, formatDate } from "@/lib/format";
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
  const [selectedNode, setSelectedNode] = useState<{
    id: string;
    name: string;
    party: string | null;
  } | null>(null);

  // Graph data
  const graphData = useCoSponsorshipGraph({
    min_weight: 5,
    limit: 300,
  });

  // Summary counts
  const politicians = usePoliticians({ page: 1, size: 1 });
  const bills = useBills({ page: 1, size: 1 });
  const votesQuery = useVotes({ page: 1, size: 5 });
  const parties = useParties();
  const pipeline = useBillPipeline();
  const topSponsors = useTopSponsors({ assembly_term: 22, limit: 10 });

  // Neighbors for selected node
  const neighbors = useNeighbors(selectedNode?.id ?? "", {
    min_weight: 1,
    limit: 8,
  });

  // Find politician ID from graph node (assembly_id) to link to detail page
  const selectedPoliticians = usePoliticians({
    name: selectedNode?.name,
    page: 1,
    size: 1,
  });

  const selectedPolId = selectedPoliticians.data?.items[0]?.id;

  function handleNodeClick(id: string, name: string, party: string | null) {
    setSelectedNode((prev) =>
      prev?.id === id ? null : { id, name, party },
    );
  }

  // Party legend from graph data
  const partyLegend = useMemo(() => {
    if (!graphData.data) return [];
    const counts = new Map<string, number>();
    for (const n of graphData.data.nodes) {
      const p = n.party ?? "무소속";
      counts.set(p, (counts.get(p) ?? 0) + 1);
    }
    return [...counts.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8);
  }, [graphData.data]);

  return (
    <div>
      {/* ── Hero: Graph Control Tower ───────────────────────────── */}
      <section className="relative overflow-hidden bg-gray-950">
        {/* Header overlay */}
        <div className="pointer-events-none absolute inset-x-0 top-0 z-10 bg-gradient-to-b from-gray-950/80 to-transparent px-6 pb-16 pt-5">
          <div className="pointer-events-auto max-w-7xl mx-auto flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h1 className="text-lg font-bold text-white sm:text-xl">
                공동발의 네트워크
              </h1>
              <p className="mt-1 text-xs text-gray-400">
                의원 간 공동발의 관계 · 노드를 클릭하여 탐색
              </p>
            </div>
            <div className="flex items-center gap-4">
              {/* Stats badges */}
              <div className="flex gap-2">
                <Link
                  to="/politicians"
                  className="rounded-lg bg-white/10 px-3 py-1.5 text-xs font-medium text-white backdrop-blur-sm transition-colors hover:bg-white/20"
                >
                  정치인{" "}
                  <span className="font-bold">
                    {politicians.data
                      ? formatNumber(politicians.data.total)
                      : "—"}
                  </span>
                </Link>
                <Link
                  to="/bills"
                  className="rounded-lg bg-white/10 px-3 py-1.5 text-xs font-medium text-white backdrop-blur-sm transition-colors hover:bg-white/20"
                >
                  법안{" "}
                  <span className="font-bold">
                    {bills.data ? formatNumber(bills.data.total) : "—"}
                  </span>
                </Link>
                <Link
                  to="/votes"
                  className="rounded-lg bg-white/10 px-3 py-1.5 text-xs font-medium text-blue-300 backdrop-blur-sm transition-colors hover:bg-white/20"
                >
                  표결{" "}
                  <span className="font-bold">
                    {votesQuery.data
                      ? formatNumber(votesQuery.data.total)
                      : "—"}
                  </span>
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Party legend overlay - bottom left */}
        <div className="pointer-events-none absolute bottom-4 left-4 z-10">
          <div className="pointer-events-auto flex flex-wrap gap-1.5">
            {partyLegend.map(([party, count]) => (
              <span
                key={party}
                className="flex items-center gap-1.5 rounded-md bg-gray-900/80 px-2 py-1 text-[10px] text-gray-300 backdrop-blur-sm"
              >
                <span
                  className="h-2 w-2 rounded-full"
                  style={{ backgroundColor: getPartyColor(party) }}
                />
                {party}
                <span className="text-gray-500">{count}</span>
              </span>
            ))}
          </div>
        </div>

        {/* Graph stats overlay - bottom right */}
        {graphData.data && (
          <div className="pointer-events-none absolute bottom-4 right-4 z-10 text-[10px] text-gray-500">
            노드 {graphData.data.nodes.length} · 엣지{" "}
            {graphData.data.edges.length}
          </div>
        )}

        {/* Selected node info overlay - right side */}
        {selectedNode && (
          <div className="pointer-events-none absolute right-4 top-36 z-10 w-56 sm:top-16 sm:w-64">
            <div className="pointer-events-auto rounded-xl border border-white/10 bg-gray-900/90 p-4 backdrop-blur-md">
              <div className="flex items-center gap-3">
                <div
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
                  style={{
                    backgroundColor: getPartyColor(selectedNode.party),
                  }}
                >
                  {selectedNode.name.charAt(0)}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-white">
                    {selectedNode.name}
                  </p>
                  <p className="text-xs text-gray-400">
                    {selectedNode.party ?? "무소속"}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-gray-500 hover:text-gray-300"
                >
                  &times;
                </button>
              </div>

              {/* Neighbors */}
              {neighbors.data && neighbors.data.length > 0 && (
                <div className="mt-3 border-t border-white/10 pt-3">
                  <p className="text-[10px] font-medium uppercase tracking-wider text-gray-500">
                    공동발의 상위
                  </p>
                  <div className="mt-1.5 space-y-1">
                    {neighbors.data.map((n) => (
                      <div
                        key={n.assembly_id}
                        className="flex items-center justify-between text-xs"
                      >
                        <div className="flex items-center gap-1.5">
                          <span
                            className="h-1.5 w-1.5 rounded-full"
                            style={{
                              backgroundColor: getPartyColor(n.party),
                            }}
                          />
                          <span className="text-gray-300">{n.name}</span>
                        </div>
                        <span className="text-gray-500">
                          {n.weight}건
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedPolId && (
                <button
                  onClick={() => navigate(`/politicians/${selectedPolId}`)}
                  className="mt-3 w-full rounded-lg bg-white/10 py-1.5 text-xs font-medium text-white transition-colors hover:bg-white/20"
                >
                  프로필 보기 &rarr;
                </button>
              )}
            </div>
          </div>
        )}

        {/* The graph itself */}
        <div className="h-[300px] w-full sm:h-[520px]">
          {graphData.isLoading ? (
            <div className="flex h-full items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-700 border-t-gray-400" />
            </div>
          ) : graphData.data && graphData.data.nodes.length > 0 ? (
            <HeroGraph
              data={graphData.data}
              selectedNodeId={selectedNode?.id ?? null}
              onNodeClick={handleNodeClick}
            />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-gray-600">
              그래프 데이터를 불러올 수 없습니다
            </div>
          )}
        </div>
      </section>

      {/* ── Below the graph: surrounding data ───────────────────── */}
      <div className="mx-auto max-w-7xl px-4 py-6">
        {/* Top sponsors — horizontal scroll */}
        {topSponsors.data && topSponsors.data.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">22대 대표발의 TOP 10</h2>
              <Link
                to="/politicians?term=22"
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
                  <div
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
                    style={{ backgroundColor: getPartyColor(pol.party) }}
                  >
                    {pol.name.charAt(0)}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{pol.name}</p>
                    <p className="text-[11px] text-gray-400">
                      {pol.party} · {formatNumber(pol.bill_count)}건
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Recent votes + Bill pipeline side by side */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
          {/* Recent votes — left 3 cols */}
          <div className="lg:col-span-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">최근 표결</h2>
              <Link
                to="/votes"
                className="text-sm text-gray-400 hover:text-gray-600"
              >
                전체 보기 &rarr;
              </Link>
            </div>
            <div className="mt-3 space-y-2">
              {votesQuery.data?.items.map((vote) => {
                const total = vote.total_members ?? 0;
                const yesPct = pct(vote.yes_count, total);
                const noPct = pct(vote.no_count, total);
                const passed =
                  vote.result === "원안가결" || vote.result === "수정가결";

                return (
                  <Link
                    key={vote.vote_id}
                    to={`/votes/${vote.vote_id}`}
                    className="group flex items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-2.5 transition-all hover:border-gray-300 hover:shadow-md"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-gray-900 group-hover:text-blue-600">
                        {vote.bill_name ?? vote.bill_id}
                      </p>
                      <p className="mt-0.5 text-[11px] text-gray-400">
                        {formatDate(vote.vote_date)}
                      </p>
                    </div>
                    <div className="hidden w-28 sm:block">
                      <div className="flex h-1.5 overflow-hidden rounded-full bg-gray-100">
                        {(vote.yes_count ?? 0) > 0 && (
                          <div
                            className="bg-emerald-500"
                            style={{ width: `${yesPct}%` }}
                          />
                        )}
                        {(vote.no_count ?? 0) > 0 && (
                          <div
                            className="bg-red-500"
                            style={{ width: `${noPct}%` }}
                          />
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-base font-bold text-emerald-600">
                        {yesPct}%
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
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={pipeline.data}
                      layout="vertical"
                      margin={{ left: 80, right: 8 }}
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
                      <Bar dataKey="count" radius={[0, 4, 4, 0]}>
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
              <div className="mt-3 flex h-56 items-center justify-center rounded-lg border border-gray-200 bg-white text-sm text-gray-400">
                불러오는 중...
              </div>
            )}
          </div>
        </div>

        {/* Party breakdown */}
        {parties.data && parties.data.length > 0 && (
          <div className="mt-6">
            <h2 className="text-lg font-semibold">정당</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {parties.data.map((p) => (
                <Link
                  key={p.id}
                  to={`/politicians?party=${encodeURIComponent(p.name)}`}
                  className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm transition-all hover:border-gray-300 hover:shadow-md"
                >
                  <span
                    className="h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: getPartyColor(p.name) }}
                  />
                  {p.name}
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
