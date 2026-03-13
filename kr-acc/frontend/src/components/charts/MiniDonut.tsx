import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

interface Segment {
  name: string;
  value: number;
  color: string;
}

interface Props {
  segments: Segment[];
  centerLabel?: string;
  centerSub?: string;
  size?: number;
}

export default function MiniDonut({
  segments,
  centerLabel,
  centerSub,
  size = 120,
}: Props) {
  return (
    <div className="relative" style={{ width: size, height: size }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={segments}
            dataKey="value"
            innerRadius="60%"
            outerRadius="90%"
            paddingAngle={2}
            strokeWidth={0}
          >
            {segments.map((s, i) => (
              <Cell key={i} fill={s.color} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      {centerLabel && (
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-lg font-bold leading-tight">{centerLabel}</span>
          {centerSub && (
            <span className="text-[10px] text-gray-400">{centerSub}</span>
          )}
        </div>
      )}
    </div>
  );
}
