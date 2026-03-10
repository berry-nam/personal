/** Official Korean party colors for the 22nd Assembly. */

const PARTY_COLORS: Record<string, string> = {
  국민의힘: "#E61E2B",
  더불어민주당: "#004EA2",
  조국혁신당: "#0033A0",
  개혁신당: "#FF7210",
  진보당: "#D6001C",
  기본소득당: "#00B0B9",
  사회민주당: "#43B02A",
};

const DEFAULT_COLOR = "#9CA3AF"; // gray-400

export function getPartyColor(party: string | null | undefined): string {
  if (!party) return DEFAULT_COLOR;
  return PARTY_COLORS[party] ?? DEFAULT_COLOR;
}

export default PARTY_COLORS;
