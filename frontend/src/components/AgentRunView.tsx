"use client";

import React, { useState } from "react";
import { AgentRunTrace, AgentTraceStep } from "@/types";
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
  Lock,
  Play,
  RefreshCw,
  Scale,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Terminal,
  UserCheck,
  XCircle,
  Zap,
} from "lucide-react";

interface AgentRunViewProps {
  trace: AgentRunTrace | null;
  isLoading: boolean;
  onRefresh: () => void;
  onStartNewRun: () => void;
  onApprove: (recommendationId: string) => Promise<void>;
  onReject: (recommendationId: string) => Promise<void>;
  isProcessing: boolean;
}

export function AgentRunView({
  trace,
  isLoading,
  onRefresh,
  onStartNewRun,
  onApprove,
  onReject,
  isProcessing,
}: AgentRunViewProps) {
  const [selectedStep, setSelectedStep] = useState<AgentTraceStep | null>(null);

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
          Launch an autonomous multi-agent run over the verified MCP tool layer to investigate root causes, quantify loss, and generate remediation proposals.
        </p>
        <button
          onClick={onStartNewRun}
          disabled={isProcessing}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium shadow-lg shadow-blue-900/30 transition"
        >
          <Play className="w-4 h-4" />
          Start Agent Investigation (ANOM-REV-001)
        </button>
      </div>
    );
  }

  const isWaitingApproval = trace.status === "WAITING_FOR_APPROVAL";
  const isCompleted = trace.status === "COMPLETED";
  const isRejected = trace.status === "REJECTED";

  // Nodes for visualization pipeline
  const workflowNodes = [
    { id: "detect", label: "DETECT", agent: "Supervisor", tool: "get_business_anomalies", step: 1 },
    { id: "evidence", label: "EVIDENCE", agent: "Data Analyst", tool: "get_anomaly_evidence", step: 2 },
    { id: "investigate", label: "INVESTIGATE", agent: "Investigator", tool: "start_investigation", step: 3 },
    { id: "root_cause", label: "ROOT CAUSE", agent: "Root Cause", tool: "get_investigation", step: 4 },
    { id: "impact", label: "IMPACT", agent: "Business Impact", tool: "calculate_business_impact", step: 5 },
    { id: "recommend", label: "RECOMMEND", agent: "Recommendation", tool: "get_recommendations", step: 6 },
    { id: "approval", label: "APPROVAL GATE", agent: "Governance", tool: "request_approval", step: 7 },
    { id: "execute", label: "EXECUTE", agent: "Action Agent", tool: "execute_approved_action", step: 9 },
    { id: "audit", label: "AUDIT", agent: "Audit Agent", tool: "get_audit_events", step: 10 },
  ];

  const getStepStatus = (nodeStep: number) => {
    const stepCount = trace.steps.length;
    if (nodeStep <= 7) {
      return "completed";
    }
    if (nodeStep === 7) {
      return isWaitingApproval ? "waiting" : "completed";
    }
    if (nodeStep > 7 && isWaitingApproval) {
      return "pending";
    }
    if (nodeStep > 7 && isRejected) {
      return "blocked";
    }
    if (nodeStep <= stepCount) {
      return "completed";
    }
    return "pending";
  };

  const getSafetyBadgeColor = (safety: string) => {
    switch (safety) {
      case "READ_ONLY":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
      case "ANALYSIS":
        return "bg-blue-500/10 text-blue-400 border-blue-500/30";
      case "PROPOSAL":
        return "bg-purple-500/10 text-purple-400 border-purple-500/30";
      case "APPROVAL":
        return "bg-amber-500/10 text-amber-400 border-amber-500/30";
      case "CONSEQUENTIAL_ACTION":
        return "bg-rose-500/10 text-rose-400 border-rose-500/30";
      default:
        return "bg-slate-700 text-slate-300 border-slate-600";
    }
  };

  const getEvidenceBadgeColor = (type?: string) => {
    switch (type) {
      case "OBSERVED":
        return "bg-emerald-950/80 text-emerald-300 border-emerald-600/40";
      case "INFERRED":
        return "bg-blue-950/80 text-blue-300 border-blue-600/40";
      case "HYPOTHESIS":
        return "bg-purple-950/80 text-purple-300 border-purple-600/40";
      case "PROPOSAL":
        return "bg-amber-950/80 text-amber-300 border-amber-600/40";
      case "ACTION_RESULT":
        return "bg-rose-950/80 text-rose-300 border-rose-600/40";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Header Banner */}
      <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-6 shadow-xl backdrop-blur">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="px-2.5 py-1 text-xs font-semibold rounded-md bg-blue-500/20 text-blue-400 border border-blue-500/30 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5" />
                PROVIDER-AGNOSTIC AGENT RUNTIME
              </span>
              <span className="text-xs text-slate-400 font-mono">Run ID: {trace.run_id}</span>
              <span
                className={`px-2.5 py-0.5 text-xs font-semibold rounded-full border ${
                  isWaitingApproval
                    ? "bg-amber-500/10 text-amber-400 border-amber-500/30 animate-pulse"
                    : isCompleted
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                    : isRejected
                    ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
                    : "bg-blue-500/10 text-blue-400 border-blue-500/30"
                }`}
              >
                {trace.status.replace(/_/g, " ")}
              </span>
            </div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              Autonomous Investigation on <span className="text-blue-400 font-mono">{trace.anomaly_id}</span>
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Deterministic multi-agent execution pipeline orchestrating 18 verified ORION MCP business tools.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onRefresh}
              disabled={isLoading || isProcessing}
              className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium rounded-lg border border-slate-700 flex items-center gap-1.5 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <button
              onClick={onStartNewRun}
              disabled={isProcessing}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-lg shadow-blue-900/30 flex items-center gap-1.5 transition"
            >
              <Play className="w-3.5 h-3.5" />
              New Agent Investigation
            </button>
          </div>
        </div>
      </div>

      {/* 2. Agent Workflow Pipeline Visualization */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg">
        <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-400" />
          Autonomous Agent Capability Graph
        </h2>
        <div className="overflow-x-auto pb-2">
          <div className="flex items-center min-w-[760px] justify-between">
            {workflowNodes.map((node, idx) => {
              const status = getStepStatus(node.step);
              return (
                <React.Fragment key={node.id}>
                  <div className="flex flex-col items-center text-center group">
                    <div
                      className={`w-10 h-10 rounded-xl border flex items-center justify-center transition-all ${
                        status === "completed"
                          ? "bg-emerald-950/80 border-emerald-500 text-emerald-400 shadow-lg shadow-emerald-950/50"
                          : status === "waiting"
                          ? "bg-amber-950/90 border-amber-400 text-amber-300 ring-2 ring-amber-400/40 animate-pulse"
                          : status === "blocked"
                          ? "bg-rose-950/80 border-rose-500 text-rose-400"
                          : "bg-slate-800/80 border-slate-700 text-slate-500"
                      }`}
                    >
                      {status === "completed" ? (
                        <CheckCircle2 className="w-5 h-5" />
                      ) : status === "waiting" ? (
                        <Lock className="w-5 h-5" />
                      ) : status === "blocked" ? (
                        <XCircle className="w-5 h-5" />
                      ) : (
                        <Bot className="w-5 h-5" />
                      )}
                    </div>
                    <span className="text-[11px] font-bold text-slate-200 mt-2">{node.label}</span>
                    <span className="text-[10px] text-slate-400 truncate max-w-[80px]">{node.agent}</span>
                    <span className="text-[9px] font-mono text-slate-500 truncate max-w-[90px]">{node.tool}</span>
                  </div>
                  {idx < workflowNodes.length - 1 && (
                    <div
                      className={`flex-1 h-0.5 mx-2 rounded ${
                        getStepStatus(workflowNodes[idx + 1].step) === "completed"
                          ? "bg-emerald-500"
                          : "bg-slate-700"
                      }`}
                    />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      </div>

      {/* 3. Interactive Human Approval Gate (Prominent Card) */}
      {isWaitingApproval && (
        <div className="bg-gradient-to-r from-amber-950/60 via-slate-900 to-amber-950/40 border-2 border-amber-500/80 rounded-xl p-6 shadow-2xl relative overflow-hidden">
          <div className="absolute -top-12 -right-12 w-40 h-40 bg-amber-500/10 rounded-full blur-3xl" />
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative z-10">
            <div className="space-y-2 max-w-2xl">
              <div className="flex items-center gap-2">
                <span className="px-2 py-0.5 text-[11px] font-bold uppercase rounded bg-amber-500 text-slate-950 flex items-center gap-1">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  HUMAN GOVERNANCE GATE
                </span>
                <span className="text-xs text-amber-300 font-medium">Autonomous Execution Paused</span>
              </div>
              <h3 className="text-lg font-bold text-white">
                Human Executive Authorization Required for {trace.active_recommendation_id}
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                The Recommendation Agent proposes applying emergency support capacity reallocation (+15 Tier-1/Tier-2 specialists, automated triage deployment) to mitigate severe SLA breaches. Consequential actions require explicit human operator approval before safe simulation execution.
              </p>
              <div className="flex flex-wrap gap-4 pt-1 text-xs">
                <div className="bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
                  <span className="text-slate-400">Target Action:</span>{" "}
                  <span className="font-mono text-amber-300">adjust_support_staffing</span>
                </div>
                <div className="bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
                  <span className="text-slate-400">Expected Recovery:</span>{" "}
                  <span className="font-semibold text-emerald-400">$350,000.00 (+25.0%)</span>
                </div>
                <div className="bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800">
                  <span className="text-slate-400">Agent Confidence:</span>{" "}
                  <span className="font-semibold text-blue-400">88.0% Grounded</span>
                </div>
              </div>
            </div>

            <div className="flex sm:flex-col gap-3 w-full md:w-auto">
              <button
                onClick={() => trace.active_recommendation_id && onApprove(trace.active_recommendation_id)}
                disabled={isProcessing}
                className="flex-1 md:flex-none px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg shadow-lg shadow-emerald-950/50 flex items-center justify-center gap-2 transition"
              >
                <UserCheck className="w-4 h-4" />
                APPROVE & EXECUTE SIMULATION
              </button>
              <button
                onClick={() => trace.active_recommendation_id && onReject(trace.active_recommendation_id)}
                disabled={isProcessing}
                className="flex-1 md:flex-none px-6 py-3 bg-rose-950/80 hover:bg-rose-900/90 text-rose-300 border border-rose-700/60 text-xs font-bold rounded-lg flex items-center justify-center gap-2 transition"
              >
                <XCircle className="w-4 h-4" />
                REJECT PROPOSAL
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 4. Safe Simulation Completed Card */}
      {isCompleted && trace.simulation_result && (
        <div className="bg-emerald-950/30 border border-emerald-500/40 rounded-xl p-6 shadow-xl">
          <div className="flex items-center gap-2 mb-3">
            <span className="px-2.5 py-0.5 text-xs font-bold rounded bg-emerald-500 text-slate-950 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5" />
              {trace.simulation_result.execution_mode || "SIMULATED ACTION"}
            </span>
            <span className="text-xs text-emerald-400 font-mono">
              Execution ID: {trace.simulation_result.execution_id}
            </span>
            <span className="text-xs text-slate-400 ml-auto font-mono">
              {trace.simulation_result.executed_at}
            </span>
          </div>
          <h3 className="text-base font-bold text-white mb-2">
            Safe Operational Simulation Completed Successfully
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 my-3">
            {trace.simulation_result.result?.changes_made?.map((change: string, idx: number) => (
              <div key={idx} className="bg-slate-950/70 p-3 rounded-lg border border-slate-800 text-xs text-slate-200 flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>{change}</span>
              </div>
            ))}
          </div>
          <p className="text-[11px] text-slate-400 italic">
            * All changes executed within safe sandbox boundaries. Rollback instructions and audit events committed to immutable operations log.
          </p>
        </div>
      )}

      {/* 5. Live Agent Execution Trace (Detailed Step Logs) */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-bold text-white flex items-center gap-2">
            <Terminal className="w-4 h-4 text-blue-400" />
            Structured Agent Execution Trace ({trace.steps.length} Steps)
          </h2>
          <span className="text-xs text-slate-400 font-mono">
            Provider: ORION LocalAgentRuntime (MCP-First)
          </span>
        </div>

        <div className="space-y-3">
          {trace.steps.map((step) => (
            <div
              key={step.step_id}
              onClick={() => setSelectedStep(step)}
              className="bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 rounded-lg p-4 transition cursor-pointer"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-md bg-slate-800 text-slate-300 text-xs font-mono font-bold flex items-center justify-center">
                    {step.step_id}
                  </span>
                  <span className="text-xs font-bold text-white">{step.agent_role}</span>
                  <ArrowRight className="w-3 h-3 text-slate-600" />
                  <span className="text-xs font-mono text-blue-400 bg-blue-950/60 px-2 py-0.5 rounded border border-blue-800/40">
                    {step.tool_called}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getSafetyBadgeColor(step.tool_safety)}`}>
                    {step.tool_safety}
                  </span>
                  {step.evidence_type && (
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${getEvidenceBadgeColor(step.evidence_type)}`}>
                      {step.evidence_type}
                    </span>
                  )}
                  <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {step.duration_ms}ms
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/60">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Input Summary
                  </span>
                  <p className="text-slate-300 text-xs">{step.input_summary}</p>
                </div>
                <div className="bg-slate-900/60 p-2.5 rounded border border-slate-800/60">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                    Output Summary
                  </span>
                  <p className="text-slate-200 text-xs">{step.output_summary}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
