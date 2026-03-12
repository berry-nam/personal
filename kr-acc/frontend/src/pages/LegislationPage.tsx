import { lazy, Suspense } from "react";
import { useSearchParams } from "react-router";
import useDocumentTitle from "@/lib/useDocumentTitle";
import { useBillPipeline } from "@/api/queries";
import { formatNumber } from "@/lib/format";
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
  { key: "bills", label: "법안" },
  { key: "votes", label: "표결" },
] as const;

type Tab = (typeof TABS)[number]["key"];

export default function LegislationPage() {
  useDocumentTitle("입법활동");
  const [searchParams, setSearchParams] = useSearchParams();
  const tab = (searchParams.get("tab") as Tab) ?? "bills";
  const pipeline = useBillPipeline();

  function switchTab(t: Tab) {
    setSearchParams(t === "bills" ? {} : { tab: t });
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold">입법활동</h1>
        {/* Pill toggle */}
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

      {/* Show pipeline chart above bills tab */}
      {tab === "bills" && pipeline.data && pipeline.data.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h2 className="mb-2 text-sm font-medium text-gray-500">
            법안 처리 현황
          </h2>
          <div className="h-40">
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
                <Tooltip formatter={(v) => formatNumber(Number(v))} />
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
      )}

      <Suspense
        fallback={
          <div className="flex h-32 items-center justify-center">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-gray-900" />
          </div>
        }
      >
        {tab === "bills" ? <BillList /> : <VoteList />}
      </Suspense>
    </div>
  );
}
