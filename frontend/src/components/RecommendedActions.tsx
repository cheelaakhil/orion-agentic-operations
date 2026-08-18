"use client";

import React from "react";
import {
  Check,
  CheckCircle2,
  FileCheck,
  Play,
  ShieldAlert,
  X,
  Zap,
} from "lucide-react";
import { Recommendation } from "@/types";

interface RecommendedActionsProps {
  recommendations: Recommendation[];
  onApprove: (recId: string) => void;
  onReject: (recId: string) => void;
  onExecute: (rec: Recommendation) => void;
  isProcessingId?: string | null;
}

export function RecommendedActions({
  recommendations,
  onApprove,
  onReject,
  onExecute,
  isProcessingId,
}: RecommendedActionsProps) {
  return (
    <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800 backdrop-blur">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-emerald-400" />
            Prioritized Recommended Actions
          </h2>
          <p className="text-xs text-slate-400">
            Evidence-backed remediation actions ranked by impact, feasibility, and risk
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono px-2.5 py-1 rounded bg-amber-950/80 text-amber-400 border border-amber-800/60 font-semibold flex items-center gap-1.5">
            <ShieldAlert className="w-3.5 h-3.5" />
            Human Approval Enforced
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {recommendations.map((rec) => {
          const status = rec.approval_status || "PENDING_APPROVAL";
          const isPending = status === "PENDING_APPROVAL";
          const isApproved = status === "APPROVED";
          const isRejected = status === "REJECTED";
          const isExecuted = status === "EXECUTED";
          const isBusy = isProcessingId === rec.recommendation_id;

          const impactStr =
            typeof rec.expected_impact === "string"
              ? rec.expected_impact
              : rec.expected_impact?.estimated_revenue_recovery
              ? `+$${(rec.expected_impact.estimated_revenue_recovery / 1000).toFixed(0)}k est. recovery (${rec.expected_impact.metric || "metric"})`
              : "Projected operational recovery";

          return (
            <div
              key={rec.recommendation_id}
              className={`p-5 rounded-lg bg-slate-950/80 border transition-all flex flex-col justify-between ${
                isApproved
                  ? "border-emerald-800/60 bg-gradient-to-b from-emerald-950/20 to-slate-950"
                  : isRejected
                  ? "border-slate-800/80 opacity-70"
                  : "border-slate-800 hover:border-slate-700"
              }`}
            >
              <div>
                {/* Header */}
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800/60">
                      Priority {rec.priority}
                    </span>
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-semibold">
                      {rec.category}
                    </span>
                  </div>

                  {/* Status Badge */}
                  <span
                    className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded font-bold border ${
                      isApproved
                        ? "bg-emerald-950 text-emerald-400 border-emerald-800/80"
                        : isRejected
                        ? "bg-rose-950 text-rose-400 border-rose-800/80"
                        : isExecuted
                        ? "bg-cyan-950 text-cyan-400 border-cyan-800/80"
                        : "bg-amber-950 text-amber-400 border-amber-800/80"
                    }`}
                  >
                    {status.replace("_", " ")}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-slate-100 mb-1">{rec.title}</h3>
                <p className="text-xs text-slate-400 line-clamp-2 mb-3">{rec.description}</p>

                {/* Impact Pill */}
                <div className="p-2.5 rounded-md bg-slate-900/90 border border-slate-800 text-xs font-mono space-y-1">
                  <div className="flex items-center justify-between text-slate-300">
                    <span className="text-slate-400 font-sans">Expected Impact:</span>
                    <span className="text-emerald-400 font-semibold truncate max-w-[200px]">{impactStr}</span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400">
                    <span>Action: <code className="text-cyan-400">{rec.action_type}</code></span>
                    <span>Risk: <strong className="text-slate-300">{rec.risks?.[0] ? "Low / Controlled" : "Low"}</strong></span>
                  </div>
                </div>
              </div>

              {/* Actions Footer */}
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
                <div className="text-[11px] text-slate-500 font-mono">
                  ID: {rec.recommendation_id}
                </div>

                <div className="flex items-center gap-2">
                  {isPending && (
                    <>
                      <button
                        onClick={() => onReject(rec.recommendation_id)}
                        disabled={isBusy}
                        className="px-3 py-1.5 rounded-md bg-slate-900 hover:bg-rose-950/60 hover:text-rose-300 text-slate-400 border border-slate-800 text-xs font-medium transition-colors flex items-center gap-1 disabled:opacity-50"
                      >
                        <X className="w-3.5 h-3.5" />
                        <span>Reject</span>
                      </button>

                      <button
                        onClick={() => onApprove(rec.recommendation_id)}
                        disabled={isBusy}
                        className="px-3.5 py-1.5 rounded-md bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-colors flex items-center gap-1.5 shadow-sm disabled:opacity-50"
                      >
                        <Check className="w-3.5 h-3.5" />
                        <span>Approve</span>
                      </button>
                    </>
                  )}

                  {isApproved && (
                    <button
                      onClick={() => onExecute(rec)}
                      disabled={isBusy}
                      className="px-3.5 py-1.5 rounded-md bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold transition-colors flex items-center gap-1.5 shadow-md shadow-cyan-600/20 disabled:opacity-50"
                    >
                      <Play className="w-3.5 h-3.5 fill-current" />
                      <span>Execute Safe Simulation</span>
                    </button>
                  )}

                  {isExecuted && (
                    <span className="text-xs text-emerald-400 font-mono flex items-center gap-1 font-medium">
                      <CheckCircle2 className="w-4 h-4" />
                      Simulation Completed
                    </span>
                  )}

                  {isRejected && (
                    <span className="text-xs text-rose-400 font-mono font-medium">
                      Action Blocked
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
