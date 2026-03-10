/** Formatting helpers. */

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  return dateStr.replace(/(\d{4})-(\d{2})-(\d{2})/, "$1.$2.$3");
}

export function formatNumber(n: number | null | undefined): string {
  if (n == null) return "—";
  return n.toLocaleString("ko-KR");
}

export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen - 1) + "…";
}
