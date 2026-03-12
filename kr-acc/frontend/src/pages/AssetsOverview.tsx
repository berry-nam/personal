import { Link } from "react-router";
import useDocumentTitle from "@/lib/useDocumentTitle";
import { useAssetRankings, useAssetAggregate } from "@/api/queries";
import { getPartyColor } from "@/lib/partyColors";
import { formatKrw } from "@/lib/format";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Cell,
  Treemap,
  ScatterChart,
  Scatter,
  CartesianGrid,
  ZAxis,
} from "recharts";

export default function AssetsOverview() {
  useDocumentTitle("재산·자금");
  const rankings = useAssetRankings(20);
  const aggregate = useAssetAggregate();

  const maxAsset = rankings.data?.[0]?.total_assets ?? 1;

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold">재산·자금</h1>

      {/* Asset Rankings — Horizontal bar chart */}
      {rankings.data && rankings.data.length > 0 && (
        <section className="rounded-lg border border-gray-200 bg-white p-5">
          <h2 className="mb-4 text-lg font-semibold">재산 상위 20인</h2>
          <div className="space-y-1.5">
            {rankings.data.map((r, i) => (
              <Link
                key={r.politician_id}
                to={`/politicians/${r.politician_id}`}
                className="group flex items-center gap-3 rounded-lg px-2 py-1.5 transition-colors hover:bg-gray-50"
              >
                <span className="w-6 text-right text-sm font-bold text-gray-300">
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
                    className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
                    style={{ backgroundColor: getPartyColor(r.party) }}
                  >
                    {r.name.charAt(0)}
                  </div>
                )}
                <div className="w-20 shrink-0">
                  <p className="text-sm font-medium group-hover:text-blue-600">
                    {r.name}
                  </p>
                  <p className="text-[10px] text-gray-400">{r.party}</p>
                </div>
                <div className="flex-1">
                  <div className="h-4 overflow-hidden rounded bg-gray-100">
                    <div
                      className="h-full rounded transition-all"
                      style={{
                        width: `${(r.total_assets / maxAsset) * 100}%`,
                        backgroundColor: getPartyColor(r.party),
                        opacity: 0.7,
                      }}
                    />
                  </div>
                </div>
                <span className="w-24 text-right text-sm font-medium text-gray-600">
                  {formatKrw(r.total_assets)}
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Aggregate by party */}
      {aggregate.data && aggregate.data.length > 0 && (
        <>
          {/* Treemap */}
          <section className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="mb-4 text-lg font-semibold">
              정당별 총 재산 (트리맵)
            </h2>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <Treemap
                  data={aggregate.data.map((a) => ({
                    name: a.party,
                    size: a.total_assets,
                    fill: getPartyColor(a.party),
                  }))}
                  dataKey="size"
                  nameKey="name"
                  stroke="#fff"
                  content={({ x, y, width, height, name, fill }) => {
                    const w = Number(width);
                    const h = Number(height);
                    if (w < 40 || h < 20) return null;
                    return (
                      <g>
                        <rect
                          x={x}
                          y={y}
                          width={w}
                          height={h}
                          fill={String(fill)}
                          stroke="#fff"
                          strokeWidth={2}
                          rx={4}
                        />
                        <text
                          x={Number(x) + w / 2}
                          y={Number(y) + h / 2}
                          textAnchor="middle"
                          dominantBaseline="central"
                          fontSize={w < 60 ? 10 : 12}
                          fill="#fff"
                          fontWeight="bold"
                        >
                          {name}
                        </text>
                      </g>
                    );
                  }}
                />
              </ResponsiveContainer>
            </div>
          </section>

          {/* Category Breakdown — Stacked bar */}
          <section className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="mb-4 text-lg font-semibold">
              정당별 재산 구성
            </h2>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={aggregate.data}
                  margin={{ left: 60, right: 8 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="party" tick={{ fontSize: 11 }} />
                  <YAxis tickFormatter={(v: number) => formatKrw(v)} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v) => formatKrw(Number(v))} />
                  <Bar dataKey="total_real_estate" name="부동산" stackId="a" fill="#3B82F6" />
                  <Bar dataKey="total_deposits" name="예금" stackId="a" fill="#22C55E" />
                  <Bar dataKey="total_securities" name="유가증권" stackId="a" fill="#F59E0B" />
                  <Bar dataKey="total_crypto" name="가상자산" stackId="a" fill="#8B5CF6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 flex justify-center gap-4 text-xs">
              {[
                { name: "부동산", color: "#3B82F6" },
                { name: "예금", color: "#22C55E" },
                { name: "유가증권", color: "#F59E0B" },
                { name: "가상자산", color: "#8B5CF6" },
              ].map((c) => (
                <span key={c.name} className="flex items-center gap-1">
                  <span
                    className="inline-block h-2 w-2 rounded-full"
                    style={{ backgroundColor: c.color }}
                  />
                  {c.name}
                </span>
              ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
