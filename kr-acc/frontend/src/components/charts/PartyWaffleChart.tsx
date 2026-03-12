import { useState } from "react";
import { useNavigate } from "react-router";
import type { PartySeat } from "@/types/api";

const COLS = 31;
const TOTAL_CELLS = 310;

interface Props {
  data: PartySeat[];
}

export default function PartyWaffleChart({ data }: Props) {
  const navigate = useNavigate();
  const [hovered, setHovered] = useState<string | null>(null);

  const totalSeats = data.reduce((sum, d) => sum + d.count, 0);

  // Build flat array of cells colored by party
  const cells: { party: string; color: string }[] = [];
  for (const seat of data) {
    for (let i = 0; i < seat.count; i++) {
      cells.push({ party: seat.party, color: seat.color_hex });
    }
  }
  // Fill remaining with empty
  while (cells.length < TOTAL_CELLS) {
    cells.push({ party: "", color: "transparent" });
  }

  const rows = Math.ceil(TOTAL_CELLS / COLS);

  return (
    <div>
      <div className="flex flex-wrap gap-[3px]">
        {cells.map((cell, i) => (
          <div
            key={i}
            className={`h-[10px] w-[10px] rounded-[2px] transition-transform sm:h-3 sm:w-3 ${
              cell.party
                ? "cursor-pointer hover:scale-125"
                : ""
            } ${hovered && hovered !== cell.party ? "opacity-30" : ""}`}
            style={{
              backgroundColor: cell.party ? cell.color : "#E5E7EB",
            }}
            onMouseEnter={() => cell.party && setHovered(cell.party)}
            onMouseLeave={() => setHovered(null)}
            onClick={() =>
              cell.party &&
              navigate(
                `/politicians?party=${encodeURIComponent(cell.party)}`,
              )
            }
          />
        ))}
      </div>

      {/* Legend */}
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1.5">
        {data.map((seat) => (
          <button
            key={seat.party}
            className={`flex items-center gap-1.5 text-xs transition-opacity ${
              hovered && hovered !== seat.party ? "opacity-40" : ""
            }`}
            onMouseEnter={() => setHovered(seat.party)}
            onMouseLeave={() => setHovered(null)}
            onClick={() =>
              navigate(
                `/politicians?party=${encodeURIComponent(seat.party)}`,
              )
            }
          >
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: seat.color_hex }}
            />
            <span className="font-medium text-gray-700">{seat.party}</span>
            <span className="text-gray-400">{seat.count}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
