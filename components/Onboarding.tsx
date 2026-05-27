"use client";
import { useState } from "react";
import s from "./Onboarding.module.css";

interface Props {
  onDone: () => void;
}

const STEPS = [
  {
    icon: "📊",
    title: "이 프로젝트란?",
    content: (
      <div className={s.contentBlock}>
        <p>
          한국 기업들은 DART 공시 시 계정명을 자유롭게 기재합니다.{" "}
          <strong>"매출액"</strong>, <strong>"수익(매출액)"</strong>, <strong>"영업수익"</strong>은 같은 개념이지만 다르게 표기됩니다.
          이 프로젝트는 39,000여 기업의 계정명을 <strong>IFRS 표준 Canonical ID</strong>로 매핑합니다.
        </p>
        <div className={s.infoBox}>
          <p className={s.infoBoxTitle}>자동 처리 기준 (전체의 약 83.6% 자동 확정)</p>
          <div className={s.infoBoxRow}>
            <span className={s.infoBoxLabel} style={{ color: "var(--cd-text-success-normal)" }}>✅ auto</span>
            <span>Seed 사전 정확 매칭 또는 AI 유사도 ≥ 0.92 → 검토 불필요</span>
          </div>
          <div className={s.infoBoxRow}>
            <span className={s.infoBoxLabel} style={{ color: "var(--cd-text-warning-normal)" }}>⚠️ flagged</span>
            <span>AI 유사도 0.65~0.92 → <strong>클러스터 탭</strong>에서 확인 필요</span>
          </div>
          <div className={s.infoBoxRow} style={{ marginBottom: 0 }}>
            <span className={s.infoBoxLabel} style={{ color: "var(--cd-text-danger-normal)" }}>❓ needs_review</span>
            <span>AI 유사도 {"<"} 0.65 → <strong>미해결 탭</strong>에서 직접 지정</span>
          </div>
        </div>
        <div className={s.tipBox}>
          <strong>예시:</strong> 매출액 → <code>ifrs-full_Revenue</code> · 임차료 → <code>ifrs-full_AdministrativeExpense</code>
        </div>
      </div>
    ),
  },
  {
    icon: "📖",
    title: "Seed 사전 & 검토 순서",
    content: (
      <div className={s.contentBlock}>
        <div className={s.infoBox}>
          <p className={s.infoBoxTitle}>권장 검토 순서</p>
          <div className={s.infoBoxRow}>
            <span className={s.infoBoxLabel}>① Seed 사전 탭</span>
            <span>533개의 공인된 계정명→Canonical 매핑 사전. 이미 확립된 목록이므로 빠르게 훑고 잘못된 것만 수정하세요.</span>
          </div>
          <div className={s.infoBoxRow}>
            <span className={s.infoBoxLabel}>② 클러스터 탭</span>
            <span>AI가 같은 Canonical로 묶은 계정명들. 각 클러스터의 헤더(분류 목적지)가 맞는지 확인 → 승인/수정.</span>
          </div>
          <div className={s.infoBoxRow} style={{ marginBottom: 0 }}>
            <span className={s.infoBoxLabel}>③ 미해결 탭</span>
            <span>AI가 분류하지 못한 항목들. 검토자가 직접 Canonical ID를 찾아 지정해야 합니다.</span>
          </div>
        </div>
        <div className={s.tipBox}>
          <strong>Seed ↔ 클러스터는 서로 다른 계정명 집합입니다.</strong>{" "}
          Seed에 있는 계정명(예: "자산총계")은 파이프라인에서 <code>auto</code>로 처리되어 클러스터에 진입하지 않습니다.
          클러스터에는 Seed에 없는 변형 계정명들("총자산", "자산합계" 등)만 존재합니다.
          따라서 Seed를 수정해도 클러스터에 캐스케이드할 동일 계정명 자체가 없습니다.
          단, Seed 수정이 의미상 관련된 클러스터 항목들을 재검토해야 한다는 신호가 될 수 있습니다.
        </div>
        <div className={s.infoBox}>
          <p className={s.infoBoxTitle}>Canonical ID 앞의 IFRS / DART 뱃지란?</p>
          <div className={s.infoBoxRow}>
            <span className={s.infoBoxLabel} style={{ color: "var(--cd-text-brand-normal)" }}>IFRS</span>
            <span><code>ifrs-full_*</code> — IASB 국제 표준 taxonomy. K-IFRS(한국채택국제회계기준)가 이 기준을 채택하므로, 대부분의 계정은 여기 해당합니다.</span>
          </div>
          <div className={s.infoBoxRow} style={{ marginBottom: 0 }}>
            <span className={s.infoBoxLabel} style={{ color: "var(--cd-text-warning-normal)" }}>DART</span>
            <span><code>dart_*</code> — 금융감독원(FSS)이 DART 공시용으로 별도 정의한 개념. IFRS에 존재하지 않는 한국 특유 항목(예: 판매비와관리비 합산)에 사용합니다.</span>
          </div>
        </div>
      </div>
    ),
  },
  {
    icon: "🎯",
    title: "검토 대상 — 무엇을 판단하나요?",
    content: (
      <div className={s.contentBlock}>
        <p>
          AI가 각 계정명에 대해 <strong>"이 표준 계정 식별자에 속할 것 같다"</strong>고 제안했습니다.
          검토자의 역할은 <strong>그 제안이 맞는지 틀린지 확인</strong>하는 것입니다.
        </p>
        <div className={s.exampleBox}>
          <p className={s.exampleTitle}>예시: AI가 아래 항목들을 <span style={{ color: "var(--cd-text-brand-normal)" }}>관리비 (AdministrativeExpense)</span>로 제안</p>
          <div className={s.exampleItem}>
            <span className={s.iconOk}>✓</span>
            <code>지급수수료</code>
            <span>→ 관리비 맞음 → <strong style={{ color: "var(--cd-text-success-normal)" }}>승인</strong></span>
          </div>
          <div className={s.exampleItem}>
            <span className={s.iconOk}>✓</span>
            <code>차량유지비</code>
            <span>→ 관리비 맞음 → <strong style={{ color: "var(--cd-text-success-normal)" }}>승인</strong></span>
          </div>
          <div className={s.exampleItem}>
            <span className={s.iconBad}>✗</span>
            <code>임대료수입</code>
            <span>→ 관리비 아님! → <strong style={{ color: "var(--cd-text-warning-normal)" }}>수정 → RentalIncome으로 변경</strong></span>
          </div>
        </div>
        <p>
          클러스터 안의 항목들이 <strong>전부 맞으면</strong> → <strong style={{ color: "var(--cd-text-success-normal)" }}>모두 승인</strong> 한 번으로 완료.{" "}
          <strong>일부만 틀리면</strong> → 해당 항목만 펼쳐서 <strong style={{ color: "var(--cd-text-warning-normal)" }}>수정(Override)</strong>.
        </p>
        <div className={s.dangerBox}>
          <strong>미해결 항목 (1,952개)</strong>: AI가 어느 표준 계정에 속하는지 판단 자체를 못 한 계정명입니다.
          "이 계정은 어떤 표준 계정 식별자에 해당하는가"를 검토자가 직접 찾아서 입력해야 합니다.
        </div>
      </div>
    ),
  },
  {
    icon: "🖊️",
    title: "검토 방법",
    content: (
      <div className={s.contentBlock}>
        <div>
          <div className={s.kbdRow}>
            <kbd>A</kbd>
            <span>또는 <strong style={{ color: "var(--cd-text-success-normal)" }}>모두 승인</strong> — 클러스터 전체를 현재 표준 계정 식별자로 확정</span>
          </div>
          <div className={s.kbdRow}>
            <kbd>S</kbd>
            <span>또는 <strong style={{ color: "var(--cd-text-default-weak)" }}>건너뛰기</strong> — 나중에 다시 검토</span>
          </div>
          <div className={s.kbdRow}>
            <kbd>O</kbd>
            <span>또는 <strong style={{ color: "var(--cd-text-warning-normal)" }}>수정(Override)</strong> — 다른 표준 계정 식별자로 변경</span>
          </div>
        </div>
        <div className={s.divider} />
        <p style={{ fontSize: "var(--cd-font-size-sm)", color: "var(--cd-text-default-weak)" }}>
          모든 결정은 <strong>서버(Vercel KV)</strong>에 자동 저장됩니다.
          화면 오른쪽 상단의 <strong>CSV 내보내기</strong>로 결정 사항을 파일로 받아
          <code>merge_reviewer_decisions.py</code>에 입력하세요.
        </p>
      </div>
    ),
  },
  {
    icon: "✅",
    title: "확인 기준",
    content: (
      <div className={s.contentBlock}>
        <p style={{ fontWeight: "var(--cd-font-weight-bold)", color: "var(--cd-text-default-strong)" }}>
          이 매핑이 맞는지 판단하는 기준:
        </p>
        <ul className={s.checkList}>
          <li className={s.checkItem}>
            <span className={s.checkIcon} style={{ color: "var(--cd-text-success-normal)" }}>✓</span>
            <span>계정의 <strong>경제적 성격</strong>이 표준 계정 식별자의 정의와 일치하는가?</span>
          </li>
          <li className={s.checkItem}>
            <span className={s.checkIcon} style={{ color: "var(--cd-text-success-normal)" }}>✓</span>
            <span>같은 클러스터의 다른 계정들도 동일한 표준 계정으로 분류하는 게 맞는가?</span>
          </li>
          <li className={s.checkItem}>
            <span className={s.checkIcon} style={{ color: "var(--cd-text-warning-normal)" }}>△</span>
            <span>재무제표 유형 배지(BS=재무상태표, IS=손익계산서, CFS=현금흐름표, CIS=포괄손익)가 계정의 성격과 맞는가?</span>
          </li>
          <li className={s.checkItem}>
            <span className={s.checkIcon} style={{ color: "var(--cd-text-danger-normal)" }}>✗</span>
            <span>계정명이 여러 의미로 해석될 수 있다면 <strong>Override</strong>하거나 <strong>Skip</strong>.</span>
          </li>
        </ul>
        <div className={s.tipBox}>
          <strong>팁:</strong> 의심스러우면 Skip이 더 낫습니다. 잘못된 매핑보다 미결이 낫습니다.
        </div>
      </div>
    ),
  },
];

export default function Onboarding({ onDone }: Props) {
  const [step, setStep] = useState(0);
  const isLast = step === STEPS.length - 1;

  return (
    <div className={s.overlay}>
      <div className={s.card}>
        <div className={s.cardHeader}>
          <div className={s.headerTop}>
            <span className={s.headerIcon}>{STEPS[step].icon}</span>
            <div className={s.headerMeta}>
              <p className={s.headerStep}>{step + 1} / {STEPS.length}</p>
              <h2 className={s.headerTitle}>{STEPS[step].title}</h2>
            </div>
          </div>
          <div className={s.progressBar}>
            <div
              className={s.progressFill}
              style={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
            />
          </div>
        </div>

        <div className={s.content}>{STEPS[step].content}</div>

        <div className={s.footer}>
          <button
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
            className={s.btnPrev}
          >
            ← 이전
          </button>
          <div className={s.dots}>
            {STEPS.map((_, i) => (
              <button
                key={i}
                onClick={() => setStep(i)}
                className={i === step ? `${s.dot} ${s.dotActive}` : s.dot}
              />
            ))}
          </div>
          {isLast ? (
            <button onClick={onDone} className={s.btnStart}>검토 시작 →</button>
          ) : (
            <button onClick={() => setStep((s) => s + 1)} className={s.btnNext}>다음 →</button>
          )}
        </div>
      </div>
    </div>
  );
}
