"use client";

/**
 * /assessments/technical — Technical Assessment
 * Mirrors the Aptitude flow but uses /api/technical/* endpoints.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { BookOpen, ArrowLeft, ArrowRight, CheckCircle2, Trophy, RotateCcw } from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import {
  QuestionCard, QuestionNavigator, AssessmentTimer,
  ProgressBar, ResultCard, LoadingState, ErrorState, ScoreRing,
} from "@/components/assessment/shared";
import {
  generateTechnicalQuestions,
  submitTechnicalAnswers,
  getPersonalizedAssessmentPaper,
  type TechnicalQuestion,
  type AnswerRecord,
} from "@/services/assessmentService";
import { getStoredToken } from "@/services/authService";

type Stage = "LOADING" | "INSTRUCTIONS" | "IN_PROGRESS" | "SUBMITTING" | "COMPLETED" | "ERROR";

const DURATION_SECONDS = 40 * 60; // 40 minutes
const N_QUESTIONS = 25;

export default function TechnicalPage() {
  const router = useRouter();
  const [stage, setStage]         = useState<Stage>("LOADING");
  const [questions, setQuestions] = useState<TechnicalQuestion[]>([]);
  const [answers, setAnswers]     = useState<Record<number, string>>({});
  const [current, setCurrent]     = useState(0);
  const [error, setError]         = useState<string | null>(null);
  const [result, setResult]       = useState<{ score: number; total: number; percentage: number } | null>(null);
  const timerExpiredRef = useRef(false);

  useEffect(() => {
    if (!getStoredToken()) { router.replace("/login"); return; }
    loadQuestions();
  }, []);

  async function loadQuestions() {
    try {
      setStage("LOADING");
      setError(null);
      let qs: TechnicalQuestion[] = [];
      try {
        const paper = await getPersonalizedAssessmentPaper();
        if (paper.technicalQuestions && paper.technicalQuestions.length > 0) {
          qs = paper.technicalQuestions;
        }
      } catch {
        qs = await generateTechnicalQuestions(N_QUESTIONS);
      }
      if (!qs.length) {
        setError("No technical questions are available right now.");
        setStage("ERROR");
        return;
      }
      setQuestions(qs);
      setStage("INSTRUCTIONS");
    } catch (err: unknown) {
      setError((err as Error)?.message ?? "Failed to load questions.");
      setStage("ERROR");
    }
  }

  const handleTimerExpire = useCallback(() => {
    if (timerExpiredRef.current) return;
    timerExpiredRef.current = true;
    submitAssessment(true);
  }, []);

  async function submitAssessment(_auto = false) {
    setStage("SUBMITTING");
    try {
      const payload: AnswerRecord[] = questions.map((q, i) => ({
        questionId:     q.id ?? q._id,
        selectedAnswer: answers[i] ?? "",
      }));
      const res = await submitTechnicalAnswers(payload);
      setResult(res);
      setStage("COMPLETED");
    } catch (err: unknown) {
      setError((err as Error)?.message ?? "Submission failed.");
      setStage("ERROR");
    }
  }

  const answeredSet = new Set(
    Object.keys(answers).filter((k) => answers[Number(k)] !== "").map(Number)
  );

  // ── LOADING ────────────────────────────────────────────────────
  if (stage === "LOADING") {
    return <AppShell title="Technical Assessment"><LoadingState message="Preparing your questions…" /></AppShell>;
  }

  // ── ERROR ──────────────────────────────────────────────────────
  if (stage === "ERROR") {
    return <AppShell title="Technical Assessment"><ErrorState message={error ?? undefined} onRetry={loadQuestions} /></AppShell>;
  }

  // ── SUBMITTING ─────────────────────────────────────────────────
  if (stage === "SUBMITTING") {
    return <AppShell title="Technical Assessment"><LoadingState message="Submitting your answers…" /></AppShell>;
  }

  // ── INSTRUCTIONS ───────────────────────────────────────────────
  if (stage === "INSTRUCTIONS") {
    return (
      <AppShell title="Technical Assessment" subtitle="Read instructions before starting">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-2xl overflow-hidden">
            <div className="px-7 py-6 border-b border-[rgba(30,41,59,0.08)] flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-[#4096ff]/08 border border-[#4096ff]/15 flex items-center justify-center">
                <BookOpen size={22} className="text-[#4096ff]" />
              </div>
              <div>
                <h2 className="text-[17px] font-bold text-[#1E293B]">Technical Assessment</h2>
                <p className="text-[12.5px] text-[#64748B] mt-0.5">
                  {questions.length} questions · 25 minutes
                </p>
              </div>
            </div>

            <div className="px-7 py-6 space-y-4">
              <h3 className="text-[13px] font-semibold text-[#1E293B] uppercase tracking-wide">Instructions</h3>
              <ul className="space-y-2.5">
                {[
                  `This test contains ${questions.length} technology-specific questions.`,
                  "You have 25 minutes to complete the assessment.",
                  "Questions cover programming, software engineering, and CS fundamentals.",
                  "Navigate freely between questions using the question panel.",
                  "Unanswered questions receive no marks.",
                  "Results are shown immediately after submission.",
                ].map((inst, i) => (
                  <li key={i} className="flex items-start gap-3 text-[13.5px] text-[#374151]">
                    <span className="w-5 h-5 rounded-full bg-[#4096ff]/10 border border-[#4096ff]/20 text-[#4096ff] text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    {inst}
                  </li>
                ))}
              </ul>

              <div className="mt-6 pt-5 border-t border-[rgba(30,41,59,0.06)]">
                <p className="text-[12.5px] font-semibold text-[#64748B] uppercase tracking-wide mb-3">Topics covered</p>
                <div className="flex flex-wrap gap-2">
                  {["Programming Concepts", "Data Structures", "Algorithms", "System Design", "Databases", "Networking"].map((t) => (
                    <span key={t} className="px-3 py-1 bg-[#F1F5F9] text-[#475569] text-[12px] font-medium rounded-lg">{t}</span>
                  ))}
                </div>
              </div>
            </div>

            <div className="px-7 py-5 border-t border-[rgba(30,41,59,0.08)] flex items-center justify-between">
              <button onClick={() => router.back()} className="flex items-center gap-1.5 text-[13px] text-[#64748B] hover:text-[#1E293B] font-medium transition-colors">
                <ArrowLeft size={14} /> Back
              </button>
              <button
                onClick={() => { timerExpiredRef.current = false; setStage("IN_PROGRESS"); }}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[14px] font-semibold transition-all shadow-[0_4px_14px_rgba(64,150,255,0.35)]"
              >
                Start Assessment <ArrowRight size={14} />
              </button>
            </div>
          </div>
        </div>
      </AppShell>
    );
  }

  // ── COMPLETED ──────────────────────────────────────────────────
  if (stage === "COMPLETED" && result) {
    const pct    = Math.round(result.percentage ?? 0);
    const passed = pct >= 40;
    return (
      <AppShell title="Technical Assessment — Results">
        <div className="max-w-2xl mx-auto space-y-5">
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-2xl p-7 flex flex-col sm:flex-row items-center gap-7">
            <ScoreRing percentage={pct} size={100} />
            <div className="text-center sm:text-left">
              <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-[12px] font-semibold mb-3 ${passed ? "bg-[#F0FDF4] text-[#15803D] border border-[#86EFAC]/50" : "bg-[#FEF2F2] text-[#B91C1C] border border-[#FECACA]/50"}`}>
                <CheckCircle2 size={13} />
                {passed ? "Passed" : "Failed"}
              </div>
              <h2 className="text-[22px] font-bold text-[#1E293B] mb-1">{pct}% Score</h2>
              <p className="text-[13px] text-[#64748B]">
                You answered {result.score} out of {result.total} questions correctly.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <ResultCard label="Correct"    value={result.score}           />
            <ResultCard label="Total"      value={result.total}           />
            <ResultCard label="Percentage" value={`${pct}%`}  accent      />
            <ResultCard label="Status"     value={passed ? "Pass" : "Fail"} />
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => { setAnswers({}); setCurrent(0); setResult(null); timerExpiredRef.current = false; loadQuestions(); }}
              className="flex-1 flex items-center justify-center gap-2 h-11 rounded-xl border border-[rgba(30,41,59,0.14)] text-[13.5px] font-semibold text-[#1E293B] hover:bg-[#F1F5F9] transition-all"
            >
              <RotateCcw size={14} /> Retake
            </button>
            <button
              onClick={() => router.push("/results")}
              className="flex-1 flex items-center justify-center gap-2 h-11 rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[13.5px] font-semibold transition-all"
            >
              <Trophy size={14} /> View All Results
            </button>
          </div>
        </div>
      </AppShell>
    );
  }

  // ── IN_PROGRESS ────────────────────────────────────────────────
  const q = questions[current];
  return (
    <AppShell title="Technical Assessment">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-5 gap-4 flex-wrap">
          <div className="flex-1 min-w-[200px]">
            <ProgressBar current={current} total={questions.length} answered={answeredSet.size} />
          </div>
          <AssessmentTimer durationSeconds={DURATION_SECONDS} onExpire={handleTimerExpire} />
        </div>

        <div className="grid lg:grid-cols-[1fr_220px] gap-5">
          <div className="space-y-4">
            <QuestionCard
              questionNumber={current + 1}
              totalQuestions={questions.length}
              question={q.question}
              options={q.options}
              selectedAnswer={answers[current] ?? null}
              onSelect={(a) => setAnswers((p) => ({ ...p, [current]: a }))}
            />
            <div className="flex items-center justify-between">
              <button
                onClick={() => setCurrent((c) => Math.max(0, c - 1))}
                disabled={current === 0}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-[rgba(30,41,59,0.14)] text-[13px] font-medium text-[#1E293B] hover:bg-[#F1F5F9] disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                <ArrowLeft size={14} /> Previous
              </button>
              {current < questions.length - 1 ? (
                <button
                  onClick={() => setCurrent((c) => Math.min(questions.length - 1, c + 1))}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[13px] font-semibold transition-all"
                >
                  Next <ArrowRight size={14} />
                </button>
              ) : (
                <button
                  onClick={() => submitAssessment(false)}
                  className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#1E293B] hover:bg-[#334155] text-white text-[13px] font-semibold transition-all"
                >
                  <CheckCircle2 size={14} /> Submit
                </button>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <QuestionNavigator total={questions.length} current={current} answered={answeredSet} onJump={(i) => setCurrent(i)} />
            {current < questions.length - 1 && (
              <button
                onClick={() => submitAssessment(false)}
                className="w-full h-10 rounded-xl border border-[#1E293B] text-[#1E293B] text-[12.5px] font-semibold hover:bg-[#1E293B] hover:text-white transition-all"
              >
                Submit Now
              </button>
            )}
            <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl px-4 py-3 text-center">
              <p className="text-[11px] text-[#64748B] mb-0.5">Answered</p>
              <p className="text-[22px] font-bold text-[#1E293B]">{answeredSet.size}</p>
              <p className="text-[11px] text-[#94A3B8]">of {questions.length}</p>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
