"use client";

import React from "react";
import {
  AlertOctagon,
  ArrowRight,
  ChevronRight,
  Clock,
  Layers,
  Sparkles,
  Zap,
} from "lucide-react";
import { Anomaly } from "@/types";

interface ActiveIncidentsProps {
  anomalies: Anomaly[];
  onSelectAnomaly: (anomalyId: string) => void;
  onTriggerInvestigation: (anomalyId: string) => void;
  investigatingId?: string | null;
}

export function ActiveIncidents({
  anomalies,
  onSelectAnomaly,
  onTriggerInvestigation,
  investigatingId,
}: ActiveIncidentsProps) {
  return (
    <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800 backdrop-blur">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <AlertOctagon className="w-4 h-4 text-rose-400" />
            Active Business Anomalies & Incidents
          </h2>
          <p className="text-xs text-slate-400">
            Statistically significant operational anomalies requiring investigation
          </p>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded bg-rose-950/80 text-rose-400 border border-rose-800/60 font-semibold">
          {anomalies.filter((a) => a.severity.toString().toUpperCase() === "CRITICAL").length} Critical
        </span>
      </div>

      <div className="space-y-3">
        {anomalies.map((anom) => {
          const isCritical = anom.severity.toString().toUpperCase() === "CRITICAL";
          const isInvestigating = investigatingId === anom.anomaly_id;

          return (
            <div
              key={anom.anomaly_id}
              className={`p-4 rounded-lg bg-slate-950/80 border transition-all ${
                isCritical
                  ? "border-rose-900/60 hover:border-rose-700/80 bg-gradient-to-r from-rose-950/20 via-slate-950 to-slate-950"
                  : "border-slate-800 hover:border-slate-700"
              }`}
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                {/* Anomaly Header & Metrics */}
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2.5 flex-wrap">
                    <span className="font-mono text-xs font-bold text-slate-200">
                      {anom.anomaly_id}
                    </span>
                    <span
                      className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold uppercase tracking-wider border ${
                        isCritical
                          ? "bg-rose-950/80 text-rose-400 border-rose-800/80"
                          : "bg-amber-950/80 text-amber-400 border-amber-800/80"
                      }`}
                    >
                      {anom.severity}
                    </span>
                    <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                      <Layers className="w-3 h-3 text-slate-500" />
                      Dimension: <strong className="text-slate-200">{anom.affected_dimension}</strong>
                    </span>
                  </div>

                  <p className="text-sm font-semibold text-slate-100 flex items-center gap-2">
                    <span>Metric: <code className="text-cyan-400">{anom.metric}</code></span>
                    <span className="text-rose-400 font-mono font-bold">
                      ({anom.change_percentage > 0 ? `+${anom.change_percentage.toFixed(1)}%` : `${anom.change_percentage.toFixed(1)}%`})
                    </span>
                  </p>

                  <div className="flex items-center gap-4 text-xs font-mono text-slate-400 pt-1">
                    <span>
                      Current: <strong className="text-slate-200">{typeof anom.current_value === "number" && anom.current_value > 1000 ? `$${anom.current_value.toLocaleString()}` : anom.current_value}</strong>
                    </span>
                    <span>
                      Baseline: <strong className="text-slate-400">{typeof anom.baseline_value === "number" && anom.baseline_value > 1000 ? `$${anom.baseline_value.toLocaleString()}` : anom.baseline_value}</strong>
                    </span>
                    <span className="text-slate-500">
                      Window: May 1 – Aug 1, 2026
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <button
                    onClick={() => onSelectAnomaly(anom.anomaly_id)}
                    className="px-3.5 py-2 rounded-lg bg-cyan-950/80 hover:bg-cyan-900 text-cyan-300 border border-cyan-800/80 text-xs font-medium transition-colors flex items-center gap-1.5 shadow-sm"
                  >
                    <span>View Dossier</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>

                  <button
                    onClick={() => onTriggerInvestigation(anom.anomaly_id)}
                    disabled={isInvestigating}
                    className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition-colors flex items-center gap-1.5 disabled:opacity-50"
                  >
                    <Zap className={`w-3.5 h-3.5 ${isInvestigating ? "animate-spin text-amber-400" : "text-amber-400"}`} />
                    <span>{isInvestigating ? "Investigating..." : "Re-Run Investigation"}</span>
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
