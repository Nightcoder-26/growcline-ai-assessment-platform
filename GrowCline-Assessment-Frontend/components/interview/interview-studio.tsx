"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Webcam from "react-webcam";
import { useReactMediaRecorder } from "react-media-recorder";
import { useSearchParams, useRouter } from "next/navigation";

import { StudioHeader }      from "./studio-header";
import { VideoStage }        from "./video-stage";
import { QuestionPanel }     from "./question-panel";
import { RecordingControls } from "./recording-controls";
import { SessionMetrics }    from "./session-metrics";
import { AlertCircle, CheckCircle2, X } from "lucide-react";

// ── Live Proctoring embeds ─────────────────────────────────────────────────
import { StatusPanel } from "@/components/live-proctoring/status-panel";
import { AlertsPanel } from "@/components/live-proctoring/alerts-panel";

import { useInterview }        from "@/hooks/useInterview";
import { useAuth }             from "@/hooks/useAuth";
import { useProctoring }       from "@/hooks/useProctoring";
import { useInterviewSession } from "@/contexts/InterviewSessionContext";
import apiClient               from "@/lib/apiClient";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CheatingStatus {
  riskScore:            number;
  multipleFaces:        number;
  tabSwitches:          number;
  faceMissing:          number;
  microphoneViolations: number;
  fullscreenExits:      number;
  recommendation:       string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function InterviewStudio() {
  const searchParams = useSearchParams();
  const router       = useRouter();
  const { userId }   = useAuth();

  const { updateSession, freezeSession } = useInterviewSession();

  const {
    interview,
    currentQuestion,
    loading,
    error: interviewError,
    startInterview,
    getNextQuestion,
    submitAnswer,
    endInterview,
  } = useInterview();

  // Query params
  const jobRole       = searchParams?.get("jobRole")       ?? "Software Engineer";
  const interviewType =
    (searchParams?.get("interviewType") as "TECHNICAL" | "HR" | "BEHAVIORAL" | "RESUME_BASED") ??
    "TECHNICAL";
  const difficulty =
    (searchParams?.get("difficulty") as "EASY" | "MEDIUM" | "HARD") ?? "MEDIUM";

  // ── UI state ─────────────────────────────────────────────────────────────

  const webcamRef = useRef<Webcam | null>(null);

  const [recording,             setRecording]             = useState(false);
  const [paused,                setPaused]                = useState(false);
  const [elapsed,               setElapsed]               = useState(0);
  const [camOn,                 setCamOn]                 = useState(true);
  const [micOn,                 setMicOn]                 = useState(true);
  const [clock,                 setClock]                 = useState("--:--");
  const [sessionStarted,        setSessionStarted]        = useState(false);
  const [sessionEnded,          setSessionEnded]          = useState(false);
  const [uploadStatus,          setUploadStatus]          = useState<"idle" | "uploading" | "done" | "error">("idle");
  const [toastMsg,              setToastMsg]              = useState<{ text: string; isError?: boolean } | null>(null);
  const [candidateAnswerText,   setCandidateAnswerText]   = useState("");
  const [answeredIds,           setAnsweredIds]           = useState<Set<string>>(new Set());

  // Per-question 2-minute countdown timer
  const QUESTION_SECONDS = 120;
  const [questionTimer,         setQuestionTimer]         = useState(QUESTION_SECONDS);
  const questionTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Question history for Previous navigation
  const [questionHistory, setQuestionHistory] = useState<import("@/hooks/useInterview").InterviewQuestion[]>([]);
  const [historyIndex,    setHistoryIndex]    = useState(-1); // -1 = live mode

  // Fullscreen UI state
  const [fullscreenRequested,   setFullscreenRequested]   = useState(false);
  const [fullscreenError,       setFullscreenError]       = useState<string | null>(null);

  // ── Cheating status (polled every 3 s) ───────────────────────────────────

  const [cheatingStatus,  setCheatingStatus]  = useState<CheatingStatus | null>(null);
  const cheatingPollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchCheatingStatus = useCallback(async () => {
    if (!interview?.id) return;
    try {
      const res  = await apiClient.get(`/api/interview/cheating/${interview.id}`);
      const data = res.data?.data as CheatingStatus;
      if (data) {
        setCheatingStatus(data);
        updateSession({
          riskScore:            data.riskScore,
          tabSwitches:          data.tabSwitches,
          multipleFaces:        data.multipleFaces,
          faceMissing:          data.faceMissing,
          microphoneViolations: data.microphoneViolations,
          fullscreenExits:      data.fullscreenExits,
          recommendation:       data.recommendation,
        });
      }
    } catch {
      // Non-fatal
    }
  }, [interview?.id, updateSession]);

  // ── react-media-recorder ─────────────────────────────────────────────────

  const {
    startRecording: startMediaRecorder,
    stopRecording:  stopMediaRecorder,
    mediaBlobUrl,
    clearBlobUrl,
  } = useReactMediaRecorder({ video: camOn, audio: micOn });

  // ── Live Proctoring hook ───────────────────────────────────────────────────

  const {
    status:              proctoringStatus,
    setStatus:           setProctoringStatus,
    alerts:              proctoringAlerts,
    logs:                proctoringLogs,
    logEvent,
    activateProctoring,
    deactivateProctoring,
  } = useProctoring(interview?.id ?? null, userId ?? null, fetchCheatingStatus);

  // ── Face detection callbacks ──────────────────────────────────────────────

  /**
   * Called by VideoStage when face presence changes.
   * ALWAYS updates the status panel display.
   * Violation event (NO_FACE) is only logged while recording (logEvent guards itself).
   */
  const handleFacePresenceChange = useCallback(
    (detected: boolean) => {
      setProctoringStatus((prev) => ({ ...prev, faceDetected: detected }));
      if (!detected) {
        logEvent("NO_FACE");
      }
    },
    [logEvent, setProctoringStatus],
  );

  const handleMultipleFacesDetected = useCallback(() => {
    logEvent("MULTIPLE_FACES");
  }, [logEvent]);

  // ── Clock ─────────────────────────────────────────────────────────────────

  useEffect(() => {
    const update = () =>
      setClock(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
    update();
    const id = setInterval(update, 1_000);
    return () => clearInterval(id);
  }, []);

  // ── Elapsed timer ─────────────────────────────────────────────────────────

  const live = recording && !paused;
  useEffect(() => {
    if (!live) return;
    const timer = setInterval(() => setElapsed((p) => p + 1), 1_000);
    return () => clearInterval(timer);
  }, [live]);

  // ── Per-question 2-minute countdown ──────────────────────────────────────
  // Resets on each new question; auto-advances when it hits 0.
  const isAutoAdvancingRef = useRef(false);

  useEffect(() => {
    if (!recording || !currentQuestion || historyIndex !== -1) return;
    setQuestionTimer(QUESTION_SECONDS);
    if (questionTimerRef.current) clearInterval(questionTimerRef.current);
    questionTimerRef.current = setInterval(() => {
      setQuestionTimer((prev) => {
        if (prev <= 1) {
          clearInterval(questionTimerRef.current!);
          if (!isAutoAdvancingRef.current) {
            isAutoAdvancingRef.current = true;
            showToast(`Time's up for Question ${currentQuestion.questionNumber}! Submitting answer & advancing…`, true);
            handleSubmitAndNext().finally(() => {
              isAutoAdvancingRef.current = false;
            });
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1_000);
    return () => {
      if (questionTimerRef.current) clearInterval(questionTimerRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recording, currentQuestion?.id, historyIndex]);

  // ── Proctoring lifecycle ────────────────────────────────────────────────────
  // Proctoring is activated ONLY when the user presses Record and deactivated
  // ONLY when they press Stop Recording (or finish/retake).
  // Do NOT auto-activate on session ready — violations before recording starts
  // are irrelevant and must not be counted.

  // ── Start interview session on mount ──────────────────────────────────────

  useEffect(() => {
    if (sessionStarted) return;
    setSessionStarted(true);
    startInterview({ jobRole, interviewType, difficulty, totalQuestions: 15 })
      .then(({ interview: sess }) => {
        updateSession({
          interviewId:     sess.id,
          sessionId:       sess.id,
          jobRole,
          startTime:       sess.startedAt ?? new Date().toISOString(),
          date:            new Date().toISOString().slice(0, 10),
          recordingStatus: "idle",
          status:          "active",
        });
      })
      .catch((err) => showToast(`Could not start interview: ${err.message}`, true));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Mirror mic → proctoring status ───────────────────────────────────────

  const prevMicOn = useRef(micOn);
  useEffect(() => {
    if (!interview?.id) return;
    if (prevMicOn.current && !micOn) {
      logEvent("MICROPHONE_DISABLED");
      setProctoringStatus((prev) => ({ ...prev, microphone: false }));
    } else if (!prevMicOn.current && micOn) {
      setProctoringStatus((prev) => ({ ...prev, microphone: true }));
    }
    prevMicOn.current = micOn;
  }, [micOn, interview?.id, logEvent, setProctoringStatus]);

  // ── Mirror cam → proctoring status ───────────────────────────────────────

  const prevCamOn = useRef(camOn);
  useEffect(() => {
    if (!interview?.id) return;
    if (prevCamOn.current && !camOn) {
      logEvent("CAMERA_DISABLED");
    }
    prevCamOn.current = camOn;
  }, [camOn, interview?.id, logEvent]);

  // ── Poll cheating status ──────────────────────────────────────────────────

  useEffect(() => {
    if (!interview?.id) return;
    fetchCheatingStatus();
    cheatingPollRef.current = setInterval(fetchCheatingStatus, 3_000);
    return () => {
      if (cheatingPollRef.current) clearInterval(cheatingPollRef.current);
    };
  }, [interview?.id, fetchCheatingStatus]);

  // ── Toast ──────────────────────────────────────────────────────────────────

  const showToast = useCallback((msg: string, isError = false) => {
    setToastMsg({ text: msg, isError });
    setTimeout(() => setToastMsg(null), 8_000);
  }, []);

  // ── Start Recording (user gesture — request fullscreen HERE) ──────────────

  const handleStartRecording = useCallback(async () => {
    setFullscreenError(null);

    // 1. Request fullscreen from this user gesture
    try {
      if (document.documentElement.requestFullscreen) {
        await document.documentElement.requestFullscreen();
        setFullscreenRequested(true);
        console.log("[STUDIO] fullscreen entered");
      }
    } catch (err) {
      // Fullscreen failed — still allow recording but show warning
      const msg = err instanceof Error ? err.message : "Fullscreen request failed";
      console.warn("[STUDIO] fullscreen request failed:", msg);
      setFullscreenError("Could not enter fullscreen. Recording continues without fullscreen lock.");
    }

    // 2. Start MediaRecorder
    setRecording(true);
    setPaused(false);
    setElapsed(0);
    setCandidateAnswerText("");
    clearBlobUrl();
    startMediaRecorder();

    // 3. Activate proctoring (enables logEvent to fire violations)
    activateProctoring();

    console.log("[STUDIO] recording started, proctoring activated");
  }, [clearBlobUrl, startMediaRecorder, activateProctoring]);

  // ── Stop Recording ────────────────────────────────────────────────────────

  const handleStopRecording = useCallback(() => {
    // Deactivate FIRST so the fullscreen exit from cleanup is NOT counted as a violation
    deactivateProctoring();
    setRecording(false);
    stopMediaRecorder();
    console.log("[STUDIO] recording stopped, proctoring deactivated");
  }, [stopMediaRecorder, deactivateProctoring]);

  // ── Retake ────────────────────────────────────────────────────────────────

  const handleRetake = useCallback(() => {
    deactivateProctoring();
    setRecording(false);
    setPaused(false);
    setElapsed(0);
    setCandidateAnswerText("");
    clearBlobUrl();
  }, [clearBlobUrl, deactivateProctoring]);

  // ── Submit answer + next question ─────────────────────────────────────────

  const handleSubmitAndNext = useCallback(async () => {
    if (!interview || !currentQuestion) return;

    // If browsing history, snap back to live mode first
    if (historyIndex !== -1) {
      setHistoryIndex(-1);
      return;
    }

    const answer = candidateAnswerText.trim() || "No response provided within 2-minute time limit.";
    try {
      const eval_ = await submitAnswer(interview.id, currentQuestion.id, answer);
      setAnsweredIds((prev) => new Set([...prev, currentQuestion.id]));

      // Push answered question to history
      setQuestionHistory((prev) => [...prev, currentQuestion]);

      if (eval_.interviewComplete) {
        showToast("Interview questions complete! Stopping continuous recording…");
        deactivateProctoring();
        setRecording(false);
        stopMediaRecorder();
        try {
          await apiClient.post(`/api/interview/end/${interview.id}`);
        } catch {
          await endInterview(interview.id);
        }
        if (document.fullscreenElement) {
          document.exitFullscreen().catch(() => {});
        }
        updateSession({
          recordingStatus: "ended",
          duration: `${Math.max(1, Math.round(elapsed / 60))} Minutes`,
        });
        freezeSession();
        setSessionEnded(true);
        return;
      }

      await getNextQuestion(interview.id);
      // Continuous recording mode: DO NOT stop recording or clear video blob!
      setCandidateAnswerText("");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to submit answer.";
      showToast(msg, true);
    }
  }, [
    interview, currentQuestion, candidateAnswerText, historyIndex,
    submitAnswer, endInterview, getNextQuestion, stopMediaRecorder,
    showToast, elapsed, updateSession, freezeSession, deactivateProctoring,
  ]);

  // ── Go to previous question (browse history) ──────────────────────────────

  const handlePrev = useCallback(() => {
    if (questionHistory.length === 0) return;
    if (historyIndex === -1) {
      // Jump to last answered question in history
      setHistoryIndex(questionHistory.length - 1);
    } else if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1);
    }
  }, [questionHistory, historyIndex]);

  // The question currently displayed (either live or from history)
  const displayedQuestion =
    historyIndex !== -1 && questionHistory[historyIndex]
      ? questionHistory[historyIndex]
      : currentQuestion;

  const displayedIndex =
    historyIndex !== -1
      ? historyIndex
      : (displayedQuestion?.questionNumber ?? 1) - 1;

  const canGoPrev = historyIndex !== -1 ? historyIndex > 0 : questionHistory.length > 0;

  // ── Upload video ──────────────────────────────────────────────────────────

  const handleUpload = useCallback(async () => {
    if (!mediaBlobUrl || !interview) {
      showToast("Nothing to upload yet. Stop recording first.");
      return;
    }
    setUploadStatus("uploading");
    try {
      const blob = await fetch(mediaBlobUrl).then((r) => r.blob());
      const form = new FormData();
      form.append("interview_id", interview.id);
      form.append("duration",     String(elapsed));
      form.append("video_file",   blob, "recording.webm");

      await apiClient.post("/api/recordings/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setUploadStatus("done");
      showToast("Recording uploaded successfully! ✅");
    } catch (err) {
      setUploadStatus("error");
      showToast(err instanceof Error ? err.message : "Upload failed.", true);
    }
  }, [mediaBlobUrl, interview, elapsed]);

  // ── Derived values ────────────────────────────────────────────────────────

  const { clarity, pace } = useMemo(
    () => (live ? { clarity: 95, pace: 78 } : { clarity: 0, pace: 0 }),
    [live],
  );

  const totalQuestions = interview?.totalQuestions ?? 15;
  const currentQNum    = interview?.currentQuestion ?? 1;
  const answeredArray  = Array.from({ length: totalQuestions }, (_, i) => {
    if (!currentQuestion) return false;
    return i + 1 < currentQuestion.questionNumber || answeredIds.has(currentQuestion.id);
  });

  const riskColor = (s: number) =>
    s < 20 ? "text-emerald-400" : s < 50 ? "text-amber-400" : "text-rose-400";
  const riskBg = (s: number) =>
    s < 20
      ? "bg-emerald-500/10 border-emerald-500/20"
      : s < 50
      ? "bg-amber-500/10 border-amber-500/20"
      : "bg-rose-500/10 border-rose-500/20";

  // ── Render: session ended ─────────────────────────────────────────────────

  if (sessionEnded) {
    return (
      <main className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-8">
        <div className="max-w-xl w-full rounded-[28px] border border-white/10 bg-[#1E293B] p-8 text-center space-y-6 shadow-2xl backdrop-blur-xl">
          <div className="text-5xl">🎉</div>
          <div>
            <h2 className="text-2xl font-bold text-white">Interview Complete!</h2>
            <p className="text-slate-400 text-sm mt-1">
              Your single continuous video recording for all questions has been finalized.
            </p>
          </div>

          {/* Upload Status Card */}
          <div className="rounded-2xl border border-slate-700 bg-[#0F172A] p-5 text-left space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-white">Full Interview Continuous Recording</p>
                <p className="text-xs text-slate-400 mt-0.5">Total Video Length: {formatTime(elapsed)}</p>
              </div>
              <span className={`text-xs px-3 py-1 rounded-full font-bold ${
                uploadStatus === "done"
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : uploadStatus === "uploading"
                  ? "bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse"
                  : "bg-blue-500/20 text-blue-400 border border-blue-500/30"
              }`}>
                {uploadStatus === "done" ? "Uploaded to Cloud ✅" : uploadStatus === "uploading" ? "Uploading…" : "Ready for Upload"}
              </span>
            </div>

            <div className="flex gap-3 pt-2">
              <button
                onClick={handleUpload}
                disabled={!mediaBlobUrl || uploadStatus === "uploading" || uploadStatus === "done"}
                className="flex-1 flex items-center justify-center gap-2 rounded-xl bg-[#4096ff] py-3 text-sm font-semibold text-white hover:bg-[#2f86ff] transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
              >
                {uploadStatus === "uploading" ? (
                  <>
                    <div className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
                    Uploading Recording…
                  </>
                ) : uploadStatus === "done" ? (
                  "✅ Video Uploaded Successfully"
                ) : (
                  "📤 Upload Recording Now"
                )}
              </button>
            </div>
          </div>

          <div className="pt-2">
            <button
              onClick={() => router.push(`/interview-analytics?interviewId=${interview?.id}`)}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-emerald-600 py-3.5 text-sm font-bold text-white hover:bg-emerald-500 transition shadow-lg"
            >
              View Analytics Report →
            </button>
          </div>
        </div>
      </main>
    );
  }

  // ── Render: loading ───────────────────────────────────────────────────────

  if (loading && !currentQuestion) {
    return (
      <main className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-[#4096ff] border-t-transparent animate-spin" />
          <p className="text-slate-600 text-sm font-semibold">Preparing your AI interview studio…</p>
        </div>
      </main>
    );
  }

  // ── Render: main studio ───────────────────────────────────────────────────

  return (
    <main className="min-h-screen bg-[#F8FAFC]">

      {/* Toast Notification */}
      {toastMsg && (
        <div
          className={`fixed top-6 right-6 z-[9999] max-w-md w-full rounded-2xl border px-5 py-4 text-white shadow-2xl backdrop-blur-xl flex items-start gap-3 transition-all duration-300 ${
            toastMsg.isError
              ? "bg-[#1E293B]/95 border-red-500/40 text-red-100 shadow-[0_10px_30px_rgba(239,68,68,0.25)]"
              : "bg-[#1E293B]/95 border-[#4096ff]/40 text-blue-100 shadow-[0_10px_30px_rgba(64,150,255,0.25)]"
          }`}
        >
          {toastMsg.isError ? (
            <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          ) : (
            <CheckCircle2 className="w-5 h-5 text-[#4096ff] shrink-0 mt-0.5" />
          )}
          <div className="flex-1 min-w-0 pr-1">
            <p className="text-[13px] font-bold tracking-tight text-white">
              {toastMsg.isError ? "System / Upload Notice" : "Notification"}
            </p>
            <p className="text-[12.5px] leading-relaxed mt-0.5 break-words font-medium opacity-90">
              {toastMsg.text}
            </p>
          </div>
          <button
            onClick={() => setToastMsg(null)}
            className="text-white/60 hover:text-white transition-colors p-1 rounded-lg hover:bg-white/10 shrink-0"
            title="Dismiss notification"
          >
            <X size={15} />
          </button>
        </div>
      )}

      {/* Fullscreen error banner */}
      {fullscreenError && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[9999] max-w-md rounded-2xl bg-amber-900/95 border border-amber-500/50 px-5 py-3.5 text-amber-100 shadow-2xl text-sm flex items-center gap-3 backdrop-blur-xl">
          <span>⚠️ {fullscreenError}</span>
          <button
            className="ml-auto text-amber-300 hover:text-white underline text-xs whitespace-nowrap font-semibold"
            onClick={async () => {
              try {
                await document.documentElement.requestFullscreen();
                setFullscreenError(null);
              } catch {/* ignore */}
            }}
          >
            Retry Fullscreen
          </button>
        </div>
      )}

      {/* Interview error banner */}
      {interviewError && (
        <div className="fixed top-6 left-1/2 -translate-x-1/2 z-[9999] max-w-md rounded-2xl bg-rose-900/95 border border-rose-500/50 px-5 py-3.5 text-rose-100 shadow-2xl text-sm backdrop-blur-xl">
          ⚠️ {interviewError}
        </div>
      )}

      <div className="relative mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8">
        <StudioHeader clock={clock} />

        {/* ── Main Layout Grid: Left Question Focus / Right Compact Video & Proctoring ── */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.6fr_1fr]">

          {/* Left Column: Recording Controls (always visible) + Question Panel (locked until recording) */}
          <div className="flex flex-col gap-5">
            <RecordingControls
              recording={recording}
              paused={paused}
              uploadStatus={uploadStatus}
              hasRecording={!!mediaBlobUrl}
              onStart={handleStartRecording}
              onPauseToggle={() => setPaused((v) => !v)}
              onStop={handleStopRecording}
              onRetake={handleRetake}
              onUpload={handleUpload}
              onSubmitNext={handleSubmitAndNext}
            />

            {/* Question is LOCKED until recording starts */}
            {!recording && !mediaBlobUrl ? (
              <div className="rounded-[28px] border border-dashed border-[#4096ff]/40 bg-[#111827]/80 p-10 flex flex-col items-center justify-center gap-4 text-center shadow-inner">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#4096ff]/10">
                  <svg className="h-8 w-8 text-[#4096ff]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11c0-1.1.9-2 2-2s2 .9 2 2-2 4-2 4m-2 0H8m4 0h.01M12 19a7 7 0 100-14 7 7 0 000 14z" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-white">Press ▶ Start Recording to Begin</h3>
                <p className="text-sm text-slate-400 max-w-xs">Your interview question will appear here once you start the recording. Each question has a <span className="text-[#4096ff] font-semibold">2-minute timer</span>.</p>
              </div>
            ) : displayedQuestion ? (
              <>
                {/* 2-minute countdown timer */}
                {recording && historyIndex === -1 && (
                  <div className={`flex items-center gap-3 rounded-2xl border px-5 py-3 ${
                    questionTimer <= 30
                      ? "border-red-500/40 bg-red-950/60 text-red-300"
                      : questionTimer <= 60
                      ? "border-amber-500/40 bg-amber-950/60 text-amber-300"
                      : "border-[#4096ff]/30 bg-[#111827]/80 text-[#4096ff]"
                  }`}>
                    <svg className="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-mono font-bold text-lg">
                      {String(Math.floor(questionTimer / 60)).padStart(2, "0")}:{String(questionTimer % 60).padStart(2, "0")}
                    </span>
                    <span className="text-sm ml-1 font-medium opacity-80">
                      {questionTimer <= 0 ? "⏰ Time up — submit or continue" : "remaining for this question"}
                    </span>
                  </div>
                )}
                {historyIndex !== -1 && (
                  <div className="rounded-2xl border border-amber-500/30 bg-amber-950/40 px-5 py-3 text-amber-300 text-sm font-medium flex items-center gap-2">
                    📖 Reviewing Question {historyIndex + 1} — <button onClick={() => setHistoryIndex(-1)} className="underline text-amber-200 hover:text-white">Return to Live Question</button>
                  </div>
                )}
                <QuestionPanel
                  question={{
                    questionId: displayedQuestion.id,
                    category:   displayedQuestion.questionType,
                    prompt:     displayedQuestion.questionText,
                    hint:       `Question ${displayedQuestion.questionNumber} of ${totalQuestions}`,
                  }}
                  index={displayedIndex}
                  total={totalQuestions}
                  answered={answeredArray}
                  loading={loading && historyIndex === -1}
                  canGoPrev={canGoPrev}
                  isTimeUp={recording && historyIndex === -1 && questionTimer <= 0}
                  onPrev={handlePrev}
                  onNext={handleSubmitAndNext}
                  onJump={() => {}}
                  candidateAnswer={historyIndex === -1 ? candidateAnswerText : ""}
                  onAnswerChange={historyIndex === -1 ? setCandidateAnswerText : undefined}
                />
              </>
            ) : (
              <div className="rounded-[28px] border border-white/10 bg-[#1E293B] p-6 flex items-center justify-center min-h-[200px]">
                <div className="w-8 h-8 rounded-full border-4 border-[#4096ff] border-t-transparent animate-spin" />
              </div>
            )}

            <SessionMetrics live={live} clarity={clarity} pace={pace} />
          </div>

          {/* Right Column: Compact PIP Webcam Stage + Proctoring Status */}
          <div className="flex flex-col gap-5">
            <VideoStage
              webcamRef={webcamRef}
              recording={recording}
              paused={paused}
              camOn={camOn}
              micOn={micOn}
              elapsed={formatTime(elapsed)}
              take={currentQNum}
              compact={true}
              faceDetected={proctoringStatus.faceDetected}
              onToggleCam={() => setCamOn((v) => !v)}
              onToggleMic={() => setMicOn((v) => !v)}
              onFacePresenceChange={handleFacePresenceChange}
              onMultipleFacesDetected={handleMultipleFacesDetected}
            />

            {/* Live Proctoring Status */}
            {interview?.id && (
              <div className="space-y-4">
                <StatusPanel
                  faceDetected={proctoringStatus.faceDetected}
                  microphone={proctoringStatus.microphone}
                  fullscreen={proctoringStatus.fullscreen}
                  network={proctoringStatus.network}
                />
                <AlertsPanel alerts={proctoringAlerts} />
              </div>
            )}
          </div>

        </div>

        {/* ── Fullscreen lock banner (shown when recording but not in fullscreen) ── */}
        {recording && !proctoringStatus.fullscreen && (
          <div className="rounded-2xl border border-amber-500/40 bg-amber-900/20 px-5 py-4 flex items-center gap-4">
            <span className="text-amber-400 text-lg">⚠️</span>
            <div className="flex-1">
              <p className="text-amber-200 font-semibold text-sm">Fullscreen Required</p>
              <p className="text-amber-300/70 text-xs mt-0.5">
                Please return to fullscreen mode. Each exit is logged as a proctoring violation.
              </p>
            </div>
            <button
              className="rounded-xl bg-amber-500 px-4 py-2 text-sm font-bold text-white hover:bg-amber-400 transition"
              onClick={async () => {
                try {
                  await document.documentElement.requestFullscreen();
                } catch {/* ignore */}
              }}
            >
              Return to Fullscreen
            </button>
          </div>
        )}

        {/* ── Live Proctoring panels ── */}
        {interview?.id && (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <div>
              <div className="mb-3 flex items-center gap-2">
                <span className="inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
                <h2 className="text-xs font-bold uppercase tracking-widest text-[#1E293B]">
                  Live Proctoring Status
                </h2>
              </div>
              <StatusPanel
                faceDetected={proctoringStatus.faceDetected}
                microphone={proctoringStatus.microphone}
                fullscreen={proctoringStatus.fullscreen}
                network={proctoringStatus.network}
              />
            </div>

            <div>
              <div className="mb-3 flex items-center gap-2">
                <span className="inline-flex h-2.5 w-2.5 rounded-full bg-amber-500 animate-pulse" />
                <h2 className="text-xs font-bold uppercase tracking-widest text-[#1E293B]">
                  Live Proctoring Alerts
                </h2>
              </div>
              <AlertsPanel alerts={proctoringAlerts} />
            </div>
          </div>
        )}

        {/* ── Risk Assessment Summary ── */}
        {interview?.id && (
          <div>
            <div className="mb-3 flex items-center gap-2">
              <span className="inline-flex h-2.5 w-2.5 rounded-full bg-[#4096ff] animate-pulse" />
              <h2 className="text-xs font-bold uppercase tracking-widest text-[#1E293B]">
                Cheating Detection Risk Engine
              </h2>
            </div>

            <div className="rounded-[28px] border border-white/10 bg-[#1E293B] p-6 shadow-2xl backdrop-blur-xl">
              {cheatingStatus ? (
                <>
                  <div className="mb-5 flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-bold text-white">Risk Assessment Summary</h3>
                      <p className="mt-1 text-sm text-slate-400">
                        Real-time risk scoring — derived from MongoDB proctoring events
                      </p>
                    </div>

                    <div className={`rounded-2xl border px-5 py-3 text-center ${riskBg(cheatingStatus.riskScore)}`}>
                      <p className={`text-3xl font-extrabold ${riskColor(cheatingStatus.riskScore)}`}>
                        {cheatingStatus.riskScore}
                      </p>
                      <p className="text-xs text-slate-400 mt-0.5 font-medium">Risk Score</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
                    {[
                      { label: "Multiple Faces",   value: cheatingStatus.multipleFaces,        icon: "👥" },
                      { label: "Tab Switches",     value: cheatingStatus.tabSwitches,          icon: "🔄" },
                      { label: "Face Missing",     value: cheatingStatus.faceMissing,          icon: "👤" },
                      { label: "Mic Violations",   value: cheatingStatus.microphoneViolations, icon: "🎙️" },
                      { label: "Fullscreen Exits", value: cheatingStatus.fullscreenExits,      icon: "⛶" },
                    ].map(({ label, value, icon }) => (
                      <div key={label} className="flex flex-col items-center rounded-2xl bg-[#0F172A] p-4">
                        <span className="text-xl">{icon}</span>
                        <span className={`mt-1 text-2xl font-bold ${value === 0 ? "text-emerald-400" : "text-rose-400"}`}>
                          {value}
                        </span>
                        <span className="mt-1 text-center text-xs text-slate-400 font-medium">{label}</span>
                      </div>
                    ))}

                    <div className="flex flex-col items-center justify-center rounded-2xl bg-[#0F172A] p-4">
                      <span className="text-xl">🛡️</span>
                      <span className={`mt-1 text-center text-sm font-semibold ${riskColor(cheatingStatus.riskScore)}`}>
                        {cheatingStatus.recommendation}
                      </span>
                      <span className="mt-1 text-xs text-slate-400 font-medium">Verdict</span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex items-center gap-4 py-2">
                  <div className="w-6 h-6 rounded-full border-2 border-[#4096ff] border-t-transparent animate-spin flex-shrink-0" />
                  <p className="text-slate-300 text-sm font-medium">
                    Initialising backend cheating detection engine…
                  </p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}