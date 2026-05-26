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
  const [selected, setSelected] = useState(currentCanonical);
  const [note, setNote] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const filtered = query.length > 0
    ? ALL_CANONICALS.filter(
        (c) =>
          c.id.toLowerCase().includes(query.toLowerCase()) ||
          c.label.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 12)
    : ALL_CANONICALS.slice(0, 12);

  const isCustomQuery = query && !ALL_CANONICALS.find((c) => c.id === query);

  return (
    <div className={s.overlay}>
      <div className={s.modal}>
        <div className={s.modalHeader}>
          <h3 className={s.modalTitle}>표준 계정 식별자 (Canonical ID) 수정</h3>
          <p className={s.modalSubtitle}>항목: <strong>{itemLabel}</strong></p>
        </div>

        <div className={s.modalBody}>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="표준 계정 식별자(Canonical ID) 또는 한글 설명 검색..."
            className={s.searchInput}
          />

          <div className={s.optionList}>
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
            {filtered.length === 0 && (
              <div className={s.emptyOption}>결과 없음</div>
            )}
          </div>

          {isCustomQuery && (
            <button
              onClick={() => setSelected(query)}
              className={selected === query ? `${s.customInput} ${s.customInputSelected}` : s.customInput}
            >
              직접 입력: <code>{query}</code>
            </button>
          )}

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
            수정 확인
          </button>
        </div>
      </div>
    </div>
  );
}
