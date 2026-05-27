"use client";
import { useState, useRef, useEffect } from "react";
import { CANONICAL_LABELS, getCanonicalLabel } from "@/lib/canonicalLabels";
import s from "./OverrideModal.module.css";

interface Props {
  currentCanonical: string;
  itemLabel: string;
  onConfirm: (newCanonical: string, note: string) => void;
  onCancel: () => void;
}

const ALL_CANONICALS = Object.entries(CANONICAL_LABELS).map(([id, label]) => ({ id, label }));

export default function OverrideModal({ currentCanonical, itemLabel, onConfirm, onCancel }: Props) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState("");
  const [note, setNote] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const filtered = query.trim().length > 0
    ? ALL_CANONICALS.filter(
        (c) =>
          c.id.toLowerCase().includes(query.toLowerCase()) ||
          c.label.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 12)
    : [];


  return (
    <div className={s.overlay}>
      <div className={s.modal}>
        <div className={s.modalHeader}>
          <h3 className={s.modalTitle}>
            <span className={s.modalItemName}>{itemLabel}</span>
            <span className={s.modalArrow}>→</span>
            <span className={s.modalDestLabel}>새 Canonical 선택</span>
          </h3>
          {currentCanonical && (
            <p className={s.modalSubtitle}>
              현재 AI 제안:{" "}
              <code className={s.currentCid}>{currentCanonical}</code>
              <span className={s.currentCidLabel}> ({getCanonicalLabel(currentCanonical)})</span>
            </p>
          )}
          <p className={s.modalHint}>
            IFRS = 국제회계기준 표준, DART = 한국 공시 전용 계정
          </p>
        </div>

        <div className={s.modalBody}>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="한글명, 영문명, 또는 ID로 검색 (예: 부채, liabilities, OtherCurrent…)"
            className={s.searchInput}
          />

          <div className={s.optionList}>
            {query.trim().length === 0 && (
              <div className={s.emptyOption}>검색어를 입력하면 표준 계정 목록이 나타납니다</div>
            )}
            {query.trim().length > 0 && filtered.length === 0 && (
              <div className={s.emptyOption}>일치하는 결과 없음</div>
            )}
            {filtered.map((c) => (
              <button
                key={c.id}
                onClick={() => setSelected(c.id)}
                className={selected === c.id ? `${s.optionItem} ${s.optionItemSelected}` : s.optionItem}
              >
                <span className={c.id.startsWith("dart_") ? `${s.optionSrcBadge} ${s.optionSrcDart}` : `${s.optionSrcBadge} ${s.optionSrcIfrs}`}>
                  {c.id.startsWith("dart_") ? "DART" : "IFRS"}
                </span>
                <div>
                  <div className={s.optionLabel}>{c.label}</div>
                  <div className={s.optionId}>{c.id}</div>
                </div>
              </button>
            ))}
          </div>

          <input
            type="text"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="메모 (선택사항)"
            className={s.noteInput}
          />

          {selected && (
            <p className={s.selectedPreview}>
              선택: <code>{selected}</code>
              <span> — {getCanonicalLabel(selected)}</span>
            </p>
          )}
        </div>

        <div className={s.modalFooter}>
          <button onClick={onCancel} className={s.btnCancel}>취소</button>
          <button
            onClick={() => selected && onConfirm(selected, note)}
            disabled={!selected}
            className={s.btnConfirm}
          >
            변경 확정
          </button>
        </div>
      </div>
    </div>
  );
}
