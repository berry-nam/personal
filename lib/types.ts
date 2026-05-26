export interface ReviewItem {
  norm: string;
  sj: "BS" | "IS" | "CFS" | "CIS";
  n: number;
  conf: number | null;
  method: string;
  top3: string[];
  status: "flagged" | "needs_review";
}

export interface Cluster {
  canonical_id: string;
  total_cw: number;
  items: ReviewItem[];
}

export interface ReviewData {
  generated_at: string;
  stats: {
    clusters: number;
    flagged: number;
    needs_review: number;
    total_cw: number;
    flagged_cw: number;
    nr_cw: number;
  };
  clusters: Cluster[];
  unresolved: ReviewItem[];
}

export type DecisionAction = "approved" | "overridden" | "skipped";

export interface Decision {
  action: DecisionAction;
  canonical_id: string;
  original_canonical: string;
  note?: string;
}

// key: `${norm}||${sj}`
export type DecisionMap = Record<string, Decision>;

export interface SeedEntry {
  norm: string;
  canonical_id: string;
  sj: "BS" | "IS" | "CFS" | "CIS";
}

export interface SeedsData {
  generated_at: string;
  count: number;
  seeds: SeedEntry[];
}
