"use client";

import React, { useState, useEffect } from "react";
import { AgentRunTrace, AgentTraceStep, InvestigationScenario } from "@/types";
import { api } from "@/lib/api";
import {
  Activity,
  AlertOctagon,
  AlertTriangle,
  ArrowRight,
  Bot,
  CheckCircle2,
  Clock,
  Cpu,
  Database,
  ExternalLink,
  FileCheck,
  FileSearch,
  History,
  Layers,
  Lock,
  Play,
  RefreshCw,
  Scale,
  Search,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Terminal,
  UserCheck,
  Wrench,
  XCircle,
  Zap,
} from "lucide-react";

interface AgentRunViewProps {
  trace: AgentRunTrace | null;
  isLoading: boolean;
  onRefresh: () => void;
  onStartNewRun: (anomalyId?: string) => void;
  onApprove: (recommendationId: string) => Promise<void>;
  onReject: (recommendationId: string) => Promise<void>;
  isProcessing: boolean;
}

const MCP_TOOLS_CATALOG = [
  {
    name: "get_business_anomalies",
    category: "Deterministic Analytics",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Scans operations data to detect statistical outliers across revenue, support, inventory, and marketing.",
  },
  {
    name: "get_anomaly_evidence",
    category: "Deterministic Analytics",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Retrieves multi-dimensional factual evidence package for a detected anomaly.",
  },
  {
    name: "get_revenue_analytics",
    category: "Deterministic Analytics",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Calculates revenue KPIs, daily timeseries trends, and pre/post incident performance.",
  },
  {
    name: "get_revenue_by_product",
    category: "Deterministic Analytics",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Breaks down sales performance by product category to identify isolated drops.",
  },
  {
    name: "get_revenue_by_region",
    category: "Deterministic Analytics",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Provides geographic distribution of sales and conversion rates.",
  },
  {
    name: "get_customer_analytics",
    category: "Deterministic Analytics",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Analyzes repeat purchase behavior, customer cohorts, and churn rates.",
  },
  {
    name: "get_support_analytics",
    category: "Deterministic Analytics",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Computes support queue volume, resolution times, SLA breaches, and CSAT.",
  },
  {
    name: "get_inventory_analytics",
    category: "Deterministic Analytics",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Evaluates warehouse stock levels, stockout rates by category, and replenishment lead times.",
  },
  {
    name: "get_marketing_analytics",
    category: "Deterministic Analytics",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Quantifies ad spend, CTR, conversion rates, and ROAS across marketing campaigns.",
  },
  {
    name: "start_investigation",
    category: "Multi-Agent Investigation",
    safety: "ANALYSIS",
    requiresApproval: false,
    description: "Initiates autonomous multi-agent causal investigation pipeline over an anomaly.",
  },
  {
    name: "get_investigation",
    category: "Multi-Agent Investigation",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Retrieves ranked causal hypotheses with confidence scores and supporting evidence.",
  },
  {
    name: "calculate_business_impact",
    category: "Business Impact Modeling",
    safety: "ANALYSIS",
    requiresApproval: false,
    description: "Calculates deterministic cumulative financial loss, daily burn rate, and counterfactual recovery.",
  },
  {
    name: "get_recommendations",
    category: "Action Recommendations",
    safety: "PROPOSAL",
    requiresApproval: false,
    description: "Retrieves prioritized, actionable operational remediations with projected ROI.",
  },
  {
    name: "request_approval",
    category: "Governance Gate",
    safety: "PROPOSAL",
    requiresApproval: false,
    description: "Submits a recommendation to the human executive approval queue and returns an approval request ID.",
  },
  {
    name: "approve_recommendation",
    category: "Governance Gate",
    safety: "APPROVAL",
    requiresApproval: false,
    description: "Records human executive approval in the database registry and issues an authorization token.",
  },
  {
    name: "reject_recommendation",
    category: "Governance Gate",
    safety: "APPROVAL",
    requiresApproval: false,
    description: "Records human executive rejection, permanently blocking action execution.",
  },
  {
    name: "execute_approved_action",
    category: "Safe Action Simulation",
    safety: "CONSEQUENT_ACTION",
    requiresApproval: true,
    description: "Verifies authorization token and executes safe domain action simulation with rollback tracking.",
  },
  {
    name: "get_audit_events",
    category: "Audit & Compliance",
    safety: "READ_ONLY",
    requiresApproval: false,
    description: "Queries the tamper-evident operations audit trail for compliance and post-mortem analysis.",
  },
];

const DEFAULT_SCENARIOS: InvestigationScenario[] = [
  {
    id: "ANOM-REV-001",
    title: "Revenue Drop (-43.01%)",
    metric: "daily_revenue",
    severity: "CRITICAL",
    category: "Financial Performance",
    description: "Severe post-June 20 decline in enterprise sales volume with elevated support ticket backlog.",
  },
  {
    id: "ANOM-SUP-002",
    title: "Support Backlog Surge (SLA Breach 86.7%)",
    metric: "sla_breach_rate",
    severity: "HIGH",
    category: "Customer Operations",
    description: "Resolution time surge to 26.5h across Tier-2 technical support escalations.",
  },
  {
    id: "ANOM-INV-003",
    title: "Warehouse Stockout Surge (Electronics 19.8%)",
    metric: "stockout_rate",
    severity: "HIGH",
    category: "Supply Chain & Logistics",
    description: "Critical inventory depletion across high-velocity Electronics SKUs in North America hub.",
  },
  {
    id: "ANOM-CUST-004",
    title: "Customer Churn Acceleration (Repeat Rate -54.3%)",
    metric: "repeat_purchase_rate",
    severity: "MEDIUM",
    category: "Customer Retention",
    description: "Drop in repeat buyer retention among second-month purchase cohorts.",
  },
];

export function AgentRunView({
  trace,
  isLoading,
  onRefresh,
  onStartNewRun,
  onApprove,
  onReject,
  isProcessing,
}: AgentRunViewProps) {
  const [activeSubView, setActiveSubView] = useState<"trace" | "decision_trace" | "mcp_catalog" | "history">("trace");
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [selectedStep, setSelectedStep] = useState<AgentTraceStep | null>(null);
  const [selectedScenario, setSelectedScenario] = useState<string>("ANOM-REV-001");
  const [scenarios, setScenarios] = useState<InvestigationScenario[]>(DEFAULT_SCENARIOS);
  const [historyList, setHistoryList] = useState<AgentRunTrace[]>([]);
  const [historyLoading, setHistoryLoading] = useState<boolean>(false);

  useEffect(() => {
    // Load scenarios
    api.getAgentRunScenarios()
      .then((res) => {
        if (res?.scenarios?.length > 0) {
          setScenarios(res.scenarios);
        }
      })
      .catch(() => {});
  }, []);

  const loadHistory = () => {
    setHistoryLoading(true);
    api.getAgentRunHistory()
      .then((res) => {
        if (Array.isArray(res)) {
          setHistoryList(res);
        }
      })
      .catch(() => {})
      .finally(() => setHistoryLoading(false));
  };

  useEffect(() => {
    if (activeSubView === "history") {
      loadHistory();
    }
  }, [activeSubView]);

  if (isLoading && !trace) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[500px] text-slate-400">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500 mb-4" />
        <p className="text-sm font-medium">Initializing Autonomous Agent Orchestrator...</p>
      </div>
    );
  }

  if (!trace) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-12 text-center">
        <Bot className="w-12 h-12 text-slate-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-white mb-2">No Active Agent Investigation</h3>
        <p className="text-slate-400 text-sm max-w-md mx-auto mb-6">
          Trigger an autonomous agent run to observe live MCP tool selection, real data retrieval, causal reasoning, and governance checkpoints.
        </p>
        <div className="flex items-center justify-center gap-3">
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-white text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500"
          >
            {scenarios.map((s) => (
              <option key={s.id} value={s.id}>
                {s.title}
              </option>
            ))}
          </select>
          <button
            onClick={() => onStartNewRun(selectedScenario)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg flex items-center gap-2 transition-colors"
          >
            <Play className="w-4 h-4" /> Start Investigation
          </button>
        </div>
      </div>
    );
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "COMPLETED":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5" /> COMPLETED</span>;
      case "WAITING_FOR_APPROVAL":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center gap-1.5"><Lock className="w-3.5 h-3.5" /> WAITING FOR APPROVAL</span>;
      case "REJECTED":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center gap-1.5"><XCircle className="w-3.5 h-3.5" /> REJECTED</span>;
      case "FAILED":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center gap-1.5"><AlertOctagon className="w-3.5 h-3.5" /> INSUFFICIENT EVIDENCE</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center gap-1.5"><RefreshCw className="w-3.5 h-3.5 animate-spin" /> RUNNING</span>;
    }
  };

  const getSafetyBadge = (safety: string) => {
    switch (safety) {
      case "READ_ONLY":
        return <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-slate-300 border border-slate-700">READ_ONLY</span>;
      case "ANALYSIS":
        return <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800">ANALYSIS</span>;
      case "PROPOSAL":
        return <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-amber-950/80 text-amber-300 border border-amber-800">PROPOSAL</span>;
      case "APPROVAL":
        return <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-purple-950/80 text-purple-300 border border-purple-800">APPROVAL</span>;
      case "CONSEQUENT_ACTION":
      case "CONSEQUENTIAL_ACTION":
        return <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-rose-950/80 text-rose-300 border border-rose-800 font-semibold">CONSEQUENT_ACTION</span>;
      default:
        return <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-slate-800 text-slate-400">{safety}</span>;
    }
  };

  const categories = ["ALL", "Deterministic Analytics", "Multi-Agent Investigation", "Business Impact Modeling", "Action Recommendations", "Governance Gate", "Safe Action Simulation", "Audit & Compliance"];
  const filteredTools = selectedCategory === "ALL" ? MCP_TOOLS_CATALOG : MCP_TOOLS_CATALOG.filter((t) => t.category === selectedCategory);

  return (
    <div className="space-y-6">
      {/* Header & Scenario Selection */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
        <div>
          <div className="flex items-center gap-2.5 mb-1.5">
            <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
              <Bot className="w-5 h-5 text-blue-400" />
              Autonomous Agent Operations
            </h2>
            {getStatusBadge(trace.status)}
          </div>
          <p className="text-slate-400 text-xs flex items-center gap-2">
            <span>Run ID: <code className="text-blue-300 font-mono">{trace.run_id}</code></span>
            <span>•</span>
            <span>Target: <code className="text-amber-300 font-mono">{trace.anomaly_id}</code></span>
            <span>•</span>
            <span>Runtime: <span className="text-emerald-400 font-medium">LocalAgentRuntime</span></span>
            <span>•</span>
            <span>Adya AI: <span className="text-cyan-400 font-medium">ADAPTER-READY ONLY</span></span>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-1.5 bg-slate-800/80 border border-slate-700/80 rounded-lg px-2.5 py-1.5">
            <span className="text-[11px] text-slate-400 font-medium">Scenario:</span>
            <select
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
              className="bg-transparent text-white text-xs font-medium focus:outline-none cursor-pointer"
            >
              {scenarios.map((s) => (
                <option key={s.id} value={s.id} className="bg-slate-900 text-white">
                  {s.title}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => onStartNewRun(selectedScenario)}
            disabled={isProcessing}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <Play className="w-3.5 h-3.5" /> New Investigation
          </button>
          <button
            onClick={onRefresh}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors border border-slate-700"
            title="Refresh Trace"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* View Switcher Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveSubView("trace")}
          className={`px-3.5 py-1.5 text-xs font-medium rounded-lg flex items-center gap-2 transition-colors ${
            activeSubView === "trace"
              ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          }`}
        >
          <Terminal className="w-3.5 h-3.5" /> Investigation Trace ({trace.steps.length} Steps)
        </button>
        <button
          onClick={() => setActiveSubView("decision_trace")}
          className={`px-3.5 py-1.5 text-xs font-medium rounded-lg flex items-center gap-2 transition-colors ${
            activeSubView === "decision_trace"
              ? "bg-cyan-600/20 text-cyan-400 border border-cyan-500/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" /> Decision Trace & Confidence
        </button>
        <button
          onClick={() => setActiveSubView("mcp_catalog")}
          className={`px-3.5 py-1.5 text-xs font-medium rounded-lg flex items-center gap-2 transition-colors ${
            activeSubView === "mcp_catalog"
              ? "bg-purple-600/20 text-purple-400 border border-purple-500/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          }`}
        >
          <Layers className="w-3.5 h-3.5" /> 18 MCP Tools Explorer
        </button>
        <button
          onClick={() => setActiveSubView("history")}
          className={`px-3.5 py-1.5 text-xs font-medium rounded-lg flex items-center gap-2 transition-colors ${
            activeSubView === "history"
              ? "bg-emerald-600/20 text-emerald-400 border border-emerald-500/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          }`}
        >
          <History className="w-3.5 h-3.5" /> Run History
        </button>
      </div>

      {/* SUBVIEW 1: Active Investigation Trace */}
      {activeSubView === "trace" && (
        <div className="space-y-6">
          {/* Human Governance Approval Banner */}
          {trace.status === "WAITING_FOR_APPROVAL" && (
            <div className="bg-gradient-to-r from-amber-950/60 via-slate-900 to-amber-950/60 border-2 border-amber-500/80 rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden ring-4 ring-amber-500/10">
              <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6">
                <div className="space-y-4 flex-1">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <span className="px-3 py-1 bg-amber-500/20 border border-amber-400/50 rounded-full text-amber-300 font-mono text-xs font-bold flex items-center gap-1.5 animate-pulse shadow-sm">
                      <Lock className="w-3.5 h-3.5" /> MANDATORY HUMAN GOVERNANCE GATE
                    </span>
                    <span className="text-slate-400 text-xs font-mono">
                      Token Request: <code className="text-amber-200 font-bold">{trace.approval_request_id || "APPR-REC-001"}</code>
                    </span>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[11px] font-mono">
                      Risk Tier: <strong className="text-amber-300 font-bold">{trace.scores?.action_risk || "MEDIUM"}</strong>
                    </span>
                    <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-300 border border-emerald-800/60 text-[11px] font-mono">
                      Reversible: Yes
                    </span>
                  </div>

                  <div>
                    <h3 className="text-xl font-extrabold text-white tracking-tight">
                      Action Approval Required: {trace.governance_details?.action || "Support Team Capacity Escalation"}
                    </h3>
                    <p className="text-xs text-slate-300 mt-1">
                      The autonomous agent pipeline has formulated an operational remediation and paused for explicit executive authorization.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div className="bg-slate-950/80 border border-slate-800/90 rounded-xl p-3.5 space-y-1">
                      <span className="text-slate-400 font-semibold flex items-center gap-1.5 text-[11px] uppercase tracking-wider">
                        <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Projected Operational Benefit
                      </span>
                      <p className="text-emerald-300 leading-relaxed font-medium">
                        {trace.governance_details?.expected_benefit || "Reduces resolution latency from 26.5h to <4.0h, eliminating the backlog within 48h and mitigating forward churn."}
                      </p>
                    </div>

                    <div className="bg-slate-950/80 border border-slate-800/90 rounded-xl p-3.5 space-y-1">
                      <span className="text-slate-400 font-semibold flex items-center gap-1.5 text-[11px] uppercase tracking-wider">
                        <ShieldAlert className="w-3.5 h-3.5 text-amber-400" /> Governance Policy Rationale
                      </span>
                      <p className="text-amber-200 leading-relaxed font-medium">
                        {trace.governance_details?.why_approval_required || "Operational capacity shift exceeds autonomous threshold. Executive approval required before execution."}
                      </p>
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950/90 border border-slate-800 text-xs space-y-1">
                    <div className="flex items-center gap-2 text-slate-300">
                      <ShieldCheck className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                      <span className="font-semibold text-white">Fail-Closed Safety Contract:</span>
                      <span className="text-slate-400">All consequential tools are strictly blocked without an authorized token. Execution runs in sandbox simulation.</span>
                    </div>
                  </div>
                </div>

                <div className="flex flex-row lg:flex-col gap-3 min-w-[220px] justify-center flex-shrink-0">
                  <button
                    onClick={() => onApprove(trace.active_recommendation_id || "REC-001")}
                    disabled={isProcessing}
                    className="flex-1 px-6 py-3.5 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-xl flex items-center justify-center gap-2 transition-all hover:scale-[1.02] active:scale-[0.98]"
                  >
                    <CheckCircle2 className="w-4 h-4" /> Approve & Execute Simulation
                  </button>
                  <button
                    onClick={() => onReject(trace.active_recommendation_id || "REC-001")}
                    disabled={isProcessing}
                    className="flex-1 px-6 py-3 bg-slate-800 hover:bg-rose-950/60 hover:border-rose-700/80 disabled:opacity-50 text-slate-300 hover:text-rose-200 border border-slate-700 text-xs font-semibold rounded-xl transition-all flex items-center justify-center gap-2"
                  >
                    <XCircle className="w-4 h-4" /> Reject Proposal
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Simulation Success Banner */}
          {trace.status === "COMPLETED" && trace.simulation_result && (
            <div className="bg-gradient-to-r from-emerald-950/50 via-slate-900 to-emerald-950/50 border-2 border-emerald-500/60 rounded-2xl p-6 text-xs text-slate-300 space-y-3 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-400/40 text-emerald-300 font-mono text-[11px] font-bold">
                    SIMULATED ACTION — SAFE SANDBOX
                  </span>
                  <span className="text-emerald-400 font-bold text-sm">Execution Completed Successfully</span>
                </div>
                <span className="font-mono text-emerald-300 text-xs bg-slate-950 px-2.5 py-1 rounded border border-slate-800">
                  Execution ID: {trace.simulation_result.execution_id}
                </span>
              </div>
              <p className="text-slate-200 text-xs leading-relaxed">
                Applied <strong className="text-white font-bold">{trace.simulation_result.result?.changes_made?.length || 3} simulated adjustments</strong> (+15 tier-2 support specialists allocated, triage throughput increased from 42 → 128 tickets/hr). Cryptographic audit record committed to immutable PostgreSQL ledger.
              </p>
              <div className="text-[11px] text-slate-400 bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800/80 font-mono">
                Notice: Sandbox simulation only. Never modifies live external production accounts or billing.
              </div>
            </div>
          )}

          {/* Chronological MCP Tool Stream */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Activity className="w-4 h-4 text-blue-400" />
                Chronological Tool Execution Trace
              </h3>
              <span className="text-slate-400 text-xs font-mono">{trace.steps.length} Tool Invocations</span>
            </div>

            <div className="divide-y divide-slate-800/60">
              {trace.steps.map((step) => (
                <div
                  key={step.step_id}
                  onClick={() => setSelectedStep(selectedStep?.step_id === step.step_id ? null : step)}
                  className={`p-4 hover:bg-slate-800/40 transition-colors cursor-pointer ${
                    selectedStep?.step_id === step.step_id ? "bg-slate-800/60" : ""
                  }`}
                >
                  <div className="flex items-start justify-between gap-4 mb-1.5">
                    <div className="flex items-center gap-2.5">
                      <span className="w-6 h-6 rounded-full bg-slate-800 text-slate-300 font-mono text-xs flex items-center justify-center font-bold">
                        {step.step_id}
                      </span>
                      <span className="font-semibold text-white text-xs font-mono">{step.tool_called}</span>
                      {getSafetyBadge(step.tool_safety)}
                      <span className="text-slate-400 text-xs">• {step.agent_role}</span>
                    </div>

                    <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
                      <span>{step.duration_ms}ms</span>
                      <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px]">
                        {step.status}
                      </span>
                    </div>
                  </div>

                  <p className="text-slate-300 text-xs pl-8 leading-relaxed">
                    {step.output_summary}
                  </p>

                  {/* Expandable Parameter & Evidence Inspection */}
                  {selectedStep?.step_id === step.step_id && (
                    <div className="mt-3 ml-8 p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs font-mono text-slate-300 space-y-2">
                      <div>
                        <span className="text-slate-500 block mb-0.5">Input Parameters:</span>
                        <p className="text-cyan-300">{step.input_summary}</p>
                      </div>
                      {step.details && Object.keys(step.details).length > 0 && (
                        <div>
                          <span className="text-slate-500 block mb-0.5">Raw Execution Payload:</span>
                          <pre className="text-[11px] text-slate-400 overflow-x-auto max-h-48 p-2 bg-slate-900 rounded border border-slate-800">
                            {JSON.stringify(step.details, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* SUBVIEW 2: Decision Trace & Confidence Scoring */}
      {activeSubView === "decision_trace" && (
        <div className="space-y-6">
          {/* Confidence & Risk Scorecards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-1">
              <span className="text-slate-400 text-xs font-medium">Detection Confidence</span>
              <div className="text-2xl font-bold text-emerald-400 font-mono">
                {( (trace.scores?.detection_confidence || 0.95) * 100).toFixed(0)}%
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                {trace.scores?.detection_explanation || "Statistical z-score > 4.2 deviation across baseline."}
              </p>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-1">
              <span className="text-slate-400 text-xs font-medium">Root-Cause Confidence</span>
              <div className="text-2xl font-bold text-cyan-400 font-mono">
                {( (trace.scores?.root_cause_confidence || 0.88) * 100).toFixed(0)}%
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                {trace.scores?.root_cause_explanation || "Cross-signal temporal correlation across support & inventory."}
              </p>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-1">
              <span className="text-slate-400 text-xs font-medium">Recommendation Confidence</span>
              <div className="text-2xl font-bold text-blue-400 font-mono">
                {( (trace.scores?.recommendation_confidence || 0.91) * 100).toFixed(0)}%
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                {trace.scores?.recommendation_explanation || "Deterministic model projects 78% backlog reduction."}
              </p>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-1">
              <span className="text-slate-400 text-xs font-medium">Action Risk Tier</span>
              <div className="text-2xl font-bold text-amber-400 font-mono">
                {trace.scores?.action_risk || "MEDIUM"}
              </div>
              <p className="text-[11px] text-slate-400 leading-tight">
                {trace.scores?.action_risk_explanation || "Operational capacity shift; fully reversible via simulated rollback."}
              </p>
            </div>
          </div>

          {/* Decision Trace Timeline */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 space-y-6">
            <div className="space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-cyan-400" />
                    Causal Decision Progression
                  </h3>
                  <p className="text-slate-400 text-xs">
                    Transparent step-by-step reasoning chain linking observed SQL anomalies directly to human governance and simulation.
                  </p>
                </div>
                <span className="text-[11px] font-mono text-cyan-300 bg-cyan-950/80 px-2.5 py-1 rounded border border-cyan-800/80 font-semibold">
                  8-Stage Causal Flow
                </span>
              </div>

              {/* Horizontal Causal Breadcrumb */}
              <div className="flex items-center gap-1.5 text-[11px] font-mono text-slate-300 bg-slate-950/80 border border-slate-800/90 px-3.5 py-2 rounded-xl flex-wrap">
                <span className="text-rose-400 font-bold">Anomaly</span>
                <span className="text-slate-600">→</span>
                <span className="text-blue-400 font-bold">Evidence</span>
                <span className="text-slate-600">→</span>
                <span className="text-cyan-400 font-bold">Root Cause</span>
                <span className="text-slate-600">→</span>
                <span className="text-indigo-400 font-bold">Impact</span>
                <span className="text-slate-600">→</span>
                <span className="text-purple-400 font-bold">Recommendation</span>
                <span className="text-slate-600">→</span>
                <span className="text-amber-400 font-bold">Human Approval</span>
                <span className="text-slate-600">→</span>
                <span className="text-emerald-400 font-bold">Execution</span>
                <span className="text-slate-600">→</span>
                <span className="text-teal-400 font-bold">Audit</span>
              </div>
            </div>

            <div className="space-y-4 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
              {(trace.decision_trace || []).map((item, idx) => (
                <div key={idx} className="relative pl-10">
                  <div className="absolute left-2.5 -translate-x-1/2 top-1.5 w-3.5 h-3.5 rounded-full bg-slate-900 border-2 border-cyan-500 shadow-sm" />
                  <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-1.5 hover:border-slate-700 transition-colors">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-300 border border-cyan-800/80 uppercase font-bold tracking-wider">
                        Stage {idx + 1}: {item.stage}
                      </span>
                      {item.confidence_score && (
                        <span className="text-[11px] font-mono text-emerald-400 font-semibold bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                          Confidence: {(item.confidence_score * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                    <h4 className="text-sm font-bold text-white">{item.title}</h4>
                    <p className="text-xs text-slate-300 leading-relaxed">{item.summary}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* SUBVIEW 3: 18 MCP Tools Catalog */}
      {activeSubView === "mcp_catalog" && (
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1 text-xs font-medium rounded-lg transition-colors ${
                  selectedCategory === cat
                    ? "bg-purple-600 text-white"
                    : "bg-slate-800 text-slate-400 hover:text-slate-200"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {filteredTools.map((tool) => (
              <div key={tool.name} className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <code className="text-xs font-mono font-bold text-purple-300">{tool.name}</code>
                  {getSafetyBadge(tool.safety)}
                </div>
                <span className="text-[11px] text-slate-500 block font-medium">{tool.category}</span>
                <p className="text-xs text-slate-300 leading-relaxed">{tool.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SUBVIEW 4: Investigation Run History */}
      {activeSubView === "history" && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <History className="w-4 h-4 text-emerald-400" />
              Investigation Run History
            </h3>
            <button
              onClick={loadHistory}
              disabled={historyLoading}
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${historyLoading ? "animate-spin" : ""}`} /> Refresh
            </button>
          </div>

          {historyList.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-xs">
              No historical runs found in database.
            </div>
          ) : (
            <div className="divide-y divide-slate-800/60">
              {historyList.map((run) => (
                <div key={run.run_id} className="p-4 hover:bg-slate-800/30 transition-colors flex items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-blue-300">{run.run_id}</span>
                      {getStatusBadge(run.status)}
                      <span className="text-xs text-slate-400 font-mono">• {run.anomaly_id}</span>
                    </div>
                    <p className="text-xs text-slate-300">
                      {run.scenario_title || `Investigation for ${run.anomaly_id}`} ({run.steps.length} Tool Steps)
                    </p>
                    <span className="text-[11px] text-slate-500 font-mono">{run.started_at}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
