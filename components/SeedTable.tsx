"use client";
import { useState, useMemo } from "react";
import type { SeedEntry, DecisionMap } from "@/lib/types";
import { getCanonicalLabel, getCanonicalShortLabel } from "@/lib/canonicalLabels";
import { itemKey } from "@/lib/storage";
import SjBadge from "./SjBadge";
import OverrideModal from "./OverrideModal";
import s from "./SeedTable.module.css";

interface Props {
  seeds: SeedEntry[];
  decisions: DecisionMap;
  onDecisions: (updates: DecisionMap) => void;
}

const PAGE_SIZE = 50;

type StatusFilter = "all" | "unreviewed" | "confirmed" | "overridden";

export default function SeedTable({ seeds, decisions, onDecisions }: Props) {
  const [query, setQuery] = useState("");
  const [filterSj, setFilterSj] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<StatusFilter>("all");
  const [page, setPage] = useState(0);
  const [overrideTarget, setOverrideTarget] = useState<SeedEntry | null>(null);

  function seedKey(e: SeedEntry) {
    return `seed||${itemKey(e.norm, e.sj)}`;
  }

  const filtered = useMemo(() => {
    return seeds.filter((e) => {
      if (filterSj !== "all" && e.sj !== filterSj) return false;
      if (query) {
        const q = query.toLowerCase();
        if (!e.norm.includes(q) && !e.canonical_id.toLowerCase().includes(q)) return false;
      }
      const dec = decisions[seedKey(e)];
      if (filterStatus === "unreviewed") return !dec;
      if (filterStatus === "confirmed") return dec?.action === "approved";
      if (filterStatus === "overridden") return dec?.action === "overridden" && dec.canonical_id !== e.canonical_id;
      return true;
    });
  }, [seeds, decisions, query, filterSj, filterStatus]);

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE);
  const pageItems = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  function handlePageChange(p: number) {
    setPage(Math.max(0, Math.min(p, totalPages - 1)));
  }

  function resetPage() { setPage(0); }

  const confirmed  = seeds.filter((e) => decisions[seedKey(e)]?.action === "approved").length;
  const overridden = seeds.filter((e) => { const dec = decisions[seedKey(e)]; return dec?.action === "overridden" && dec.canonical_id !== e.canonical_id; }).length;
  const unreviewed = seeds.length - confirmed - overridden;

  return (
    <>
      {overrideTarget && (
        <OverrideModal
          currentCanonical={overrideTarget.canonical_id}
          itemLabel={overrideTarget.norm}
          onConfirm={(cid, note) => {
            onDecisions({
              [seedKey(overrideTarget)]: {
                action: "overridden",
                canonical_id: cid,
                original_canonical: overrideTarget.canonical_id,
                note,
              },
            });
            setOverrideTarget(null);
          }}
          onCancel={() => setOverrideTarget(null)}
        />
      )}

      <div className={s.panel}>
        <div className={s.toolbar}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <p className={s.toolbarTitle}>Seed 사전 — 사전 정의 매핑 ({seeds.length}개)</p>
            <p className={s.toolbarSub}>K-IFRS/K-GAAP 회계 기준에 기반한 계정명 → Canonical ID 매핑. 직접 확인 · 수정하세요.</p>
          </div>

          <div className={s.statsBar}>
            <span className={s.statChip}><span className={`${s.dot} ${s.dotUnreviewed}`} />{unreviewed} 미검토</span>
            <span className={s.statChip}><span className={`${s.dot} ${s.dotConfirmed}`} />{confirmed} 확인</span>
            <span className={s.statChip}><span className={`${s.dot} ${s.dotOverridden}`} />{overridden} 수정됨</span>
          </div>
        </div>

        <div className={s.toolbar} style={{ paddingTop: 0, paddingBottom: "var(--cd-space-inset-base)" }}>
          <input
            type="text"
            value={query}
            onChange={(e) => { setQuery(e.target.value); resetPage(); }}
            placeholder="계정명 또는 canonical ID 검색…"
            className={s.searchInput}
          />

          <div className={s.filterGroup}>
            {(["all", "BS", "IS", "CFS", "CIS"] as const).map((v) => (
              <button
                key={v}
                onClick={() => { setFilterSj(v); resetPage(); }}
                className={filterSj === v ? `${s.filterBtn} ${s.filterBtnActive}` : s.filterBtn}
              >
                {v === "all" ? "전체" : v}
              </button>
            ))}
          </div>

          <div className={s.filterGroup}>
            {([
              ["all", "전체"],
              ["unreviewed", "미검토"],
              ["confirmed", "확인됨"],
              ["overridden", "수정됨"],
            ] as [StatusFilter, string][]).map(([v, label]) => (
              <button
                key={v}
                onClick={() => { setFilterStatus(v); resetPage(); }}
                className={filterStatus === v ? `${s.filterBtn} ${s.filterBtnActive}` : s.filterBtn}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className={s.tableWrap}>
          <table className={s.table}>
            <thead className={s.thead}>
              <tr>
                <th>계정명</th>
                <th>재무</th>
                <th>Canonical ID</th>
                <th>설명</th>
                <th>상태</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {pageItems.length === 0 && (
                <tr><td colSpan={6} className={s.empty}>결과 없음</td></tr>
              )}
              {pageItems.map((e) => {
                const dec = decisions[seedKey(e)];
                const isOverridden = dec?.action === "overridden" && dec.canonical_id !== e.canonical_id;
                const isConfirmed = dec?.action === "approved";
                const displayCid = isOverridden ? dec.canonical_id : e.canonical_id;
                return (
                  <tr key={`${e.norm}||${e.sj}`} className={s.row}>
                    <td className={s.normCell}>{e.norm}</td>
                    <td><SjBadge sj={e.sj} /></td>
                    <td className={s.canonicalCell}>
                      {isOverridden
                        ? <><span style={{ textDecoration: "line-through", color: "var(--cd-text-default-weakest)", marginRight: 4 }}>{e.canonical_id.replace(/^(ifrs-full_|dart_)/, "")}</span><span style={{ color: "var(--cd-text-warning-normal)" }}>{dec.canonical_id.replace(/^(ifrs-full_|dart_)/, "")}</span></>
                        : e.canonical_id.replace(/^(ifrs-full_|dart_)/, "")
                      }
                    </td>
                    <td className={s.labelCell}>{getCanonicalLabel(displayCid)}</td>
                    <td className={s.decisionCell}>
                      {isConfirmed  && <span className={s.chipConfirmed}>✓ 확인됨</span>}
                      {isOverridden && <span className={s.chipOverridden}>✎ 수정됨</span>}
                      {!dec         && <span className={s.chipUnreviewed}>미검토</span>}
                    </td>
                    <td className={s.actionsCell}>
                      {!isConfirmed && (
                        <button
                          className={s.btnConfirm}
                          onClick={() =>
                            onDecisions({
                              [seedKey(e)]: { action: "approved", canonical_id: e.canonical_id, original_canonical: e.canonical_id },
                            })
                          }
                        >
                          ✓ 확인
                        </button>
                      )}
                      <button className={s.btnOverride} onClick={() => setOverrideTarget(e)}>
                        ✎ 수정
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className={s.pagination}>
            <span>{filtered.length}개 중 {page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, filtered.length)}</span>
            <div className={s.pageButtons}>
              <button className={s.pageBtn} onClick={() => handlePageChange(page - 1)} disabled={page === 0}>←</button>
              {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                const p = totalPages <= 7 ? i : Math.max(0, Math.min(page - 3, totalPages - 7)) + i;
                return (
                  <button
                    key={p}
                    onClick={() => handlePageChange(p)}
                    className={p === page ? `${s.pageBtn} ${s.pageBtnActive}` : s.pageBtn}
                  >
                    {p + 1}
                  </button>
                );
              })}
              <button className={s.pageBtn} onClick={() => handlePageChange(page + 1)} disabled={page >= totalPages - 1}>→</button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
