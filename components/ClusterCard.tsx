"use client";
import { useState } from "react";
import type { Cluster, ReviewItem, Decision, DecisionMap } from "@/lib/types";
import { getCanonicalLabel, getCanonicalShortLabel, canonicalSource } from "@/lib/canonicalLabels";
import { itemKey } from "@/lib/storage";
import OverrideModal from "./OverrideModal";
import SjBadge from "./SjBadge";
import s from "./ClusterCard.module.css";

interface Props {
  cluster: Cluster;
  decisions: DecisionMap;
  onDecisions: (updates: DecisionMap) => void;
  isActive: boolean;
}

function confClass(conf: number | null, styles: typeof s) {
  if (conf === null) return styles.confNone;
  if (conf >= 0.85) return styles.confGood;
  if (conf >= 0.70) return styles.confOk;
  return styles.confBad;
}

function ItemDecisionBadge({ decision, styles }: { decision: Decision | undefined; styles: typeof s }) {
  if (!decision) return null;
  if (decision.action === "approved")
    return <span className={styles.decisionApproved}>✓ 승인</span>;
  if (decision.action === "overridden")
    return <span className={styles.decisionOverride}>✎ {decision.canonical_id.replace(/^(ifrs-full_|dart_)/, "")}</span>;
  return <span className={styles.decisionSkipped}>— 건너뜀</span>;
}

export default function ClusterCard({ cluster, decisions, onDecisions, isActive }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [overrideItem, setOverrideItem] = useState<ReviewItem | null>(null);
  const [overrideAll, setOverrideAll] = useState(false);

  const isDart = canonicalSource(cluster.canonical_id) === "dart";
  const decidedCount = cluster.items.filter((it) => decisions[itemKey(it.norm, it.sj)]).length;
  const total = cluster.items.length;
  const allDecided = decidedCount === total;

  function approveAll() {
    const updates: DecisionMap = {};
    for (const it of cluster.items) {
      updates[itemKey(it.norm, it.sj)] = {
        action: "approved",
        canonical_id: cluster.canonical_id,
        original_canonical: cluster.canonical_id,
      };
    }
    onDecisions(updates);
  }

  function skipAll() {
    const updates: DecisionMap = {};
    for (const it of cluster.items) {
      updates[itemKey(it.norm, it.sj)] = {
        action: "skipped",
        canonical_id: cluster.canonical_id,
        original_canonical: cluster.canonical_id,
      };
    }
    onDecisions(updates);
  }

  function handleOverrideAll(newCid: string, note: string) {
    const updates: DecisionMap = {};
    for (const it of cluster.items) {
      updates[itemKey(it.norm, it.sj)] = {
        action: "overridden",
        canonical_id: newCid,
        original_canonical: cluster.canonical_id,
        note,
      };
    }
    onDecisions(updates);
    setOverrideAll(false);
  }

  function handleOverrideItem(it: ReviewItem, newCid: string, note: string) {
    onDecisions({
      [itemKey(it.norm, it.sj)]: {
        action: "overridden",
        canonical_id: newCid,
        original_canonical: cluster.canonical_id,
        note,
      },
    });
    setOverrideItem(null);
  }

  const cardCls = [
    s.card,
    isActive ? s.cardActive : "",
    allDecided ? s.cardDone : "",
  ].filter(Boolean).join(" ");

  return (
    <>
      <div className={cardCls}>
        <div className={s.cardHeader}>
          <div className={s.headerRow}>
            <div className={s.headerLeft}>
              <div className={s.sourceTags}>
                <span className={isDart ? s.srcDart : s.srcIfrs}>
                  {isDart ? "DART" : "IFRS"}
                </span>
                <span className={s.canonicalShort}>
                  {getCanonicalShortLabel(cluster.canonical_id)}
                </span>
              </div>
              <p className={s.canonicalId}>{cluster.canonical_id}</p>
              <p className={s.canonicalLabel}>{getCanonicalLabel(cluster.canonical_id)}</p>
            </div>
            <div className={s.headerRight}>
              <div className={s.companyCount}>{cluster.total_cw.toLocaleString()}</div>
              <div className={s.companyLabel}>기업수</div>
            </div>
          </div>

          {total > 0 && (
            <div className={s.clusterProgress}>
              <div className={s.progressTrack}>
                <div
                  className={s.progressFill}
                  style={{ width: `${(decidedCount / total) * 100}%` }}
                />
              </div>
              <span className={s.progressLabel}>{decidedCount}/{total}</span>
            </div>
          )}
        </div>

        <div className={s.actions}>
          <button onClick={approveAll} className={s.btnApprove}>✓ 모두 승인</button>
          <button onClick={() => setOverrideAll(true)} className={s.btnOverride}>✎ 수정</button>
          <button onClick={skipAll} className={s.btnSkip}>건너뛰기</button>
          <button onClick={() => setExpanded((e) => !e)} className={s.btnExpand}>
            {expanded ? "▲" : "▼"} ({total})
          </button>
        </div>

        {expanded && (
          <div className={s.itemList}>
            {cluster.items.map((it) => {
              const dec = decisions[itemKey(it.norm, it.sj)];
              return (
                <div key={`${it.norm}||${it.sj}`} className={s.itemRow}>
                  <SjBadge sj={it.sj} />
                  <div className={s.itemInfo}>
                    <span className={s.itemName}>{it.norm}</span>
                    {it.top3.length > 1 && (
                      <div className={s.itemAlt}>
                        alt: {it.top3.slice(1).map((c) => c.replace(/^(ifrs-full_|dart_)/, "")).join(" · ")}
                      </div>
                    )}
                  </div>
                  <span className={s.itemCount}>{it.n.toLocaleString()}</span>
                  <span className={`${s.itemConf} ${confClass(it.conf, s)}`}>
                    {it.conf ? it.conf.toFixed(2) : "—"}
                  </span>
                  <ItemDecisionBadge decision={dec} styles={s} />
                  <button
                    onClick={() => setOverrideItem(it)}
                    className={s.btnItemOverride}
                    title="이 항목만 수정"
                  >
                    ✎
                  </button>
                </div>
              );
            })}
          </div>
        )}
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
          currentCanonical={overrideItem.top3[0] ?? ""}
          itemLabel={overrideItem.norm}
          onConfirm={(cid, note) => handleOverrideItem(overrideItem, cid, note)}
          onCancel={() => setOverrideItem(null)}
        />
      )}
    </>
  );
}
