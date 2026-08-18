"use client";

import React, { useState } from "react";
import {
  Calendar,
  ChevronDown,
  ChevronRight,
  Filter,
  History,
  Search,
  Shield,
  User,
} from "lucide-react";
import { AuditEventItem } from "@/types";

interface AuditViewProps {
  events: AuditEventItem[];
}

export function AuditView({ events }: AuditViewProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedEventType, setSelectedEventType] = useState<string>("ALL");
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);

  const eventTypes = [
    "ALL",
    "ANOMALY_DETECTED",
    "INVESTIGATION_STARTED",
    "EVIDENCE_GENERATED",
    "ROOT_CAUSE_IDENTIFIED",
    "RECOMMENDATION_CREATED",
    "APPROVAL_REQUESTED",
    "ACTION_APPROVED",
    "ACTION_REJECTED",
    "ACTION_EXECUTED",
  ];

  const filteredEvents = events.filter((ev) => {
    const matchesType = selectedEventType === "ALL" || ev.event_type === selectedEventType;
    const matchesSearch =
      searchTerm === "" ||
      ev.entity_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ev.actor?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ev.action?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ev.event_type?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesType && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-6 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <History className="w-4 h-4 text-cyan-400" />
            Immutable Operations Audit Log
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Tamper-evident operational chronicle tracking anomaly detections, AI investigations, human approvals, and execution traces.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono px-3 py-1.5 rounded-md bg-slate-950 text-slate-300 border border-slate-800">
            Total Records: <strong>{events.length}</strong>
          </span>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search entity, actor, action..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
          <Filter className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
          <select
            value={selectedEventType}
            onChange={(e) => setSelectedEventType(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            {eventTypes.map((t) => (
              <option key={t} value={t}>
                {t.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-xl bg-slate-900/70 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Event Type</th>
                <th className="py-3 px-4">Entity</th>
                <th className="py-3 px-4">Action</th>
                <th className="py-3 px-4">Actor</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredEvents.map((ev) => {
                const isExpanded = expandedEventId === ev.event_id;
                const timeStr = ev.timestamp ? new Date(ev.timestamp).toLocaleString() : "N/A";

                return (
                  <React.Fragment key={ev.event_id}>
                    <tr className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 text-slate-400 whitespace-nowrap">{timeStr}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded font-bold uppercase text-[10px] bg-slate-800 text-cyan-300 border border-slate-700">
                          {ev.event_type}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-200 font-semibold">
                        {ev.entity_type}:{ev.entity_id}
                      </td>
                      <td className="py-3 px-4 text-slate-300 max-w-[200px] truncate">{ev.action}</td>
                      <td className="py-3 px-4 text-slate-400">
                        <span className="flex items-center gap-1">
                          <User className="w-3 h-3 text-slate-500" />
                          {ev.actor}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-emerald-400 font-semibold">{ev.status}</span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => setExpandedEventId(isExpanded ? null : ev.event_id)}
                          className="p-1 rounded hover:bg-slate-800 text-slate-400"
                        >
                          {isExpanded ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                        </button>
                      </td>
                    </tr>

                    {/* Expandable JSON details */}
                    {isExpanded && (
                      <tr className="bg-slate-950/90 border-y border-slate-800">
                        <td colSpan={7} className="p-4">
                          <div className="p-3 rounded-lg bg-[#0B1120] border border-slate-800 space-y-1">
                            <span className="text-[11px] text-slate-400 font-bold uppercase">Audit Event Payload</span>
                            <pre className="text-[11px] text-cyan-300 overflow-x-auto p-2">
                              {JSON.stringify(ev.details || ev, null, 2)}
                            </pre>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
