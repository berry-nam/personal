import { useMemo } from "react";
import { Link } from "react-router";
import useDocumentTitle from "@/lib/useDocumentTitle";
import {
  useAssetRankings,
  useAssetAggregate,
  useAssetItemStocks,
  useAssetItemRealEstate,
  useAssetItemCrypto,
  useFundRankings,
  useAllCompanyHoldings,
} from "@/api/queries";
import { getPartyColor } from "@/lib/partyColors";
import { formatKrw } from "@/lib/format";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  CartesianGrid,
  Cell,
  PieChart,
  Pie,
} from "recharts";

const CATEGORY_COLORS: Record<string, string> = {
  부동산: "#3B82F6",
  예금: "#22C55E",
  유가증권: "#F59E0B",
  가상자산: "#8B5CF6",
};

// Reusable ranking list for each category
function RankingCard({
  title,
  subtitle,
  data,
  field,
  limit = 10,
  color,
}: {
  title: string;
  subtitle: string;
  data: {
    politician_id: number;
    name: string;
    party: string | null;
    photo_url: string | null;
    total_assets: number;
    total_real_estate: number | null;
    total_deposits: number | null;
    total_securities: number | null;
    total_crypto: number | null;
  }[];
  field: "total_assets" | "total_real_estate" | "total_deposits" | "total_securities" | "total_crypto";
  limit?: number;
  color?: string;
}) {
  const sorted = useMemo(
    () =>
      [...data]
        .sort((a, b) => ((b[field] as number) ?? 0) - ((a[field] as number) ?? 0))
        .filter((r) => ((r[field] as number) ?? 0) > 0)
        .slice(0, limit),
    [data, field, limit],
  );
  const maxVal = (sorted[0]?.[field] as number) ?? 1;

  if (sorted.length === 0) return null;

  return (
    <section className="rounded-lg border border-gray-200 bg-white p-5">
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mb-3 text-xs text-gray-400">{subtitle}</p>
      <div className="space-y-1">
        {sorted.map((r, i) => {
          const value = (r[field] as number) ?? 0;
          return (
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
                      width: `${Math.max((value / maxVal) * 100, 2)}%`,
                      backgroundColor: color ?? getPartyColor(r.party),
                      opacity: 0.75,
                    }}
                  />
                </div>
              </div>
              <span className="w-20 text-right text-sm font-semibold tabular-nums text-gray-700">
                {formatKrw(value)}
              </span>
            </Link>
          );
        })}
      </div>
    </section>
  );
}

export default function AssetsOverview() {
  useDocumentTitle("재산·자금");

  // Fetch ALL rankings (large limit to have enough for per-category sorting)
  const rankings = useAssetRankings(50);
  const rankingsRealEstate = useAssetRankings(20, "real_estate");
  const rankingsDeposits = useAssetRankings(20, "deposits");
  const rankingsSecurities = useAssetRankings(20, "securities");
  const rankingsCrypto = useAssetRankings(20, "crypto");
  const aggregate = useAssetAggregate();

  // Detail item data
  const stocks = useAssetItemStocks(20);
  const realEstate = useAssetItemRealEstate(20);
  const crypto = useAssetItemCrypto(20);
  const funds = useFundRankings(undefined, 20);
  const companies = useAllCompanyHoldings();

  // Summary stats from rankings
  const summaryStats = useMemo(() => {
    if (!rankings.data || rankings.data.length === 0) return null;
    const total = rankings.data.reduce((s, r) => s + r.total_assets, 0);
    const avg = Math.round(total / rankings.data.length);
    const median =
      rankings.data.length > 0
        ? rankings.data[Math.floor(rankings.data.length / 2)].total_assets
        : 0;
    const top = rankings.data[0];
    return { total, avg, median, top, count: rankings.data.length };
  }, [rankings.data]);

  // Category totals from aggregate
  const categoryTotals = useMemo(() => {
    if (!aggregate.data) return [];
    const totals = aggregate.data.reduce(
      (acc, a) => ({
        real_estate: acc.real_estate + a.total_real_estate,
        deposits: acc.deposits + a.total_deposits,
        securities: acc.securities + a.total_securities,
        crypto: acc.crypto + a.total_crypto,
      }),
      { real_estate: 0, deposits: 0, securities: 0, crypto: 0 },
    );
    return [
      { name: "부동산", value: totals.real_estate, color: CATEGORY_COLORS["부동산"] },
      { name: "예금", value: totals.deposits, color: CATEGORY_COLORS["예금"] },
      { name: "유가증권", value: totals.securities, color: CATEGORY_COLORS["유가증권"] },
      { name: "가상자산", value: totals.crypto, color: CATEGORY_COLORS["가상자산"] },
    ];
  }, [aggregate.data]);

  const categoryTotal = categoryTotals.reduce((s, c) => s + c.value, 0);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">재산·자금</h1>
        <p className="mt-1 text-sm text-gray-500">
          국회의원 재산공개 데이터 기반 비교 분석
        </p>
      </div>

      {/* ── Section 1: Summary Stats ──────────────────── */}
      {summaryStats && (
        <section className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
            <p className="text-xs font-medium text-gray-500">재산 1위</p>
            <p className="mt-1 text-lg font-bold">{summaryStats.top.name}</p>
            <p className="text-sm font-semibold text-blue-600">
              {formatKrw(summaryStats.top.total_assets)}
            </p>
            <p className="text-[10px] text-gray-400">{summaryStats.top.party}</p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
            <p className="text-xs font-medium text-gray-500">의원 평균 재산</p>
            <p className="mt-2 text-2xl font-bold">{formatKrw(summaryStats.avg)}</p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
            <p className="text-xs font-medium text-gray-500">재산 중앙값</p>
            <p className="mt-2 text-2xl font-bold">{formatKrw(summaryStats.median)}</p>
          </div>
          <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
            <p className="text-xs font-medium text-gray-500">전체 재산 합계</p>
            <p className="mt-2 text-2xl font-bold">{formatKrw(summaryStats.total)}</p>
            <p className="text-[10px] text-gray-400">{summaryStats.count}명 합산</p>
          </div>
        </section>
      )}

      {/* ── Section 2: Category Overview (Pie + Bars) ── */}
      {categoryTotals.length > 0 && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Pie chart */}
          <section className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="mb-1 text-lg font-semibold">재산 유형별 비중</h2>
            <p className="mb-2 text-xs text-gray-400">
              전체 의원 재산의 카테고리별 구성
            </p>
            <div className="flex items-center justify-center">
              <div className="h-56 w-56">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryTotals}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={90}
                      paddingAngle={2}
                    >
                      {categoryTotals.map((c) => (
                        <Cell key={c.name} fill={c.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v) => formatKrw(Number(v))} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="mt-2 flex flex-wrap justify-center gap-3 text-xs">
              {categoryTotals.map((c) => (
                <span key={c.name} className="flex items-center gap-1.5">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: c.color }}
                  />
                  {c.name}{" "}
                  <span className="font-semibold">
                    {categoryTotal > 0
                      ? ((c.value / categoryTotal) * 100).toFixed(1)
                      : 0}
                    %
                  </span>
                </span>
              ))}
            </div>
          </section>

          {/* Category bars */}
          <section className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="mb-1 text-lg font-semibold">유형별 총액 비교</h2>
            <p className="mb-3 text-xs text-gray-400">부동산 · 예금 · 유가증권 · 가상자산</p>
            <div className="space-y-3">
              {categoryTotals.map((c) => {
                const maxCat = Math.max(...categoryTotals.map((x) => x.value)) || 1;
                return (
                  <div key={c.name}>
                    <div className="mb-1 flex items-center justify-between text-xs">
                      <span className="flex items-center gap-1.5 font-medium text-gray-700">
                        <span
                          className="h-2.5 w-2.5 rounded-full"
                          style={{ backgroundColor: c.color }}
                        />
                        {c.name}
                      </span>
                      <span className="font-semibold">{formatKrw(c.value)}</span>
                    </div>
                    <div className="h-6 overflow-hidden rounded bg-gray-100">
                      <div
                        className="h-full rounded"
                        style={{
                          width: `${(c.value / maxCat) * 100}%`,
                          backgroundColor: c.color,
                          minWidth: "4px",
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        </div>
      )}

      {/* ── Section 3: 총 재산 Top 20 ─────────────────── */}
      {rankings.data && rankings.data.length > 0 && (
        <RankingCard
          title="총 재산 상위 20인"
          subtitle="최신 재산공개 기준 · 클릭하여 의원 프로필 확인"
          data={rankings.data}
          field="total_assets"
          limit={20}
        />
      )}

      {/* ── Section 4: Category-specific Rankings (2-col grid) ── */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {rankingsRealEstate.data && rankingsRealEstate.data.length > 0 && (
          <RankingCard
            title="부동산 상위 10인"
            subtitle="부동산 보유액 기준"
            data={rankingsRealEstate.data}
            field="total_real_estate"
            limit={10}
            color={CATEGORY_COLORS["부동산"]}
          />
        )}
        {rankingsDeposits.data && rankingsDeposits.data.length > 0 && (
          <RankingCard
            title="예금 상위 10인"
            subtitle="예금 보유액 기준"
            data={rankingsDeposits.data}
            field="total_deposits"
            limit={10}
            color={CATEGORY_COLORS["예금"]}
          />
        )}
        {rankingsSecurities.data && rankingsSecurities.data.length > 0 && (
          <RankingCard
            title="유가증권 상위 10인"
            subtitle="주식·채권 등 유가증권 기준"
            data={rankingsSecurities.data}
            field="total_securities"
            limit={10}
            color={CATEGORY_COLORS["유가증권"]}
          />
        )}
        {rankingsCrypto.data && rankingsCrypto.data.length > 0 && (
          <RankingCard
            title="가상자산 상위 10인"
            subtitle="비트코인·이더리움 등 가상자산 기준"
            data={rankingsCrypto.data}
            field="total_crypto"
            limit={10}
            color={CATEGORY_COLORS["가상자산"]}
          />
        )}
      </div>

      {/* ── Section 5: Party Aggregate ────────────────── */}
      {aggregate.data && aggregate.data.length > 0 && (
        <>
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Party total assets */}
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h2 className="mb-1 text-lg font-semibold">정당별 총 재산</h2>
              <p className="mb-4 text-xs text-gray-400">
                소속 의원 재산 합산 · 정당별 비교
              </p>
              <div className="space-y-2">
                {aggregate.data
                  .filter((a) => a.total_assets > 0)
                  .map((a) => {
                    const maxPartyAsset = aggregate.data![0].total_assets || 1;
                    return (
                      <div key={a.party} className="flex items-center gap-3">
                        <span className="w-20 text-right text-xs font-medium text-gray-600">
                          {a.party}
                        </span>
                        <div className="flex-1">
                          <div className="h-7 overflow-hidden rounded bg-gray-100">
                            <div
                              className="flex h-full items-center rounded pl-2 text-[10px] font-bold text-white"
                              style={{
                                width: `${(a.total_assets / maxPartyAsset) * 100}%`,
                                backgroundColor: getPartyColor(a.party),
                                minWidth: "30px",
                              }}
                            >
                              {formatKrw(a.total_assets)}
                            </div>
                          </div>
                        </div>
                        <span className="w-10 text-right text-xs text-gray-400">
                          {a.count}명
                        </span>
                      </div>
                    );
                  })}
              </div>
            </section>

            {/* Per-capita average by party */}
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h2 className="mb-1 text-lg font-semibold">1인당 평균 재산</h2>
              <p className="mb-4 text-xs text-gray-400">
                정당별 의원 1인당 평균 총 재산
              </p>
              {(() => {
                const perCapita = aggregate.data
                  .filter((a) => a.count > 0 && a.total_assets > 0)
                  .map((a) => ({
                    party: a.party,
                    avg: Math.round(a.total_assets / a.count),
                    count: a.count,
                  }))
                  .sort((a, b) => b.avg - a.avg);
                const maxAvg = perCapita[0]?.avg || 1;
                return (
                  <div className="space-y-2">
                    {perCapita.map((a) => (
                      <div key={a.party} className="flex items-center gap-3">
                        <span className="w-20 text-right text-xs font-medium text-gray-600">
                          {a.party}
                        </span>
                        <div className="flex-1">
                          <div className="h-7 overflow-hidden rounded bg-gray-100">
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
                      </div>
                    ))}
                  </div>
                );
              })()}
            </section>

            {/* Party real estate comparison */}
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h2 className="mb-1 text-lg font-semibold">정당별 부동산 총액</h2>
              <p className="mb-4 text-xs text-gray-400">어떤 정당이 부동산을 가장 많이 보유하고 있는가?</p>
              {(() => {
                const sorted = [...aggregate.data]
                  .filter((a) => a.total_real_estate > 0)
                  .sort((a, b) => b.total_real_estate - a.total_real_estate);
                const max = sorted[0]?.total_real_estate || 1;
                return (
                  <div className="space-y-2">
                    {sorted.map((a) => (
                      <div key={a.party} className="flex items-center gap-3">
                        <span className="w-20 text-right text-xs font-medium text-gray-600">
                          {a.party}
                        </span>
                        <div className="flex-1">
                          <div className="h-7 overflow-hidden rounded bg-gray-100">
                            <div
                              className="flex h-full items-center rounded pl-2 text-[10px] font-bold text-white"
                              style={{
                                width: `${(a.total_real_estate / max) * 100}%`,
                                backgroundColor: CATEGORY_COLORS["부동산"],
                                minWidth: "30px",
                              }}
                            >
                              {formatKrw(a.total_real_estate)}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                );
              })()}
            </section>

            {/* Party securities comparison */}
            <section className="rounded-lg border border-gray-200 bg-white p-5">
              <h2 className="mb-1 text-lg font-semibold">정당별 유가증권 총액</h2>
              <p className="mb-4 text-xs text-gray-400">정당별 주식·채권 등 유가증권 비교</p>
              {(() => {
                const sorted = [...aggregate.data]
                  .filter((a) => a.total_securities > 0)
                  .sort((a, b) => b.total_securities - a.total_securities);
                const max = sorted[0]?.total_securities || 1;
                return (
                  <div className="space-y-2">
                    {sorted.map((a) => (
                      <div key={a.party} className="flex items-center gap-3">
                        <span className="w-20 text-right text-xs font-medium text-gray-600">
                          {a.party}
                        </span>
                        <div className="flex-1">
                          <div className="h-7 overflow-hidden rounded bg-gray-100">
                            <div
                              className="flex h-full items-center rounded pl-2 text-[10px] font-bold text-white"
                              style={{
                                width: `${(a.total_securities / max) * 100}%`,
                                backgroundColor: CATEGORY_COLORS["유가증권"],
                                minWidth: "30px",
                              }}
                            >
                              {formatKrw(a.total_securities)}
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                );
              })()}
            </section>
          </div>

          {/* Category breakdown stacked */}
          <section className="rounded-lg border border-gray-200 bg-white p-5">
            <h2 className="mb-1 text-lg font-semibold">
              정당별 재산 구성 비교
            </h2>
            <p className="mb-4 text-xs text-gray-400">
              부동산 · 예금 · 유가증권 · 가상자산
            </p>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={aggregate.data.filter((a) => a.total_assets > 0)}
                  margin={{ left: 60, right: 8 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="party" tick={{ fontSize: 11 }} />
                  <YAxis
                    tickFormatter={(v: number) => formatKrw(v)}
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip formatter={(v) => formatKrw(Number(v))} />
                  <Bar dataKey="total_real_estate" name="부동산" stackId="a" fill="#3B82F6" />
                  <Bar dataKey="total_deposits" name="예금" stackId="a" fill="#22C55E" />
                  <Bar dataKey="total_securities" name="유가증권" stackId="a" fill="#F59E0B" />
                  <Bar dataKey="total_crypto" name="가상자산" stackId="a" fill="#8B5CF6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 flex justify-center gap-4 text-xs">
              {Object.entries(CATEGORY_COLORS).map(([name, color]) => (
                <span key={name} className="flex items-center gap-1">
                  <span
                    className="inline-block h-2 w-2 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                  {name}
                </span>
              ))}
            </div>
          </section>
        </>
      )}

      {/* ── Section 6: 주식 보유 상세 (종목별) ────────── */}
      {stocks.data && stocks.data.length > 0 && (
        <section className="rounded-lg border border-gray-200 bg-white p-5">
          <h2 className="mb-1 text-lg font-semibold">주식·유가증권 보유 상세</h2>
          <p className="mb-3 text-xs text-gray-400">
            종목명 · 종목코드 · 보유자 관계 · 보유 금액 (전체 의원 기준 상위)
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-gray-500">
                  <th className="py-2 pr-2">#</th>
                  <th className="py-2 pr-3">종목/상품명</th>
                  <th className="py-2 pr-3">유형</th>
                  <th className="py-2 pr-3">관계</th>
                  <th className="py-2 pr-3">의원</th>
                  <th className="py-2 pr-3">정당</th>
                  <th className="py-2 text-right">금액</th>
                </tr>
              </thead>
              <tbody>
                {stocks.data.map((item, i) => (
                  <tr key={`${item.politician_id}-${item.description}-${i}`} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 pr-2 text-xs text-gray-400">{i + 1}</td>
                    <td className="py-2 pr-3 font-medium">{item.description}</td>
                    <td className="py-2 pr-3 text-xs text-gray-500">{item.subcategory}</td>
                    <td className="py-2 pr-3 text-xs text-gray-500">{item.relation}</td>
                    <td className="py-2 pr-3">
                      <Link to={`/politicians/${item.politician_id}`} className="text-blue-600 hover:underline">
                        {item.name}
                      </Link>
                    </td>
                    <td className="py-2 pr-3">
                      <span
                        className="inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold text-white"
                        style={{ backgroundColor: getPartyColor(item.party) }}
                      >
                        {item.party}
                      </span>
                    </td>
                    <td className="py-2 text-right font-semibold tabular-nums">{formatKrw(item.value_krw ?? 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ── Section 7: 부동산 보유 상세 (소재지별) ──── */}
      {realEstate.data && realEstate.data.length > 0 && (
        <section className="rounded-lg border border-gray-200 bg-white p-5">
          <h2 className="mb-1 text-lg font-semibold">부동산 보유 상세</h2>
          <p className="mb-3 text-xs text-gray-400">
            소재지 · 부동산 유형 · 보유자 관계 · 공시가액
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-gray-500">
                  <th className="py-2 pr-2">#</th>
                  <th className="py-2 pr-3">소재지/상세</th>
                  <th className="py-2 pr-3">유형</th>
                  <th className="py-2 pr-3">관계</th>
                  <th className="py-2 pr-3">의원</th>
                  <th className="py-2 pr-3">정당</th>
                  <th className="py-2 text-right">금액</th>
                </tr>
              </thead>
              <tbody>
                {realEstate.data.map((item, i) => (
                  <tr key={`${item.politician_id}-${item.description}-${i}`} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 pr-2 text-xs text-gray-400">{i + 1}</td>
                    <td className="py-2 pr-3 font-medium">{item.description}</td>
                    <td className="py-2 pr-3 text-xs text-gray-500">{item.subcategory}</td>
                    <td className="py-2 pr-3 text-xs text-gray-500">{item.relation}</td>
                    <td className="py-2 pr-3">
                      <Link to={`/politicians/${item.politician_id}`} className="text-blue-600 hover:underline">
                        {item.name}
                      </Link>
                    </td>
                    <td className="py-2 pr-3">
                      <span
                        className="inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold text-white"
                        style={{ backgroundColor: getPartyColor(item.party) }}
                      >
                        {item.party}
                      </span>
                    </td>
                    <td className="py-2 text-right font-semibold tabular-nums">{formatKrw(item.value_krw ?? 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ── Section 8: 가상자산 보유 상세 ──────────── */}
      {crypto.data && crypto.data.length > 0 && (
        <section className="rounded-lg border border-gray-200 bg-white p-5">
          <h2 className="mb-1 text-lg font-semibold">가상자산 보유 상세</h2>
          <p className="mb-3 text-xs text-gray-400">
            비트코인·이더리움 등 가상자산 종류별 보유 현황
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-gray-500">
                  <th className="py-2 pr-2">#</th>
                  <th className="py-2 pr-3">자산명</th>
                  <th className="py-2 pr-3">유형</th>
                  <th className="py-2 pr-3">관계</th>
                  <th className="py-2 pr-3">의원</th>
                  <th className="py-2 pr-3">정당</th>
                  <th className="py-2 text-right">금액</th>
                </tr>
              </thead>
              <tbody>
                {crypto.data.map((item, i) => (
                  <tr key={`${item.politician_id}-${item.description}-${i}`} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 pr-2 text-xs text-gray-400">{i + 1}</td>
                    <td className="py-2 pr-3 font-medium">{item.description}</td>
                    <td className="py-2 pr-3 text-xs text-gray-500">{item.subcategory}</td>
                    <td className="py-2 pr-3 text-xs text-gray-500">{item.relation}</td>
                    <td className="py-2 pr-3">
                      <Link to={`/politicians/${item.politician_id}`} className="text-blue-600 hover:underline">
                        {item.name}
                      </Link>
                    </td>
                    <td className="py-2 pr-3">
                      <span
                        className="inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold text-white"
                        style={{ backgroundColor: getPartyColor(item.party) }}
                      >
                        {item.party}
                      </span>
                    </td>
                    <td className="py-2 text-right font-semibold tabular-nums">{formatKrw(item.value_krw ?? 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* ── Section 9: 정치자금 수입 순위 ────────────── */}
      {funds.data && funds.data.length > 0 && (
        <section className="rounded-lg border border-gray-200 bg-white p-5">
          <h2 className="mb-1 text-lg font-semibold">정치자금 수입 TOP 20</h2>
          <p className="mb-3 text-xs text-gray-400">
            후원회 기준 · 수입총액 · 지출총액 · 잔액
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-gray-500">
                  <th className="py-2 pr-2">#</th>
                  <th className="py-2 pr-3">의원</th>
                  <th className="py-2 pr-3">정당</th>
                  <th className="py-2 pr-3">연도</th>
                  <th className="py-2 text-right">수입</th>
                  <th className="py-2 text-right">지출</th>
                  <th className="py-2 text-right">잔액</th>
                </tr>
              </thead>
              <tbody>
                {funds.data.map((f, i) => (
                  <tr key={`${f.politician_id}-${f.fund_year}`} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 pr-2 text-xs text-gray-400">{i + 1}</td>
                    <td className="py-2 pr-3">
                      <Link to={`/politicians/${f.politician_id}`} className="text-blue-600 hover:underline font-medium">
                        {f.name}
                      </Link>
                    </td>
                    <td className="py-2 pr-3">
                      <span
                        className="inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold text-white"
                        style={{ backgroundColor: getPartyColor(f.party) }}
                      >
                        {f.party}
                      </span>
                    </td>
                    <td className="py-2 pr-3 text-xs">{f.fund_year}</td>
                    <td className="py-2 text-right font-semibold tabular-nums text-green-700">{formatKrw(f.income_total ?? 0)}</td>
                    <td className="py-2 text-right font-semibold tabular-nums text-red-600">{formatKrw(f.expense_total ?? 0)}</td>
                    <td className="py-2 text-right font-semibold tabular-nums">
                      {formatKrw(f.balance ?? 0)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {/* Visual bar chart for fund income */}
          <div className="mt-4 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={funds.data.slice(0, 10)} margin={{ left: 50, right: 8 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-30} textAnchor="end" height={50} />
                <YAxis tickFormatter={(v: number) => formatKrw(v)} tick={{ fontSize: 10 }} />
                <Tooltip formatter={(v) => formatKrw(Number(v))} />
                <Bar dataKey="income_total" name="수입" fill="#22C55E">
                  {funds.data.slice(0, 10).map((f) => (
                    <Cell key={f.politician_id} fill={getPartyColor(f.party)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}

      {/* ── Section 10: 기업 관계 ──────────────────── */}
      {companies.data && companies.data.length > 0 && (
        <section className="rounded-lg border border-gray-200 bg-white p-5">
          <h2 className="mb-1 text-lg font-semibold">의원-기업 관계 현황</h2>
          <p className="mb-3 text-xs text-gray-400">
            주식 보유 · 임원 겸직 · 이해관계 기업 전체 목록 (종목코드 · 업종 포함)
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs text-gray-500">
                  <th className="py-2 pr-2">#</th>
                  <th className="py-2 pr-3">기업명</th>
                  <th className="py-2 pr-3">종목코드</th>
                  <th className="py-2 pr-3">업종</th>
                  <th className="py-2 pr-3">관계</th>
                  <th className="py-2 pr-3">의원</th>
                  <th className="py-2 pr-3">정당</th>
                  <th className="py-2 pr-3">기준연도</th>
                  <th className="py-2 text-right">금액</th>
                </tr>
              </thead>
              <tbody>
                {companies.data.map((c, i) => (
                  <tr key={`${c.politician_id}-${c.corp_name}-${i}`} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 pr-2 text-xs text-gray-400">{i + 1}</td>
                    <td className="py-2 pr-3 font-medium">{c.corp_name}</td>
                    <td className="py-2 pr-3 text-xs font-mono text-gray-500">{c.stock_code || "-"}</td>
                    <td className="py-2 pr-3 text-xs text-gray-500 max-w-[200px] truncate">{c.industry || "-"}</td>
                    <td className="py-2 pr-3">
                      <span className="inline-block rounded bg-orange-100 px-1.5 py-0.5 text-[10px] font-semibold text-orange-700">
                        {c.relation_type}
                      </span>
                    </td>
                    <td className="py-2 pr-3">
                      <Link to={`/politicians/${c.politician_id}`} className="text-blue-600 hover:underline">
                        {c.name}
                      </Link>
                    </td>
                    <td className="py-2 pr-3">
                      <span
                        className="inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold text-white"
                        style={{ backgroundColor: getPartyColor(c.party) }}
                      >
                        {c.party}
                      </span>
                    </td>
                    <td className="py-2 pr-3 text-xs">{c.source_year || "-"}</td>
                    <td className="py-2 text-right font-semibold tabular-nums">{c.value_krw ? formatKrw(c.value_krw) : "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
