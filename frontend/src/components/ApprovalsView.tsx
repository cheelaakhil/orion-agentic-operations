"use client";

import React, { useState } from "react";
import {
  AlertTriangle,
  Check,
  CheckCircle2,
  Filter,
  Play,
  ShieldAlert,
  ShieldCheck,
  X,
  XCircle,
} from "lucide-react";
import { Recommendation } from "@/types";

interface ApprovalsViewProps {
  recommendations: Recommendation[];
  onApprove: (recId: string) => void;
  onReject: (recId: string) => void;
  onExecute: (rec: Recommendation) => void;
  isProcessingId?: string | null;
}

export function ApprovalsView({
  recommendations,
  onApprove,
  onReject,
  onExecute,
  isProcessingId,
}: ApprovalsViewProps) {
  const [filter, setFilter] = useState<"ALL" | "PENDING_APPROVAL" | "APPROVED" | "REJECTED">("ALL");

  const filteredRecs = recommendations.filter((r) => {
    const status = r.approval_status || "PENDING_APPROVAL";
    if (filter === "ALL") return true;
    return status === filter;
  });

  return (
    <div className="space-y-6">
      {/* Governance Banner */}
      <div className="p-5 rounded-xl bg-gradient-to-r from-amber-950/40 via-slate-900 to-slate-900 border border-amber-800/60 flex items-start gap-4">
        <div className="p-3 rounded-lg bg-amber-950 border border-amber-800/80 text-amber-400 flex-shrink-0">
          <ShieldAlert className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
            Executive Human-in-the-Loop Governance Queue
          </h2>
          <p className="text-xs text-slate-300 mt-1 leading-relaxed max-w-3xl">
            In compliance with ORION operational safety guidelines, no autonomous action may modify systems or execute simulations without explicit human executive authorization.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-xs text-slate-400 font-mono">Filter by State:</span>
          {(["ALL", "PENDING_APPROVAL", "APPROVED", "REJECTED"] as const).map((st) => (
            <button
              key={st}
              onClick={() => setFilter(st)}
              className={`px-3 py-1 rounded-md text-xs font-mono font-medium transition-colors ${
                filter === st
                  ? "bg-cyan-950 text-cyan-400 border border-cyan-800"
                  : "bg-slate-900 text-slate-400 border border-slate-800 hover:text-slate-200"
              }`}
            >
              {st.replace("_", " ")}
            </button>
          ))}
        </div>

        <span className="text-xs font-mono text-slate-400">
          Showing {filteredRecs.length} of {recommendations.length} action proposals
        </span>
      </div>

      {/* Approvals Table / Card Stack */}
      <div className="space-y-4">
        {filteredRecs.map((rec) => {
          const status = rec.approval_status || "PENDING_APPROVAL";
          const isPending = status === "PENDING_APPROVAL";
          const isApproved = status === "APPROVED";
          const isRejected = status === "REJECTED";
          const isExecuted = status === "EXECUTED";
          const isBusy = isProcessingId === rec.recommendation_id;

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
                    <span className="text-xs font-mono text-slate-400">
                      ID: {rec.recommendation_id}
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
                  <p className="text-xs text-slate-300 leading-relaxed max-w-4xl">{rec.description}</p>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2 text-xs font-mono">
                    <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                      <span className="text-slate-400">Action:</span> <strong className="text-cyan-400">{rec.action_type}</strong>
                    </div>
                    <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                      <span className="text-slate-400">Expected Recovery:</span> <strong className="text-emerald-400">+$1.45M – $2.10M</strong>
                    </div>
                    <div className="p-2.5 rounded bg-slate-950 border border-slate-800">
                      <span className="text-slate-400">Target Root Cause:</span> <strong className="text-slate-200">HYP-001</strong>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row items-center gap-2 flex-shrink-0">
                  {isPending && (
                    <>
                      <button
                        onClick={() => onReject(rec.recommendation_id)}
                        disabled={isBusy}
                        className="w-full sm:w-auto px-4 py-2 rounded-lg bg-slate-900 hover:bg-rose-950/60 hover:text-rose-300 text-slate-400 border border-slate-800 text-xs font-semibold transition-colors flex items-center justify-center gap-1.5 disabled:opacity-50"
                      >
                        <X className="w-4 h-4" />
                        <span>Reject</span>
                      </button>

                      <button
                        onClick={() => onApprove(rec.recommendation_id)}
                        disabled={isBusy}
                        className="w-full sm:w-auto px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-colors flex items-center justify-center gap-1.5 shadow-md shadow-emerald-600/20 disabled:opacity-50"
                      >
                        <Check className="w-4 h-4" />
                        <span>Approve Action</span>
                      </button>
                    </>
                  )}

                  {isApproved && (
                    <button
                      onClick={() => onExecute(rec)}
                      disabled={isBusy}
                      className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold transition-colors flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/30"
                    >
                      <Play className="w-4 h-4 fill-current" />
                      <span>Execute Safe Simulation</span>
                    </button>
                  )}

                  {isExecuted && (
                    <span className="text-xs text-emerald-400 font-mono font-semibold flex items-center gap-1.5">
                      <CheckCircle2 className="w-5 h-5" />
                      Simulation Executed
                    </span>
                  )}

                  {isRejected && (
                    <span className="text-xs text-rose-400 font-mono font-semibold flex items-center gap-1.5">
                      <XCircle className="w-5 h-5" />
                      Rejected by Operator
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
