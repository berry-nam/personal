export type TaxonomyNode = {
  id?: string;
  label: string;
  children?: TaxonomyNode[];
};

export type TaxonomySection = {
  sj: "BS" | "IS" | "CFS" | "CIS";
  label: string;
  sublabel: string;
  children: TaxonomyNode[];
};

export const TAXONOMY_SECTIONS: TaxonomySection[] = [
  {
    sj: "BS",
    label: "재무상태표",
    sublabel: "Balance Sheet",
    children: [
      {
        id: "ifrs-full_Assets",
        label: "자산총계",
        children: [
          {
            id: "ifrs-full_CurrentAssets",
            label: "유동자산",
            children: [
              { id: "ifrs-full_CashAndCashEquivalents",          label: "현금및현금성자산" },
              { id: "ifrs-full_ShorttermInvestments",            label: "단기금융상품" },
              { id: "ifrs-full_TradeAndOtherCurrentReceivables", label: "매출채권" },
              { id: "ifrs-full_OtherCurrentReceivables",         label: "미수금" },
              { id: "ifrs-full_CurrentPrepayments",              label: "선급금/선급비용" },
              { id: "ifrs-full_Inventories",                     label: "재고자산" },
              { id: "ifrs-full_CurrentTaxAssets",                label: "당기법인세자산" },
              { id: "ifrs-full_OtherCurrentAssets",              label: "기타유동자산" },
            ],
          },
          {
            id: "ifrs-full_NoncurrentAssets",
            label: "비유동자산",
            children: [
              {
                id: "ifrs-full_PropertyPlantAndEquipment",
                label: "유형자산",
                children: [
                  { id: "ifrs-full_Land",                       label: "토지" },
                  { id: "ifrs-full_Buildings",                  label: "건물" },
                  { id: "ifrs-full_Machinery",                  label: "기계장치" },
                  { id: "ifrs-full_ConstructionInProgress",     label: "건설중인자산" },
                  { id: "dart_AccumulatedDepreciation",         label: "감가상각누계액" },
                ],
              },
              {
                id: "ifrs-full_IntangibleAssetsAndGoodwill",
                label: "무형자산",
                children: [
                  { id: "ifrs-full_Goodwill",              label: "영업권" },
                  { id: "ifrs-full_ComputerSoftware",      label: "소프트웨어" },
                  { id: "ifrs-full_OtherIntangibleAssets", label: "기타무형자산" },
                ],
              },
              { id: "ifrs-full_InvestmentProperty",                                        label: "투자부동산" },
              { id: "ifrs-full_InvestmentsAccountedForUsingEquityMethod",                  label: "관계기업투자" },
              { id: "ifrs-full_OtherNoncurrentFinancialAssets",                            label: "장기금융자산" },
              { id: "ifrs-full_FinancialAssetsAtFairValueThroughOtherComprehensiveIncome", label: "FVOCI 금융자산" },
              { id: "ifrs-full_FinancialAssetsAtFairValueThroughProfitOrLoss",             label: "FVTPL 금융자산" },
              { id: "ifrs-full_DerivativeFinancialAssets",                                 label: "파생상품자산" },
              { id: "ifrs-full_DeferredTaxAssets",                                         label: "이연법인세자산" },
              { id: "ifrs-full_NetDefinedBenefitAssetLiability",                           label: "순확정급여자산" },
              { id: "ifrs-full_PlanAssetsAtFairValue",                                     label: "퇴직연금운용자산" },
              { id: "dart_RetirementBenefitPlanAssets",                                    label: "퇴직연금운용자산 (DART)" },
              { id: "ifrs-full_OtherNoncurrentAssets",                                     label: "기타비유동자산" },
              { id: "dart_AllowanceForDoubtfulAccounts",                                   label: "대손충당금" },
            ],
          },
        ],
      },
      {
        id: "ifrs-full_Liabilities",
        label: "부채총계",
        children: [
          {
            id: "ifrs-full_CurrentLiabilities",
            label: "유동부채",
            children: [
              { id: "ifrs-full_TradeAndOtherCurrentPayables",    label: "매입채무" },
              { id: "ifrs-full_OtherCurrentPayables",            label: "미지급금" },
              { id: "ifrs-full_CurrentTaxLiabilitiesCurrent",    label: "당기법인세부채" },
              { id: "ifrs-full_CurrentAdvancesFromCustomers",    label: "선수금" },
              { id: "ifrs-full_CurrentBorrowings",               label: "단기차입금" },
              { id: "dart_CurrentPortionOfLongTermBorrowings",   label: "유동성장기부채" },
              { id: "ifrs-full_OtherCurrentLiabilities",         label: "기타유동부채" },
            ],
          },
          {
            id: "ifrs-full_NoncurrentLiabilities",
            label: "비유동부채",
            children: [
              { id: "ifrs-full_NoncurrentBorrowings",        label: "장기차입금" },
              { id: "ifrs-full_DefinedBenefitLiability",     label: "확정급여부채" },
              { id: "ifrs-full_DeferredTaxLiabilities",      label: "이연법인세부채" },
              { id: "ifrs-full_NoncurrentProvisions",        label: "충당부채" },
              { id: "ifrs-full_DerivativeFinancialLiabilities", label: "파생상품부채" },
              { id: "ifrs-full_OtherNoncurrentLiabilities",  label: "임대보증금 등" },
            ],
          },
        ],
      },
      {
        id: "ifrs-full_Equity",
        label: "자본총계",
        children: [
          {
            id: "ifrs-full_EquityAttributableToOwnersOfParent",
            label: "지배기업지분",
            children: [
              { id: "ifrs-full_IssuedCapital",       label: "자본금" },
              { id: "ifrs-full_SharePremium",        label: "자본잉여금" },
              { id: "ifrs-full_RetainedEarnings",    label: "이익잉여금(결손금)" },
              { id: "ifrs-full_TreasuryShares",      label: "자기주식" },
              { id: "ifrs-full_OtherEquityInterest", label: "자본조정" },
              { id: "ifrs-full_OtherReserves",       label: "이익준비금" },
              { id: "ifrs-full_StatutoryReserve",    label: "이익준비금 (법정)" },
              { id: "ifrs-full_RevaluationSurplus",  label: "재평가적립금" },
            ],
          },
          { id: "ifrs-full_NoncontrollingInterests", label: "비지배지분" },
          { id: "ifrs-full_EquityAndLiabilities",    label: "부채와자본총계" },
        ],
      },
    ],
  },

  {
    sj: "IS",
    label: "손익계산서",
    sublabel: "Income Statement",
    children: [
      { id: "ifrs-full_Revenue",     label: "매출/수익" },
      { id: "ifrs-full_CostOfSales", label: "매출원가" },
      { id: "ifrs-full_GrossProfit", label: "매출총이익" },
      {
        label: "판매비와관리비",
        children: [
          { id: "dart_SellingGeneralAndAdministrativeExpenses", label: "판관비 합계" },
          { id: "ifrs-full_DistributionCosts",                  label: "판매비" },
          { id: "ifrs-full_SellingExpense",                     label: "판매비 (분류)" },
          { id: "ifrs-full_AdministrativeExpense",              label: "관리비" },
          { id: "ifrs-full_WagesAndSalaries",                   label: "급여" },
          { id: "ifrs-full_ResearchAndDevelopmentExpense",      label: "연구개발비" },
          { id: "ifrs-full_TaxExpenseOtherThanIncomeTaxExpense", label: "세금과공과" },
        ],
      },
      { id: "dart_OperatingIncomeLoss",   label: "영업이익(손실)" },
      { id: "ifrs-full_OtherIncome",      label: "기타수익" },
      { id: "ifrs-full_OtherExpense",     label: "기타비용" },
      { id: "dart_NonOperatingRevenue",   label: "영업외수익" },
      { id: "dart_NonOperatingExpense",   label: "영업외비용" },
      {
        id: "ifrs-full_FinanceIncome",
        label: "금융수익",
        children: [
          { id: "ifrs-full_InterestRevenueExpense", label: "이자수익" },
          { id: "ifrs-full_DividendIncome",         label: "배당금수익" },
          { id: "ifrs-full_RentalIncome",           label: "임대료수입" },
          { id: "ifrs-full_ForeignExchangeGain",    label: "외환차익" },
        ],
      },
      {
        id: "ifrs-full_FinanceCosts",
        label: "금융비용",
        children: [
          { id: "ifrs-full_ForeignExchangeLoss", label: "외환차손" },
        ],
      },
      { id: "ifrs-full_ShareOfProfitLossOfAssociatesAndJointVenturesAccountedForUsingEquityMethod", label: "지분법손익" },
      { id: "ifrs-full_ProfitLossBeforeTax",                    label: "법인세차감전이익" },
      { id: "ifrs-full_IncomeTaxExpenseContinuingOperations",   label: "법인세비용" },
      { id: "ifrs-full_ProfitLoss",                             label: "당기순이익(손실)" },
      { id: "ifrs-full_ProfitLossFromDiscontinuedOperations",   label: "중단영업손익" },
      { id: "ifrs-full_BasicEarningsLossPerShare",              label: "기본EPS" },
      { id: "ifrs-full_DilutedEarningsLossPerShare",            label: "희석EPS" },
      {
        label: "재고 변동",
        children: [
          { id: "ifrs-full_FinishedGoods",    label: "제품 재고" },
          { id: "ifrs-full_PurchasesOfGoods", label: "당기매입액" },
        ],
      },
    ],
  },

  {
    sj: "CFS",
    label: "현금흐름표",
    sublabel: "Cash Flow Statement",
    children: [
      {
        id: "ifrs-full_CashFlowsFromUsedInOperatingActivities",
        label: "영업활동현금흐름",
        children: [
          {
            label: "비현금 조정",
            children: [
              { id: "ifrs-full_AdjustmentsForNoncashItems",     label: "비현금항목 조정" },
              { id: "dart_DepreciationExpense",                 label: "감가상각비" },
              { id: "dart_AmortisationExpense",                 label: "무형자산상각비" },
              { id: "dart_RetirementBenefitExpense",            label: "퇴직급여" },
              { id: "dart_GainOnDisposalOfTangibleAssets",      label: "유형자산처분이익" },
              { id: "dart_LossOnDisposalOfTangibleAssets",      label: "유형자산처분손실" },
              { id: "dart_OtherAdjustments",                    label: "타계정 대체" },
            ],
          },
          {
            id: "ifrs-full_AdjustmentsForChangesInWorkingCapital",
            label: "운전자본 변동",
            children: [
              { id: "dart_ChangeInTradeReceivables",       label: "매출채권 변동" },
              { id: "dart_ChangeInInventories",            label: "재고자산 변동" },
              { id: "dart_ChangeInTradePayables",          label: "매입채무 변동" },
              { id: "dart_ChangeInPrepayments",            label: "선급금 변동" },
              { id: "dart_ChangeInAdvancesFromCustomers",  label: "선수금 변동" },
              { id: "dart_ChangeInDepositsReceived",       label: "보증금 변동" },
              { id: "dart_ChangeInCurrentTaxLiabilities",  label: "법인세부채 변동" },
              { id: "dart_ChangeInCurrentTaxAssets",       label: "법인세자산 변동" },
              { id: "dart_ChangeInAccruedIncome",          label: "미수수익 변동" },
            ],
          },
          { id: "ifrs-full_AdjustmentsForForeignExchangeGainsLosses", label: "외화환산 조정" },
        ],
      },
      {
        id: "ifrs-full_CashFlowsFromUsedInInvestingActivities",
        label: "투자활동현금흐름",
        children: [
          { id: "dart_AcquisitionOfPropertyPlantEquipment",              label: "유형자산 취득" },
          { id: "dart_ProceedsFromDisposalOfPropertyPlantEquipment",     label: "유형자산 처분" },
          { id: "dart_AcquisitionOfIntangibleAssets",                    label: "무형자산 취득" },
          { id: "dart_ProceedsFromDisposalOfIntangibleAssets",           label: "무형자산 처분" },
          { id: "dart_AcquisitionOfShorttermFinancialInstruments",       label: "단기금융상품 취득" },
          { id: "dart_ProceedsFromShorttermFinancialInstruments",        label: "단기금융상품 처분" },
          { id: "dart_AcquisitionOfLongtermFinancialInstruments",        label: "장기금융상품 취득" },
          { id: "dart_ProceedsFromDisposalOfLongtermFinancialInstruments", label: "장기금융상품 처분" },
          { id: "dart_AcquisitionOfDeposits",                            label: "보증금 지급" },
          { id: "dart_ProceedsFromDisposalOfDeposits",                   label: "보증금 회수" },
          { id: "dart_LoansGranted",                                     label: "대여금 지급" },
          { id: "dart_LoansRepaid",                                      label: "대여금 회수" },
          { id: "dart_AcquisitionOfInvestmentProperty",                  label: "투자부동산 취득" },
          { id: "dart_ProceedsFromDisposalOfInvestmentProperty",         label: "투자부동산 처분" },
          { id: "dart_AcquisitionOfInvestmentsInAssociates",             label: "관계기업 투자" },
          { id: "dart_ProceedsFromDisposalOfInvestmentsInAssociates",    label: "관계기업 처분" },
        ],
      },
      {
        id: "ifrs-full_CashFlowsFromUsedInFinancingActivities",
        label: "재무활동현금흐름",
        children: [
          { id: "dart_ProceedsFromShorttermBorrowings",  label: "단기차입금 차입" },
          { id: "dart_RepaymentOfShorttermBorrowings",   label: "단기차입금 상환" },
          { id: "dart_ProceedsFromLongtermBorrowings",   label: "장기차입금 차입" },
          { id: "dart_RepaymentOfLongtermBorrowings",    label: "장기차입금 상환" },
          { id: "dart_ProceedsFromIssuanceOfCapital",    label: "유상증자" },
          { id: "dart_ProceedsFromIssuanceOfBonds",      label: "사채 발행" },
          { id: "dart_RepaymentOfBonds",                 label: "사채 상환" },
          { id: "ifrs-full_DividendsPaid",               label: "배당금 지급" },
          { id: "ifrs-full_RepaymentsOfLeaseLiabilities", label: "리스부채 상환" },
          { id: "dart_SeverancePay",                     label: "퇴직금 지급" },
        ],
      },
      { id: "ifrs-full_EffectOfExchangeRateChangesOnCashAndCashEquivalents", label: "환율변동효과" },
      { id: "dart_NetIncreaseDecreaseInCash",                               label: "현금 순증감" },
      { id: "ifrs-full_CashAndCashEquivalentsAtBeginningOfPeriod",          label: "기초현금" },
    ],
  },

  {
    sj: "CIS",
    label: "포괄손익계산서",
    sublabel: "Comprehensive Income",
    children: [
      {
        id: "ifrs-full_ComprehensiveIncome",
        label: "총포괄이익",
        children: [
          { id: "ifrs-full_ProfitLoss", label: "당기순이익 (→IS)" },
          {
            id: "ifrs-full_OtherComprehensiveIncome",
            label: "기타포괄손익 (OCI)",
            children: [
              {
                id: "ifrs-full_OtherComprehensiveIncomeThatWillNotBeReclassifiedToProfitOrLossNetOfTax",
                label: "재분류 안 되는 OCI",
              },
              {
                id: "ifrs-full_OtherComprehensiveIncomeThatWillBeReclassifiedToProfitOrLossNetOfTax",
                label: "재분류될 수 있는 OCI",
                children: [
                  { id: "ifrs-full_ReserveOfExchangeDifferencesOnTranslation", label: "해외사업환산손익" },
                  {
                    id: "ifrs-full_OtherComprehensiveIncomeShareOfOtherComprehensiveIncomeOfAssociatesAndJointVenturesAccountedForUsingEquityMethod",
                    label: "지분법자본변동",
                  },
                ],
              },
            ],
          },
          { id: "ifrs-full_ComprehensiveIncomeAttributableToOwnersOfParent", label: "지배기업귀속 포괄이익" },
        ],
      },
    ],
  },
];
