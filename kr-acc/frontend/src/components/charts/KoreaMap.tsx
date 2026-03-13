import { useState } from "react";
import { useNavigate } from "react-router";
import type { RegionSeat } from "@/types/api";

// Simplified SVG paths for Korean regions (approximate boundaries)
const REGIONS: {
  id: string;
  name: string;
  path: string;
  labelX: number;
  labelY: number;
}[] = [
  { id: "서울", name: "서울", path: "M165,155 l20,-5 l12,8 l5,18 l-10,15 l-20,2 l-12,-15z", labelX: 172, labelY: 172 },
  { id: "인천", name: "인천", path: "M138,150 l25,-5 l5,15 l-5,22 l-20,3 l-10,-20z", labelX: 147, labelY: 170 },
  { id: "경기", name: "경기", path: "M130,115 l55,-15 l25,25 l10,35 l-5,35 l-30,15 l-20,-5 l-25,10 l-15,-25 l5,-30 l-10,-20z", labelX: 165, labelY: 145 },
  { id: "강원", name: "강원", path: "M210,100 l55,-10 l30,30 l-5,55 l-30,25 l-25,-10 l-20,-30 l-15,-35z", labelX: 245, labelY: 145 },
  { id: "충북", name: "충북", path: "M175,195 l30,-5 l25,15 l5,30 l-20,20 l-30,-5 l-15,-25z", labelX: 200, labelY: 225 },
  { id: "충남", name: "충남", path: "M110,200 l40,-10 l20,15 l10,30 l-15,25 l-35,5 l-25,-25z", labelX: 140, labelY: 235 },
  { id: "대전", name: "대전", path: "M160,250 l18,-3 l8,12 l-5,15 l-18,3 l-8,-12z", labelX: 168, labelY: 262 },
  { id: "세종", name: "세종", path: "M148,235 l15,-3 l5,10 l-8,10 l-12,-5z", labelX: 153, labelY: 245 },
  { id: "전북", name: "전북", path: "M100,275 l55,-10 l15,25 l-5,35 l-45,10 l-25,-25z", labelX: 135, labelY: 305 },
  { id: "전남", name: "전남", path: "M75,330 l50,-10 l30,10 l10,40 l-20,30 l-45,5 l-30,-30z", labelX: 115, labelY: 365 },
  { id: "광주", name: "광주", path: "M105,330 l15,-3 l8,12 l-5,15 l-15,2 l-8,-12z", labelX: 112, labelY: 342 },
  { id: "경북", name: "경북", path: "M220,195 l50,-15 l25,30 l5,50 l-25,25 l-40,5 l-20,-35z", labelX: 260, labelY: 245 },
  { id: "대구", name: "대구", path: "M240,270 l18,-3 l8,12 l-5,15 l-18,3 l-8,-12z", labelX: 248, labelY: 282 },
  { id: "경남", name: "경남", path: "M180,290 l45,-5 l25,25 l-5,40 l-40,10 l-30,-25z", labelX: 215, labelY: 325 },
  { id: "울산", name: "울산", path: "M270,275 l18,-5 l10,15 l-5,18 l-18,3 l-10,-15z", labelX: 278, labelY: 290 },
  { id: "부산", name: "부산", path: "M255,320 l20,-5 l12,15 l-8,18 l-20,2 l-10,-15z", labelX: 265, labelY: 335 },
  { id: "제주", name: "제주", path: "M95,430 l45,-5 l10,15 l-10,18 l-40,5 l-12,-18z", labelX: 118, labelY: 445 },
];

interface Props {
  data: RegionSeat[];
}

export default function KoreaMap({ data }: Props) {
  const navigate = useNavigate();
  const [hovered, setHovered] = useState<string | null>(null);

  const regionMap = new Map(data.map((d) => [d.region, d]));
  const maxTotal = Math.max(...data.filter((d) => d.region !== "비례대표").map((d) => d.total), 1);

  // Find dominant party for coloring
  function getDominantParty(region: string): { party: string; color: string } {
    const r = regionMap.get(region);
    if (!r || !r.parties) return { party: "", color: "#E5E7EB" };
    const entries = Object.entries(r.parties);
    if (entries.length === 0) return { party: "", color: "#E5E7EB" };
    entries.sort((a, b) => b[1] - a[1]);
    const party = entries[0][0];
    const COLORS: Record<string, string> = {
      "국민의힘": "#E61E2B",
      "더불어민주당": "#004EA2",
      "조국혁신당": "#0033A0",
      "개혁신당": "#FF7210",
    };
    return { party, color: COLORS[party] || "#6B7280" };
  }

  const hoveredData = hovered ? regionMap.get(hovered) : null;

  return (
    <div className="relative">
      <svg viewBox="60 70 260 420" className="w-full max-w-md mx-auto">
        {REGIONS.map((r) => {
          const regionData = regionMap.get(r.id);
          const total = regionData?.total ?? 0;
          const { color } = getDominantParty(r.id);
          const opacity = total > 0 ? 0.4 + (total / maxTotal) * 0.5 : 0.15;

          return (
            <g
              key={r.id}
              className="cursor-pointer transition-all"
              onMouseEnter={() => setHovered(r.id)}
              onMouseLeave={() => setHovered(null)}
              onClick={() =>
                navigate(`/politicians?region=${encodeURIComponent(r.id)}`)
              }
            >
              <path
                d={r.path}
                fill={color}
                fillOpacity={hovered === r.id ? 0.9 : opacity}
                stroke="#fff"
                strokeWidth={hovered === r.id ? 2 : 1}
                className="transition-all"
              />
              <text
                x={r.labelX}
                y={r.labelY}
                textAnchor="middle"
                dominantBaseline="central"
                fontSize={total > 20 ? 9 : 7}
                fontWeight={hovered === r.id ? 700 : 500}
                fill={hovered === r.id ? "#111" : "#374151"}
                className="pointer-events-none select-none"
              >
                {r.name}
              </text>
              {total > 0 && (
                <text
                  x={r.labelX}
                  y={r.labelY + 11}
                  textAnchor="middle"
                  fontSize={7}
                  fill="#6B7280"
                  className="pointer-events-none select-none"
                >
                  {total}명
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* Tooltip */}
      {hoveredData && (
        <div className="absolute top-2 right-2 rounded-lg border border-gray-200 bg-white p-3 shadow-lg text-sm">
          <p className="font-bold">{hovered}</p>
          <p className="text-gray-500 text-xs">{hoveredData.total}명</p>
          <div className="mt-1.5 space-y-0.5">
            {Object.entries(hoveredData.parties)
              .sort((a, b) => b[1] - a[1])
              .slice(0, 5)
              .map(([party, count]) => (
                <div key={party} className="flex justify-between gap-4 text-xs">
                  <span className="text-gray-600">{party}</span>
                  <span className="font-medium">{count}</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
