"use client";

import {
  Play,
  ScanFace,
  Users,
  AlertTriangle,
  CheckCircle2,
  MonitorSmartphone,
} from "lucide-react";

import { TimelineEvent } from "./types";

interface WarningTimelineProps {
  timeline: TimelineEvent[];
}

export function WarningTimeline({
  timeline,
}: WarningTimelineProps) {
  const getEventStyle = (severity: TimelineEvent["severity"]) => {
    switch (severity) {
      case "danger":
        return {
          icon: AlertTriangle,
          color: "bg-red-500",
        };

      case "warning":
        return {
          icon: Users,
          color: "bg-yellow-500",
        };

      case "info":
        return {
          icon: MonitorSmartphone,
          color: "bg-blue-500",
        };

      default:
        return {
          icon: CheckCircle2,
          color: "bg-green-500",
        };
    }
  };

  return (
    <div className="rounded-[28px] border border-white/10 bg-[#111827]/90 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-xl">

      {/* Header */}

      <div className="mb-8">

        <h2 className="text-xl font-bold text-white">
          Event Timeline
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Chronological interview monitoring events
        </p>

      </div>

      {timeline.length === 0 ? (
        <div className="rounded-2xl bg-[#0F172A] p-8 text-center">

          <Play className="mx-auto h-10 w-10 text-[#4096FF]" />

          <p className="mt-4 text-slate-400">
            Waiting for interview events...
          </p>

        </div>
      ) : (
        <div className="relative flex items-start gap-6 overflow-x-auto pb-2">

          <div className="absolute left-0 right-0 top-5 h-0.5 bg-slate-700" />

          {timeline.map((event) => {
            const style = getEventStyle(event.severity);
            const Icon = style.icon;

            return (
              <div
                key={event.id}
                className="relative z-10 flex min-w-[120px] flex-col items-center"
              >
                {/* Circle */}

                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full ${style.color} shadow-lg transition-all duration-300 hover:scale-110`}
                >
                  <Icon className="h-5 w-5 text-white" />
                </div>

                {/* Content */}

                <div className="mt-4 text-center">

                  <p className="text-sm font-semibold text-white">
                    {event.title}
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    {event.subtitle}
                  </p>

                  <p className="mt-2 font-mono text-[11px] text-slate-500">
                    {event.time}
                  </p>

                </div>

              </div>
            );
          })}

        </div>
      )}

    </div>
  );
}