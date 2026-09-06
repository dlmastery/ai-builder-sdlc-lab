// Hand-mirrored from the API's OpenAPI schema until `pnpm gen:api` regenerates `api.gen.ts`.
// Keep shapes identical to apps/api/src/ledgerlens_api/schemas.py.

export type SessionOut = {
  user: { id: string; email: string; display_name: string };
  tenant: { id: string; name: string; slug: string };
  role: string;
  csrf_token: string;
};

export type ModelVersionOut = {
  id: string;
  kind: string;
  name: string;
  pinned: boolean;
  config: Record<string, unknown>;
  metrics: Record<string, unknown>;
  created_at: string;
};

export type JobOut = {
  id: string;
  kind: string;
  status: string;
  queue: string;
  attempts: number;
  error: string | null;
  created_at: string;
};

export type DocumentOut = {
  id: string;
  kind: string;
  original_filename: string;
  status: string;
  page_count: number;
  difficulty: number | null;
  vendor_id: string | null;
  created_at: string;
  updated_at: string;
};

export type DocumentRowOut = DocumentOut & {
  thumbnail_url: string | null;
  vendor_name: string | null;
  decision: string | null;
  reasons: Array<Record<string, unknown>>;
  field_count: number;
  grounded_fields: number;
};

export type AlternativeOut = { rank: number; value: string | null; probability: number };

export type CorrectionOut = { old_value: string | null; new_value: string | null; created_at: string };

export type FieldOut = {
  id: string;
  name: string;
  line_index: number | null;
  value: string | null;
  normalized_value: string | null;
  raw_confidence: number | null;
  calibrated_confidence: number | null;
  grounded: boolean;
  boxes: number[][];
  stability: number | null;
  alternatives: AlternativeOut[];
  corrections: CorrectionOut[];
};

export type OcrWordOut = { text: string; box: number[]; score: number };

export type SignalOut = {
  id: string;
  kind: string;
  scope: string | null;
  evidence: Record<string, unknown>;
  intent_path: string | null;
  status: string;
  created_at: string;
};

export type SubscriptionOut = {
  plan: PlanOut;
  provider: string;
  status: string;
  current_period_end: string | null;
} | null;

export type VerifierResultOut = {
  rule: string;
  passed: boolean;
  field_id: string | null;
  detail: Record<string, unknown> | null;
};

export type VerdictOut = {
  decision: string;
  reasons: Array<Record<string, unknown>>;
  threshold: number | null;
};

export type ExtractionOut = {
  id: string;
  model_version: ModelVersionOut;
  ocr_version: ModelVersionOut | null;
  latency_ms: number | null;
  fields: FieldOut[];
  verifier_results: VerifierResultOut[];
  verdict: VerdictOut | null;
  created_at: string;
};

export type PageOut = {
  number: number;
  width: number;
  height: number;
  image_url: string;
  quality: Record<string, number> | null;
  ocr_words: OcrWordOut[];
};

export type DocumentDetailOut = DocumentOut & {
  pages: PageOut[];
  extraction: ExtractionOut | null;
  job: JobOut | null;
  vendor_name: string | null;
  approved: boolean;
};

export type Paginated<T> = { items: T[]; total: number };

export type PlanOut = {
  code: string;
  name: string;
  monthly_price_cents: number;
  included_documents: number;
  per_document_cents: number;
  features: string[];
};

export type DatasetOut = {
  id: string;
  name: string;
  kind: string;
  sources: Array<Record<string, unknown>>;
  split_policy: Record<string, unknown>;
  counts: Record<string, number>;
  created_at: string;
};

export type EvalScoreOut = {
  field_name: string | null;
  vendor_id: string | null;
  split: string;
  metric: string;
  value: number;
  support: number | null;
};

export type FieldStats = {
  tp: number;
  fp: number;
  fn: number;
  precision: number;
  recall: number;
  f1: number;
  support: number;
};

export type EvalSummary = {
  split: string;
  documents: number;
  field_f1: number;
  per_field: Record<string, FieldStats>;
  per_vendor: Record<string, Record<string, FieldStats>>;
  latency_ms_p50: number | null;
  errors_sample: Array<{ item_id: string; field: string; truth: unknown; pred: unknown }>;
  evaluated_at: string;
};

export type ModelVersionDetailOut = ModelVersionOut & {
  parent_id: string | null;
  dataset_id: string | null;
  job_id: string | null;
  artifact_object_key: string | null;
  card: string | null;
  eval_summary: EvalSummary | null;
  scores: EvalScoreOut[];
  pinned_at: string | null;
};

export type VendorOut = {
  id: string;
  name: string;
  documents: number;
  corrections: number;
  curve: Array<{
    model_version: string;
    fields: number;
    corrections: number;
    accuracy: number | null;
    created_at: string | null;
  }>;
};

export type ProductionOut = {
  pinned: Record<string, ModelVersionOut>;
  documents: Record<string, number>;
  jobs: Record<string, number>;
  billing_provider: string;
  open_signals: number;
};
