"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Webcam from "react-webcam";
import { useReactMediaRecorder } from "react-media-recorder";
import { useSearchParams, useRouter } from "next/navigation";

import { StudioHeader } from "./studio-header";
import { VideoStage } from "./video-stage";
import { QuestionPanel } from "./question-panel";
import { RecordingControls } from "./recording-controls";
import { SessionMetrics } from "./session-metrics";

// ── Live Proctoring embeds ─────────────────────────────────────────────────
import { StatusPanel } from "@/components/live-proctoring/status-panel";
import { AlertsPanel } from "@/components/live-proctoring/alerts-panel";

import { useInterview } from "@/hooks/useInterview";
import { useAuth } from "@/hooks/useAuth";
import { useProctoring } from "@/hooks/useProctoring";
import apiClient from "@/lib/apiClient";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

// ---------------------------------------------------------------------------
// Cheating Status shape (from GET /api/interview/cheating/{id})
// ---------------------------------------------------------------------------

interface CheatingStatus {
  riskScore: number;
  multipleFaces: number;
  tabSwitches: number;
  faceMissing: number;
  microphoneViolations: number;
  fullscreenExits: number;
  recommendation: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function InterviewStudio() {
  const searchParams = useSearchParams();
  const router       = useRouter();
  const { userId }   = useAuth();

  const {
    interview,
    currentQuestion,
    evaluation,
    summary,
    loading,
    error: interviewError,
    startInterview,
    getNextQuestion,
    submitAnswer,
    endInterview,
  } = useInterview();

  // Read config from query params (or fall back to sensible defaults)
  const jobRole      = searchParams?.get("jobRole")      ?? "Software Engineer";
  const interviewType =
    (searchParams?.get("interviewType") as "TECHNICAL" | "HR" | "BEHAVIORAL" | "RESUME_BASED") ??
    "TECHNICAL";
  const difficulty =
    (searchParams?.get("difficulty") as "EASY" | "MEDIUM" | "HARD") ?? "MEDIUM";

  // ── UI state ─────────────────────────────────────────────────────────────

  const webcamRef = useRef<Webcam | null>(null);
  const [recording,     setRecording]     = useState(false);
  const [paused,        setPaused]        = useState(false);
  const [elapsed,       setElapsed]       = useState(0);
  const [camOn,         setCamOn]         = useState(true);
  const [micOn,         setMicOn]         = useState(true);
  const [clock,         setClock]         = useState("--:--");
  const [sessionStarted, setSessionStarted] = useState(false);
  const [sessionEnded,   setSessionEnded]   = useState(false);
  const [uploadStatus,  setUploadStatus]  = useState<"idle" | "uploading" | "done" | "error">("idle");
  const [toastMsg,      setToastMsg]      = useState<string | null>(null);
  const [candidateAnswerText, setCandidateAnswerText] = useState("");

  // Track answered question IDs so we can show progress dots
  const [answeredIds, setAnsweredIds] = useState<Set<string>>(new Set());

  // ── Cheating status state (polled every 10 s once session starts) ────────

  const [cheatingStatus, setCheatingStatus] = useState<CheatingStatus | null>(null);
  const cheatingPollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // ── react-media-recorder ─────────────────────────────────────────────────

  const { startRecording: startMediaRecorder, stopRecording: stopMediaRecorder, mediaBlobUrl, clearBlobUrl } =
    useReactMediaRecorder({
      video: camOn,
      audio: micOn,
    });

  // ── Live Proctoring hook ───────────────────────────────────────────────────
  const {
    status: proctoringStatus,
    setStatus: setProctoringStatus,
    alerts: proctoringAlerts,
    logs:   proctoringLogs,
    logEvent,
  } = useProctoring(interview?.id ?? null, userId ?? null);

  // Handle Face Presence / Away Warnings
  const handleFacePresenceChange = useCallback((detected: boolean) => {
    setProctoringStatus((prev) => ({ ...prev, faceDetected: detected }));
    if (!detected) {
      logEvent("NO_FACE");
    }
  }, [logEvent, setProctoringStatus]);

  // ── Clock ──────────────────────────────────────────────────────────────────

  useEffect(() => {
    const updateClock = () => {
      setClock(
        new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      );
    };
    updateClock();
    const id = setInterval(updateClock, 1000);
    return () => clearInterval(id);
  }, []);

  // ── Elapsed timer ─────────────────────────────────────────────────────────

  const live = recording && !paused;
  useEffect(() => {
    if (!live) return;
    const timer = setInterval(() => setElapsed((prev) => prev + 1), 1000);
    return () => clearInterval(timer);
  }, [live]);

  // ── Start session (fetches first AI question) ─────────────────────────────

  useEffect(() => {
    if (sessionStarted) return;
    setSessionStarted(true);
    startInterview({ jobRole, interviewType, difficulty, totalQuestions: 5 }).catch(
      (err) => showToast(`Could not start interview: ${err.message}`, true)
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Mirror mic state into proctoring ──────────────────────────────────────
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

  // ── Mirror cam state into proctoring ──────────────────────────────────────
  const prevCamOn = useRef(camOn);
  useEffect(() => {
    if (!interview?.id) return;
    if (prevCamOn.current && !camOn) {
      logEvent("CAMERA_DISABLED");
    }
    prevCamOn.current = camOn;
  }, [camOn, interview?.id, logEvent]);

  // ── Cheating status polling (every 10 s once interview is live) ───────────

  useEffect(() => {
    if (!interview?.id) return;

    const fetchCheatingStatus = async () => {
      try {
        const res = await apiClient.get(`/api/interview/cheating/${interview.id}`);
        const data = res.data?.data as CheatingStatus;
        if (data) setCheatingStatus(data);
      } catch {
        // Non-fatal: cheating status poll failure does not disrupt interview
      }
    };

    fetchCheatingStatus();
    cheatingPollRef.current = setInterval(fetchCheatingStatus, 10_000);

    return () => {
      if (cheatingPollRef.current) clearInterval(cheatingPollRef.current);
    };
  }, [interview?.id]);

  // ── Toast helper ──────────────────────────────────────────────────────────

  const showToast = (msg: string, _isError = false) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 4000);
  };

  // ── Recording controls ────────────────────────────────────────────────────

  const handleStartRecording = useCallback(() => {
    setRecording(true);
    setPaused(false);
    setElapsed(0);
    setCandidateAnswerText("");
    clearBlobUrl();
    startMediaRecorder();
  }, [clearBlobUrl, startMediaRecorder]);

  const handleStopRecording = useCallback(() => {
    setRecording(false);
    stopMediaRecorder();
  }, [stopMediaRecorder]);

  const handleRetake = useCallback(() => {
    setRecording(false);
    setPaused(false);
    setElapsed(0);
    setCandidateAnswerText("");
    clearBlobUrl();
  }, [clearBlobUrl]);

  // ── Submit answer text + move to next question ────────────────────────────

  const handleSubmitAndNext = useCallback(async () => {
    if (!interview || !currentQuestion) return;

    const answer = candidateAnswerText.trim() || "No spoken answer recorded.";
    try {
      const eval_ = await submitAnswer(interview.id, currentQuestion.id, answer);
      setAnsweredIds((prev) => new Set([...prev, currentQuestion.id]));

      if (eval_.interviewComplete) {
        showToast("Interview complete! Generating analytics report…");

        try {
          await apiClient.post(`/api/interview/end/${interview.id}`);
        } catch {
          await endInterview(interview.id);
        }

        setSessionEnded(true);

        setTimeout(() => {
          router.push(`/interview-analytics?interviewId=${interview.id}`);
        }, 1500);
        return;
      }

      await getNextQuestion(interview.id);
      setRecording(false);
      setPaused(false);
      setElapsed(0);
      setCandidateAnswerText("");
      clearBlobUrl();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to submit answer.";
      showToast(msg, true);
    }
  }, [interview, currentQuestion, candidateAnswerText, submitAnswer, endInterview, getNextQuestion, clearBlobUrl, router]);

  // ── Upload video blob ─────────────────────────────────────────────────────

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
      form.append("duration", String(elapsed));
      form.append("video_file", blob, "recording.webm");

      await apiClient.post("/api/recordings/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setUploadStatus("done");
      showToast("Recording uploaded successfully! ✅");
    } catch (err) {
      setUploadStatus("error");
      const msg = err instanceof Error ? err.message : "Upload failed.";
      showToast(msg, true);
    }
  }, [mediaBlobUrl, interview, elapsed]);

  // ── Derived values ────────────────────────────────────────────────────────

  const { clarity, pace } = useMemo(() => {
    if (!live) return { clarity: 0, pace: 0 };
    return { clarity: 95, pace: 78 };
  }, [live]);

  const totalQuestions = interview?.totalQuestions ?? 5;
  const currentQNum    = interview?.currentQuestion ?? 1;
  const answeredArray  = Array.from({ length: totalQuestions }, (_, i) => {
    if (!currentQuestion) return false;
    const qNum = currentQuestion.questionNumber;
    return i + 1 < qNum || answeredIds.has(currentQuestion.id);
  });

  // ── Risk colour helper for the cheating widget ────────────────────────────

  const riskColor = (score: number) =>
    score < 20 ? "text-emerald-400" : score < 50 ? "text-amber-400" : "text-rose-400";
  const riskBg = (score: number) =>
    score < 20 ? "bg-emerald-500/10 border-emerald-500/20" : score < 50 ? "bg-amber-500/10 border-amber-500/20" : "bg-rose-500/10 border-rose-500/20";

  // ── Render: Session ended (brief transition before redirect) ──────────────

  if (sessionEnded) {
    return (
      <main className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-8">
        <div className="max-w-lg w-full rounded-[28px] border border-white/10 bg-[#1E293B] p-8 text-center space-y-4 shadow-2xl">
          <div className="text-5xl">🎉</div>
          <h2 className="text-2xl font-bold text-white">Interview Complete!</h2>
          <p className="text-slate-400">
            Your session has ended. Redirecting to your detailed Analytics Report...
          </p>
          <div className="flex justify-center mt-4">
            <div className="w-8 h-8 rounded-full border-4 border-[#4096ff] border-t-transparent animate-spin" />
          </div>
        </div>
      </main>
    );
  }

  // ── Render: Loading initial question ──────────────────────────────────────

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

  // ── Render: Main studio ───────────────────────────────────────────────────

  return (
    <main className="min-h-screen bg-[#F8FAFC]">
      {/* Toast */}
      {toastMsg && (
        <div className="fixed top-4 right-4 z-50 max-w-sm rounded-2xl bg-[#1E293B] border border-white/10 px-5 py-3 text-white shadow-xl text-sm">
          {toastMsg}
        </div>
      )}

      {/* Global error banner */}
      {interviewError && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 max-w-md rounded-2xl bg-rose-900/90 border border-rose-500/40 px-5 py-3 text-rose-100 shadow-xl text-sm">
          ⚠️ {interviewError}
        </div>
      )}

      <div className="relative mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8">
        <StudioHeader clock={clock} />

        {/* ── Main grid: Camera + Question/Controls ─────────────────────── */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.6fr_1fr]">
          <VideoStage
            webcamRef={webcamRef}
            recording={recording}
            paused={paused}
            camOn={camOn}
            micOn={micOn}
            elapsed={formatTime(elapsed)}
            take={currentQNum}
            faceDetected={proctoringStatus.faceDetected}
            onToggleCam={() => setCamOn((v) => !v)}
            onToggleMic={() => setMicOn((v) => !v)}
            onFacePresenceChange={handleFacePresenceChange}
          />

          <div className="flex flex-col gap-4">
            {currentQuestion ? (
              <QuestionPanel
                question={{
                  questionId: currentQuestion.id,
                  category:   currentQuestion.questionType,
                  prompt:     currentQuestion.questionText,
                  hint:       `Question ${currentQuestion.questionNumber} of ${totalQuestions}`,
                }}
                index={currentQNum - 1}
                total={totalQuestions}
                answered={answeredArray}
                loading={loading}
                onPrev={() => {}}
                onNext={handleSubmitAndNext}
                onJump={() => {}}
                candidateAnswer={candidateAnswerText}
                onAnswerChange={setCandidateAnswerText}
              />
            ) : (
              <div className="rounded-[28px] border border-white/10 bg-[#1E293B] p-6 flex items-center justify-center min-h-[200px]">
                <div className="w-8 h-8 rounded-full border-4 border-[#4096ff] border-t-transparent animate-spin" />
              </div>
            )}

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

            <SessionMetrics live={live} clarity={clarity} pace={pace} />
          </div>
        </div>

        {/* ── Live Proctoring Status Panel ──────────────────────────────── */}
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

        {/* ── Cheating Detection Widget ─────────────────────────────────── */}
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
                        Real-time risk scoring engine — live updates from backend
                      </p>
                    </div>

                    <div
                      className={`rounded-2xl border px-5 py-3 text-center ${riskBg(cheatingStatus.riskScore)}`}
                    >
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
                      <div
                        key={label}
                        className="flex flex-col items-center rounded-2xl bg-[#0F172A] p-4"
                      >
                        <span className="text-xl">{icon}</span>
                        <span
                          className={`mt-1 text-2xl font-bold ${
                            value === 0 ? "text-emerald-400" : "text-rose-400"
                          }`}
                        >
                          {value}
                        </span>
                        <span className="mt-1 text-center text-xs text-slate-400 font-medium">{label}</span>
                      </div>
                    ))}

                    <div className="flex flex-col items-center justify-center rounded-2xl bg-[#0F172A] p-4">
                      <span className="text-xl">🛡️</span>
                      <span
                        className={`mt-1 text-center text-sm font-semibold ${riskColor(cheatingStatus.riskScore)}`}
                      >
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