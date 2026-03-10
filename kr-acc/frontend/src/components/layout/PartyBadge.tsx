import { getPartyColor } from "@/lib/partyColors";

interface PartyBadgeProps {
  party: string | null | undefined;
}

export default function PartyBadge({ party }: PartyBadgeProps) {
  if (!party) return <span className="text-sm text-gray-400">무소속</span>;

  const color = getPartyColor(party);
  return (
    <span className="inline-flex items-center gap-1.5 text-sm">
      <span
        className="inline-block h-2.5 w-2.5 rounded-full"
        style={{ backgroundColor: color }}
      />
      {party}
    </span>
  );
}
