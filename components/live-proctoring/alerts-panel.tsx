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
            Live Alerts
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Monitor suspicious candidate activity
          </p>

        </div>

        <div className="rounded-full bg-red-500/10 px-3 py-1">

          <span className="text-sm font-semibold text-red-400">
            {alerts.length} Active
          </span>

        </div>

      </div>

      {/* Alerts */}

      <div className="space-y-4">

        {alerts.length === 0 ? (
          <div className="rounded-2xl bg-[#0F172A] p-6 text-center">

            <CheckCircle2 className="mx-auto h-8 w-8 text-green-400" />

            <p className="mt-3 text-sm text-slate-400">
              No active alerts
            </p>

          </div>
        ) : (
          alerts.map((alert) => {
            const style = getAlertStyle(alert.severity);
            const Icon = style.icon;

            return (
              <div
                key={alert.id}
                className="rounded-2xl bg-[#0F172A] p-4 transition-all duration-300 hover:-translate-y-1 hover:bg-[#162033]"
              >
                <div className="flex items-start gap-4">

                  <div className={`rounded-xl ${style.bg} p-2`}>

                    <Icon className={`h-5 w-5 ${style.color}`} />

                  </div>

                  <div className="flex-1">

                    <div className="flex items-center justify-between">

                      <h3 className="font-semibold text-white">
                        {alert.title}
                      </h3>

                      <span className="text-xs text-slate-500">
                        {alert.time}
                      </span>

                    </div>

                    <p className="mt-1 text-sm text-slate-400">
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