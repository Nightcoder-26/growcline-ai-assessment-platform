"use client";

import {
  CheckCircle2,
  AlertTriangle,
  Users,
  ScanFace,
  MonitorSmartphone,
} from "lucide-react";

import { ActivityEvent } from "./types";

interface ActivityLogProps {
  logs: ActivityEvent[];
}

export function ActivityLog({ logs }: ActivityLogProps) {
  const getLogStyle = (severity: ActivityEvent["severity"]) => {
    switch (severity) {
      case "danger":
        return {
          icon: AlertTriangle,
          color: "text-red-400",
          bg: "bg-red-500/10",
        };

      case "warning":
        return {
          icon: Users,
          color: "text-yellow-400",
          bg: "bg-yellow-500/10",
        };

      case "info":
        return {
          icon: MonitorSmartphone,
          color: "text-blue-400",
          bg: "bg-blue-500/10",
        };

      default:
        return {
          icon: CheckCircle2,
          color: "text-green-400",
          bg: "bg-green-500/10",
        };
    }
  };

  return (
    <div className="rounded-[28px] border border-white/10 bg-[#111827]/90 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-xl">

      {/* Header */}

      <div className="mb-6 flex items-center justify-between">

        <div>

          <h2 className="text-xl font-bold text-white">
            Activity Log
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Live interview session events
          </p>

        </div>

        <div className="flex items-center gap-2 rounded-full border border-green-500/20 bg-green-500/10 px-4 py-2">

          <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-green-400"></span>

          <span className="text-sm font-medium text-green-400">
            Live Feed
          </span>

        </div>

      </div>

      {/* Log List */}

      <div className="max-h-[300px] space-y-3 overflow-y-auto pr-2">

        {logs.length === 0 ? (
          <div className="rounded-2xl bg-[#0F172A] p-6 text-center">

            <ScanFace className="mx-auto h-8 w-8 text-[#4096FF]" />

            <p className="mt-3 text-sm text-slate-400">
              Waiting for interview activity...
            </p>

          </div>
        ) : (
          logs.map((log) => {
            const style = getLogStyle(log.severity);
            const Icon = style.icon;

            return (
              <div
                key={log.id}
                className="flex items-center gap-4 rounded-2xl bg-[#0F172A] p-4 transition-all duration-300 hover:-translate-y-1 hover:bg-[#162033]"
              >
                <div className={`rounded-xl ${style.bg} p-2`}>

                  <Icon className={`h-5 w-5 ${style.color}`} />

                </div>

                <div className="flex-1">

                  <div className="flex items-center justify-between">

                    <h3 className="font-medium text-white">
                      {log.event}
                    </h3>

                    <span className="font-mono text-xs text-slate-500">
                      {log.time}
                    </span>

                  </div>

                </div>

              </div>
            );
          })
        )}

      </div>

    </div>
  );
}