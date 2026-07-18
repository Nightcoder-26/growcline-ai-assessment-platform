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
    <div className="rounded-[28px] border border-white/10 bg-[#111827]/90 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-xl">

      {/* Heading */}

      <div className="mb-6">

        <h2 className="text-xl font-bold text-white">
          Candidate Monitoring
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Live proctoring status
        </p>

      </div>

      <div className="space-y-4">

        {/* Face Detection */}

        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4 transition-all duration-300 hover:bg-[#162033]">

          <div className="flex items-center gap-3">

            <Camera className="h-5 w-5 text-[#4096FF]" />

            <span className="text-white">
              Face Detection
            </span>

          </div>

          <div className="flex items-center gap-2">

            {faceDetected ? (
              <>
                <CheckCircle2 className="h-5 w-5 text-green-400" />
                <span className="font-medium text-green-400">
                  Detected
                </span>
              </>
            ) : (
              <>
                <XCircle className="h-5 w-5 text-red-400" />
                <span className="font-medium text-red-400">
                  Missing
                </span>
              </>
            )}

          </div>

        </div>

        {/* Microphone */}

        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4 transition-all duration-300 hover:bg-[#162033]">

          <div className="flex items-center gap-3">

            <Mic className="h-5 w-5 text-[#4096FF]" />

            <span className="text-white">
              Microphone
            </span>

          </div>

          <div className="flex items-center gap-2">

            {microphone ? (
              <>
                <CheckCircle2 className="h-5 w-5 text-green-400" />
                <span className="font-medium text-green-400">
                  Active
                </span>
              </>
            ) : (
              <>
                <XCircle className="h-5 w-5 text-red-400" />
                <span className="font-medium text-red-400">
                  Muted
                </span>
              </>
            )}

          </div>

        </div>

        {/* Fullscreen */}

        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4 transition-all duration-300 hover:bg-[#162033]">

          <div className="flex items-center gap-3">

            <Monitor className="h-5 w-5 text-[#4096FF]" />

            <span className="text-white">
              Fullscreen
            </span>

          </div>

          <div className="flex items-center gap-2">

            {fullscreen ? (
              <>
                <CheckCircle2 className="h-5 w-5 text-green-400" />
                <span className="font-medium text-green-400">
                  Enabled
                </span>
              </>
            ) : (
              <>
                <XCircle className="h-5 w-5 text-red-400" />
                <span className="font-medium text-red-400">
                  Exited
                </span>
              </>
            )}

          </div>

        </div>

        {/* Network */}

        <div className="flex items-center justify-between rounded-2xl bg-[#0F172A] p-4 transition-all duration-300 hover:bg-[#162033]">

          <div className="flex items-center gap-3">

            <Wifi className="h-5 w-5 text-[#4096FF]" />

            <span className="text-white">
              Network
            </span>

          </div>

          <span
            className={`font-semibold ${
              network === "Excellent"
                ? "text-green-400"
                : network === "Good"
                ? "text-yellow-400"
                : "text-red-400"
            }`}
          >
            {network}
          </span>

        </div>

      </div>

    </div>
  );
}