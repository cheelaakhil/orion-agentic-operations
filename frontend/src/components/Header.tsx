"use client";

import React from "react";
import { AlertCircle, Calendar, RefreshCw, Sparkles } from "lucide-react";

interface HeaderProps {
  onRefresh: () => void;
  isLoading: boolean;
  activeIncidentTitle?: string;
  onOpenIncident?: () => void;
}

export function Header({
  onRefresh,
  isLoading,
  activeIncidentTitle = "ANOM-REV-001: -43.01% Daily Revenue Collapse (Support SLA & Stockout Incident)",
  onOpenIncident,
}: HeaderProps) {
  return (
    <header className="h-16 bg-[#0B1120]/90 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-20">
      {/* Active Incident Warning Marquee */}
      <div className="flex items-center gap-3 max-w-2xl overflow-hidden">
        <button
          onClick={onOpenIncident}
          className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-rose-950/60 border border-rose-800/80 text-rose-300 hover:bg-rose-900/60 hover:text-rose-100 transition-colors text-xs font-medium"
        >
          <AlertCircle className="w-3.5 h-3.5 text-rose-400 animate-pulse flex-shrink-0" />
          <span className="font-semibold text-rose-400">CRITICAL INCIDENT:</span>
          <span className="truncate">{activeIncidentTitle}</span>
          <span className="text-[10px] underline ml-1 text-rose-300 font-mono">View Dossier →</span>
        </button>
      </div>

      {/* Controls & Date Context */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300">
          <Calendar className="w-3.5 h-3.5 text-slate-500" />
          <span>2026-05-01 → 2026-08-01</span>
        </div>

        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium transition-colors disabled:opacity-50 shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin text-cyan-400" : "text-slate-400"}`} />
          <span>{isLoading ? "Syncing..." : "Refresh"}</span>
        </button>
      </div>
    </header>
  );
}
