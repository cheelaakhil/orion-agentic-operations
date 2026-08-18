export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "critical" | "high" | "medium" | "low";

export interface Anomaly {
  anomaly_id: string;
  metric: string;
  current_value: number;
  baseline_value: number;
  change_absolute: number;
  change_percentage: number;
  severity: Severity;
  affected_dimension: string;
  status?: string;
  evidence?: {
    baseline_period?: string;
    evaluation_period?: string;
    [key: string]: any;
  };
}

export interface EvidencePackage {
  anomaly_id: string;
  target_metric: string;
  baseline_window: { start: string; end: string };
  evaluation_window: { start: string; end: string };
  generated_at: string;
  revenue: {
    baseline_revenue: number;
    evaluation_revenue: number;
    change_percentage: number;
    by_region_baseline: Record<string, number>;
    by_region_evaluation: Record<string, number>;
    by_category_baseline: Record<string, number>;
    by_category_evaluation: Record<string, number>;
    by_segment_baseline: Record<string, number>;
    by_segment_evaluation: Record<string, number>;
    top_declining_products: Array<{ product_id: string; name: string; revenue: number }>;
  };
  support: {
    baseline_ticket_volume: number;
    evaluation_ticket_volume: number;
    baseline_avg_resolution_hours: number;
    evaluation_avg_resolution_hours: number;
    baseline_median_resolution_hours: number;
    evaluation_median_resolution_hours: number;
    baseline_sla_breach_rate: number;
    evaluation_sla_breach_rate: number;
    baseline_csat: number;
    evaluation_csat: number;
    tickets_by_category: Record<string, number>;
    tickets_by_region: Record<string, number>;
  };
  inventory: {
    baseline_stockout_rate: number;
    evaluation_stockout_rate: number;
    stockout_rate_by_category: Record<string, number>;
    units_sold_baseline: number;
    units_sold_evaluation: number;
    critically_low_products: Array<{ product_id: string; name: string; category: string; quantity: number; region: string }>;
  };
  customers: {
    baseline_repeat_purchase_rate: number;
    evaluation_repeat_purchase_rate: number;
    new_customers_acquired: number;
    repeat_customers_evaluation: number;
    segment_distribution: Record<string, number>;
  };
  marketing: {
    total_spend: number;
    total_conversions: number;
    conversion_rate: number;
    attributed_revenue: number;
    roas: number;
    channel_performance: Array<{ channel: string; spend: number; conversions: number; roas: number }>;
  };
}

export interface InvestigationTimelineStep {
  step_order: number;
  agent_name: string;
  status: string;
  started_at: string;
  completed_at?: string;
  summary?: string;
}

export interface RootCauseHypothesis {
  hypothesis_id: string;
  description: string;
  confidence: number;
  evidence: Array<{
    source_dimension: string;
    metric: string;
    observation: string;
    value?: any;
  }>;
  causal_chain: string[];
  addresses_dimensions?: string[];
}

export interface BusinessImpactReport {
  total_revenue_loss: number;
  customer_churn_count: number;
  projected_30d_risk: number;
  projected_90d_risk: number;
  severity: Severity;
  narrative: string;
}

export interface Recommendation {
  recommendation_id: string;
  investigation_id?: string;
  title: string;
  description: string;
  category: "immediate" | "short_term" | "long_term";
  priority: number;
  expected_impact: string | { metric?: string; estimated_improvement_pct?: number; estimated_revenue_recovery?: number; confidence?: number };
  implementation?: { difficulty?: string; estimated_cost?: number; steps?: string[] };
  risks?: string[];
  requires_human_approval?: boolean;
  requires_approval?: boolean;
  action_type: string;
  approval_status?: string;
  created_at?: string;
}

export interface Investigation {
  investigation_id: string;
  anomaly_id: string;
  status: string;
  confidence_score: number;
  summary: string;
  root_causes?: RootCauseHypothesis[];
  business_impact?: BusinessImpactReport;
  timeline?: InvestigationTimelineStep[];
  observations?: {
    observed?: string[];
    inferred?: string[];
    hypotheses?: string[];
  };
  requires_approval?: boolean;
  started_at: string;
  completed_at?: string;
}

export interface AuditEventItem {
  event_id: string;
  timestamp: string;
  event_type: string;
  entity_type: string;
  entity_id: string;
  action: string;
  actor: string;
  status: string;
  details?: Record<string, any>;
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
}

export interface AgentTraceStep {
  step_id: number;
  timestamp: string;
  agent_role: string;
  tool_called: string;
  tool_safety: string;
  input_summary: string;
  output_summary: string;
  status: string;
  duration_ms: number;
  evidence_type?: string;
  details?: Record<string, any>;
}

export interface AgentRunTrace {
  run_id: string;
  anomaly_id: string;
  status: string;
  started_at: string;
  completed_at?: string;
  steps: AgentTraceStep[];
  active_recommendation_id?: string;
  approval_request_id?: string;
  approval_status?: string;
  simulation_result?: Record<string, any>;
  error?: string;
}

