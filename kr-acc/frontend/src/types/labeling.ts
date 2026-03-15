/** TypeScript types for the labeling tool API. */

export interface LabelingUser {
  id: number;
  email: string;
  display_name: string;
  role: "labeler" | "admin";
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: LabelingUser;
}

export interface TaskSummary {
  id: number;
  query_id: string;
  query_text: string;
  query_metadata: QueryMetadata;
  status: "pending" | "assigned" | "completed" | "reviewed";
  assigned_to: number | null;
  assigned_at: string | null;
  completed_at: string | null;
  created_at: string;
  result_count: number;
  label_count: number;
}

export interface QueryMetadata {
  uc: string;
  sector: string;
  size: string;
  complexity: string;
  source: string;
  audit: string;
}

export interface TaskResult {
  id: number;
  company_name: string;
  company_metadata: Record<string, unknown> | null;
  rank_position: number | null;
}

export interface RubricScore {
  criterion_id: number;
  criterion_name?: string;
  score: "yes" | "partially" | "no";
  note: string | null;
}

export interface Label {
  id: number;
  result_id: number;
  labeler_id: number;
  overall_rating: number;
  rank_position: number | null;
  justification: string | null;
  rubric_scores: RubricScore[];
}

export interface TaskDetail {
  id: number;
  query_id: string;
  query_text: string;
  query_metadata: QueryMetadata;
  status: string;
  assigned_to: number | null;
  results: TaskResult[];
  labels: Label[];
}

export interface TaskListResponse {
  items: TaskSummary[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface RubricCriterion {
  id: number;
  name: string;
  description: string | null;
  weight: number;
  criteria_type: string;
  display_order: number;
  is_active: boolean;
}

export interface LabelInput {
  result_id: number;
  overall_rating: number;
  rank_position: number | null;
  justification: string | null;
  rubric_scores: { criterion_id: number; score: string; note?: string | null }[];
}

export interface LabelerStats {
  id: number;
  name: string;
  email: string;
  role: string;
  completed: number;
  assigned: number;
  current_task: string | null;
}

export interface ProgressStats {
  total_tasks: number;
  pending: number;
  assigned: number;
  completed: number;
  reviewed: number;
  per_labeler: LabelerStats[];
}

export interface LabelerInfo {
  id: number;
  display_name: string;
  email: string;
  role: string;
}
