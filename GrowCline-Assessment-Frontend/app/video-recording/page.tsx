/**
 * Video Recording Page
 *
 * Supports optional URL params:
 *   /video-recording?jobRole=Backend+Developer&interviewType=TECHNICAL&difficulty=MEDIUM
 *
 * Defaults to: Software Engineer / TECHNICAL / MEDIUM
 *
 * Shows a pre-flight system check screen before launching InterviewStudio.
 * InterviewStudio uses react-media-recorder which requires browser APIs
 * (Web Worker, MediaRecorder) — it must be loaded client-side only.
 */
"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import {
  Camera, Mic, Wifi, CheckCircle2, XCircle, Loader2,
  AlertTriangle, ArrowRight, RefreshCw, ShieldCheck,
  Video, Clock, Users,
} from "lucide-react";

// Disable SSR for InterviewStudio — react-media-recorder uses Web Worker
// which is not available in Node.js
const InterviewStudio = dynamic(
  () =>
    import("@/components/interview/interview-studio").then((m) => ({
      default: m.InterviewStudio,
    })),
  {
    ssr: false,
    loading: () => (
      <div className="min-h-screen bg-[#0F172A] flex items-center justify-center">
        <div className="w-10 h-10 rounded-full border-4 border-[#4096ff] border-t-transparent animate-spin" />
      </div>
    ),
  }
);

// ─── System check types ──────────────────────────────────────────────────────

type CheckState = "idle" | "checking" | "pass" | "fail" | "warn";

interface SystemCheck {
  id: string;
  label: string;
  description: string;
  state: CheckState;
  detail?: string;
}

// ─── Pre-Check Screen ────────────────────────────────────────────────────────

function PreCheckScreen({ onProceed }: { onProceed: () => void }) {
  const [checks, setChecks] = useState<SystemCheck[]>([
    {
      id: "camera",
      label: "Camera",
      description: "A working webcam is required for video proctoring.",
      state: "idle",
    },
    {
      id: "microphone",
      label: "Microphone",
      description: "A working microphone is required for AI analysis.",
      state: "idle",
    },
    {
      id: "browser",
      label: "Browser Support",
      description: "Modern browser with MediaRecorder API required.",
      state: "idle",
    },
    {
      id: "connection",
      label: "Internet Connection",
      description: "Stable connection required for session recording.",
      state: "idle",
    },
  ]);

  const [running, setRunning] = useState(false);
  const [done, setDone]       = useState(false);
  const [stream, setStream]   = useState<MediaStream | null>(null);

  function updateCheck(id: string, update: Partial<SystemCheck>) {
    setChecks((prev) =>
      prev.map((c) => (c.id === id ? { ...c, ...update } : c))
    );
  }

  async function runChecks() {
    setRunning(true);
    setDone(false);

    // Reset
    setChecks((prev) => prev.map((c) => ({ ...c, state: "checking" as CheckState, detail: undefined })));

    // Stop any existing stream
    if (stream) {
      stream.getTracks().forEach((t) => t.stop());
      setStream(null);
    }

    // ── 1. Browser support ──────────────────────────────────────────
    await delay(400);
    const hasMediaRecorder =
      typeof window !== "undefined" &&
      typeof MediaRecorder !== "undefined" &&
      typeof navigator.mediaDevices?.getUserMedia === "function";

    updateCheck("browser", {
      state: hasMediaRecorder ? "pass" : "fail",
      detail: hasMediaRecorder
        ? "MediaRecorder API supported"
        : "Please use Chrome, Firefox, or Edge",
    });

    if (!hasMediaRecorder) {
      updateCheck("camera",      { state: "fail", detail: "Browser not supported" });
      updateCheck("microphone",  { state: "fail", detail: "Browser not supported" });
      updateCheck("connection",  { state: "warn", detail: "Unknown" });
      setDone(true);
      setRunning(false);
      return;
    }

    // ── 2. Camera + Microphone ──────────────────────────────────────
    await delay(500);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      setStream(mediaStream);

      const videoTrack = mediaStream.getVideoTracks()[0];
      const audioTrack = mediaStream.getAudioTracks()[0];

      updateCheck("camera", {
        state: videoTrack ? "pass" : "fail",
        detail: videoTrack
          ? `Detected: ${videoTrack.label || "Webcam"}`
          : "No camera found",
      });

      updateCheck("microphone", {
        state: audioTrack ? "pass" : "fail",
        detail: audioTrack
          ? `Detected: ${audioTrack.label || "Microphone"}`
          : "No microphone found",
      });
    } catch (err: unknown) {
      const message = (err as Error)?.message ?? "";
      const detail = message.includes("Permission")
        ? "Access denied — please allow camera & mic"
        : message.includes("NotFound")
        ? "No device found"
        : "Could not access device";

      updateCheck("camera",     { state: "fail", detail });
      updateCheck("microphone", { state: "fail", detail });
    }

    // ── 3. Connection check ─────────────────────────────────────────
    await delay(600);
    const isOnline = navigator.onLine;
    updateCheck("connection", {
      state: isOnline ? "pass" : "fail",
      detail: isOnline ? "Connected" : "No internet connection detected",
    });

    setDone(true);
    setRunning(false);
  }

  // Run checks on mount
  useEffect(() => {
    runChecks();
    // Cleanup stream on unmount
    return () => {
      stream?.getTracks().forEach((t) => t.stop());
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const allPass   = done && checks.every((c) => c.state === "pass" || c.state === "warn");
  const hasError  = done && checks.some((c) => c.state === "fail");

  return (
    <div
      className="min-h-screen flex items-center justify-center p-6"
      style={{
        background: "radial-gradient(ellipse at 20% 50%, rgba(64,150,255,0.08) 0%, transparent 60%), #0F172A",
      }}
    >
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <div
            className="inline-flex w-16 h-16 rounded-2xl items-center justify-center mb-4 shadow-[0_0_30px_rgba(64,150,255,0.35)]"
            style={{ background: "linear-gradient(135deg, #1e3a5f 0%, #1e4080 100%)", border: "1px solid rgba(64,150,255,0.3)" }}
          >
            <ShieldCheck size={28} className="text-[#4096ff]" />
          </div>
          <h1 className="text-[24px] font-bold text-white mb-1">System Pre-Check</h1>
          <p className="text-[13.5px] text-[#94A3B8]">
            Verifying your setup before starting the AI interview session
          </p>
        </div>

        {/* Check cards */}
        <div className="space-y-3 mb-6">
          {checks.map((check) => (
            <CheckRow key={check.id} check={check} />
          ))}
        </div>

        {/* Status message */}
        {done && (
          <div
            className={`rounded-xl px-4 py-3 mb-5 flex items-center gap-3 ${
              hasError
                ? "bg-red-500/10 border border-red-500/25"
                : "bg-emerald-500/10 border border-emerald-500/25"
            }`}
          >
            {hasError ? (
              <>
                <AlertTriangle size={16} className="text-red-400 shrink-0" />
                <p className="text-[13px] text-red-300">
                  Some checks failed. Please fix the issues above and retry, or proceed anyway.
                </p>
              </>
            ) : (
              <>
                <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                <p className="text-[13px] text-emerald-300">
                  All systems ready! You can proceed to start your interview.
                </p>
              </>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          {done && (
            <button
              onClick={runChecks}
              disabled={running}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-700 text-[13px] font-medium text-[#94A3B8] hover:text-white hover:border-slate-600 transition-all disabled:opacity-40"
            >
              <RefreshCw size={13} className={running ? "animate-spin" : ""} />
              Retry
            </button>
          )}
          <button
            onClick={onProceed}
            disabled={running || !done}
            className="flex-1 flex items-center justify-center gap-2 h-11 rounded-xl text-white text-[14px] font-bold transition-all disabled:opacity-40 disabled:cursor-not-allowed"
            style={{
              background: allPass ? "#4096ff" : hasError ? "#64748B" : "#4096ff",
              boxShadow: allPass ? "0 4px 16px rgba(64,150,255,0.4)" : "none",
            }}
          >
            {running ? (
              <>
                <Loader2 size={15} className="animate-spin" />
                Running checks…
              </>
            ) : (
              <>
                {allPass ? "Start Interview" : "Proceed Anyway"}
                <ArrowRight size={14} />
              </>
            )}
          </button>
        </div>

        {/* Interview info strip */}
        <div className="mt-6 grid grid-cols-3 gap-3">
          {[
            { icon: Clock,  label: "Session",   value: "~30 mins" },
            { icon: Video,  label: "Recording", value: "Enabled" },
            { icon: Users,  label: "AI Proctor", value: "Active" },
          ].map((item) => (
            <div
              key={item.label}
              className="rounded-xl px-3 py-3 text-center"
              style={{ background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)" }}
            >
              <item.icon size={15} className="text-[#4096ff] mx-auto mb-1" />
              <p className="text-[10px] text-[#64748B] font-medium">{item.label}</p>
              <p className="text-[12px] text-white font-bold">{item.value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Check Row ───────────────────────────────────────────────────────────────

function CheckRow({ check }: { check: SystemCheck }) {
  const iconMap: Record<string, React.ElementType> = {
    camera:      Camera,
    microphone:  Mic,
    browser:     ShieldCheck,
    connection:  Wifi,
  };
  const Icon = iconMap[check.id] ?? ShieldCheck;

  const stateStyles: Record<CheckState, string> = {
    idle:     "border-slate-700 bg-slate-800/50",
    checking: "border-slate-600 bg-slate-800/50",
    pass:     "border-emerald-500/30 bg-emerald-500/5",
    warn:     "border-amber-500/30 bg-amber-500/5",
    fail:     "border-red-500/30 bg-red-500/5",
  };

  const iconColorMap: Record<CheckState, string> = {
    idle:     "text-[#64748B]",
    checking: "text-[#4096ff]",
    pass:     "text-emerald-400",
    warn:     "text-amber-400",
    fail:     "text-red-400",
  };

  return (
    <div
      className={`flex items-center gap-4 px-4 py-3.5 rounded-xl border transition-all ${stateStyles[check.state]}`}
    >
      <div
        className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
        style={{ background: "rgba(255,255,255,0.04)" }}
      >
        <Icon size={17} className={iconColorMap[check.state]} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[13px] font-semibold text-white">{check.label}</p>
        <p className="text-[11.5px] text-[#64748B] truncate">
          {check.state === "checking"
            ? "Checking…"
            : check.detail ?? check.description}
        </p>
      </div>
      <div className="shrink-0">
        {check.state === "checking" ? (
          <Loader2 size={16} className="text-[#4096ff] animate-spin" />
        ) : check.state === "pass" ? (
          <CheckCircle2 size={16} className="text-emerald-400" />
        ) : check.state === "fail" ? (
          <XCircle size={16} className="text-red-400" />
        ) : check.state === "warn" ? (
          <AlertTriangle size={16} className="text-amber-400" />
        ) : null}
      </div>
    </div>
  );
}

// ─── Utility ─────────────────────────────────────────────────────────────────

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ─── Page Component ───────────────────────────────────────────────────────────

export default function Page() {
  const [ready, setReady] = useState(false);

  if (!ready) {
    return <PreCheckScreen onProceed={() => setReady(true)} />;
  }

  return <InterviewStudio />;
}