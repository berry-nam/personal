interface Segment {
  label: string;
  value: number;
  color: string;
}

interface Props {
  segments: Segment[];
  height?: number;
  showLabels?: boolean;
}

export default function StackedBar({
  segments,
  height = 24,
  showLabels = true,
}: Props) {
  const total = segments.reduce((s, seg) => s + seg.value, 0);
  if (total === 0) return null;

  return (
    <div>
      <div
        className="flex overflow-hidden rounded-full"
        style={{ height }}
      >
        {segments.map((seg) => {
          const pct = (seg.value / total) * 100;
          if (pct === 0) return null;
          return (
            <div
              key={seg.label}
              className="relative transition-all"
              style={{
                width: `${pct}%`,
                backgroundColor: seg.color,
                minWidth: pct > 0 ? 2 : 0,
              }}
              title={`${seg.label}: ${seg.value} (${pct.toFixed(1)}%)`}
            />
          );
        })}
      </div>
      {showLabels && (
        <div className="mt-1.5 flex flex-wrap gap-x-3 gap-y-0.5">
          {segments.map((seg) => {
            const pct = total > 0 ? ((seg.value / total) * 100).toFixed(1) : "0";
            return (
              <span key={seg.label} className="flex items-center gap-1 text-xs text-gray-600">
                <span
                  className="inline-block h-2 w-2 rounded-full"
                  style={{ backgroundColor: seg.color }}
                />
                {seg.label} {pct}%
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
