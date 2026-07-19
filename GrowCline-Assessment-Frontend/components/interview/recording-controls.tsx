"use client";

import {
  Circle,
  Pause,
  Play,
  RotateCcw,
  Square,
  Upload,
  CheckCircle,
  Loader2,
  Send,
} from "lucide-react";

type UploadStatus = "idle" | "uploading" | "done" | "error";

interface RecordingControlsProps {
  recording: boolean;
  paused: boolean;
  uploadStatus: UploadStatus;
  hasRecording: boolean;
  onStart: () => void;
  onPauseToggle: () => void;
  onStop: () => void;
  onRetake: () => void;
  onUpload: () => void;
  onSubmitNext: () => void;
}

export function RecordingControls({
  recording,
  paused,
  uploadStatus,
  hasRecording,
  onStart,
  onPauseToggle,
  onStop,
  onRetake,
  onUpload,
  onSubmitNext,
}: RecordingControlsProps) {
  return (
    <div className="rounded-[28px] border border-white/10 bg-[#111827]/90 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-xl">

      {/* Heading */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white">Recording Controls</h2>
        <p className="mt-1 text-sm text-slate-400">
          Record your response clearly before moving to the next question.
        </p>
      </div>

      {/* Primary controls */}
      {!recording ? (
        <button
          id="btn-start-recording"
          onClick={onStart}
          className="flex w-full items-center justify-center gap-3 rounded-2xl bg-[#4096ff] py-4 text-lg font-semibold text-white transition-all duration-300 hover:scale-[1.02] hover:bg-[#2f86ff]"
        >
          <Circle className="h-5 w-5 fill-current" />
          Start Recording
        </button>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          <button
            id="btn-pause-recording"
            onClick={onPauseToggle}
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
            id="btn-stop-recording"
            onClick={onStop}
            className="flex items-center justify-center gap-2 rounded-2xl bg-red-500 py-4 font-semibold text-white transition hover:bg-red-600"
          >
            <Square className="h-5 w-5 fill-current" />
            Stop
          </button>
        </div>
      )}

      {/* Divider */}
      <div className="my-6 h-px bg-slate-700" />

      {/* Secondary actions */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <button
          id="btn-retake"
          onClick={onRetake}
          className="flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-800 py-3 text-white transition hover:border-[#4096ff]"
        >
          <RotateCcw className="h-5 w-5" />
          Retake
        </button>

        {/* Upload button — real upload, disabled until blob exists */}
        <button
          id="btn-upload"
          onClick={onUpload}
          disabled={!hasRecording || uploadStatus === "uploading"}
          className="flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-800 py-3 text-white transition hover:border-[#4096ff] disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {uploadStatus === "uploading" ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Uploading…
            </>
          ) : uploadStatus === "done" ? (
            <>
              <CheckCircle className="h-5 w-5 text-green-400" />
              Uploaded
            </>
          ) : (
            <>
              <Upload className="h-5 w-5" />
              Upload
            </>
          )}
        </button>
      </div>

      {/* Submit answer & next question */}
      <button
        id="btn-submit-next"
        onClick={onSubmitNext}
        className="flex w-full items-center justify-center gap-2 rounded-2xl bg-emerald-600 py-3 font-semibold text-white transition hover:bg-emerald-500"
      >
        <Send className="h-5 w-5" />
        Submit Answer &amp; Next Question
      </button>
    </div>
  );
}