"use client";

import React from "react";
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  FileCheck,
  History,
  Play,
  Search,
  ShieldAlert,
  XCircle,
} from "lucide-react";
import { AuditEventItem } from "@/types";

interface TimelineProps {
  events: AuditEventItem[];
  onViewAll?: () => void;
}

export function RecentAuditTimeline({ events, onViewAll }: TimelineProps) {
  const getEventBadge = (type: string) => {
    switch (type) {
      case "ANOMALY_DETECTED":
        return { color: "text-rose-400 border-rose-800/80 bg-rose-950/80", icon: AlertCircle };
      case "INVESTIGATION_STARTED":
      case "EVIDENCE_GENERATED":
        return { color: "text-cyan-400 border-cyan-800/80 bg-cyan-950/80", icon: Search };
      case "ROOT_CAUSE_IDENTIFIED":
      case "IMPACT_CALCULATED":
        return { color: "text-indigo-400 border-indigo-800/80 bg-indigo-950/80", icon: History };
      case "RECOMMENDATION_CREATED":
        return { color: "text-blue-400 border-blue-800/80 bg-blue-950/80", icon: FileCheck };
      case "APPROVAL_REQUESTED":
        return { color: "text-amber-400 border-amber-800/80 bg-amber-950/80", icon: ShieldAlert };
      case "ACTION_APPROVED":
      case "ACTION_EXECUTED":
        return { color: "text-emerald-400 border-emerald-800/80 bg-emerald-950/80", icon: CheckCircle2 };
      case "ACTION_REJECTED":
        return { color: "text-rose-400 border-rose-800/80 bg-rose-950/80", icon: XCircle };
      default:
        return { color: "text-slate-400 border-slate-700 bg-slate-900", icon: Clock };
    }
  };

  return (
    <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800 backdrop-blur">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <History className="w-4 h-4 text-cyan-400" />
            Live Audit Stream & Operations Timeline
          </h2>
          <p className="text-xs text-slate-400">
            Immutable chronicle of agent investigations, human decisions, and action executions
          </p>
        </div>
        <button
          onClick={onViewAll}
          className="text-xs font-mono font-medium px-3 py-1.5 rounded-md bg-slate-800 text-slate-300 hover:bg-slate-700 transition-colors"
        >
          Full Audit Log →
        </button>
      </div>

      <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
        {events.slice(0, 7).map((ev, idx) => {
          const { color, icon: Icon } = getEventBadge(ev.event_type);
          const timeFormatted = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "Recently";

          return (
            <div key={ev.event_id || idx} className="relative group">
              {/* Dot Icon */}
              <div
                className={`absolute -left-6 top-1 w-5 h-5 rounded-full border flex items-center justify-center ${color} bg-[#090D16] group-hover:scale-110 transition-transform`}
              >
                <Icon className="w-2.5 h-2.5" />
              </div>

              {/* Event Content */}
              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 hover:border-slate-700 transition-colors">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded font-bold border ${color}`}>
                      {ev.event_type.replace(/_/g, " ")}
                    </span>
                    <span className="text-xs font-mono text-slate-300">
                      {ev.entity_type}:{ev.entity_id}
                    </span>
                    <span className="text-[11px] text-slate-500 font-mono">
                      (by <strong className="text-slate-400">{ev.actor}</strong>)
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 font-mono pt-0.5">
                    Action: {ev.action} • Status: <span className="text-emerald-400 font-semibold">{ev.status}</span>
                  </p>
                </div>

                <div className="text-[11px] font-mono text-slate-500 whitespace-nowrap">
                  {timeFormatted}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
