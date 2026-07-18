"use client";

import {
  Camera,
  Mic,
  Video,
  Clock3,
  CheckCircle2,
} from "lucide-react";

interface SessionMetricsProps {
  live: boolean;
  clarity: number;
  pace: number;
}

export function SessionMetrics({ live }: SessionMetricsProps) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-[#111827]/90 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-xl">

      {/* Heading */}

      <div className="mb-6">

        <h2 className="text-xl font-bold text-white">
          Recording Status
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Current interview session information
        </p>

      </div>

      <div className="space-y-4">

        {/* Camera */}

        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4">

          <div className="flex items-center gap-3">

            <Camera className="h-5 w-5 text-[#4096ff]" />

            <span className="text-white">
              Camera
            </span>

          </div>

          <div className="flex items-center gap-2">

            <CheckCircle2 className="h-5 w-5 text-green-400" />

            <span className="text-green-400 font-medium">
              Connected
            </span>

          </div>

        </div>

        {/* Microphone */}

        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4">

          <div className="flex items-center gap-3">

            <Mic className="h-5 w-5 text-[#4096ff]" />

            <span className="text-white">
              Microphone
            </span>

          </div>

          <div className="flex items-center gap-2">

            <CheckCircle2 className="h-5 w-5 text-green-400" />

            <span className="text-green-400 font-medium">
              Connected
            </span>

          </div>

        </div>

        {/* Recording */}

        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4">

          <div className="flex items-center gap-3">

            <Video className="h-5 w-5 text-[#4096ff]" />

            <span className="text-white">
              Recording
            </span>

          </div>

          <div className="flex items-center gap-2">

            <span
              className={`h-3 w-3 rounded-full ${
                live ? "animate-pulse bg-red-500" : "bg-slate-500"
              }`}
            />

            <span
              className={`font-medium ${
                live ? "text-red-400" : "text-slate-400"
              }`}
            >
              {live ? "Recording Live" : "Ready"}
            </span>

          </div>

        </div>

        {/* Quality */}

        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4">

          <div className="flex items-center gap-3">

            <Clock3 className="h-5 w-5 text-[#4096ff]" />

            <span className="text-white">
              Video Quality
            </span>

          </div>

          <span className="font-semibold text-white">
            1080p • 30 FPS
          </span>

        </div>

      </div>

    </div>
  );
}