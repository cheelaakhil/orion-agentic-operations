"use client";

import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Cpu,
  Loader2,
  Play,
  ShieldCheck,
  Terminal,
  X,
} from "lucide-react";
import { Recommendation } from "@/types";

interface ActionModalProps {
  recommendation: Recommendation | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirmExecute: (rec: Recommendation) => Promise<any>;
}

export function ActionExecutionModal({
  recommendation,
  isOpen,
  onClose,
  onConfirmExecute,
}: ActionModalProps) {
  const [step, setStep] = useState<"ready" | "executing" | "completed" | "error">("ready");
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      setStep("ready");
      setExecutionResult(null);
      setErrorMsg(null);
    }
  }, [isOpen]);

  if (!isOpen || !recommendation) return null;

  const handleRun = async () => {
    setStep("executing");
    try {
      const result = await onConfirmExecute(recommendation);
      setExecutionResult(result);
      setStep("completed");
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to execute simulated action");
      setStep("error");
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-[#0F172A] border border-cyan-800/80 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="p-5 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-400">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base font-bold text-slate-100">Safe Operational Action Execution</h3>
                <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                  SIMULATED ACTION
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">Action ID: {recommendation.action_type}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg hover:bg-slate-800 text-slate-400">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Workflow State Tracker */}
        <div className="p-5 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between text-xs font-mono">
          <div className="flex items-center gap-2 text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
            <span>1. Human Approved</span>
          </div>
          <div className="h-0.5 w-12 bg-slate-800"></div>
          <div className={`flex items-center gap-2 ${step === "executing" ? "text-cyan-400 animate-pulse" : step === "completed" ? "text-emerald-400" : "text-slate-500"}`}>
            <Terminal className="w-4 h-4" />
            <span>2. Executing Simulation</span>
          </div>
          <div className="h-0.5 w-12 bg-slate-800"></div>
          <div className={`flex items-center gap-2 ${step === "completed" ? "text-emerald-400 font-bold" : "text-slate-500"}`}>
            <CheckCircle2 className="w-4 h-4" />
            <span>3. Completed & Logged</span>
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto font-mono text-xs">
          <div className="p-3.5 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1">
            <span className="text-slate-400">Target Proposal:</span>
            <p className="text-slate-200 font-bold font-sans">{recommendation.title}</p>
            <p className="text-slate-400 font-sans text-xs pt-1">{recommendation.description}</p>
          </div>

          {step === "ready" && (
            <div className="p-4 rounded-lg bg-cyan-950/20 border border-cyan-800/40 text-cyan-300 font-sans space-y-2">
              <p className="font-semibold text-xs flex items-center gap-2">
                <Play className="w-3.5 h-3.5 fill-current" />
                Ready to initiate controlled simulation.
              </p>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                This execution runs against verified local models and will dispatch operational updates to the simulated support queue and inventory registers. Full telemetry will be appended to the immutable audit trail.
              </p>
            </div>
          )}

          {step === "executing" && (
            <div className="p-6 rounded-lg bg-slate-950 border border-cyan-800/60 flex flex-col items-center justify-center gap-3 text-cyan-400">
              <Loader2 className="w-8 h-8 animate-spin" />
              <span className="font-bold">Executing domain simulation handler...</span>
              <span className="text-[11px] text-slate-400">Simulating resource reallocations and queue dispatch</span>
            </div>
          )}

          {step === "completed" && executionResult && (
            <div className="space-y-3">
              <div className="p-4 rounded-lg bg-emerald-950/30 border border-emerald-800/60 text-emerald-300 space-y-2">
                <div className="flex items-center gap-2 font-bold text-sm">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Simulation Succeeded (Execution ID: {executionResult.execution_id})</span>
                </div>
                <p className="text-xs text-slate-300 font-sans">
                  The following operational adjustments were safely simulated:
                </p>
                <ul className="space-y-1 pt-1 text-slate-200 text-xs">
                  {executionResult.result?.changes_made?.map((change: string, i: number) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-emerald-400">✓</span>
                      <span>{change}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-400">
                <span>Affected Metrics: </span>
                <strong className="text-cyan-400">
                  {executionResult.result?.metrics_affected?.join(", ")}
                </strong>
              </div>
            </div>
          )}

          {step === "error" && (
            <div className="p-4 rounded-lg bg-rose-950/40 border border-rose-800/80 text-rose-300 space-y-1">
              <div className="flex items-center gap-2 font-bold text-xs">
                <AlertTriangle className="w-4 h-4 text-rose-400" />
                <span>Simulation Execution Blocked</span>
              </div>
              <p className="text-xs text-rose-200 font-mono">{errorMsg}</p>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-900 border-t border-slate-800 flex items-center justify-end gap-3">
          {step === "ready" && (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={handleRun}
                className="px-5 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold transition-all shadow-md shadow-cyan-600/30 flex items-center gap-2"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Confirm & Run Simulation</span>
              </button>
            </>
          )}

          {step === "completed" && (
            <button
              onClick={onClose}
              className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all"
            >
              Close & Return to Dashboard
            </button>
          )}

          {step === "error" && (
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold"
            >
              Dismiss
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
