"use client";
import { useState } from "react";
import type { Cluster, ReviewItem, Decision, DecisionMap } from "@/lib/types";
import { getCanonicalLabel, getCanonicalShortLabel, canonicalSource } from "@/lib/canonicalLabels";
import { itemKey } from "@/lib/storage";
import OverrideModal from "./OverrideModal";
import SjBadge from "./SjBadge";
import s from "./ClusterDetail.module.css";

interface Props {
  cluster: Cluster;
  decisions: DecisionMap;
  onDecisions: (updates: DecisionMap) => void;
  onDelete: (key: string) => void;
}

function confClass(conf: number | null, styles: typeof s) {
  if (conf === null) return styles.confNone;
  if (conf >= 0.85) return styles.confGood;
  if (conf >= 0.70) return styles.confOk;
  return styles.confBad;
}

function ItemStatus({ decision, styles }: { decision: Decision | undefined; styles: typeof s }) {
  if (!decision) return null;
  if (decision.action === "approved")
    return <span className={styles.decisionApproved}>✓ 승인</span>;
  if (decision.action === "overridden")
    return <span className={styles.decisionOverride}>✎ {decision.canonical_id.replace(/^(ifrs-full_|dart_)/, "")}</span>;
  return <span className={styles.decisionSkipped}>건너뜀</span>;
}

export default function ClusterDetail({ cluster, decisions, onDecisions, onDelete }: Props) {
  const [overrideItem, setOverrideItem] = useState<ReviewItem | null>(null);
  const [overrideAll, setOverrideAll] = useState(false);
  const [itemFilter, setItemFilter] = useState<"all" | "pending" | "decided">("all");

  const isDart = canonicalSource(cluster.canonical_id) === "dart";
  const decidedCount = cluster.items.filter((it) => decisions[itemKey(it.norm, it.sj)]).length;
  const total = cluster.items.length;
  const pendingCount = total - decidedCount;

  const visibleItems = cluster.items.filter((it) => {
    const dec = decisions[itemKey(it.norm, it.sj)];
    if (itemFilter === "pending") return !dec;
    if (itemFilter === "decided") return !!dec;
    return true;
  });

  function approveAll() {
    const updates: DecisionMap = {};
    for (const it of cluster.items)
      updates[itemKey(it.norm, it.sj)] = { action: "approved", canonical_id: cluster.canonical_id, original_canonical: cluster.canonical_id };
    onDecisions(updates);
  }

  function skipAll() {
    const updates: DecisionMap = {};
    for (const it of cluster.items)
      updates[itemKey(it.norm, it.sj)] = { action: "skipped", canonical_id: cluster.canonical_id, original_canonical: cluster.canonical_id };
    onDecisions(updates);
  }

  function approveItem(it: ReviewItem) {
    onDecisions({ [itemKey(it.norm, it.sj)]: { action: "approved", canonical_id: cluster.canonical_id, original_canonical: cluster.canonical_id } });
  }

  function handleOverrideAll(newCid: string, note: string) {
    const updates: DecisionMap = {};
    for (const it of cluster.items)
      updates[itemKey(it.norm, it.sj)] = { action: "overridden", canonical_id: newCid, original_canonical: cluster.canonical_id, note };
    onDecisions(updates);
    setOverrideAll(false);
  }

  function handleOverrideItem(it: ReviewItem, newCid: string, note: string) {
    onDecisions({ [itemKey(it.norm, it.sj)]: { action: "overridden", canonical_id: newCid, original_canonical: cluster.canonical_id, note } });
    setOverrideItem(null);
  }

  return (
    <>
      <div className={s.panel}>
        {/* Sticky header */}
        <div className={s.detailHeader}>
          <div className={s.titleRow}>
            <div className={s.titleLeft}>
              <div className={s.sourceTags}>
                <span className={isDart ? s.srcDart : s.srcIfrs}>{isDart ? "DART" : "IFRS"}</span>
                <span className={s.canonicalShort}>{getCanonicalShortLabel(cluster.canonical_id)}</span>
              </div>
              <p className={s.canonicalId}>{cluster.canonical_id}</p>
              <p className={s.canonicalLabel}>{getCanonicalLabel(cluster.canonical_id)}</p>
              <p className={s.mappingHint}>↓ 아래 계정들의 분류 목적지</p>
            </div>
            <div className={s.titleRight}>
              <div className={s.companyCount}>{cluster.total_cw.toLocaleString()}</div>
              <div className={s.companyLabel}>기업</div>
              <div className={s.progressLabel}>{decidedCount}/{total} 완료</div>
            </div>
          </div>
          <div className={s.headerActions}>
            <button onClick={skipAll} className={s.btnSkip}>건너뛰기</button>
            <button onClick={() => setOverrideAll(true)} className={s.btnOverride}>✎ 수정</button>
            <button onClick={approveAll} className={s.btnApprove}>✓ 모두 승인</button>
          </div>
        </div>

        {/* Item filter */}
        <div className={s.itemFilter}>
          {([
            ["all",     "전체",  total],
            ["pending", "미결",  pendingCount],
            ["decided", "완료",  decidedCount],
          ] as const).map(([v, label, count]) => (
            <button
              key={v}
              onClick={() => setItemFilter(v)}
              className={itemFilter === v ? `${s.filterBtn} ${s.filterBtnActive}` : s.filterBtn}
            >
              {label}
              <span className={s.filterCount}>{count}</span>
            </button>
          ))}
        </div>

        {/* Column headers */}
        <div className={s.tableHeader}>
          <span>구분</span>
          <span>계정명</span>
          <span className={s.alignRight}>기업수</span>
          <span className={s.alignRight}>유사도</span>
          <span>결정</span>
          <span />
        </div>

        {/* Items */}
        {visibleItems.map((it) => {
          const dec = decisions[itemKey(it.norm, it.sj)];
          return (
            <div key={`${it.norm}||${it.sj}`} className={s.itemRow}>
              <span><SjBadge sj={it.sj} /></span>
              <div className={s.itemNameWrap}>
                <span className={s.itemName}>{it.norm}</span>
                {it.top3.length > 1 && (
                  <span className={s.itemAlt}>
                    {it.top3.slice(1).map((c) => c.replace(/^(ifrs-full_|dart_)/, "")).join(" · ")}
                  </span>
                )}
              </div>
              <span className={`${s.colN} ${s.mono}`}>{it.n.toLocaleString()}</span>
              <span className={`${s.colConf} ${s.mono} ${confClass(it.conf, s)}`}>
                {it.conf !== null ? it.conf.toFixed(2) : "—"}
              </span>
              <span className={s.colDecision}><ItemStatus decision={dec} styles={s} /></span>
              <span className={s.colActions}>
                {dec ? (
                  <button onClick={() => onDelete(itemKey(it.norm, it.sj))} className={s.btnItemUndo} title="결정 취소">↩</button>
                ) : (
                  <button onClick={() => approveItem(it)} className={s.btnItemApprove} title="승인">✓</button>
                )}
                <button onClick={() => setOverrideItem(it)} className={s.btnItemOverride} title="수정">✎</button>
              </span>
            </div>
          );
        })}
      </div>

      {overrideAll && (
        <OverrideModal
          currentCanonical={cluster.canonical_id}
          itemLabel={`클러스터 전체 (${total}개 항목)`}
          onConfirm={handleOverrideAll}
          onCancel={() => setOverrideAll(false)}
        />
      )}
      {overrideItem && (
        <OverrideModal
          currentCanonical={cluster.canonical_id}
          itemLabel={overrideItem.norm}
          onConfirm={(cid, note) => handleOverrideItem(overrideItem, cid, note)}
          onCancel={() => setOverrideItem(null)}
        />
      )}
    </>
  );
}
