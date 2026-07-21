"use client";

import {
  Camera,
  Mic,
  Monitor,
  Wifi,
  CheckCircle2,
  XCircle,
} from "lucide-react";

interface StatusPanelProps {
  faceDetected: boolean;
  microphone: boolean;
  fullscreen: boolean;
  network: "Excellent" | "Good" | "Poor";
}

export function StatusPanel({
  faceDetected,
  microphone,
  fullscreen,
  network,
}: StatusPanelProps) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-[#1E293B] p-6 shadow-2xl backdrop-blur-xl">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white">
          Candidate Monitoring
        </h2>

        <p className="mt-1 text-sm text-slate-400 font-medium">
          Live real-time backend proctoring status
        </p>
      </div>

      <div className="space-y-4">
        {/* Face Detection */}
        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4 transition-all hover:bg-[#162033]">
          <div className="flex items-center gap-3">
            <Camera className="h-5 w-5 text-[#4096ff]" />
            <span className="text-white font-medium text-sm">
              Face &amp; Presence Detection
            </span>
          </div>

          <div className="flex items-center gap-2">
            {faceDetected ? (
              <>
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                <span className="font-semibold text-emerald-400 text-sm">
                  Detected
                </span>
              </>
            ) : (
              <>
                <XCircle className="h-5 w-5 text-rose-400" />
                <span className="font-semibold text-rose-400 text-sm animate-pulse">
                  Subject Away
                </span>
              </>
            )}
          </div>
        </div>

        {/* Microphone */}
        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4 transition-all hover:bg-[#162033]">
          <div className="flex items-center gap-3">
            <Mic className="h-5 w-5 text-[#4096ff]" />
            <span className="text-white font-medium text-sm">
              Microphone Stream
            </span>
          </div>

          <div className="flex items-center gap-2">
            {microphone ? (
              <>
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                <span className="font-semibold text-emerald-400 text-sm">
                  Active
                </span>
              </>
            ) : (
              <>
                <XCircle className="h-5 w-5 text-rose-400" />
                <span className="font-semibold text-rose-400 text-sm">
                  Muted
                </span>
              </>
            )}
          </div>
        </div>

        {/* Fullscreen */}
        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4 transition-all hover:bg-[#162033]">
          <div className="flex items-center gap-3">
            <Monitor className="h-5 w-5 text-[#4096ff]" />
            <span className="text-white font-medium text-sm">
              Fullscreen Lock
            </span>
          </div>

          <div className="flex items-center gap-2">
            {fullscreen ? (
              <>
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                <span className="font-semibold text-emerald-400 text-sm">
                  Active
                </span>
              </>
            ) : (
              <>
                <XCircle className="h-5 w-5 text-rose-400" />
                <span className="font-semibold text-rose-400 text-sm">
                  Exited
                </span>
              </>
            )}
          </div>
        </div>

        {/* Network */}
        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4 transition-all hover:bg-[#162033]">
          <div className="flex items-center gap-3">
            <Wifi className="h-5 w-5 text-[#4096ff]" />
            <span className="text-white font-medium text-sm">
              Connection Stability
            </span>
          </div>

          <span
            className={`font-bold text-sm ${
              network === "Excellent"
                ? "text-emerald-400"
                : network === "Good"
                ? "text-amber-400"
                : "text-rose-400"
            }`}
          >
            {network}
          </span>
        </div>
      </div>
    </div>
  );
}