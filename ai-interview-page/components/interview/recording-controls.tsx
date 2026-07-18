"use client";

import {
  Circle,
  Pause,
  Play,
  RotateCcw,
  Square,
  Upload,
} from "lucide-react";

interface RecordingControlsProps {
  recording: boolean;
  paused: boolean;
  onStart: () => void;
  onPauseToggle: () => void;
  onStop: () => void;
  onRetake: () => void;
}

export function RecordingControls({
  recording,
  paused,
  onStart,
  onPauseToggle,
  onStop,
  onRetake,
}: RecordingControlsProps) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-[#111827]/90 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-xl">

      {/* Heading */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white">
          Recording Controls
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Record your response clearly before moving to the next question.
        </p>
      </div>

      {!recording ? (
        <button
          onClick={() => {
            console.log("✅ START BUTTON CLICKED");
            onStart();
          }}
          className="flex w-full items-center justify-center gap-3 rounded-2xl bg-[#4096ff] py-4 text-lg font-semibold text-white transition-all duration-300 hover:scale-[1.02] hover:bg-[#2f86ff]"
        >
          <Circle className="h-5 w-5 fill-current" />
          Start Recording
        </button>
      ) : (
        <div className="grid grid-cols-2 gap-4">

          <button
            onClick={() => {
              console.log("⏸ PAUSE CLICKED");
              onPauseToggle();
            }}
            className="flex items-center justify-center gap-2 rounded-2xl bg-slate-700 py-4 font-semibold text-white transition hover:bg-slate-600"
          >
            {paused ? (
              <>
                <Play className="h-5 w-5" />
                Resume
              </>
            ) : (
              <>
                <Pause className="h-5 w-5" />
                Pause
              </>
            )}
          </button>

          <button
            onClick={() => {
              console.log("⏹ STOP CLICKED");
              onStop();
            }}
            className="flex items-center justify-center gap-2 rounded-2xl bg-red-500 py-4 font-semibold text-white transition hover:bg-red-600"
          >
            <Square className="h-5 w-5 fill-current" />
            Stop
          </button>

        </div>
      )}

      {/* Divider */}
      <div className="my-6 h-px bg-slate-700" />

      {/* Secondary Actions */}
      <div className="grid grid-cols-2 gap-4">

        <button
          onClick={() => {
            console.log("🔄 RETAKE CLICKED");
            onRetake();
          }}
          className="flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-800 py-3 text-white transition hover:border-[#4096ff]"
        >
          <RotateCcw className="h-5 w-5" />
          Retake
        </button>

        <button
          onClick={() => {
            console.log("⬆️ UPLOAD CLICKED");
            alert("Upload functionality will be connected with FastAPI.");
          }}
          className="flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-800 py-3 text-white transition hover:border-[#4096ff]"
        >
          <Upload className="h-5 w-5" />
          Upload
        </button>

      </div>

    </div>
  );
}