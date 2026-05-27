import type { DecisionMap, Decision } from "./types";

const LS_KEY = "taxonomy_decisions_v1";

export function itemKey(norm: string, sj: string) {
  return `${norm}||${sj}`;
}

// localStorage helpers (used as local cache + offline fallback)
function lsLoad(): DecisionMap {
  if (typeof window === "undefined") return {};
  try {
    return JSON.parse(localStorage.getItem(LS_KEY) ?? "{}");
  } catch {
    return {};
  }
}

function lsSave(map: DecisionMap) {
  if (typeof window === "undefined") return;
  localStorage.setItem(LS_KEY, JSON.stringify(map));
}

// Server API calls
export async function loadDecisions(): Promise<DecisionMap> {
  try {
    const res = await fetch("/api/decisions");
    const { decisions } = (await res.json()) as { decisions: DecisionMap };
    // Merge with any local-only changes in case of prior API failures
    const local = lsLoad();
    const merged = { ...local, ...decisions };
    lsSave(merged);
    return merged;
  } catch {
    return lsLoad();
  }
}

export async function deleteDecisions(keys: string[]): Promise<DecisionMap> {
  const local = lsLoad();
  for (const k of keys) delete local[k];
  lsSave(local);
  try {
    const res = await fetch("/api/decisions", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keys }),
    });
    const { decisions } = (await res.json()) as { decisions: DecisionMap };
    lsSave(decisions);
    return decisions;
  } catch {
    return local;
  }
}

export async function saveDecisions(updates: DecisionMap): Promise<DecisionMap> {
  // Optimistic local save
  const local = lsLoad();
  const next = { ...local, ...updates };
  lsSave(next);

  try {
    const res = await fetch("/api/decisions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ updates }),
    });
    const { decisions } = (await res.json()) as { decisions: DecisionMap };
    lsSave(decisions);
    return decisions;
  } catch {
    return next;
  }
}

export function exportCsv(decisions: DecisionMap): void {
  const rows: string[] = [
    "account_nm_norm,sj_div,canonical_id,action,original_canonical,note",
  ];
  for (const [key, d] of Object.entries(decisions)) {
    const [norm, sj] = key.split("||");
    const row = [norm, sj, d.canonical_id, d.action, d.original_canonical, d.note ?? ""]
      .map((v) => `"${String(v).replace(/"/g, '""')}"`)
      .join(",");
    rows.push(row);
  }
  const blob = new Blob([rows.join("\n")], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `taxonomy_decisions_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
