"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Webcam from "react-webcam";

import { StudioHeader } from "./studio-header";
import { VideoStage } from "./video-stage";
import { QuestionPanel, type Question } from "./question-panel";
import { RecordingControls } from "./recording-controls";
import { SessionMetrics } from "./session-metrics";

const QUESTIONS: Question[] = [
  {
    category: "Introduction",
    prompt: "Tell us about yourself and what drew you to product design.",
    hint: "Keep it to 60–90 seconds. Highlight the throughline that connects your experience to this role.",
  },
  {
    category: "Behavioral",
    prompt: "Describe a project where you had to balance user needs with tight business constraints.",
    hint: "Use the STAR method — Situation, Task, Action, Result.",
  },
  {
    category: "Technical",
    prompt: "Explain a challenging technical problem you solved recently.",
    hint: "Focus on your approach rather than only the final solution.",
  },
  {
    category: "Closing",
    prompt: "Why should we hire you for this role?",
    hint: "Summarize your strengths confidently.",
  },
];

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;

  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export function InterviewStudio() {
  const webcamRef = useRef<Webcam | null>(null);

  const [questionIndex, setQuestionIndex] = useState(0);

  const [recording, setRecording] = useState(false);
  const [paused, setPaused] = useState(false);

  const [elapsed, setElapsed] = useState(0);

  const [camOn, setCamOn] = useState(true);
  const [micOn, setMicOn] = useState(true);

  const [answered, setAnswered] = useState<boolean[]>(
    QUESTIONS.map(() => false)
  );

  const [clock, setClock] = useState("--:--");

  const live = recording && !paused;

  useEffect(() => {
    if (!live) return;

    const timer = setInterval(() => {
      setElapsed((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [live]);

  useEffect(() => {
    const updateClock = () => {
      setClock(
        new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })
      );
    };

    updateClock();

    const id = setInterval(updateClock, 1000);

    return () => clearInterval(id);
  }, []);

  const startRecording = useCallback(() => {
    setRecording(true);
    setPaused(false);
    setElapsed(0);
  }, []);

  const stopRecording = useCallback(() => {
    setRecording(false);

    setAnswered((prev) => {
      const copy = [...prev];
      copy[questionIndex] = true;
      return copy;
    });
  }, [questionIndex]);

  const retake = useCallback(() => {
    setRecording(false);
    setPaused(false);
    setElapsed(0);
  }, []);

  const gotoQuestion = useCallback((index: number) => {
    if (index < 0 || index >= QUESTIONS.length) return;

    setQuestionIndex(index);

    setRecording(false);
    setPaused(false);
    setElapsed(0);
  }, []);

  const { clarity, pace } = useMemo(() => {
    if (!live)
      return {
        clarity: 0,
        pace: 0,
      };

    return {
      clarity: 95,
      pace: 78,
    };
  }, [live]);

  return (
    <main className="min-h-screen bg-background">

      <div className="pointer-events-none fixed inset-0 overflow-hidden">

        <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />

        <div className="absolute -bottom-52 right-0 h-[32rem] w-[32rem] rounded-full bg-primary/5 blur-3xl" />

      </div>

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
            take={questionIndex + 1}
            onToggleCam={() => setCamOn((v) => !v)}
            onToggleMic={() => setMicOn((v) => !v)}
          />

          <div className="flex flex-col gap-4">

            <QuestionPanel
              question={QUESTIONS[questionIndex]}
              index={questionIndex}
              total={QUESTIONS.length}
              answered={answered}
              onPrev={() => gotoQuestion(questionIndex - 1)}
              onNext={() => gotoQuestion(questionIndex + 1)}
              onJump={gotoQuestion}
            />

            <RecordingControls
              recording={recording}
              paused={paused}
              onStart={startRecording}
              onPauseToggle={() => setPaused((v) => !v)}
              onStop={stopRecording}
              onRetake={retake}
            />

            <SessionMetrics
              live={live}
              clarity={clarity}
              pace={pace}
            />

          </div>

        </div>

      </div>

    </main>
  );
}