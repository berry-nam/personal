// Korean + English descriptions for canonical IDs
export const CANONICAL_LABELS: Record<string, string> = {
  // ── Income Statement ──────────────────────────────────────────────────────
  "ifrs-full_Revenue":                              "매출/수익 · Revenue",
  "ifrs-full_CostOfSales":                          "매출원가 · Cost of Sales",
  "ifrs-full_GrossProfit":                          "매출총이익 · Gross Profit",
  "ifrs-full_DistributionCosts":                    "판매비 · Distribution Costs",
  "ifrs-full_AdministrativeExpense":                "관리비 · Administrative Expense",
  "ifrs-full_SellingExpense":                       "판매비 · Selling Expense",
  "dart_SellingGeneralAndAdministrativeExpenses":   "판매비와관리비 · SG&A Expenses",
  "dart_OperatingIncomeLoss":                       "영업이익(손실) · Operating Income/Loss",
  "ifrs-full_OtherIncome":                          "기타수익 · Other Income",
  "ifrs-full_OtherExpense":                         "기타비용 · Other Expense",
  "dart_NonOperatingRevenue":                       "영업외수익 · Non-operating Revenue",
  "dart_NonOperatingExpense":                       "영업외비용 · Non-operating Expense",
  "ifrs-full_FinanceIncome":                        "금융수익 · Finance Income",
  "ifrs-full_FinanceCosts":                         "금융비용 · Finance Costs",
  "ifrs-full_InterestRevenueExpense":               "이자수익 · Interest Revenue",
  "ifrs-full_DividendIncome":                       "배당금수익 · Dividend Income",
  "ifrs-full_RentalIncome":                         "임대료수입 · Rental Income",
  "ifrs-full_WagesAndSalaries":                     "급여 · Wages and Salaries",
  "ifrs-full_ProfitLossBeforeTax":                  "법인세비용차감전순이익 · Profit Before Tax",
  "ifrs-full_IncomeTaxExpenseContinuingOperations": "법인세비용 · Income Tax Expense",
  "ifrs-full_ProfitLoss":                           "당기순이익(손실) · Profit/Loss",
  "ifrs-full_OtherComprehensiveIncome":             "기타포괄손익 · Other Comprehensive Income",
  "ifrs-full_ComprehensiveIncome":                  "총포괄이익 · Comprehensive Income",
  "ifrs-full_TaxExpenseOtherThanIncomeTaxExpense":  "세금과공과 · Tax (Non-Income)",
  "ifrs-full_ResearchAndDevelopmentExpense":        "연구개발비 · R&D Expense",
  "ifrs-full_ForeignExchangeGain":                  "외환차익 · Foreign Exchange Gain",
  "ifrs-full_ForeignExchangeLoss":                  "외환차손 · Foreign Exchange Loss",
  "ifrs-full_ShareOfProfitLossOfAssociatesAndJointVenturesAccountedForUsingEquityMethod":
                                                    "지분법손익 · Share of Profit/Loss (Equity Method)",
  "ifrs-full_ProfitLossFromDiscontinuedOperations": "중단영업손익 · Discontinued Operations",
  "ifrs-full_BasicEarningsLossPerShare":            "기본주당이익(손실) · Basic EPS",
  "ifrs-full_DilutedEarningsLossPerShare":          "희석주당이익(손실) · Diluted EPS",
  "ifrs-full_FinishedGoods":                        "제품 (기초/기말 재고) · Finished Goods",
  "ifrs-full_PurchasesOfGoods":                     "당기매입액 · Purchases of Goods",

  // ── Balance Sheet — Assets ────────────────────────────────────────────────
  "ifrs-full_Assets":                               "자산총계 · Total Assets",
  "ifrs-full_CurrentAssets":                        "유동자산 · Current Assets",
  "ifrs-full_NoncurrentAssets":                     "비유동자산 · Non-current Assets",
  "ifrs-full_CashAndCashEquivalents":               "현금및현금성자산 · Cash and Equivalents",
  "ifrs-full_ShorttermInvestments":                 "단기금융상품 · Short-term Investments",
  "ifrs-full_OtherNoncurrentFinancialAssets":       "장기금융자산 · Other Non-current Financial Assets",
  "ifrs-full_TradeAndOtherCurrentReceivables":      "매출채권 · Trade Receivables",
  "ifrs-full_OtherCurrentReceivables":              "미수금 · Other Current Receivables",
  "ifrs-full_CurrentPrepayments":                   "선급금/선급비용 · Current Prepayments",
  "ifrs-full_Inventories":                          "재고자산 · Inventories",
  "ifrs-full_OtherCurrentAssets":                   "기타유동자산 · Other Current Assets",
  "ifrs-full_PropertyPlantAndEquipment":            "유형자산 · Property, Plant & Equipment",
  "ifrs-full_Land":                                 "토지 · Land",
  "ifrs-full_Buildings":                            "건물 · Buildings",
  "ifrs-full_Machinery":                            "기계장치 · Machinery",
  "ifrs-full_ConstructionInProgress":               "건설중인자산 · Construction in Progress",
  "ifrs-full_IntangibleAssetsAndGoodwill":          "무형자산 · Intangible Assets & Goodwill",
  "ifrs-full_Goodwill":                             "영업권 · Goodwill",
  "ifrs-full_ComputerSoftware":                     "소프트웨어 · Computer Software",
  "ifrs-full_OtherIntangibleAssets":                "기타무형자산 · Other Intangible Assets",
  "ifrs-full_InvestmentProperty":                   "투자부동산 · Investment Property",
  "ifrs-full_InvestmentsAccountedForUsingEquityMethod":
                                                    "관계기업투자 · Equity Method Investments",
  "ifrs-full_FinancialAssetsAtFairValueThroughOtherComprehensiveIncome":
                                                    "기타포괄손익-공정가치 금융자산 · FVOCI Financial Assets",
  "ifrs-full_FinancialAssetsAtFairValueThroughProfitOrLoss":
                                                    "당기손익-공정가치 금융자산 · FVTPL Financial Assets",
  "ifrs-full_DerivativeFinancialAssets":            "파생상품자산 · Derivative Assets",
  "ifrs-full_DeferredTaxAssets":                    "이연법인세자산 · Deferred Tax Assets",
  "ifrs-full_CurrentTaxAssets":                     "당기법인세자산 · Current Tax Assets",
  "ifrs-full_OtherNoncurrentAssets":                "기타비유동자산 · Other Non-current Assets",
  "ifrs-full_NetDefinedBenefitAssetLiability":      "순확정급여자산(부채) · Net Defined Benefit Asset",
  "ifrs-full_PlanAssetsAtFairValue":                "퇴직연금운용자산 · Plan Assets",
  "dart_RetirementBenefitPlanAssets":               "퇴직연금운용자산 · Retirement Benefit Plan Assets",
  "dart_AllowanceForDoubtfulAccounts":              "대손충당금 · Allowance for Doubtful Accounts",

  // ── Balance Sheet — Liabilities ───────────────────────────────────────────
  "ifrs-full_Liabilities":                          "부채총계 · Total Liabilities",
  "ifrs-full_CurrentLiabilities":                   "유동부채 · Current Liabilities",
  "ifrs-full_NoncurrentLiabilities":                "비유동부채 · Non-current Liabilities",
  "ifrs-full_TradeAndOtherCurrentPayables":         "매입채무 · Trade Payables",
  "ifrs-full_OtherCurrentPayables":                 "미지급금 · Other Current Payables",
  "ifrs-full_CurrentTaxLiabilitiesCurrent":         "당기법인세부채 · Current Tax Liabilities",
  "ifrs-full_CurrentAdvancesFromCustomers":         "선수금 · Advances from Customers",
  "ifrs-full_CurrentBorrowings":                    "단기차입금 · Current Borrowings",
  "ifrs-full_NoncurrentBorrowings":                 "장기차입금 · Non-current Borrowings",
  "ifrs-full_DefinedBenefitLiability":              "확정급여부채 · Defined Benefit Liability",
  "ifrs-full_DeferredTaxLiabilities":               "이연법인세부채 · Deferred Tax Liabilities",
  "ifrs-full_NoncurrentProvisions":                 "충당부채 · Non-current Provisions",
  "ifrs-full_DerivativeFinancialLiabilities":       "파생상품부채 · Derivative Liabilities",
  "ifrs-full_OtherCurrentLiabilities":              "기타유동부채 · Other Current Liabilities",
  "ifrs-full_OtherNoncurrentLiabilities":           "임대보증금 등 기타비유동부채 · Other Non-current Liabilities",
  "dart_CurrentPortionOfLongTermBorrowings":        "유동성장기부채 · Current Portion of LT Debt",

  // ── Balance Sheet — Equity ────────────────────────────────────────────────
  "ifrs-full_Equity":                               "자본총계 · Total Equity",
  "ifrs-full_EquityAndLiabilities":                 "부채와자본총계 · Equity and Liabilities",
  "ifrs-full_IssuedCapital":                        "자본금 · Issued Capital",
  "ifrs-full_SharePremium":                         "주식발행초과금/자본잉여금 · Share Premium",
  "ifrs-full_RetainedEarnings":                     "이익잉여금(결손금) · Retained Earnings",
  "ifrs-full_TreasuryShares":                       "자기주식 · Treasury Shares",
  "ifrs-full_OtherEquityInterest":                  "자본조정/기타자본 · Other Equity",
  "ifrs-full_OtherReserves":                        "이익준비금/임의적립금 · Other Reserves",
  "ifrs-full_StatutoryReserve":                     "이익준비금 · Statutory Reserve",
  "ifrs-full_RevaluationSurplus":                   "재평가적립금 · Revaluation Surplus",
  "ifrs-full_NoncontrollingInterests":              "비지배지분 · Non-controlling Interests",
  "ifrs-full_EquityAttributableToOwnersOfParent":   "지배기업지분 · Equity Attr. to Owners",

  // ── Cash Flow Statement ───────────────────────────────────────────────────
  "ifrs-full_CashFlowsFromUsedInOperatingActivities":  "영업활동현금흐름 · Operating CF",
  "ifrs-full_CashFlowsFromUsedInInvestingActivities":  "투자활동현금흐름 · Investing CF",
  "ifrs-full_CashFlowsFromUsedInFinancingActivities":  "재무활동현금흐름 · Financing CF",
  "ifrs-full_CashAndCashEquivalentsAtBeginningOfPeriod": "기초현금 · Cash at Beginning",
  "ifrs-full_AdjustmentsForChangesInWorkingCapital":   "운전자본 변동 · WC Changes",
  "ifrs-full_AdjustmentsForNoncashItems":              "비현금항목 조정 · Non-cash Adjustments",
  "ifrs-full_AdjustmentsForForeignExchangeGainsLosses":"외화환산손익 조정 · FX Adjustment",
  "ifrs-full_EffectOfExchangeRateChangesOnCashAndCashEquivalents":
                                                       "환율변동효과 · FX Effect on Cash",
  "ifrs-full_DividendsPaid":                           "배당금 지급 · Dividends Paid",
  "ifrs-full_RepaymentsOfLeaseLiabilities":            "리스부채 상환 · Lease Repayments",
  "dart_NetIncreaseDecreaseInCash":                    "현금 순증감 · Net Change in Cash",
  "dart_DepreciationExpense":                          "감가상각비 · Depreciation",
  "dart_AmortisationExpense":                          "무형자산상각비 · Amortisation",
  "dart_RetirementBenefitExpense":                     "퇴직급여 · Retirement Benefit",
  "dart_GainOnDisposalOfTangibleAssets":               "유형자산처분이익 · Gain on PPE Disposal",
  "dart_LossOnDisposalOfTangibleAssets":               "유형자산처분손실 · Loss on PPE Disposal",
  "dart_ChangeInTradeReceivables":                     "매출채권 변동 · Change in Receivables",
  "dart_ChangeInInventories":                          "재고자산 변동 · Change in Inventories",
  "dart_ChangeInTradePayables":                        "매입채무 변동 · Change in Payables",
  "dart_ChangeInPrepayments":                          "선급금 변동 · Change in Prepayments",
  "dart_ChangeInAdvancesFromCustomers":                "선수금 변동 · Change in Advances",
  "dart_ChangeInDepositsReceived":                     "보증금 변동 · Change in Deposits Received",
  "dart_ChangeInCurrentTaxLiabilities":                "당기법인세부채 변동 · Change in Tax Liabilities",
  "dart_ChangeInCurrentTaxAssets":                     "당기법인세자산 변동 · Change in Tax Assets",
  "dart_ChangeInAccruedIncome":                        "미수수익 변동 · Change in Accrued Income",
  "dart_AcquisitionOfPropertyPlantEquipment":          "유형자산 취득 · PPE Acquisition",
  "dart_ProceedsFromDisposalOfPropertyPlantEquipment": "유형자산 처분 · PPE Disposal",
  "dart_AcquisitionOfIntangibleAssets":                "무형자산 취득 · Intangible Acquisition",
  "dart_ProceedsFromDisposalOfIntangibleAssets":       "무형자산 처분 · Intangible Disposal",
  "dart_AcquisitionOfShorttermFinancialInstruments":   "단기금융상품 취득 · ST Financial Acquisition",
  "dart_ProceedsFromShorttermFinancialInstruments":    "단기금융상품 처분 · ST Financial Disposal",
  "dart_AcquisitionOfLongtermFinancialInstruments":    "장기금융상품 취득 · LT Financial Acquisition",
  "dart_ProceedsFromDisposalOfLongtermFinancialInstruments":
                                                       "장기금융상품 처분 · LT Financial Disposal",
  "dart_AcquisitionOfDeposits":                        "보증금 지급 · Acquisition of Deposits",
  "dart_ProceedsFromDisposalOfDeposits":               "보증금 회수 · Proceeds from Deposits",
  "dart_LoansGranted":                                 "대여금 지급 · Loans Granted",
  "dart_LoansRepaid":                                  "대여금 회수 · Loans Repaid",
  "dart_AcquisitionOfInvestmentProperty":              "투자부동산 취득 · Investment Property Acquisition",
  "dart_ProceedsFromDisposalOfInvestmentProperty":     "투자부동산 처분 · Investment Property Disposal",
  "dart_AcquisitionOfInvestmentsInAssociates":         "관계기업 투자 · Associates Acquisition",
  "dart_ProceedsFromDisposalOfInvestmentsInAssociates":"관계기업 처분 · Associates Disposal",
  "dart_ProceedsFromShorttermBorrowings":              "단기차입금 차입 · ST Borrowings Proceeds",
  "dart_RepaymentOfShorttermBorrowings":               "단기차입금 상환 · ST Borrowings Repayment",
  "dart_ProceedsFromLongtermBorrowings":               "장기차입금 차입 · LT Borrowings Proceeds",
  "dart_RepaymentOfLongtermBorrowings":                "장기차입금 상환 · LT Borrowings Repayment",
  "dart_ProceedsFromIssuanceOfCapital":                "유상증자 · Capital Issuance",
  "dart_ProceedsFromIssuanceOfBonds":                  "사채 발행 · Bond Issuance",
  "dart_RepaymentOfBonds":                             "사채 상환 · Bond Repayment",
  "dart_SeverancePay":                                 "퇴직금 지급 · Severance Payments",
  "dart_OtherAdjustments":                             "타계정 대체 · Other Adjustments",
  "dart_AccumulatedDepreciation":                      "감가상각누계액 · Accumulated Depreciation",

  // ── OCI ──────────────────────────────────────────────────────────────────
  "ifrs-full_OtherComprehensiveIncomeThatWillNotBeReclassifiedToProfitOrLossNetOfTax":
    "재분류되지 않는 OCI (확정급여 재측정 등) · OCI - Won't Reclassify",
  "ifrs-full_OtherComprehensiveIncomeThatWillBeReclassifiedToProfitOrLossNetOfTax":
    "재분류될 수 있는 OCI (현금흐름위험회피 등) · OCI - May Reclassify",
  "ifrs-full_ReserveOfExchangeDifferencesOnTranslation":
    "해외사업환산손익 · Translation Reserve",
  "ifrs-full_OtherComprehensiveIncomeShareOfOtherComprehensiveIncomeOfAssociatesAndJointVenturesAccountedForUsingEquityMethod":
    "지분법자본변동 · Share of OCI of Associates",
};

export function getCanonicalLabel(id: string): string {
  return CANONICAL_LABELS[id] ?? id;
}

export function getCanonicalShortLabel(id: string): string {
  const full = CANONICAL_LABELS[id];
  if (!full) return id.replace(/^(ifrs-full_|dart_)/, "");
  return full.split(" · ")[0];
}

export function canonicalSource(id: string): "ifrs" | "dart" {
  return id.startsWith("dart_") ? "dart" : "ifrs";
}
