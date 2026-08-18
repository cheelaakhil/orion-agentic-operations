import {
  Anomaly,
  AuditEventItem,
  EvidencePackage,
  HealthCheckResponse,
  Investigation,
  Recommendation,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

async function fetcher<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!res.ok) {
      let errorMsg = `API request failed with status ${res.status}`;
      try {
        const errorData = await res.json();
        if (errorData?.detail) {
          errorMsg = typeof errorData.detail === "string" ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch {
        // use default error message
      }
      throw new Error(errorMsg);
    }

    return await res.json();
  } catch (err: any) {
    console.error(`Fetch Error [${endpoint}]:`, err);
    throw err;
  }
}

export const api = {
  // System Health
  getHealth: () => fetcher<HealthCheckResponse>("/health"),

  // Anomalies
  getAnomalies: (params?: { start_date?: string; end_date?: string; dimension?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetcher<Anomaly[]>(`/anomalies${query ? `?${query}` : ""}`);
  },

  getEvidencePackage: (anomalyId: string) =>
    fetcher<EvidencePackage>(`/anomalies/${anomalyId}/evidence`),

  // Analytics
  getRevenueAnalytics: (params?: { start_date?: string; end_date?: string; granularity?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetcher<any>(`/analytics/revenue${query ? `?${query}` : ""}`);
  },

  getSupportAnalytics: (params?: { start_date?: string; end_date?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetcher<any>(`/analytics/support${query ? `?${query}` : ""}`);
  },

  getInventoryAnalytics: (params?: { start_date?: string; end_date?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetcher<any>(`/analytics/inventory${query ? `?${query}` : ""}`);
  },

  getCustomersAnalytics: (params?: { start_date?: string; end_date?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetcher<any>(`/analytics/customers${query ? `?${query}` : ""}`);
  },

  getMarketingAnalytics: (params?: { start_date?: string; end_date?: string }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetcher<any>(`/analytics/marketing${query ? `?${query}` : ""}`);
  },

  // Investigations
  createInvestigation: (anomalyId: string, dimensions?: string[]) =>
    fetcher<any>("/investigations", {
      method: "POST",
      body: JSON.stringify({ anomaly_id: anomalyId, dimensions }),
    }),

  listInvestigations: (limit = 20, offset = 0) =>
    fetcher<Investigation[]>(`/investigations?limit=${limit}&offset=${offset}`),

  getInvestigation: (investigationId: string) =>
    fetcher<Investigation>(`/investigations/${investigationId}`),

  getInvestigationRecommendations: (investigationId: string) =>
    fetcher<Recommendation[]>(`/investigations/${investigationId}/recommendations`),

  // Recommendations & Human Approval
  approveRecommendation: (recommendationId: string, decidedBy = "OperationsExecutive", reason = "Approved via Executive Operations Dashboard") =>
    fetcher<{ status: string; approval_id: string; message: string }>(
      `/recommendations/${recommendationId}/approve`,
      {
        method: "POST",
        body: JSON.stringify({ decided_by: decidedBy, decision_reason: reason }),
      }
    ),

  rejectRecommendation: (recommendationId: string, decidedBy = "OperationsExecutive", reason = "Rejected via Executive Operations Dashboard") =>
    fetcher<{ status: string; approval_id: string; message: string }>(
      `/recommendations/${recommendationId}/reject`,
      {
        method: "POST",
        body: JSON.stringify({ decided_by: decidedBy, decision_reason: reason }),
      }
    ),

  // Action Execution (Safe Simulation)
  executeAction: (actionId: string, payload: { action_type: string; approval_id: string; investigation_id: string; parameters?: any }) =>
    fetcher<any>(`/actions/${actionId}/execute`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  // Audit Trail
  getAuditTrail: (params?: { event_type?: string; entity_id?: string; limit?: number; offset?: number }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetcher<AuditEventItem[]>(`/audit${query ? `?${query}` : ""}`);
  },

  // Agent Run Orchestration (Milestone 6A)
  startAgentRun: (anomalyId: string = "ANOM-REV-001") =>
    fetcher<any>("/agent-run/start", {
      method: "POST",
      body: JSON.stringify({ anomaly_id: anomalyId }),
    }),

  getLatestAgentRun: () =>
    fetcher<any>("/agent-run/latest"),

  getAgentRun: (runId: string) =>
    fetcher<any>(`/agent-run/${runId}`),

  approveAgentRun: (runId: string, recommendationId: string, approver = "ExecutiveOperationsVP", reason = "Approved via Agent Run Dashboard") =>
    fetcher<any>(`/agent-run/${runId}/approve`, {
      method: "POST",
      body: JSON.stringify({ recommendation_id: recommendationId, approver, reason }),
    }),

  rejectAgentRun: (runId: string, recommendationId: string, rejector = "ExecutiveOperationsVP", reason = "Rejected via Agent Run Dashboard") =>
    fetcher<any>(`/agent-run/${runId}/reject`, {
      method: "POST",
      body: JSON.stringify({ recommendation_id: recommendationId, rejector, reason }),
    }),
};

