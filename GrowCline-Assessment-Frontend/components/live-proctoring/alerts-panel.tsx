"use client";

import {
  AlertTriangle,
  Users,
  MonitorSmartphone,
  CheckCircle2,
} from "lucide-react";

import { AlertEvent } from "./types";

interface AlertsPanelProps {
  alerts: AlertEvent[];
}

export function AlertsPanel({ alerts }: AlertsPanelProps) {
  const getAlertStyle = (severity: AlertEvent["severity"]) => {
    switch (severity) {
      case "danger":
        return {
          icon: AlertTriangle,
          color: "text-rose-400",
          bg: "bg-rose-500/10",
        };

      case "warning":
        return {
          icon: Users,
          color: "text-amber-400",
          bg: "bg-amber-500/10",
        };

      case "info":
        return {
          icon: MonitorSmartphone,
          color: "text-[#4096ff]",
          bg: "bg-[#4096ff]/10",
        };

      default:
        return {
          icon: CheckCircle2,
          color: "text-emerald-400",
          bg: "bg-emerald-500/10",
        };
    }
  };

  return (
    <div className="rounded-[28px] border border-white/10 bg-[#1E293B] p-6 shadow-2xl backdrop-blur-xl">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">
            Live Proctoring Warning Logs
          </h2>

          <p className="mt-1 text-sm text-slate-400 font-medium">
            Real-time candidate violation activity
          </p>
        </div>

        <div className="rounded-full bg-rose-500/10 border border-rose-500/20 px-3 py-1">
          <span className="text-xs font-bold text-rose-400">
            {alerts.length} Warnings
          </span>
        </div>
      </div>

      {/* Alerts */}
      <div className="space-y-4">
        {alerts.length === 0 ? (
          <div className="rounded-2xl bg-[#0F172A] p-6 text-center">
            <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-400" />
            <p className="mt-3 text-sm text-slate-400 font-medium">
              No proctoring violations recorded
            </p>
          </div>
        ) : (
          alerts.map((alert) => {
            const style = getAlertStyle(alert.severity);
            const Icon = style.icon;

            return (
              <div
                key={alert.id}
                className="rounded-2xl bg-[#0F172A] p-4 transition-all duration-300 hover:bg-[#162033]"
              >
                <div className="flex items-start gap-4">
                  <div className={`rounded-xl ${style.bg} p-2`}>
                    <Icon className={`h-5 w-5 ${style.color}`} />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-white text-sm">
                        {alert.title}
                      </h3>

                      <span className="text-xs text-slate-400 font-mono">
                        {alert.time}
                      </span>
                    </div>

                    <p className="mt-1 text-xs text-slate-400">
                      {alert.message}
                    </p>
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