"use client";
import { useEffect, useState, useCallback, useRef } from "react";
import type { ReviewData, DecisionMap, ReviewItem, SeedsData } from "@/lib/types";
import { loadDecisions, saveDecisions, exportCsv, itemKey } from "@/lib/storage";
import { getCanonicalLabel, getCanonicalShortLabel } from "@/lib/canonicalLabels";
import ClusterCard from "@/components/ClusterCard";
import Onboarding from "@/components/Onboarding";
import OverrideModal from "@/components/OverrideModal";
import SjBadge from "@/components/SjBadge";
import SeedTable from "@/components/SeedTable";
import s from "./page.module.css";

export default function ReviewPage() {
  const [data, setData] = useState<ReviewData | null>(null);
  const [seedsData, setSeedsData] = useState<SeedsData | null>(null);
  const [decisions, setDecisions] = useState<DecisionMap>({});
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [activeIdx, setActiveIdx] = useState(0);
  const [filterSj, setFilterSj] = useState<Set<string>>(new Set(["BS", "IS", "CFS", "CIS"]));
  const [filterDone, setFilterDone] = useState<"all" | "pending" | "done">("all");
  const [tab, setTab] = useState<"clusters" | "unresolved" | "seeds">("clusters");
  const [unresolvedOverride, setUnresolvedOverride] = useState<ReviewItem | null>(null);
  const [saving, setSaving] = useState(false);
  const activeCardRef = useRef<HTMLDivElement>(null);

  // Load data + decisions from server
  useEffect(() => {
    fetch("/data/review_data.json")
      .then((r) => r.json())
      .then((d: ReviewData) => setData(d));

    fetch("/data/seeds.json")
      .then((r) => r.json())
      .then((d: SeedsData) => setSeedsData(d));

    loadDecisions().then(setDecisions);

    const seen = localStorage.getItem("taxonomy_onboarding_seen");
    if (!seen) setShowOnboarding(true);
  }, []);

  async function handleDecisions(updates: DecisionMap) {
    // Optimistic update
    setDecisions((prev) => ({ ...prev, ...updates }));
    setSaving(true);
    const next = await saveDecisions(updates);
    setDecisions(next);
    setSaving(false);
  }

  function dismissOnboarding() {
    localStorage.setItem("taxonomy_onboarding_seen", "1");
    setShowOnboarding(false);
  }

  // Filtered clusters
  const filteredClusters = (data?.clusters ?? []).filter((c) => {
    const hasSj = c.items.some((it) => filterSj.has(it.sj));
    if (!hasSj) return false;
    if (filterDone === "pending") {
      return c.items.some((it) => !decisions[itemKey(it.norm, it.sj)]);
    }
    if (filterDone === "done") {
      return c.items.every((it) => !!decisions[itemKey(it.norm, it.sj)]);
    }
    return true;
  });

  // Keyboard nav
  const handleKey = useCallback(
    (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      if (tab !== "clusters" || filteredClusters.length === 0) return;
      const cluster = filteredClusters[activeIdx];
      if (!cluster) return;
      if (e.key === "a" || e.key === "A") {
        const updates: DecisionMap = {};
        for (const it of cluster.items) {
          updates[itemKey(it.norm, it.sj)] = {
            action: "approved",
            canonical_id: cluster.canonical_id,
            original_canonical: cluster.canonical_id,
          };
        }
        handleDecisions(updates);
        setActiveIdx((i) => Math.min(i + 1, filteredClusters.length - 1));
      } else if (e.key === "s" || e.key === "S") {
        const updates: DecisionMap = {};
        for (const it of cluster.items) {
          updates[itemKey(it.norm, it.sj)] = {
            action: "skipped",
            canonical_id: cluster.canonical_id,
            original_canonical: cluster.canonical_id,
          };
        }
        handleDecisions(updates);
        setActiveIdx((i) => Math.min(i + 1, filteredClusters.length - 1));
      } else if (e.key === "ArrowDown" || e.key === "j") {
        setActiveIdx((i) => Math.min(i + 1, filteredClusters.length - 1));
      } else if (e.key === "ArrowUp" || e.key === "k") {
        setActiveIdx((i) => Math.max(i - 1, 0));
      }
    },
    [tab, filteredClusters, activeIdx]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [handleKey]);

  useEffect(() => {
    activeCardRef.current?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [activeIdx]);

  if (!data) {
    return <div className={s.loading}>데이터 로딩 중…</div>;
  }

  // Progress stats
  const totalItems = data.stats.flagged + data.stats.needs_review;
  const decidedItems = Object.keys(decisions).length;
  const approvedItems = Object.values(decisions).filter((d) => d.action === "approved").length;
  const clustersDone = (data?.clusters ?? []).filter((c) =>
    c.items.every((it) => !!decisions[itemKey(it.norm, it.sj)])
  ).length;

  return (
    <>
      {showOnboarding && <Onboarding onDone={dismissOnboarding} />}
      {unresolvedOverride && (
        <OverrideModal
          currentCanonical=""
          itemLabel={unresolvedOverride.norm}
          onConfirm={(cid, note) => {
            handleDecisions({
              [itemKey(unresolvedOverride.norm, unresolvedOverride.sj)]: {
                action: "overridden",
                canonical_id: cid,
                original_canonical: "",
                note,
              },
            });
            setUnresolvedOverride(null);
          }}
          onCancel={() => setUnresolvedOverride(null)}
        />
      )}

      <header className={s.header}>
        <div className={s.headerInner}>
          <div className={s.headerTitleGroup}>
            <h1 className={s.headerTitle}>재무계정 분류 검토</h1>
            <p className={s.headerSubtitle}>Korean DART → IFRS Canonical Mapping</p>
          </div>

          <div className={s.headerProgress}>
            <div className={s.progressStat}>
              <div className={s.progressStatNum}>
                {clustersDone}<span>/{data.stats.clusters}</span>
              </div>
              <div className={s.progressStatLabel}>클러스터</div>
            </div>
            <div className={s.progressBar}>
              <div
                className={s.progressFill}
                style={{ width: `${totalItems > 0 ? (decidedItems / totalItems) * 100 : 0}%` }}
              />
            </div>
            <div className={s.progressStat}>
              <div className={s.progressStatNum}>{approvedItems.toLocaleString()}</div>
              <div className={s.progressStatLabel}>승인됨</div>
            </div>
          </div>

          <div className={s.headerActions}>
            <div className={saving ? s.savingDotPending : s.savingDot} title={saving ? "저장 중…" : "저장됨"} />
            <button onClick={() => exportCsv(decisions)} className={s.btnExport}>
              CSV 내보내기
            </button>
            <button onClick={() => setShowOnboarding(true)} className={s.btnHelp} title="도움말">
              ?
            </button>
          </div>
        </div>

        <div className={s.kbdHints}>
          <span><kbd>A</kbd> 승인</span>
          <span><kbd>S</kbd> 건너뛰기</span>
          <span><kbd>↑↓</kbd> 이동</span>
        </div>
      </header>

      <div className={s.layout}>
        <aside className={s.sidebar}>
          <div className={s.filterCard}>
            <p className={s.filterTitle}>재무제표</p>
            {["BS", "IS", "CFS", "CIS"].map((sj) => (
              <label key={sj} className={s.filterRow}>
                <input
                  type="checkbox"
                  checked={filterSj.has(sj)}
                  onChange={(e) => {
                    const next = new Set(filterSj);
                    if (e.target.checked) next.add(sj); else next.delete(sj);
                    setFilterSj(next);
                  }}
                />
                <SjBadge sj={sj} />
              </label>
            ))}
          </div>

          <div className={s.filterCard}>
            <p className={s.filterTitle}>상태</p>
            {(["all", "pending", "done"] as const).map((v) => (
              <label key={v} className={s.filterRow}>
                <input
                  type="radio"
                  name="filterDone"
                  checked={filterDone === v}
                  onChange={() => setFilterDone(v)}
                />
                {{ all: "전체", pending: "미결", done: "완료" }[v]}
              </label>
            ))}
          </div>

          <div className={s.statsCard}>
            <p className={s.statsTitle}>전체 통계</p>
            <div className={s.statsRow}><span>클러스터</span><span className={s.statsVal}>{data.stats.clusters}</span></div>
            <div className={s.statsRow}><span>flagged</span><span className={s.statsVal}>{data.stats.flagged.toLocaleString()}</span></div>
            <div className={s.statsRow}><span>미해결</span><span className={s.statsVal}>{data.stats.needs_review.toLocaleString()}</span></div>
            <div className={s.statsRow}><span>총 기업수</span><span className={s.statsVal}>{data.stats.total_cw.toLocaleString()}</span></div>
          </div>
        </aside>

        <main className={s.main}>
          <div className={s.tabs}>
            <button onClick={() => setTab("clusters")} className={tab === "clusters" ? s.tabActive : s.tab}>
              클러스터 ({filteredClusters.length})
            </button>
            <button onClick={() => setTab("unresolved")} className={tab === "unresolved" ? s.tabActive : s.tab}>
              미해결 항목 ({data.unresolved.length})
            </button>
            <button onClick={() => setTab("seeds")} className={tab === "seeds" ? s.tabActive : s.tab}>
              Seed 사전 ({seedsData?.count ?? "…"})
            </button>
          </div>

          {tab === "clusters" && (
            <div className={s.clusterList}>
              {filteredClusters.length === 0 && (
                <div className={s.emptyState}>조건에 맞는 클러스터가 없습니다</div>
              )}
              {filteredClusters.map((cluster, idx) => (
                <div
                  key={cluster.canonical_id}
                  ref={idx === activeIdx ? activeCardRef : null}
                  onClick={() => setActiveIdx(idx)}
                >
                  <ClusterCard
                    cluster={cluster}
                    decisions={decisions}
                    onDecisions={handleDecisions}
                    isActive={idx === activeIdx}
                  />
                </div>
              ))}
            </div>
          )}

          {tab === "seeds" && seedsData && (
            <SeedTable
              seeds={seedsData.seeds}
              decisions={decisions}
              onDecisions={handleDecisions}
            />
          )}

          {tab === "unresolved" && (
            <div className={s.unresolvedPanel}>
              <div className={s.unresolvedHeader}>
                <p className={s.unresolvedHeaderTitle}>미해결 항목 (needs_review)</p>
                <p className={s.unresolvedHeaderSub}>AI 신뢰도 &lt; 0.65 — 직접 canonical ID를 지정하세요.</p>
              </div>
              <div>
                {data.unresolved.map((it) => {
                  const dec = decisions[itemKey(it.norm, it.sj)];
                  return (
                    <div key={`${it.norm}||${it.sj}`} className={s.unresolvedItem}>
                      <SjBadge sj={it.sj} />
                      <div className={s.unresolvedInfo}>
                        <div className={s.unresolvedName}>{it.norm}</div>
                        {it.top3.length > 0 && (
                          <div className={s.unresolvedSuggests}>
                            제안: {it.top3.map((c) => c.replace(/^(ifrs-full_|dart_)/, "")).join(" · ")}
                          </div>
                        )}
                      </div>
                      <span className={s.unresolvedCount}>{it.n.toLocaleString()}</span>
                      {dec ? (
                        <span className={s.unresolvedDecided}>
                          ✓ {dec.canonical_id.replace(/^(ifrs-full_|dart_)/, "")}
                        </span>
                      ) : (
                        <button
                          onClick={() => setUnresolvedOverride(it)}
                          className={s.btnAssign}
                        >
                          지정
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  );
}
