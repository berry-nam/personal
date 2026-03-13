/** Official Korean party colors (17~22대). */

const PARTY_COLORS: Record<string, string> = {
  // 22대
  국민의힘: "#E61E2B",
  더불어민주당: "#004EA2",
  조국혁신당: "#0033A0",
  개혁신당: "#FF7210",
  진보당: "#D6001C",
  기본소득당: "#00B0B9",
  사회민주당: "#43B02A",
  // Historical (17~21대)
  새누리당: "#E61E2B",
  한나라당: "#E61E2B",
  자유한국당: "#E61E2B",
  미래통합당: "#E61E2B",
  새정치민주연합: "#004EA2",
  민주통합당: "#004EA2",
  열린우리당: "#009640",
  대통합민주신당: "#004EA2",
  통합민주당: "#004EA2",
  민주당: "#004EA2",
  정의당: "#FFCC00",
  국민의당: "#EA5504",
  바른미래당: "#00AACC",
  바른정당: "#00AACC",
  민생당: "#00C73C",
  자유선진당: "#E0007A",
  창조한국당: "#FF8C00",
  미래희망연대: "#00A0E2",
  통합진보당: "#D6001C",
  민주노동당: "#D6001C",
  새천년민주당: "#004EA2",
};

const DEFAULT_COLOR = "#9CA3AF"; // gray-400

export function getPartyColor(party: string | null | undefined): string {
  if (!party) return DEFAULT_COLOR;
  return PARTY_COLORS[party] ?? DEFAULT_COLOR;
}

export default PARTY_COLORS;
