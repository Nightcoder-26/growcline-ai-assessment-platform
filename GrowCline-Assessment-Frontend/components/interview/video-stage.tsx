"use client";

import Webcam from "react-webcam";
import {
  Maximize2,
  Mic,
  MicOff,
  Video,
  VideoOff,
} from "lucide-react";

interface VideoStageProps {
  webcamRef: React.RefObject<Webcam | null>;
  recording: boolean;
  paused: boolean;
  camOn: boolean;
  micOn: boolean;
  elapsed: string;
  take: number;
  onToggleCam: () => void;
  onToggleMic: () => void;
}

export function VideoStage({
  webcamRef,
  recording,
  paused,
  camOn,
  micOn,
  elapsed,
  take,
  onToggleCam,
  onToggleMic,
}: VideoStageProps) {
  const live = recording && !paused;

  return (
    <div className="relative overflow-hidden rounded-[28px] border border-white/10 bg-[#111827]/90 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-xl">

      {/* ================= HEADER ================= */}

      <div className="absolute left-0 right-0 top-0 z-20 flex items-center justify-between p-5">

        <div className="flex items-center gap-2 rounded-full border border-red-500/30 bg-black/50 px-4 py-2 backdrop-blur-md">

          <span
            className={`h-3 w-3 rounded-full ${
              live
                ? "animate-pulse bg-red-500"
                : "bg-green-500"
            }`}
          />

          <span
            className={`font-semibold ${
              live
                ? "text-red-400"
                : "text-green-400"
            }`}
          >
            {live ? "REC LIVE" : "READY"}
          </span>

        </div>

        <div className="flex gap-3">

          <div className="rounded-full border border-white/10 bg-black/50 px-4 py-2 text-sm">
            HD
          </div>

          <button className="rounded-full border border-white/10 bg-black/50 p-3 transition hover:bg-[#4096FF]">

            <Maximize2 size={18} />

          </button>

        </div>

      </div>

      {/* ================= WEBCAM ================= */}

      <div className="relative h-[520px] w-full bg-black">

        {camOn ? (

          <Webcam
            ref={webcamRef}
            audio={false}
            mirrored
            screenshotFormat="image/jpeg"
            videoConstraints={{
              facingMode: "user",
              width: 1280,
              height: 720,
            }}
            className="h-full w-full object-cover"
          />

        ) : (

          <div className="flex h-full items-center justify-center">

            <div className="text-center">

              <VideoOff
                className="mx-auto h-16 w-16 text-slate-500"
              />

              <h3 className="mt-4 text-xl font-semibold">
                Camera Disabled
              </h3>

            </div>

          </div>

        )}

      </div>

      {/* ================= FOOTER ================= */}

      <div className="flex items-center justify-between border-t border-white/10 bg-[#0F172A] px-6 py-5">

        <div>

          <h3 className="font-semibold">
            Candidate Preview
          </h3>

          <p className="text-sm text-slate-400">

            {elapsed}

          </p>

        </div>

        <div className="flex gap-4">

          <button
            onClick={onToggleMic}
            className={`rounded-full p-3 transition ${
              micOn
                ? "bg-[#4096FF]"
                : "bg-red-500"
            }`}
          >
            {micOn ? (
              <Mic size={18} />
            ) : (
              <MicOff size={18} />
            )}
          </button>

          <button
            onClick={onToggleCam}
            className={`rounded-full p-3 transition ${
              camOn
                ? "bg-[#4096FF]"
                : "bg-red-500"
            }`}
          >
            {camOn ? (
              <Video size={18} />
            ) : (
              <VideoOff size={18} />
            )}
          </button>

        </div>

      </div>

    </div>
  );
}