"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Webcam from "react-webcam";
import { useReactMediaRecorder } from "react-media-recorder";
import { useSearchParams } from "next/navigation";

import { StudioHeader } from "./studio-header";
import { VideoStage } from "./video-stage";
import { QuestionPanel } from "./question-panel";
import { RecordingControls } from "./recording-controls";
import { SessionMetrics } from "./session-metrics";

import { useInterview } from "@/hooks/useInterview";
import { useAuth } from "@/hooks/useAuth";
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
// Component
// ---------------------------------------------------------------------------

export function InterviewStudio() {
  const searchParams = useSearchParams();
  const { userId } = useAuth();

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
  const jobRole = searchParams?.get("jobRole") ?? "Software Engineer";
  const interviewType = (searchParams?.get("interviewType") as "TECHNICAL" | "HR" | "BEHAVIORAL" | "RESUME_BASED") ?? "TECHNICAL";
  const difficulty = (searchParams?.get("difficulty") as "EASY" | "MEDIUM" | "HARD") ?? "MEDIUM";

  // ── UI state ─────────────────────────────────────────────────────────────

  const webcamRef = useRef<Webcam | null>(null);
  const [recording, setRecording] = useState(false);
  const [paused, setPaused] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [camOn, setCamOn] = useState(true);
  const [micOn, setMicOn] = useState(true);
  const [clock, setClock] = useState("--:--");
  const [sessionStarted, setSessionStarted] = useState(false);
  const [sessionEnded, setSessionEnded] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "done" | "error">("idle");
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [candidateAnswerText, setCandidateAnswerText] = useState("");

  // Track answered question IDs so we can show progress dots
  const [answeredIds, setAnsweredIds] = useState<Set<string>>(new Set());

  // ── react-media-recorder ─────────────────────────────────────────────────

  const { startRecording: startMediaRecorder, stopRecording: stopMediaRecorder, mediaBlobUrl, clearBlobUrl } =
    useReactMediaRecorder({
      video: camOn,
      audio: micOn,
    });

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

  // ── Toast helper ──────────────────────────────────────────────────────────

  const showToast = (msg: string, isError = false) => {
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
        showToast("Interview complete! Ending session…");
        await endInterview(interview.id);
        setSessionEnded(true);
        return;
      }

      // Fetch next question
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
  }, [interview, currentQuestion, candidateAnswerText, submitAnswer, endInterview, getNextQuestion, clearBlobUrl]);

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

  // Total/current question counts come from the API response
  const totalQuestions = interview?.totalQuestions ?? 5;
  const currentQNum = interview?.currentQuestion ?? 1;
  // Build a boolean answered array for the progress dots
  const answeredArray = Array.from({ length: totalQuestions }, (_, i) => {
    if (!currentQuestion) return false;
    const qNum = currentQuestion.questionNumber;
    return i + 1 < qNum || answeredIds.has(currentQuestion.id);
  });

  // ── Render: Session ended ─────────────────────────────────────────────────

  if (sessionEnded && summary) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center p-8">
        <div className="max-w-lg w-full rounded-[28px] border border-white/10 bg-[#111827]/90 p-8 text-center space-y-4">
          <div className="text-5xl">🎉</div>
          <h2 className="text-2xl font-bold text-white">Interview Complete!</h2>
          <p className="text-slate-400">
            You answered {summary.questionsAnswered} of {summary.totalQuestions} questions.
          </p>
          {summary.averageScore !== null && (
            <p className="text-3xl font-bold text-[#4096ff]">
              Average Score: {Math.round(summary.averageScore)}/100
            </p>
          )}
          <p className="text-sm text-slate-500">
            Duration: {formatTime(summary.actualDurationSeconds ?? 0)}
          </p>
        </div>
      </main>
    );
  }

  // ── Render: Loading initial question ──────────────────────────────────────

  if (loading && !currentQuestion) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-[#4096ff] border-t-transparent animate-spin" />
          <p className="text-slate-400 text-sm">Preparing your AI interview…</p>
        </div>
      </main>
    );
  }

  // ── Render: Main studio ───────────────────────────────────────────────────

  return (
    <main className="min-h-screen bg-background">
      {/* Background glows */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute -bottom-52 right-0 h-[32rem] w-[32rem] rounded-full bg-primary/5 blur-3xl" />
      </div>

      {/* Toast */}
      {toastMsg && (
        <div className="fixed top-4 right-4 z-50 max-w-sm rounded-2xl bg-[#111827] border border-white/10 px-5 py-3 text-white shadow-xl text-sm">
          {toastMsg}
        </div>
      )}

      {/* Global error banner */}
      {interviewError && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 max-w-md rounded-2xl bg-red-900/80 border border-red-500/40 px-5 py-3 text-red-200 shadow-xl text-sm">
          ⚠️ {interviewError}
        </div>
      )}

      <div className="relative mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8">
        <StudioHeader clock={clock} />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.6fr_1fr]">
          <VideoStage
            webcamRef={webcamRef}
            recording={recording}
            paused={paused}
            camOn={camOn}
            micOn={micOn}
            elapsed={formatTime(elapsed)}
            take={currentQNum}
            onToggleCam={() => setCamOn((v) => !v)}
            onToggleMic={() => setMicOn((v) => !v)}
          />

          <div className="flex flex-col gap-4">
            {currentQuestion ? (
              <QuestionPanel
                question={{
                  questionId: currentQuestion.id,
                  category: currentQuestion.questionType,
                  prompt: currentQuestion.questionText,
                  hint: `Question ${currentQuestion.questionNumber} of ${totalQuestions}`,
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
              <div className="rounded-[28px] border border-white/10 bg-[#111827]/90 p-6 flex items-center justify-center min-h-[200px]">
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
      </div>
    </main>
  );
}