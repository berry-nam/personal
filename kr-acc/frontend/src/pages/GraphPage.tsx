import { useState, useMemo } from "react";
import { Link, useNavigate } from "react-router";
import {
  useCoSponsorshipGraph,
  useParties,
  useTopSponsors,
} from "@/api/queries";
import useDocumentTitle from "@/lib/useDocumentTitle";
import ForceGraph from "@/components/graph/ForceGraph";
import { getPartyColor } from "@/lib/partyColors";
import { formatNumber } from "@/lib/format";

export default function GraphPage() {
  useDocumentTitle("네트워크");
  const navigate = useNavigate();
  const [party, setParty] = useState<string | undefined>();
  const [minWeight, setMinWeight] = useState(3);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const { data, isLoading } = useCoSponsorshipGraph({
    party,
    min_weight: minWeight,
    limit: 800,
  });
  const parties = useParties();
  const topSponsors = useTopSponsors({ assembly_term: 22, limit: 5 });

  // Compute stats
  const stats = useMemo(() => {
    if (!data) return null;
    const partyGroups = new Map<string, number>();
    for (const n of data.nodes) {
      const p = n.party ?? "무소속";
      partyGroups.set(p, (partyGroups.get(p) ?? 0) + 1);
    }
    // Find most connected node
    const connectionCount = new Map<string, number>();
    for (const e of data.edges) {
      connectionCount.set(
        e.source,
        (connectionCount.get(e.source) ?? 0) + 1,
      );
      connectionCount.set(
        e.target,
        (connectionCount.get(e.target) ?? 0) + 1,
      );
    }
    let hubNode = { id: "", count: 0 };
    for (const [id, count] of connectionCount) {
      if (count > hubNode.count) hubNode = { id, count };
    }
    const hubInfo = data.nodes.find((n) => n.id === hubNode.id);

    // Cross-party edges
    let crossParty = 0;
    const nodeParty = new Map(data.nodes.map((n) => [n.id, n.party]));
    for (const e of data.edges) {
      if (nodeParty.get(e.source) !== nodeParty.get(e.target)) crossParty++;
    }

    return {
      partyGroups: [...partyGroups.entries()].sort((a, b) => b[1] - a[1]),
      hub: hubInfo
        ? { name: hubInfo.name, party: hubInfo.party, connections: hubNode.count }
        : null,
      crossPartyRate:
        data.edges.length > 0
          ? ((crossParty / data.edges.length) * 100).toFixed(1)
          : "0",
      totalEdges: data.edges.length,
    };
  }, [data]);

  // Selected node info
  const selectedInfo = useMemo(() => {
    if (!data || !selectedNode) return null;
    const node = data.nodes.find((n) => n.id === selectedNode);
    if (!node) return null;
    const neighbors = new Set<string>();
    for (const e of data.edges) {
      if (e.source === selectedNode) neighbors.add(e.target);
      if (e.target === selectedNode) neighbors.add(e.source);
    }
    const neighborNodes = data.nodes.filter((n) => neighbors.has(n.id));
    return { ...node, neighbors: neighborNodes };
  }, [data, selectedNode]);

  return (
    <div className="-mx-4 -mt-4 sm:-mx-6 sm:-mt-6">
      {/* Full-viewport dark layout */}
      <div className="relative bg-gray-950 text-white">
        {/* Top bar overlay */}
        <div className="pointer-events-none absolute inset-x-0 top-0 z-10 bg-gradient-to-b from-gray-950/90 to-transparent">
          <div className="pointer-events-auto mx-auto max-w-7xl px-4 py-4">
            <h1 className="text-xl font-bold">22대 국회 관계도</h1>
            <p className="mt-1 text-xs text-gray-400">
              의원 간 공동발의 네트워크 · 인물 중심 관계 탐색
            </p>

            {/* Controls */}
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <div className="flex flex-wrap gap-1">
                <button
                  onClick={() => setParty(undefined)}
                  className={`rounded-full px-3 py-1 text-xs transition-colors ${
                    !party
                      ? "bg-white/20 text-white"
                      : "bg-white/5 text-gray-400 hover:bg-white/10"
                  }`}
                >
                  전체
                </button>
                {parties.data
                  ?.filter((p) =>
                    data?.nodes.some((n) => n.party === p.name),
                  )
                  .map((p) => (
                    <button
                      key={p.id}
                      onClick={() => setParty(p.name)}
                      className={`flex items-center gap-1 rounded-full px-3 py-1 text-xs transition-colors ${
                        party === p.name
                          ? "bg-white/20 text-white"
                          : "bg-white/5 text-gray-400 hover:bg-white/10"
                      }`}
                    >
                      <span
                        className="inline-block h-2 w-2 rounded-full"
                        style={{ backgroundColor: getPartyColor(p.name) }}
                      />
                      {p.name}
                    </button>
                  ))}
              </div>
              <label className="flex items-center gap-2 text-xs text-gray-400">
                밀도
                <input
                  type="range"
                  min={1}
                  max={15}
                  value={minWeight}
                  onChange={(e) => setMinWeight(Number(e.target.value))}
                  className="w-20 accent-white"
                />
                <span className="w-4 text-center font-mono text-gray-300">
                  {minWeight}
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Stats overlay — bottom left */}
        {stats && (
          <div className="pointer-events-none absolute bottom-4 left-4 z-10 space-y-2">
            <div className="pointer-events-auto rounded-lg bg-gray-900/80 px-3 py-2 backdrop-blur-sm">
              <div className="flex gap-4 text-xs">
                <div>
                  <p className="text-gray-500">노드</p>
                  <p className="font-bold">
                    {formatNumber(data?.nodes.length ?? 0)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500">연결</p>
                  <p className="font-bold">{formatNumber(stats.totalEdges)}</p>
                </div>
                <div>
                  <p className="text-gray-500">교차정당</p>
                  <p className="font-bold text-amber-400">
                    {stats.crossPartyRate}%
                  </p>
                </div>
              </div>
            </div>
            {stats.hub && (
              <div className="pointer-events-auto rounded-lg bg-gray-900/80 px-3 py-2 backdrop-blur-sm">
                <p className="text-[10px] text-gray-500">허브 의원</p>
                <p className="text-sm font-bold">
                  {stats.hub.name}{" "}
                  <span className="font-normal text-gray-400">
                    ({stats.hub.party})
                  </span>
                </p>
                <p className="text-[10px] text-gray-400">
                  {stats.hub.connections}개 연결
                </p>
              </div>
            )}
          </div>
        )}

        {/* Party legend — bottom right */}
        {stats && (
          <div className="pointer-events-none absolute bottom-4 right-4 z-10">
            <div className="pointer-events-auto flex flex-wrap gap-1.5">
              {stats.partyGroups.map(([partyName, count]) => (
                <span
                  key={partyName}
                  className="flex items-center gap-1 rounded bg-gray-900/80 px-2 py-1 text-[10px] text-gray-300 backdrop-blur-sm"
                >
                  <span
                    className="h-2 w-2 rounded-full"
                    style={{ backgroundColor: getPartyColor(partyName) }}
                  />
                  {partyName} {count}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Selected node detail — right overlay */}
        {selectedInfo && (
          <div className="pointer-events-none absolute right-4 top-36 z-10 w-60">
            <div className="pointer-events-auto rounded-xl border border-white/10 bg-gray-900/90 p-4 backdrop-blur-md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-semibold">{selectedInfo.name}</p>
                  <p className="text-xs text-gray-400">
                    {selectedInfo.party ?? "무소속"}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedNode(null)}
                  className="text-gray-500 hover:text-gray-300"
                >
                  &times;
                </button>
              </div>
              <p className="mt-2 text-xs text-gray-500">
                공동발의 연결 {selectedInfo.neighbors.length}명
              </p>
              <div className="mt-1.5 max-h-32 space-y-0.5 overflow-y-auto">
                {selectedInfo.neighbors.slice(0, 10).map((n) => (
                  <div
                    key={n.id}
                    className="flex items-center gap-1.5 text-xs"
                  >
                    <span
                      className="h-1.5 w-1.5 rounded-full"
                      style={{ backgroundColor: getPartyColor(n.party) }}
                    />
                    <span className="text-gray-300">{n.name}</span>
                  </div>
                ))}
              </div>
              <button
                onClick={() =>
                  navigate(
                    `/politicians?name=${encodeURIComponent(selectedInfo.name)}`,
                  )
                }
                className="mt-3 w-full rounded-lg bg-white/10 py-1.5 text-xs font-medium transition-colors hover:bg-white/20"
              >
                프로필 보기 &rarr;
              </button>
            </div>
          </div>
        )}

        {/* The graph */}
        <div className="h-[calc(100vh-56px)]">
          {isLoading ? (
            <div className="flex h-full items-center justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-gray-700 border-t-gray-400" />
            </div>
          ) : data && data.nodes.length > 0 ? (
            <ForceGraph data={data} width={1400} height={800} />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-gray-600">
              표시할 데이터가 없습니다. 밀도를 낮춰보세요.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
