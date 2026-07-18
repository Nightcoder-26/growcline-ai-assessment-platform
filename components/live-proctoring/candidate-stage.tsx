"use client";

import { useRef } from "react";
import Webcam from "react-webcam";
import {
  Camera,
  Mic,
  Circle,
  MonitorSmartphone,
} from "lucide-react";

export function CandidateStage() {
  const webcamRef = useRef<Webcam | null>(null);

  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-card shadow-xl">

      {/* ===================== TOP OVERLAY ===================== */}

      <div className="absolute inset-x-0 top-0 z-20 flex items-center justify-between p-5">

        {/* Recording Badge */}

        <div className="flex items-center gap-2 rounded-full border border-red-500/30 bg-black/50 backdrop-blur-md px-4 py-2 shadow-lg">

          <Circle
            size={12}
            className="fill-red-500 text-red-500 animate-pulse"
          />

          <span className="text-sm font-semibold tracking-wide text-red-400">
            REC LIVE
          </span>

        </div>

        {/* Camera Quality */}

        <div className="flex items-center gap-3">

          <div className="rounded-full border border-white/10 bg-black/50 backdrop-blur-md px-4 py-2 text-sm font-medium shadow-lg">
            FPS 30
          </div>

          <div className="rounded-full border border-white/10 bg-black/50 backdrop-blur-md px-4 py-2 text-sm font-medium shadow-lg">
            HD
          </div>

        </div>

      </div>

      {/* ===================== WEBCAM ===================== */}

      <div className="relative h-[520px] w-full overflow-hidden bg-black">

        <Webcam
          ref={webcamRef}
          audio={false}
          mirrored
          className="h-full w-full object-cover"
        />

      </div>

      {/* ===================== FOOTER ===================== */}

      <div className="flex items-center justify-between border-t border-white/10 bg-background px-6 py-5">

        {/* Candidate Details */}

        <div>

          <h3 className="text-lg font-semibold">
            Sarang Bahikar
          </h3>

          <p className="text-sm text-muted-foreground">
            Software Engineer Candidate
          </p>

        </div>

        {/* Live Status */}

        <div className="flex items-center gap-6 text-sm">

          {/* Camera */}

          <div className="flex items-center gap-2">

            <Camera
              size={18}
              className="text-green-500"
            />

            <span className="h-2 w-2 rounded-full bg-green-500"></span>

            <span>Camera</span>

          </div>

          {/* Microphone */}

          <div className="flex items-center gap-2">

            <Mic
              size={18}
              className="text-green-500"
            />

            <span className="h-2 w-2 rounded-full bg-green-500"></span>

            <span>Microphone</span>

          </div>

          {/* Fullscreen */}

          <div className="flex items-center gap-2">

            <MonitorSmartphone
              size={18}
              className="text-green-500"
            />

            <span className="h-2 w-2 rounded-full bg-green-500"></span>

            <span>Fullscreen</span>

          </div>

        </div>

      </div>

    </div>
  );
}