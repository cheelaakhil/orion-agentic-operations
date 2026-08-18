"use client";

import React from "react";
import { AlertOctagon, ArrowDownRight, DollarSign, FileSearch, ShieldAlert } from "lucide-react";

interface KpiCardsProps {
  revenueAtRisk: number;
  criticalCount: number;
  investigationsCount: number;
  pendingApprovalsCount: number;
  onCardClick?: (tab: string) => void;
}

export function KpiCards({
  revenueAtRisk = 5093055,
  criticalCount = 2,
  investigationsCount = 1,
  pendingApprovalsCount = 2,
  onCardClick,
}: KpiCardsProps) {
  const cards = [
    {
      id: "incidents",
      title: "Revenue at Risk (30d)",
      value: `$${(revenueAtRisk / 1_000_000).toFixed(2)}M`,
      subtext: "Unmitigated run-rate projection",
      trend: "-$123.1k/day deficit",
      icon: DollarSign,
      color: "text-rose-400",
      bgGradient: "from-rose-950/40 to-slate-900/40",
      borderColor: "border-rose-800/60",
      glow: "glow-critical",
    },
    {
      id: "incidents",
      title: "Critical Anomalies",
      value: `${criticalCount}`,
      subtext: "Support SLA & Revenue Breakdown",
      trend: "+20,055% SLA breach spike",
      icon: AlertOctagon,
      color: "text-rose-400",
      bgGradient: "from-rose-950/30 to-slate-900/40",
      borderColor: "border-rose-800/50",
      glow: "",
    },
    {
      id: "investigations",
      title: "Active Investigations",
      value: `${investigationsCount}`,
      subtext: "Multi-agent causal pipelines",
      trend: "Confidence score: 88%",
      icon: FileSearch,
      color: "text-cyan-400",
      bgGradient: "from-cyan-950/30 to-slate-900/40",
      borderColor: "border-cyan-800/50",
      glow: "glow-accent",
    },
    {
      id: "approvals",
      title: "Pending Approvals",
      value: `${pendingApprovalsCount}`,
      subtext: "Awaiting human authorization",
      trend: "Immediate action required",
      icon: ShieldAlert,
      color: "text-amber-400",
      bgGradient: "from-amber-950/30 to-slate-900/40",
      borderColor: "border-amber-800/50",
      glow: "glow-warning",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.title}
            onClick={() => onCardClick?.(card.id)}
            className={`p-5 rounded-xl bg-gradient-to-b ${card.bgGradient} border ${card.borderColor} ${card.glow} cursor-pointer hover:border-slate-600 transition-all shadow-md group`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                {card.title}
              </span>
              <div className="p-2 rounded-lg bg-slate-900/80 border border-slate-800 group-hover:scale-105 transition-transform">
                <Icon className={`w-4 h-4 ${card.color}`} />
              </div>
            </div>

            <div className="mt-3 flex items-baseline gap-2">
              <span className={`text-2xl lg:text-3xl font-bold font-mono tracking-tight text-slate-100`}>
                {card.value}
              </span>
            </div>

            <div className="mt-2.5 flex items-center justify-between text-xs border-t border-slate-800/80 pt-2.5">
              <span className="text-slate-400 truncate">{card.subtext}</span>
              <span className={`font-mono text-[11px] font-medium flex items-center gap-0.5 ${card.color}`}>
                <ArrowDownRight className="w-3 h-3 flex-shrink-0" />
                {card.trend}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
