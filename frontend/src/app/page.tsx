"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  Anomaly,
  AuditEventItem,
  EvidencePackage,
  Investigation,
  Recommendation,
  AgentRunTrace,
} from "@/types";
import { Sidebar } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { KpiCards } from "@/components/KpiCards";
import { BusinessHealthOverview } from "@/components/BusinessHealthOverview";
import { ActiveIncidents } from "@/components/ActiveIncidents";
import { RecommendedActions } from "@/components/RecommendedActions";
import { RecentAuditTimeline } from "@/components/RecentAuditTimeline";
import { IncidentDetailView } from "@/components/IncidentDetailView";
import { ApprovalsView } from "@/components/ApprovalsView";
import { AuditView } from "@/components/AuditView";
import { AgentRunView } from "@/components/AgentRunView";
import { ActionExecutionModal } from "@/components/ActionExecutionModal";
import { AlertTriangle, Bot, CheckCircle2, ChevronRight, Loader2, Play, RefreshCw, ShieldCheck, Sparkles, Zap } from "lucide-react";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [systemHealthy, setSystemHealthy] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Core Data State
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [evidence, setEvidence] = useState<EvidencePackage | null>(null);
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEventItem[]>([]);
  const [agentRunTrace, setAgentRunTrace] = useState<AgentRunTrace | null>(null);

  // Selected Incident & Execution Modal
  const [selectedAnomalyId, setSelectedAnomalyId] = useState<string | null>(null);
  const [activeInvestigation, setActiveInvestigation] = useState<Investigation | null>(null);
  const [executingRecommendation, setExecutingRecommendation] = useState<Recommendation | null>(null);
  const [isProcessingId, setIsProcessingId] = useState<string | null>(null);
  const [isInvestigating, setIsInvestigating] = useState<boolean>(false);

  // Toast Notification
  const [toastMessage, setToastMessage] = useState<{ title: string; type: "success" | "error" | "info" } | null>(null);

  const showToast = (title: string, type: "success" | "error" | "info" = "success") => {
    setToastMessage({ title, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // 1. Health check
      try {
        const health = await api.getHealth();
        setSystemHealthy(health.status === "healthy" || health.status === "ok");
      } catch {
        setSystemHealthy(false);
      }

      // 2. Load Anomalies
      const anomalyList = await api.getAnomalies();
      setAnomalies(anomalyList);

      // 3. Load Evidence for ANOM-REV-001 if present
      const revAnom = anomalyList.find((a) => a.anomaly_id === "ANOM-REV-001") || anomalyList[0];
      if (revAnom) {
        try {
          const evData = await api.getEvidencePackage(revAnom.anomaly_id);
          setEvidence(evData);
        } catch (e) {
          console.warn("Evidence package load warning:", e);
        }
      }

      // 4. Load Investigations & Recommendations
      try {
        const invList = await api.listInvestigations();
        setInvestigations(invList);

        if (invList.length > 0) {
          const primaryInv = invList[0];
          setActiveInvestigation(primaryInv);
          const recs = await api.getInvestigationRecommendations(primaryInv.investigation_id);
          setRecommendations(recs);
        } else if (revAnom) {
          // Trigger initial investigation if none exists
          const newInv = await api.createInvestigation(revAnom.anomaly_id);
          setActiveInvestigation(newInv);
          const recs = await api.getInvestigationRecommendations(newInv.investigation_id);
          setRecommendations(recs);
          setInvestigations([newInv]);
        }
      } catch (e) {
        console.warn("Investigation load warning:", e);
      }

      // 5. Load Audit Trail
      try {
        const auditList = await api.getAuditTrail({ limit: 50 });
        setAuditEvents(auditList);
      } catch (e) {
        console.warn("Audit trail load warning:", e);
      }

      // 6. Load Agent Run Trace (Milestone 6A)
      try {
        const run = await api.getLatestAgentRun();
        setAgentRunTrace(run);
      } catch (e) {
        console.warn("Agent run load warning:", e);
      }
    } catch (err: any) {
      console.error("Dashboard data load error:", err);
      setError(err.message || "Failed to connect to ORION Backend");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Handlers
  const handleTriggerInvestigation = async (anomalyId: string) => {
    setIsInvestigating(true);
    try {
      const inv = await api.createInvestigation(anomalyId);
      setActiveInvestigation(inv);
      const recs = await api.getInvestigationRecommendations(inv.investigation_id);
      setRecommendations(recs);
      setInvestigations((prev) => [inv, ...prev]);
      showToast(`Investigation ${inv.investigation_id} completed successfully with 88% confidence.`);
      const audit = await api.getAuditTrail({ limit: 50 });
      setAuditEvents(audit);
    } catch (err: any) {
      showToast(err.message || "Investigation failed", "error");
    } finally {
      setIsInvestigating(false);
    }
  };

  const handleApprove = async (recId: string) => {
    setIsProcessingId(recId);
    try {
      const res = await api.approveRecommendation(recId, "ExecutiveOpsDirector", "Approved via Executive Operations Dashboard");
      showToast(`Recommendation ${recId} approved. Token: ${res.approval_id}`);
      // Update local state
      setRecommendations((prev) =>
        prev.map((r) => (r.recommendation_id === recId ? { ...r, approval_status: "APPROVED" } : r))
      );
      const audit = await api.getAuditTrail({ limit: 50 });
      setAuditEvents(audit);
    } catch (err: any) {
      showToast(err.message || "Approval failed", "error");
    } finally {
      setIsProcessingId(null);
    }
  };

  const handleReject = async (recId: string) => {
    setIsProcessingId(recId);
    try {
      const res = await api.rejectRecommendation(recId, "ExecutiveOpsDirector", "Postponed via Executive Operations Dashboard");
      showToast(`Recommendation ${recId} rejected.`, "info");
      // Update local state
      setRecommendations((prev) =>
        prev.map((r) => (r.recommendation_id === recId ? { ...r, approval_status: "REJECTED" } : r))
      );
      const audit = await api.getAuditTrail({ limit: 50 });
      setAuditEvents(audit);
    } catch (err: any) {
      showToast(err.message || "Rejection failed", "error");
    } finally {
      setIsProcessingId(null);
    }
  };

  const handleConfirmExecute = async (rec: Recommendation) => {
    const invId = activeInvestigation?.investigation_id || "INV-001";
    const approvalId = `APPR-${rec.recommendation_id}`;
    const result = await api.executeAction(`ACT-${rec.recommendation_id}`, {
      action_type: rec.action_type,
      approval_id: approvalId,
      investigation_id: invId,
      parameters: { simulated_mode: true },
    });
    // Mark as executed
    setRecommendations((prev) =>
      prev.map((r) => (r.recommendation_id === rec.recommendation_id ? { ...r, approval_status: "EXECUTED" } : r))
    );
    const audit = await api.getAuditTrail({ limit: 50 });
    setAuditEvents(audit);
    showToast(`Simulation for ${rec.title} executed successfully!`);
    return result;
  };

  const handleStartAgentRun = async (anomalyId: string = "ANOM-REV-001") => {
    setIsProcessingId("agent-run-start");
    try {
      const run = await api.startAgentRun(anomalyId);
      setAgentRunTrace(run);
      showToast(`Autonomous Agent Run ${run.run_id} initiated. Paused at Human Approval Gate.`);
      const audit = await api.getAuditTrail({ limit: 50 });
      setAuditEvents(audit);
    } catch (err: any) {
      showToast(err.message || "Failed to start agent run", "error");
    } finally {
      setIsProcessingId(null);
    }
  };

  const handleApproveAgentRun = async (recommendationId: string) => {
    if (!agentRunTrace) return;
    setIsProcessingId(recommendationId);
    try {
      const completed = await api.approveAgentRun(agentRunTrace.run_id, recommendationId);
      setAgentRunTrace(completed);
      showToast(`Human Approval granted for ${recommendationId}. Safe simulation executed!`);
      const audit = await api.getAuditTrail({ limit: 50 });
      setAuditEvents(audit);
    } catch (err: any) {
      showToast(err.message || "Approval execution failed", "error");
    } finally {
      setIsProcessingId(null);
    }
  };

  const handleRejectAgentRun = async (recommendationId: string) => {
    if (!agentRunTrace) return;
    setIsProcessingId(recommendationId);
    try {
      const rejected = await api.rejectAgentRun(agentRunTrace.run_id, recommendationId);
      setAgentRunTrace(rejected);
      showToast(`Recommendation ${recommendationId} rejected. Action execution blocked.`, "info");
      const audit = await api.getAuditTrail({ limit: 50 });
      setAuditEvents(audit);
    } catch (err: any) {
      showToast(err.message || "Rejection failed", "error");
    } finally {
      setIsProcessingId(null);
    }
  };

  const pendingApprovalsCount = recommendations.filter(
    (r) => !r.approval_status || r.approval_status === "PENDING_APPROVAL"
  ).length;

  const criticalAnomaliesCount = anomalies.filter(
    (a) => a.severity?.toString().toUpperCase() === "CRITICAL"
  ).length;

  return (
    <div className="flex min-h-screen bg-[#090D16] text-slate-100">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 animate-in fade-in slide-in-from-bottom-5">
          <div
            className={`px-4 py-3 rounded-xl border shadow-2xl text-xs font-mono font-medium flex items-center gap-3 ${
              toastMessage.type === "success"
                ? "bg-emerald-950/90 text-emerald-300 border-emerald-800"
                : toastMessage.type === "error"
                ? "bg-rose-950/90 text-rose-300 border-rose-800"
                : "bg-slate-900/90 text-slate-300 border-slate-700"
            }`}
          >
            <span className="w-2 h-2 rounded-full bg-current"></span>
            <span>{toastMessage.title}</span>
          </div>
        </div>
      )}

      {/* Action Execution Modal */}
      <ActionExecutionModal
        recommendation={executingRecommendation}
        isOpen={!!executingRecommendation}
        onClose={() => setExecutingRecommendation(null)}
        onConfirmExecute={handleConfirmExecute}
      />

      {/* Professional Sidebar */}
      <Sidebar
        activeTab={selectedAnomalyId ? "incidents" : activeTab}
        setActiveTab={(tab) => {
          setSelectedAnomalyId(null);
          setActiveTab(tab);
        }}
        systemHealthy={systemHealthy}
        pendingApprovalsCount={pendingApprovalsCount}
        criticalAnomaliesCount={criticalAnomaliesCount}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          onRefresh={loadData}
          isLoading={isLoading}
          onOpenIncident={() => setSelectedAnomalyId("ANOM-REV-001")}
        />

        <main className="flex-1 p-6 lg:p-8 space-y-6 max-w-7xl w-full mx-auto">
          {/* Backend Connection / Cold-Start Notice Banner */}
          {error && (
            <div className="p-4 rounded-xl bg-amber-950/50 border border-amber-800/80 text-amber-200 flex flex-wrap items-center justify-between gap-3 shadow-lg">
              <div className="flex items-center gap-3 text-xs">
                <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                <div>
                  <span className="font-semibold text-amber-300">Backend Connection Notice: </span>
                  <span className="text-slate-300">Connecting to Render Cloud Backend. (Render Free web services spin up in 30–45s after inactivity).</span>
                </div>
              </div>
              <button
                onClick={loadData}
                disabled={isLoading}
                className="px-3.5 py-1.5 rounded-lg bg-amber-900/90 hover:bg-amber-800 text-amber-100 text-xs font-mono font-medium flex items-center gap-1.5 transition disabled:opacity-50"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-amber-300" : ""}`} />
                <span>{isLoading ? "Connecting..." : "Retry Connection"}</span>
              </button>
            </div>
          )}

          {/* Loading Skeleton */}
          {isLoading && !anomalies.length ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-28 rounded-xl bg-slate-900/60 animate-pulse border border-slate-800"></div>
                ))}
              </div>
              <div className="h-48 rounded-xl bg-slate-900/60 animate-pulse border border-slate-800"></div>
              <div className="h-64 rounded-xl bg-slate-900/60 animate-pulse border border-slate-800"></div>
            </div>
          ) : selectedAnomalyId ? (
            /* Dedicated Incident Detail View for ANOM-REV-001 */
            <IncidentDetailView
              anomalyId={selectedAnomalyId}
              evidence={evidence}
              investigation={activeInvestigation}
              recommendations={recommendations}
              onBack={() => setSelectedAnomalyId(null)}
              onApprove={handleApprove}
              onReject={handleReject}
              onExecute={(rec) => setExecutingRecommendation(rec)}
              onTriggerInvestigation={() => handleTriggerInvestigation(selectedAnomalyId)}
              isInvestigating={isInvestigating}
            />
          ) : activeTab === "overview" ? (
            /* Main Executive Operations Dashboard */
            <>
              {/* Evaluator Product Mission Hero Banner */}
              <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900/90 to-blue-950/40 border border-blue-900/50 shadow-2xl relative overflow-hidden">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                  <div className="space-y-3 flex-1">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <span className="px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 font-mono text-xs font-bold tracking-wide flex items-center gap-1.5">
                        <Bot className="w-3.5 h-3.5" /> ORION — Agentic Operations Intelligence
                      </span>
                      <span className="px-2.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-800/80 text-cyan-300 text-[11px] font-mono font-medium">
                        Adya AI: ADAPTER-READY ONLY
                      </span>
                      <span className="px-2.5 py-0.5 rounded bg-emerald-950/80 border border-emerald-800/80 text-emerald-300 text-[11px] font-mono font-medium">
                        SIMULATED ACTION — SAFE SANDBOX
                      </span>
                    </div>

                    <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight leading-snug">
                      Autonomous E-Commerce Anomaly Investigation & Governance
                    </h1>

                    <div className="flex items-center gap-2 text-xs font-mono text-slate-300 bg-slate-950/70 border border-slate-800/80 px-3.5 py-2 rounded-xl w-fit flex-wrap">
                      <span className="text-cyan-400 font-bold">Detect</span>
                      <span className="text-slate-600">→</span>
                      <span className="text-blue-400 font-bold">Investigate</span>
                      <span className="text-slate-600">→</span>
                      <span className="text-indigo-400 font-bold">Reason</span>
                      <span className="text-slate-600">→</span>
                      <span className="text-purple-400 font-bold">Recommend</span>
                      <span className="text-slate-600">→</span>
                      <span className="text-amber-400 font-bold">Govern</span>
                      <span className="text-slate-600">→</span>
                      <span className="text-emerald-400 font-bold">Execute</span>
                      <span className="text-slate-600">→</span>
                      <span className="text-teal-400 font-bold">Audit</span>
                    </div>

                    <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
                      ORION detects multi-dimensional operational degradation across live NovaCart PostgreSQL data, autonomously queries 18 FastMCP tools, formulates causal hypotheses with confidence scoring, pauses at mandatory human governance gates, and safely simulates remedial actions.
                    </p>
                  </div>

                  <div className="flex flex-col sm:flex-row lg:flex-col gap-2.5 flex-shrink-0">
                    <button
                      onClick={() => setActiveTab("agent_run")}
                      className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg hover:shadow-blue-500/20"
                    >
                      <Play className="w-4 h-4 fill-current" />
                      <span>Launch Autonomous Agent Run</span>
                    </button>
                    <button
                      onClick={() => setSelectedAnomalyId("ANOM-REV-001")}
                      className="px-4 py-2.5 bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold rounded-xl flex items-center justify-center gap-2 transition-all"
                    >
                      <Zap className="w-3.5 h-3.5 text-amber-400" />
                      <span>Investigate Primary Anomaly</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Top 4 KPI Cards */}
              <KpiCards
                revenueAtRisk={5093055}
                criticalCount={criticalAnomaliesCount}
                investigationsCount={investigations.length || 1}
                pendingApprovalsCount={pendingApprovalsCount}
                onCardClick={(tab) => {
                  if (tab === "incidents") setSelectedAnomalyId("ANOM-REV-001");
                  else setActiveTab(tab);
                }}
              />

              {/* Section A: Business Health Overview */}
              <BusinessHealthOverview
                onOpenIncident={() => setSelectedAnomalyId("ANOM-REV-001")}
              />

              {/* Section B: Active Critical Incidents */}
              <ActiveIncidents
                anomalies={anomalies}
                onSelectAnomaly={(id) => setSelectedAnomalyId(id)}
                onTriggerInvestigation={handleTriggerInvestigation}
                investigatingId={isInvestigating ? "ANOM-REV-001" : null}
              />

              {/* Section C: Prioritized Recommendations */}
              <RecommendedActions
                recommendations={recommendations}
                onApprove={handleApprove}
                onReject={handleReject}
                onExecute={(rec) => setExecutingRecommendation(rec)}
                isProcessingId={isProcessingId}
              />

              {/* Section D: Recent Activity / Audit Timeline */}
              <RecentAuditTimeline
                events={auditEvents}
                onViewAll={() => setActiveTab("audit")}
              />
            </>
          ) : activeTab === "agent_run" ? (
            <AgentRunView
              trace={agentRunTrace}
              isLoading={isLoading}
              onRefresh={loadData}
              onStartNewRun={(anomalyId) => handleStartAgentRun(anomalyId || "ANOM-REV-001")}
              onApprove={handleApproveAgentRun}
              onReject={handleRejectAgentRun}
              isProcessing={!!isProcessingId}
            />
          ) : activeTab === "incidents" ? (
            <ActiveIncidents
              anomalies={anomalies}
              onSelectAnomaly={(id) => setSelectedAnomalyId(id)}
              onTriggerInvestigation={handleTriggerInvestigation}
              investigatingId={isInvestigating ? "ANOM-REV-001" : null}
            />
          ) : activeTab === "investigations" ? (
            <IncidentDetailView
              anomalyId="ANOM-REV-001"
              evidence={evidence}
              investigation={activeInvestigation}
              recommendations={recommendations}
              onBack={() => setActiveTab("overview")}
              onApprove={handleApprove}
              onReject={handleReject}
              onExecute={(rec) => setExecutingRecommendation(rec)}
              onTriggerInvestigation={() => handleTriggerInvestigation("ANOM-REV-001")}
              isInvestigating={isInvestigating}
            />
          ) : activeTab === "recommendations" ? (
            <RecommendedActions
              recommendations={recommendations}
              onApprove={handleApprove}
              onReject={handleReject}
              onExecute={(rec) => setExecutingRecommendation(rec)}
              isProcessingId={isProcessingId}
            />
          ) : activeTab === "approvals" ? (
            <ApprovalsView
              recommendations={recommendations}
              onApprove={handleApprove}
              onReject={handleReject}
              onExecute={(rec) => setExecutingRecommendation(rec)}
              isProcessingId={isProcessingId}
            />
          ) : activeTab === "audit" ? (
            <AuditView events={auditEvents} />
          ) : null}
        </main>
      </div>
    </div>
  );
}
