"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { TaxonomyNode, TaxonomySection } from "@/lib/taxonomyData";
import s from "./TaxonomyTree.module.css";

interface Props {
  sections: TaxonomySection[];
  activeCanonicalId?: string;
  clusterIds?: Set<string>;
}

function nodeKey(node: TaxonomyNode, parentKey: string): string {
  return node.id ?? `${parentKey}:${node.label}`;
}

function findAncestorKeys(
  nodes: TaxonomyNode[],
  targetId: string,
  parentKey: string
): string[] | null {
  for (const node of nodes) {
    const key = nodeKey(node, parentKey);
    if (node.id === targetId) return [];
    if (node.children) {
      const sub = findAncestorKeys(node.children, targetId, key);
      if (sub !== null) return [key, ...sub];
    }
  }
  return null;
}

interface NodeProps {
  node: TaxonomyNode;
  parentKey: string;
  depth: number;
  expandedKeys: Set<string>;
  activeCanonicalId?: string;
  clusterIds?: Set<string>;
  onToggle: (key: string) => void;
  onActiveMount: (el: HTMLElement) => void;
}

function TreeNode({
  node,
  parentKey,
  depth,
  expandedKeys,
  activeCanonicalId,
  clusterIds,
  onToggle,
  onActiveMount,
}: NodeProps) {
  const key = nodeKey(node, parentKey);
  const hasChildren = !!(node.children && node.children.length > 0);
  const isExpanded = expandedKeys.has(key);
  const isActive = !!(node.id && node.id === activeCanonicalId);
  const hasCluster = !!(node.id && clusterIds?.has(node.id));
  const isDart = !!(node.id && node.id.startsWith("dart_"));

  const callbackRef = useCallback(
    (el: HTMLElement | null) => {
      if (el && isActive) onActiveMount(el);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [isActive, activeCanonicalId]
  );

  return (
    <div>
      <div
        ref={callbackRef}
        className={`${s.treeNode} ${isActive ? s.treeNodeActive : ""}`}
        style={{ paddingLeft: `${6 + depth * 10}px` }}
        onClick={() => hasChildren && onToggle(key)}
        role={hasChildren ? "button" : undefined}
        tabIndex={hasChildren ? 0 : undefined}
        onKeyDown={(e) => {
          if (hasChildren && (e.key === "Enter" || e.key === " ")) {
            e.preventDefault();
            onToggle(key);
          }
        }}
      >
        <span className={s.nodeChevron}>
          {hasChildren ? (isExpanded ? "▾" : "▸") : ""}
        </span>
        <span className={s.nodeLabel}>{node.label}</span>
        {isDart && <span className={s.dartBadge}>D</span>}
        {hasCluster && !isActive && <span className={s.clusterDot} />}
      </div>

      {hasChildren && isExpanded && (
        <div>
          {node.children!.map((child) => (
            <TreeNode
              key={nodeKey(child, key)}
              node={child}
              parentKey={key}
              depth={depth + 1}
              expandedKeys={expandedKeys}
              activeCanonicalId={activeCanonicalId}
              clusterIds={clusterIds}
              onToggle={onToggle}
              onActiveMount={onActiveMount}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function TaxonomyTree({ sections, activeCanonicalId, clusterIds }: Props) {
  const [expandedKeys, setExpandedKeys] = useState<Set<string>>(() => {
    return new Set(sections.map((sec) => sec.sj));
  });

  const bodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!activeCanonicalId) return;
    const keysToAdd: string[] = [];
    for (const sec of sections) {
      const ancestors = findAncestorKeys(sec.children, activeCanonicalId, sec.sj);
      if (ancestors !== null) {
        keysToAdd.push(sec.sj, ...ancestors);
        break;
      }
    }
    if (keysToAdd.length > 0) {
      setExpandedKeys((prev) => {
        const next = new Set(prev);
        keysToAdd.forEach((k) => next.add(k));
        return next;
      });
    }
  }, [activeCanonicalId, sections]);

  const handleActiveMount = useCallback((el: HTMLElement) => {
    el.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, []);

  const toggleKey = useCallback((key: string) => {
    setExpandedKeys((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }, []);

  return (
    <div className={s.tree}>
      <div className={s.treeHeader}>
        <span className={s.treeHeaderTitle}>IFRS / DART 분류 체계</span>
        <span className={s.treeHeaderSub}>Taxonomy Reference</span>
      </div>
      <div ref={bodyRef} className={s.treeBody}>
        {sections.map((sec) => {
          const secExpanded = expandedKeys.has(sec.sj);
          return (
            <div key={sec.sj} className={s.section}>
              <div
                className={s.sectionHeader}
                onClick={() => toggleKey(sec.sj)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    toggleKey(sec.sj);
                  }
                }}
              >
                <span className={`${s.sjBadge} ${s[`sj${sec.sj}`]}`}>{sec.sj}</span>
                <span className={s.sectionLabel}>{sec.label}</span>
                <span className={s.sectionSublabel}>{sec.sublabel}</span>
                <span className={s.sectionChevron}>{secExpanded ? "▾" : "▸"}</span>
              </div>

              {secExpanded && (
                <div className={s.sectionBody}>
                  {sec.children.map((node) => (
                    <TreeNode
                      key={nodeKey(node, sec.sj)}
                      node={node}
                      parentKey={sec.sj}
                      depth={0}
                      expandedKeys={expandedKeys}
                      activeCanonicalId={activeCanonicalId}
                      clusterIds={clusterIds}
                      onToggle={toggleKey}
                      onActiveMount={handleActiveMount}
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
