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
          한국 기업들은 DART에 재무제표를 공시할 때 계정명을 자유롭게 기재합니다.
          <br />
          <strong>"매출액"</strong>, <strong>"수익(매출액)"</strong>, <strong>"영업수익"</strong>… 이 모두가 동일한 개념입니다.
        </p>
        <p>
          이 프로젝트의 목표는 39,000여 개 기업의 다양한 계정명을{" "}
          <strong>IFRS 표준 canonical ID (표준 계정 식별자)</strong>로 매핑하는 것입니다.
          Canonical ID란 국제 회계 기준(IFRS)이 각 계정 개념에 부여한 고유한 영문 식별자입니다.
          <br />
          예: <code>매출액 → ifrs-full_Revenue (수익)</code>
        </p>
        <div className={s.infoBox}>
          <p className={s.infoBoxTitle}>자동 매칭은 두 단계로 작동합니다:</p>
          <div className={s.infoBoxRow}>
            <span className={s.infoBoxLabel}>① Seed 사전</span>
            <span>K-IFRS/K-GAAP 기준으로 사전 정의된 계정명 → canonical ID 매핑표 (533개). Seed에 있으면 100% 확도로 자동 확정됩니다. <strong>"Seed 사전" 탭에서 직접 확인·수정 가능합니다.</strong></span>
          </div>
          <div className={s.infoBoxRow}>
            <span className={s.infoBoxLabel}>② AI 임베딩</span>
            <span>Seed에 없는 계정명은 AI(bge-m3)가 의미적 유사도를 계산해 가장 가까운 canonical을 제안합니다. 신뢰도 점수(0~1)로 표시됩니다.</span>
          </div>
        </div>
        <div className={s.infoBox} style={{ marginTop: 0 }}>
          <p className={s.infoBoxTitle}>자동 처리 vs 검토 필요 기준</p>
          <div className={s.infoBoxRow}>
            <span className={s.infoBoxLabel} style={{ color: "var(--cd-text-success-normal)" }}>✅ 자동 확정</span>
            <span>① Seed 사전 정확 매칭 <strong>또는</strong> ② AI 유사도 <strong>≥ 0.92</strong> → 전체의 83.6%</span>
          </div>
          <div className={s.infoBoxRow}>
            <span className={s.infoBoxLabel} style={{ color: "var(--cd-text-warning-normal)" }}>⚠️ 검토 필요</span>
            <span>AI 유사도 <strong>0.65 ~ 0.92</strong> — 제안은 있지만 확신 부족 → 클러스터 탭</span>
          </div>
          <div className={s.infoBoxRow} style={{ marginBottom: 0 }}>
            <span className={s.infoBoxLabel} style={{ color: "var(--cd-text-danger-normal)" }}>❓ 직접 지정</span>
            <span>AI 유사도 <strong>{"< 0.65"}</strong> — 제안 자체를 못 함 → 미해결 항목 탭</span>
          </div>
        </div>
      </div>
    ),
  },
  {
    icon: "🏷️",
    title: "Status 종류",
    content: (
      <div className={s.contentBlock}>
        <div className={`${s.statusRow} ${s.statusAuto}`}>
          <span className={`${s.statusLabel} ${s.autoLabel}`}>✅ auto</span>
          <span className={s.autoBody}>Seed 사전 정확 매칭 또는 AI 유사도 ≥ 0.92로 자동 확정된 항목. <strong>검토 불필요.</strong></span>
        </div>
        <div className={`${s.statusRow} ${s.statusFlagged}`}>
          <span className={`${s.statusLabel} ${s.flagLabel}`}>⚠️ flagged</span>
          <span className={s.flagBody}>AI가 제안은 했지만 신뢰도가 <strong>0.65~0.92</strong> 사이. 제안이 맞는지 확인 필요.</span>
        </div>
        <div className={`${s.statusRow} ${s.statusNeedsReview}`}>
          <span className={`${s.statusLabel} ${s.reviewLabel}`}>❓ needs_review</span>
          <span className={s.reviewBody}>AI가 신뢰도 있는 제안을 못 함 (&lt;0.65). 검토자가 직접 canonical ID를 지정해야 함.</span>
        </div>
        <p style={{ fontSize: "var(--cd-font-size-sm)", color: "var(--cd-text-default-weakest)" }}>
          n_companies = 해당 계정명을 사용하는 기업 수 (많을수록 중요)
        </p>
      </div>
    ),
  },
  {
    icon: "🎯",
    title: "검토 대상 — 무엇을 판단하나요?",
    content: (
      <div className={s.contentBlock}>
        <p>
          AI가 각 계정명에 대해 <strong>"이 canonical ID에 속할 것 같다"</strong>고 제안했습니다.
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
          <strong>미해결 항목 (1,952개)</strong>: AI가 어느 canonical에 속하는지 판단 자체를 못 한 계정명입니다.
          "이 계정은 어떤 canonical ID에 해당하는가"를 검토자가 직접 찾아서 입력해야 합니다.
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
            <span>또는 <strong style={{ color: "var(--cd-text-success-normal)" }}>모두 승인</strong> — 클러스터 전체를 현재 canonical ID로 확정</span>
          </div>
          <div className={s.kbdRow}>
            <kbd>S</kbd>
            <span>또는 <strong style={{ color: "var(--cd-text-default-weak)" }}>건너뛰기</strong> — 나중에 다시 검토</span>
          </div>
          <div className={s.kbdRow}>
            <kbd>O</kbd>
            <span>또는 <strong style={{ color: "var(--cd-text-warning-normal)" }}>수정(Override)</strong> — 다른 canonical ID로 변경</span>
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
            <span>계정의 <strong>경제적 성격</strong>이 canonical ID의 정의와 일치하는가?</span>
          </li>
          <li className={s.checkItem}>
            <span className={s.checkIcon} style={{ color: "var(--cd-text-success-normal)" }}>✓</span>
            <span>같은 클러스터의 다른 계정들도 동일 canonical이 맞는가?</span>
          </li>
          <li className={s.checkItem}>
            <span className={s.checkIcon} style={{ color: "var(--cd-text-warning-normal)" }}>△</span>
            <span>sj_div (BS/IS/CFS)가 canonical ID의 재무제표 위치와 일치하는가?</span>
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
