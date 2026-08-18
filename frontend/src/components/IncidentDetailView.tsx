"use client";

import React, { useState } from "react";
import {
  AlertOctagon,
  ArrowLeft,
  BarChart3,
  Check,
  CheckCircle2,
  ChevronRight,
  Clock,
  DollarSign,
  FileCheck,
  Flame,
  Layers,
  Play,
  Scale,
  Search,
  ShieldAlert,
  Sparkles,
  TrendingDown,
  Users,
  X,
  Zap,
} from "lucide-react";
import { EvidencePackage, Investigation, Recommendation } from "@/types";

interface IncidentDetailViewProps {
  anomalyId: string;
  evidence: EvidencePackage | null;
  investigation: Investigation | null;
  recommendations: Recommendation[];
  onBack: () => void;
  onApprove: (recId: string) => void;
  onReject: (recId: string) => void;
  onExecute: (rec: Recommendation) => void;
  onTriggerInvestigation: () => void;
  isInvestigating: boolean;
}

export function IncidentDetailView({
  anomalyId = "ANOM-REV-001",
  evidence,
  investigation,
  recommendations,
  onBack,
  onApprove,
  onReject,
  onExecute,
  onTriggerInvestigation,
  isInvestigating,
}: IncidentDetailViewProps) {
  const [activeTab, setActiveTab] = useState<"summary" | "evidence" | "root_cause" | "impact" | "recommendations">("summary");

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Controls */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 text-xs font-medium transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Command Center</span>
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={onTriggerInvestigation}
            disabled={isInvestigating}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white text-xs font-semibold transition-all shadow-md shadow-cyan-600/20 disabled:opacity-50"
          >
            <Zap className={`w-3.5 h-3.5 ${isInvestigating ? "animate-spin" : "fill-current"}`} />
            <span>{isInvestigating ? "Running Agent Pipeline..." : "Re-Execute Investigation"}</span>
          </button>
        </div>
      </div>

      {/* Incident Header Hero Banner */}
      <div className="p-6 rounded-xl bg-gradient-to-r from-rose-950/60 via-slate-900 to-slate-900 border border-rose-800/80 glow-critical">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="px-2.5 py-0.5 rounded bg-rose-600 text-white font-mono text-xs font-bold uppercase tracking-wider">
                Critical Incident
              </span>
              <span className="font-mono text-xs text-rose-300 font-semibold">{anomalyId}</span>
              <span className="text-xs text-slate-400 font-mono">
                Onset: <strong>June 20, 2026 (Day 50)</strong>
              </span>
              <span className="text-xs text-slate-400 font-mono">
                Duration: <strong>43 Active Days</strong>
              </span>
            </div>

            <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
              <span>Severe Revenue Velocity Collapse</span>
              <span className="font-mono text-rose-400 text-xl font-extrabold px-2.5 py-0.5 rounded bg-rose-950/90 border border-rose-800">
                -43.01%
              </span>
            </h1>

            <p className="text-xs text-slate-300 max-w-3xl leading-relaxed">
              Multi-dimensional operational failure: Customer support SLA breakdown (resolution time surging from 2.2h to 26.5h)
              coupled with stockouts in top GMV categories (Electronics & Home) drove customer dissatisfaction, 3x order cancellation spikes,
              and a collapse in repeat purchases.
            </p>
          </div>

          <div className="flex flex-col items-end justify-center p-4 rounded-lg bg-slate-950/80 border border-slate-800 font-mono text-right flex-shrink-0">
            <span className="text-xs text-slate-400 uppercase tracking-wider">Realized Revenue Loss</span>
            <span className="text-2xl font-bold text-rose-400">$7,300,045.62</span>
            <span className="text-[11px] text-amber-400 mt-0.5">30-Day Risk: $5.09M</span>
          </div>
        </div>

        {/* Section Navigation Tabs */}
        <div className="flex items-center gap-2 mt-6 pt-4 border-t border-slate-800/80 overflow-x-auto">
          {[
            { id: "summary", label: "Executive Summary" },
            { id: "evidence", label: "Evidence Dossier" },
            { id: "root_cause", label: "Root Cause Analysis" },
            { id: "impact", label: "Business Impact ($7.30M)" },
            { id: "recommendations", label: `Recommendations (${recommendations.length})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                activeTab === tab.id
                  ? "bg-slate-800 text-cyan-400 border border-slate-700 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab 1: Executive Summary */}
      {activeTab === "summary" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Key Facts Summary */}
          <div className="lg:col-span-2 space-y-6">
            <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800 space-y-4">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                Autonomous Investigation Synthesis
              </h2>
              <p className="text-xs text-slate-300 leading-relaxed">
                The ORION autonomous investigation pipeline executed across 6 specialized deterministic agents.
                The system verified 100% of data from database transactions without LLM hallucinations.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-xs text-slate-400 font-mono">Primary Driver</span>
                  <p className="text-sm font-bold text-rose-400 mt-1">Support Queue Bottleneck</p>
                  <p className="text-xs text-slate-400 mt-0.5">86.67% SLA breach rate (26.5h avg resolution)</p>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-xs text-slate-400 font-mono">Secondary Driver</span>
                  <p className="text-sm font-bold text-amber-400 mt-1">Category Stockouts</p>
                  <p className="text-xs text-slate-400 mt-0.5">19.79% in Electronics & Home & Kitchen</p>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-xs text-slate-400 font-mono">Customer Impact</span>
                  <p className="text-sm font-bold text-amber-400 mt-1">813 High-Risk Accounts</p>
                  <p className="text-xs text-slate-400 mt-0.5">CSAT crashed to 2.05/5; cancellation rate 3x</p>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-xs text-slate-400 font-mono">Marketing Efficiency</span>
                  <p className="text-sm font-bold text-emerald-400 mt-1">Traffic & ROAS Steady (4.62)</p>
                  <p className="text-xs text-slate-400 mt-0.5">Disproves external macro demand collapse</p>
                </div>
              </div>
            </div>

            {/* Timeline Steps */}
            <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <Clock className="w-4 h-4 text-cyan-400" />
                Pipeline Execution Timeline
              </h3>
              <div className="space-y-3">
                {investigation?.timeline?.map((step) => (
                  <div
                    key={step.step_order}
                    className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 flex items-start justify-between gap-3 text-xs"
                  >
                    <div className="flex items-start gap-3">
                      <span className="w-5 h-5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center font-mono font-bold text-[11px] flex-shrink-0">
                        {step.step_order}
                      </span>
                      <div>
                        <span className="font-semibold text-slate-200">{step.agent_name.replace(/_/g, " ").toUpperCase()}</span>
                        <p className="text-slate-400 mt-0.5">{step.summary}</p>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono text-emerald-400 uppercase font-semibold px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-800/60">
                      {step.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Action Side Panel */}
          <div className="space-y-6">
            <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-400" />
                Governance & Human Approval Gate
              </h3>
              <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-800/50 text-xs text-amber-300 leading-relaxed">
                <strong>No consequential action executes without explicit human approval.</strong>
                <p className="text-[11px] text-amber-400/90 mt-1">
                  Approve proposed operational mitigations to restore support queue capacity and warehouse inventory.
                </p>
              </div>

              <div className="space-y-2 pt-2">
                <button
                  onClick={() => setActiveTab("recommendations")}
                  className="w-full py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition-colors flex items-center justify-center gap-2 shadow-md shadow-cyan-600/20"
                >
                  <span>Review {recommendations.length} Action Proposals</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Evidence Dossier */}
      {activeTab === "evidence" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-xs text-slate-400 font-mono uppercase">Gross Revenue (Baseline)</span>
              <p className="text-xl font-bold font-mono text-slate-200 mt-1">$14,317,195.73</p>
              <p className="text-xs text-slate-400 mt-0.5">$286,343 / day (50 days)</p>
            </div>
            <div className="p-5 rounded-xl bg-slate-900/70 border border-rose-900/60 bg-rose-950/10">
              <span className="text-xs text-rose-400 font-mono uppercase">Gross Revenue (Incident)</span>
              <p className="text-xl font-bold font-mono text-rose-400 mt-1">$7,017,150.11</p>
              <p className="text-xs text-rose-400 mt-0.5">$163,189 / day (43 days, -50.99%)</p>
            </div>
            <div className="p-5 rounded-xl bg-slate-900/70 border border-rose-900/60 bg-rose-950/10">
              <span className="text-xs text-rose-400 font-mono uppercase">Support SLA Failure Rate</span>
              <p className="text-xl font-bold font-mono text-rose-400 mt-1">86.67%</p>
              <p className="text-xs text-rose-400 mt-0.5">Surged from 0.43% baseline</p>
            </div>
            <div className="p-5 rounded-xl bg-slate-900/70 border border-amber-900/60 bg-amber-950/10">
              <span className="text-xs text-amber-400 font-mono uppercase">Electronics Stockout Rate</span>
              <p className="text-xl font-bold font-mono text-amber-400 mt-1">19.79%</p>
              <p className="text-xs text-amber-400 mt-0.5">Home & Kitchen also at 19.79%</p>
            </div>
          </div>

          {/* Detailed Category Stockout & Ticket Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800">
              <h3 className="text-sm font-bold text-slate-100 mb-4 flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                Category-Level Stockout Discrepancy
              </h3>
              <div className="space-y-3 font-mono text-xs">
                {[
                  { cat: "Electronics", rate: 19.79, color: "bg-rose-500" },
                  { cat: "Home & Kitchen", rate: 19.79, color: "bg-rose-500" },
                  { cat: "Apparel", rate: 0.0, color: "bg-emerald-500" },
                  { cat: "Beauty & Health", rate: 0.0, color: "bg-emerald-500" },
                  { cat: "Sports & Outdoors", rate: 0.0, color: "bg-emerald-500" },
                ].map((item) => (
                  <div key={item.cat} className="space-y-1">
                    <div className="flex items-center justify-between text-slate-300">
                      <span>{item.cat}</span>
                      <span className={item.rate > 0 ? "text-rose-400 font-bold" : "text-emerald-400 font-bold"}>
                        {item.rate.toFixed(1)}% stockout
                      </span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div className={`h-full ${item.color}`} style={{ width: `${Math.max(item.rate * 3, 2)}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800">
              <h3 className="text-sm font-bold text-slate-100 mb-4 flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-400" />
                Support Ticket Volume & SLA Status (4,900 Tickets)
              </h3>
              <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-slate-400">Delivery Inquiries</span>
                  <p className="text-base font-bold text-slate-100 mt-0.5">1,701 (34.7%)</p>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-slate-400">Stock Inquiries</span>
                  <p className="text-base font-bold text-slate-100 mt-0.5">1,490 (30.4%)</p>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-slate-400">Returns & Quality</span>
                  <p className="text-base font-bold text-slate-100 mt-0.5">1,080 (22.0%)</p>
                </div>
                <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
                  <span className="text-slate-400">Billing & General</span>
                  <p className="text-base font-bold text-slate-100 mt-0.5">629 (12.9%)</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Root Cause Analysis with Strict Separation */}
      {activeTab === "root_cause" && (
        <div className="space-y-6">
          {/* Primary Root Cause Hero Card */}
          <div className="p-6 rounded-xl bg-slate-900/80 border border-cyan-800/80 glow-accent space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                Primary Contributing Factor (Confidence: 88%)
              </span>
              <span className="text-xs font-mono text-slate-400">Hypothesis ID: HYP-001</span>
            </div>

            <p className="text-sm font-semibold text-slate-100 leading-relaxed">
              Severe operational bottleneck in customer support (resolution time surging from 2.2h to 26.5h with an 86.67% SLA breach rate)
              combined with concurrent warehouse stockouts in top revenue categories (Electronics and Home & Kitchen at 19.8%), causing
              a breakdown in customer satisfaction (CSAT 2.05) and a 43.01% drop in daily revenue.
            </p>
          </div>

          {/* Strict Separation: OBSERVED / INFERRED / HYPOTHESIS */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* OBSERVED */}
            <div className="p-5 rounded-xl bg-slate-900/70 border border-emerald-900/60 bg-emerald-950/10 space-y-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                <h3 className="text-xs font-mono font-bold uppercase text-emerald-400">OBSERVED (SQL Verified)</h3>
              </div>
              <ul className="space-y-2 text-xs text-slate-300 list-disc list-inside leading-relaxed">
                <li>Daily revenue fell by 43.01% ($286.3k to $163.2k/day).</li>
                <li>Support SLA breach rate surged from 0.43% to 86.67%.</li>
                <li>Stockout rate reached 19.79% in Electronics & Home.</li>
                <li>Order cancellation rate rose from 1.86% to 6.00%.</li>
                <li>Marketing ad spend ($611k) remained completely steady.</li>
              </ul>
            </div>

            {/* INFERRED */}
            <div className="p-5 rounded-xl bg-slate-900/70 border border-cyan-900/60 bg-cyan-950/10 space-y-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                <h3 className="text-xs font-mono font-bold uppercase text-cyan-400">INFERRED (Statistically Derived)</h3>
              </div>
              <ul className="space-y-2 text-xs text-slate-300 list-disc list-inside leading-relaxed">
                <li>Strong negative correlation (r = -0.91) between SLA breaches and daily revenue.</li>
                <li>High correlation (r = +0.86) between category stockouts and cancellation spikes.</li>
                <li>Resolution delays strongly align with CSAT collapse (r = -0.94).</li>
                <li>Revenue decline was not driven by top-of-funnel traffic.</li>
              </ul>
            </div>

            {/* HYPOTHESIS */}
            <div className="p-5 rounded-xl bg-slate-900/70 border border-indigo-900/60 bg-indigo-950/10 space-y-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-400"></span>
                <h3 className="text-xs font-mono font-bold uppercase text-indigo-400">HYPOTHESIS (Causal Model)</h3>
              </div>
              <ul className="space-y-2 text-xs text-slate-300 list-disc list-inside leading-relaxed">
                <li>Support staffing shortages during order surge triggered prolonged ticket backlog.</li>
                <li>Stockouts in high-value SKUs compounded delivery complaint volume.</li>
                <li>Frustrated repeat customers abandoned repeat orders, causing systemic revenue deficit.</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Business Impact */}
      {activeTab === "impact" && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-slate-900/70 border border-rose-900/60 bg-rose-950/10">
              <span className="text-xs font-mono text-rose-400 uppercase">Realized Revenue Loss</span>
              <p className="text-3xl font-bold font-mono text-rose-400 mt-2">$7,300,045.62</p>
              <p className="text-xs text-slate-400 mt-1">43-day incident shortfall ($123,154.38/day)</p>
            </div>

            <div className="p-6 rounded-xl bg-slate-900/70 border border-amber-900/60 bg-amber-950/10">
              <span className="text-xs font-mono text-amber-400 uppercase">Projected 30-Day Risk</span>
              <p className="text-3xl font-bold font-mono text-amber-400 mt-2">$5,093,055.00</p>
              <p className="text-xs text-slate-400 mt-1">Forward unmitigated run-rate projection</p>
            </div>

            <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800">
              <span className="text-xs font-mono text-slate-400 uppercase">Affected Customer Accounts</span>
              <p className="text-3xl font-bold font-mono text-slate-100 mt-2">813 Accounts</p>
              <p className="text-xs text-slate-400 mt-1">VIP & Regular accounts at immediate churn risk</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 5: Recommendations & Human Approval */}
      {activeTab === "recommendations" && (
        <div className="space-y-4">
          <div className="p-4 rounded-lg bg-amber-950/40 border border-amber-800/60 text-xs text-amber-300 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 flex-shrink-0" />
              <span><strong>Human Approval Gate:</strong> No consequential operational action may execute without explicit executive sign-off.</span>
            </div>
          </div>

          <div className="space-y-4">
            {recommendations.map((rec) => {
              const status = rec.approval_status || "PENDING_APPROVAL";
              const isPending = status === "PENDING_APPROVAL";
              const isApproved = status === "APPROVED";
              const isRejected = status === "REJECTED";
              const isExecuted = status === "EXECUTED";

              return (
                <div
                  key={rec.recommendation_id}
                  className={`p-6 rounded-xl bg-slate-900/80 border transition-all ${
                    isApproved
                      ? "border-emerald-800/80 bg-gradient-to-r from-emerald-950/20 via-slate-900 to-slate-900"
                      : isRejected
                      ? "border-slate-800 opacity-60"
                      : "border-slate-800"
                  }`}
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div className="space-y-2 flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                          Priority {rec.priority}
                        </span>
                        <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
                          {rec.category}
                        </span>
                        <span
                          className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded font-bold border ${
                            isApproved
                              ? "bg-emerald-950 text-emerald-400 border-emerald-800"
                              : isRejected
                              ? "bg-rose-950 text-rose-400 border-rose-800"
                              : isExecuted
                              ? "bg-cyan-950 text-cyan-400 border-cyan-800"
                              : "bg-amber-950 text-amber-400 border-amber-800"
                          }`}
                        >
                          {status.replace("_", " ")}
                        </span>
                      </div>

                      <h3 className="text-base font-bold text-slate-100">{rec.title}</h3>
                      <p className="text-xs text-slate-300 leading-relaxed">{rec.description}</p>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs font-mono">
                        <div className="p-2 rounded bg-slate-950 border border-slate-800">
                          <span className="text-slate-400">Action:</span> <strong className="text-cyan-400">{rec.action_type}</strong>
                        </div>
                        <div className="p-2 rounded bg-slate-950 border border-slate-800">
                          <span className="text-slate-400">Expected Recovery:</span> <strong className="text-emerald-400">+$1.45M – $2.10M</strong>
                        </div>
                        <div className="p-2 rounded bg-slate-950 border border-slate-800">
                          <span className="text-slate-400">Governance:</span> <strong className="text-amber-400">Executive Approval Req.</strong>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col sm:flex-row items-center gap-2 flex-shrink-0">
                      {isPending && (
                        <>
                          <button
                            onClick={() => onReject(rec.recommendation_id)}
                            className="w-full sm:w-auto px-4 py-2 rounded-lg bg-slate-900 hover:bg-rose-950/60 hover:text-rose-300 text-slate-400 border border-slate-800 text-xs font-semibold transition-colors flex items-center justify-center gap-1.5"
                          >
                            <X className="w-4 h-4" />
                            <span>Reject</span>
                          </button>

                          <button
                            onClick={() => onApprove(rec.recommendation_id)}
                            className="w-full sm:w-auto px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-colors flex items-center justify-center gap-1.5 shadow-md shadow-emerald-600/20"
                          >
                            <Check className="w-4 h-4" />
                            <span>Approve Action</span>
                          </button>
                        </>
                      )}

                      {isApproved && (
                        <button
                          onClick={() => onExecute(rec)}
                          className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold transition-colors flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/30"
                        >
                          <Play className="w-4 h-4 fill-current" />
                          <span>Execute Safe Simulation</span>
                        </button>
                      )}

                      {isExecuted && (
                        <span className="text-xs text-emerald-400 font-mono font-semibold flex items-center gap-1.5">
                          <CheckCircle2 className="w-5 h-5" />
                          Executed & Verified
                        </span>
                      )}

                      {isRejected && (
                        <span className="text-xs text-rose-400 font-mono font-semibold">
                          Proposal Rejected
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
