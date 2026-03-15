const RATING_LABELS: Record<number, { label: string; color: string }> = {
  5: { label: "완벽", color: "bg-emerald-600 text-white" },
  4: { label: "우수", color: "bg-blue-600 text-white" },
  3: { label: "보통", color: "bg-yellow-500 text-white" },
  2: { label: "약함", color: "bg-orange-500 text-white" },
  1: { label: "무관", color: "bg-red-600 text-white" },
};

interface Props {
  value: number | null;
  onChange: (rating: number) => void;
}

export default function RatingSelector({ value, onChange }: Props) {
  return (
    <div className="flex gap-1">
      {[5, 4, 3, 2, 1].map((r) => {
        const entry = RATING_LABELS[r]!;
        const { label, color } = entry;
        const active = value === r;
        return (
          <button
            key={r}
            onClick={() => onChange(r)}
            className={`rounded px-2.5 py-1 text-xs font-medium transition-all ${
              active
                ? `${color} ring-2 ring-white ring-offset-2 ring-offset-gray-900`
                : "bg-gray-700 text-gray-400 hover:bg-gray-600 hover:text-gray-200"
            }`}
          >
            {r} {label}
          </button>
        );
      })}
    </div>
  );
}
