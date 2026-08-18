"use client";

import React from "react";
import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  BarChart3,
  CheckCircle,
  HelpCircle,
  Package,
  TrendingDown,
  Users,
} from "lucide-react";

interface HealthProps {
  onOpenIncident?: () => void;
}

export function BusinessHealthOverview({ onOpenIncident }: HealthProps) {
  const dimensions = [
    {
      id: "revenue",
      title: "Revenue Velocity",
      status: "DEGRADED",
      statusColor: "text-rose-400 bg-rose-950/60 border-rose-800/80",
      current: "$163,189 / day",
      baseline: "$286,343 / day",
      change: "-43.01%",
      changeType: "negative",
      description: "Severe decline concentrated post-June 20 ($7.30M realized loss).",
      progress: 57,
      progressColor: "bg-rose-500",
    },
    {
      id: "support",
      title: "Support SLA & CSAT",
      status: "CRITICAL FAILURE",
      statusColor: "text-rose-400 bg-rose-950/60 border-rose-800/80",
      current: "86.67% SLA Breach",
      baseline: "0.43% SLA Breach",
      change: "+20,055%",
      changeType: "negative",
      description: "Average resolution ballooned from 2.2h to 26.5h; CSAT dropped to 2.05/5.",
      progress: 14,
      progressColor: "bg-rose-500",
    },
    {
      id: "inventory",
      title: "Warehouse Inventory",
      status: "SELECTIVE SHORTAGE",
      statusColor: "text-amber-400 bg-amber-950/60 border-amber-800/80",
      current: "19.79% Stockout (Electronics)",
      baseline: "0.00% Stockout",
      change: "+19.8% pts",
      changeType: "negative",
      description: "Severe stockouts isolated to top GMV categories: Electronics & Home.",
      progress: 68,
      progressColor: "bg-amber-500",
    },
    {
      id: "customers",
      title: "Customer Retention",
      status: "AT RISK",
      statusColor: "text-amber-400 bg-amber-950/60 border-amber-800/80",
      current: "87.66% Repeat Rate",
      baseline: "98.09% Repeat Rate",
      change: "-10.63%",
      changeType: "negative",
      description: "Order cancellation rate tripled from 1.86% to 6.00%; 813 VIP/Regulars at risk.",
      progress: 74,
      progressColor: "bg-amber-500",
    },
    {
      id: "marketing",
      title: "Marketing Efficiency",
      status: "HEALTHY",
      statusColor: "text-emerald-400 bg-emerald-950/60 border-emerald-800/80",
      current: "4.62 ROAS ($611k Spend)",
      baseline: "4.62 ROAS",
      change: "0.0%",
      changeType: "neutral",
      description: "Top-of-funnel traffic & clicks remain steady. Demand collapse is NOT external.",
      progress: 95,
      progressColor: "bg-emerald-500",
    },
  ];

  return (
    <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800 backdrop-blur">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-cyan-400" />
            Operational Health Overview
          </h2>
          <p className="text-xs text-slate-400">
            Multi-dimensional telemetry across core e-commerce business operations
          </p>
        </div>
        <button
          onClick={onOpenIncident}
          className="text-xs font-mono font-medium px-3 py-1.5 rounded-md bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 hover:bg-cyan-900/60 transition-colors"
        >
          View Causal Mapping →
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {dimensions.map((dim) => (
          <div
            key={dim.id}
            onClick={dim.id !== "marketing" ? onOpenIncident : undefined}
            className={`p-4 rounded-lg bg-slate-950/60 border border-slate-800/80 flex flex-col justify-between hover:border-slate-700 transition-all ${
              dim.id !== "marketing" ? "cursor-pointer" : ""
            }`}
          >
            <div>
              <div className="flex items-center justify-between gap-1 mb-2">
                <span className="text-xs font-semibold text-slate-300 truncate">{dim.title}</span>
                <span
                  className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase font-bold tracking-wider ${dim.statusColor}`}
                >
                  {dim.status}
                </span>
              </div>

              <div className="mt-2">
                <p className="text-sm font-bold font-mono text-slate-100">{dim.current}</p>
                <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1 font-mono">
                  <span>Base: {dim.baseline}</span>
                  <span
                    className={`font-semibold ${
                      dim.changeType === "negative"
                        ? "text-rose-400"
                        : dim.changeType === "positive"
                        ? "text-emerald-400"
                        : "text-slate-400"
                    }`}
                  >
                    {dim.change}
                  </span>
                </div>
              </div>

              {/* Progress / Fulfillment Bar */}
              <div className="w-full bg-slate-800/80 h-1.5 rounded-full overflow-hidden mt-3">
                <div
                  className={`h-full rounded-full ${dim.progressColor}`}
                  style={{ width: `${dim.progress}%` }}
                ></div>
              </div>
            </div>

            <p className="text-[11px] text-slate-400 mt-3 pt-2.5 border-t border-slate-800/60 line-clamp-2">
              {dim.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
