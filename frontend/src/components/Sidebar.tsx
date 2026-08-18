"use client";

import React from "react";
import {
  Activity,
  AlertTriangle,
  Bot,
  CheckCircle2,
  FileCheck,
  History,
  LayoutDashboard,
  Radio,
  Search,
  ShieldAlert,
} from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  systemHealthy: boolean;
  pendingApprovalsCount: number;
  criticalAnomaliesCount: number;
}

export function Sidebar({
  activeTab,
  setActiveTab,
  systemHealthy,
  pendingApprovalsCount,
  criticalAnomaliesCount,
}: SidebarProps) {
  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    {
      id: "agent_run",
      label: "Agent Run (MCP)",
      icon: Bot,
      badge: "LIVE",
      badgeColor: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    },
    {
      id: "incidents",
      label: "Incidents",
      icon: AlertTriangle,
      badge: criticalAnomaliesCount > 0 ? `${criticalAnomaliesCount}` : undefined,
      badgeColor: "bg-rose-500/20 text-rose-400 border-rose-500/30",
    },
    { id: "investigations", label: "Investigations", icon: Search },
    { id: "recommendations", label: "Recommendations", icon: FileCheck },
    {
      id: "approvals",
      label: "Approvals",
      icon: ShieldAlert,
      badge: pendingApprovalsCount > 0 ? `${pendingApprovalsCount}` : undefined,
      badgeColor: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    },
    { id: "audit", label: "Audit Trail", icon: History },
  ];

  return (
    <aside className="w-64 bg-[#0B1120] border-r border-slate-800 flex flex-col h-screen sticky top-0 select-none z-30">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <Radio className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="font-bold text-lg tracking-wider text-slate-100 flex items-center gap-1.5">
              ORION
              <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                v0.3
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Business Operations Intel</p>
          </div>
        </div>
      </div>

      {/* System Status Pill */}
      <div className="px-4 py-3">
        <div className="flex items-center justify-between px-3 py-2 rounded-md bg-slate-900/90 border border-slate-800">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              <span
                className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  systemHealthy ? "bg-emerald-400" : "bg-rose-400"
                }`}
              ></span>
              <span
                className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                  systemHealthy ? "bg-emerald-500" : "bg-rose-500"
                }`}
              ></span>
            </span>
            <span className="text-xs font-medium text-slate-300">
              {systemHealthy ? "System Operational" : "Backend Offline"}
            </span>
          </div>
          <Activity className="w-3.5 h-3.5 text-slate-500" />
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-2 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-slate-800 text-cyan-400 border border-slate-700/80 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[11px] font-mono px-2 py-0.5 rounded-full border font-semibold ${item.badgeColor}`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Adya Integration Status Indicator */}
      <div className="px-3 py-2 border-t border-slate-800/60 bg-slate-950/20">
        <div className="flex flex-col gap-1 p-2.5 rounded-lg bg-slate-900/80 border border-slate-800/80">
          <div className="flex items-center justify-between text-[10px] font-mono">
            <span className="text-slate-400">Runtime:</span>
            <span className="text-cyan-400 font-medium">LocalAgentRuntime</span>
          </div>
          <div className="flex items-center justify-between text-[10px] font-mono">
            <span className="text-slate-400">Adya AI:</span>
            <span className="text-amber-400 font-semibold">ADAPTER-READY ONLY</span>
          </div>
        </div>
      </div>

      {/* Executive Footer */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-xs text-cyan-300">
            EO
          </div>
          <div className="overflow-hidden">
            <p className="text-xs font-medium text-slate-200 truncate">Executive Operations</p>
            <p className="text-[10px] text-slate-500 truncate">NovaCart Command Center</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
