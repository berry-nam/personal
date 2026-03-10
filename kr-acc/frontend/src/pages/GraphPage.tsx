import { useState } from "react";
import { useCoSponsorshipGraph, useParties } from "@/api/queries";
import ForceGraph from "@/components/graph/ForceGraph";

export default function GraphPage() {
  const [party, setParty] = useState<string | undefined>();
  const [minWeight, setMinWeight] = useState(5);

  const { data, isLoading } = useCoSponsorshipGraph({
    party,
    min_weight: minWeight,
    limit: 500,
  });
  const parties = useParties();

  return (
    <div>
      <h1 className="text-2xl font-bold">공동발의 네트워크</h1>
      <p className="mt-1 text-sm text-gray-500">
        의원 간 공동발의 관계를 시각화합니다. 선의 굵기는 공동발의 법안 수를
        나타냅니다.
      </p>

      {/* Controls */}
      <div className="mt-4 flex flex-wrap items-center gap-3">
        <div className="flex flex-wrap gap-1">
          <button
            onClick={() => setParty(undefined)}
            className={`rounded-full px-3 py-1 text-xs ${
              !party
                ? "bg-gray-900 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            전체
          </button>
          {parties.data?.map((p) => (
            <button
              key={p.id}
              onClick={() => setParty(p.name)}
              className={`rounded-full px-3 py-1 text-xs ${
                party === p.name
                  ? "bg-gray-900 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-gray-200"
              }`}
            >
              {p.name}
            </button>
          ))}
        </div>
        <label className="flex items-center gap-2 text-sm text-gray-600">
          최소 공동발의
          <input
            type="range"
            min={1}
            max={20}
            value={minWeight}
            onChange={(e) => setMinWeight(Number(e.target.value))}
            className="w-24"
          />
          <span className="w-6 text-center font-mono">{minWeight}</span>
        </label>
      </div>

      {/* Graph */}
      <div className="mt-4 overflow-hidden rounded-lg border border-gray-200 bg-white">
        {isLoading ? (
          <div className="flex h-[600px] items-center justify-center text-gray-500">
            불러오는 중...
          </div>
        ) : data && data.nodes.length > 0 ? (
          <ForceGraph data={data} width={1200} height={600} />
        ) : (
          <div className="flex h-[600px] items-center justify-center text-gray-400">
            표시할 데이터가 없습니다. 최소 공동발의 수를 낮춰보세요.
          </div>
        )}
      </div>

      {data && (
        <p className="mt-2 text-xs text-gray-400">
          노드 {data.nodes.length}개, 엣지 {data.edges.length}개
        </p>
      )}
    </div>
  );
}
