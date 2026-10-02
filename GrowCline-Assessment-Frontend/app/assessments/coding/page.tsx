"use client";

/**
 * /assessments/coding — Personalized Coding Assessment (15 LeetCode-style Problems)
 * Split layout: problem statement (left) + Monaco editor (right)
 * States: LOADING → INSTRUCTIONS → IN_PROGRESS → SUBMITTING → COMPLETED → ERROR
 *
 * Key features vs. old version:
 *  - Real /api/coding/run with per-case LeetCode-style result panel
 *  - Per-problem Submit button → /api/coding/submit-one (hidden test counts only)
 *  - Per-problem codeMap + languageMap (no shared language)
 *  - Monaco Editor with syntax highlighting (dark theme)
 *  - stdin-reading starter templates for all 5 languages
 *  - sessionStorage autosave per problem
 */

import { useEffect, useState, useRef, useCallback, lazy, Suspense } from "react";
import { useRouter } from "next/navigation";
import {
  Code2, ArrowLeft, ArrowRight, CheckCircle2,
  Play, Trophy, RotateCcw, ChevronDown, Terminal,
  XCircle, Loader2, Sparkles, Send, AlertCircle,
} from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import {
  AssessmentTimer, ResultCard, LoadingState, ErrorState, ScoreRing,
} from "@/components/assessment/shared";
import {
  generateCodingQuestions,
  submitCodingAnswers,
  runCode,
  submitOneProblem,
  getPersonalizedAssessmentPaper,
  type CodingQuestion,
  type CodingSubmission,
  type RunResult,
  type SubmitOneResult,
  type SubmitAllResult,
} from "@/services/assessmentService";
import { getStoredToken } from "@/services/authService";

// Lazy-load Monaco to avoid SSR issues
const Editor = lazy(() => import("@monaco-editor/react"));

// ── Types ─────────────────────────────────────────────────────────────────────

type Stage = "LOADING" | "INSTRUCTIONS" | "IN_PROGRESS" | "SUBMITTING" | "COMPLETED" | "ERROR";
type RunState = "idle" | "running" | "done";
type ProblemStatus = "not_attempted" | "attempted" | "accepted";

// ── Constants ─────────────────────────────────────────────────────────────────

const DURATION_SECONDS = 60 * 60; // 60 minutes
const N_QUESTIONS = 15;
const SESSION_KEY = "growcline_coding_v2";

// stdin-reading starter templates
const STARTER_CODE: Record<string, string> = {
  Python: `import sys

def solve():
    data = sys.stdin.read().split()
    # Parse input and implement your solution
    pass

solve()
`,
  JavaScript: `const fs = require('fs');
const input = fs.readFileSync('/dev/stdin', 'utf8').trim();
const lines = input.split('\\n');

// Parse input and implement your solution
`,
  Java: `import java.util.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        // Parse input and implement your solution
        sc.close();
    }
}
`,
  "C++": `#include <bits/stdc++.h>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    // Parse input and implement your solution
    return 0;
}
`,
  C: `#include <stdio.h>
#include <stdlib.h>

int main() {
    // Parse input and implement your solution
    return 0;
}
`,
};

const LANGUAGES = Object.keys(STARTER_CODE);

// Monaco language IDs
const MONACO_LANG: Record<string, string> = {
  Python: "python",
  JavaScript: "javascript",
  Java: "java",
  "C++": "cpp",
  C: "c",
};

// ── Status badge config ───────────────────────────────────────────────────────

const STATUS_VERDICT_COLOR: Record<string, string> = {
  "Accepted":              "text-green-600 bg-green-50 border-green-200",
  "Wrong Answer":          "text-red-600 bg-red-50 border-red-200",
  "Compilation Error":     "text-orange-600 bg-orange-50 border-orange-200",
  "Runtime Error":         "text-purple-600 bg-purple-50 border-purple-200",
  "Time Limit Exceeded":   "text-yellow-700 bg-yellow-50 border-yellow-200",
  "Memory Limit Exceeded": "text-yellow-700 bg-yellow-50 border-yellow-200",
  "Judge Unavailable":     "text-gray-600 bg-gray-50 border-gray-200",
};

function verdictColor(status: string): string {
  return STATUS_VERDICT_COLOR[status] ?? "text-gray-600 bg-gray-50 border-gray-200";
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function saveSession(codeMap: Record<number, string>, langMap: Record<number, string>) {
  try {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify({ codeMap, langMap }));
  } catch {}
}

function loadSession(): { codeMap: Record<number, string>; langMap: Record<number, string> } | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch { return null; }
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function CodingPage() {
  const router = useRouter();

  const [stage, setStage]         = useState<Stage>("LOADING");
  const [questions, setQuestions] = useState<CodingQuestion[]>([]);
  const [current, setCurrent]     = useState(0);
  const [error, setError]         = useState<string | null>(null);

  // Per-problem code and language maps
  const [codeMap, setCodeMap]   = useState<Record<number, string>>({});
  const [langMap, setLangMap]   = useState<Record<number, string>>({});

  // Per-problem status badges
  const [statusMap, setStatusMap] = useState<Record<number, ProblemStatus>>({});

  // Run state for current problem
  const [runState, setRunState]   = useState<RunState>("idle");
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [runError, setRunError]   = useState<string | null>(null);

  // Per-problem submit result (for badge + inline panel)
  const [submitMap, setSubmitMap] = useState<Record<number, SubmitOneResult>>({});
  const [submitting, setSubmitting] = useState(false);

  // Final submit-all result
  const [finalResult, setFinalResult] = useState<SubmitAllResult | null>(null);

  const timerRef = useRef(false);

  // ── Load questions ──────────────────────────────────────────────────────────

  async function loadQuestions() {
    try {
      setStage("LOADING");
      setError(null);

      let qs: CodingQuestion[] = [];
      try {
        const paper = await getPersonalizedAssessmentPaper();
        if (paper.codingQuestions?.length > 0) {
          qs = paper.codingQuestions;
        }
      } catch {
        qs = await generateCodingQuestions(N_QUESTIONS);
      }

      if (!qs.length) {
        setError("No personalized coding problems available right now.");
        setStage("ERROR");
        return;
      }

      setQuestions(qs);

      // Restore or initialise code/lang maps
      const saved = loadSession();
      const newCodeMap: Record<number, string> = {};
      const newLangMap: Record<number, string> = {};

      qs.forEach((q, idx) => {
        const defaultLang = LANGUAGES.includes(q.programmingLanguage) ? q.programmingLanguage : "Python";
        newLangMap[idx] = saved?.langMap?.[idx] ?? defaultLang;
        newCodeMap[idx] = saved?.codeMap?.[idx] ?? STARTER_CODE[newLangMap[idx]];
      });

      setCodeMap(newCodeMap);
      setLangMap(newLangMap);
      setStatusMap(Object.fromEntries(qs.map((_, i) => [i, "not_attempted" as ProblemStatus])));

      setStage("INSTRUCTIONS");
    } catch (err: unknown) {
      setError((err as Error)?.message ?? "Failed to load coding problems.");
      setStage("ERROR");
    }
  }

  useEffect(() => {
    if (!getStoredToken()) { router.replace("/login"); return; }
    loadQuestions();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ── Per-problem helpers ─────────────────────────────────────────────────────

  const currentLang = langMap[current] ?? "Python";
  const currentCode = codeMap[current] ?? STARTER_CODE[currentLang];

  function updateCode(val: string | undefined) {
    const code = val ?? "";
    setCodeMap(prev => {
      const next = { ...prev, [current]: code };
      saveSession(next, langMap);
      return next;
    });
    // Mark as "attempted" once the candidate edits
    setStatusMap(prev => {
      if (prev[current] === "not_attempted") {
        return { ...prev, [current]: "attempted" };
      }
      return prev;
    });
  }

  function handleLanguageChange(lang: string) {
    setLangMap(prev => {
      const next = { ...prev, [current]: lang };
      // Only inject starter if current slot is empty / unchanged
      setCodeMap(cPrev => {
        const existing = cPrev[current];
        const isStarter = Object.values(STARTER_CODE).includes(existing ?? "");
        const nextCode = isStarter ? STARTER_CODE[lang] : (existing ?? STARTER_CODE[lang]);
        const nextMap = { ...cPrev, [current]: nextCode };
        saveSession(nextMap, next);
        return nextMap;
      });
      return next;
    });
  }

  // ── Run ────────────────────────────────────────────────────────────────────

  async function handleRun() {
    const q = questions[current];
    if (!q || runState === "running") return;

    setRunState("running");
    setRunResult(null);
    setRunError(null);

    try {
      const res = await runCode(q.id || q._id, currentCode, currentLang);
      setRunResult(res);
      setRunState("done");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
        ?? (err as Error)?.message ?? "Run request failed.";
      setRunError(msg);
      setRunState("done");
    }
  }

  // ── Per-problem Submit ─────────────────────────────────────────────────────

  async function handleSubmitOne() {
    const q = questions[current];
    if (!q || submitting) return;

    setSubmitting(true);
    try {
      const res = await submitOneProblem(q.id || q._id, currentCode, currentLang);
      setSubmitMap(prev => ({ ...prev, [current]: res }));
      setStatusMap(prev => ({
        ...prev,
        [current]: res.status === "Accepted" ? "accepted" : "attempted",
      }));
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
        ?? (err as Error)?.message ?? "Submission failed.";
      setRunError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  // ── Submit All ─────────────────────────────────────────────────────────────

  const handleSubmitAll = useCallback(async () => {
    if (stage === "SUBMITTING" || stage === "COMPLETED") return;
    setStage("SUBMITTING");

    try {
      const submissions: CodingSubmission[] = questions.map((q, idx) => ({
        questionId: q.id || q._id,
        code:       codeMap[idx] ?? "",
        language:   langMap[idx] ?? "python",
      }));
      const res = await submitCodingAnswers(submissions);
      setFinalResult(res);
      setStage("COMPLETED");
    } catch (err: unknown) {
      setError((err as Error)?.message ?? "Submission failed.");
      setStage("ERROR");
    }
  }, [questions, codeMap, langMap, stage]);

  // ── Navigate problem ──────────────────────────────────────────────────────

  function goTo(idx: number) {
    setCurrent(idx);
    setRunState("idle");
    setRunResult(null);
    setRunError(null);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // RENDER STATES
  // ─────────────────────────────────────────────────────────────────────────

  if (stage === "LOADING") {
    return <AppShell title="Coding Assessment"><LoadingState message="Generating 15 personalized LeetCode-style coding problems..." /></AppShell>;
  }

  if (stage === "ERROR") {
    return <AppShell title="Coding Assessment"><ErrorState message={error ?? undefined} onRetry={loadQuestions} /></AppShell>;
  }

  if (stage === "SUBMITTING") {
    return <AppShell title="Coding Assessment"><LoadingState message="Evaluating your coding submissions against hidden test cases..." /></AppShell>;
  }

  // ── INSTRUCTIONS ────────────────────────────────────────────────────────────
  if (stage === "INSTRUCTIONS") {
    return (
      <AppShell title="Coding Assessment" subtitle="Read instructions before starting">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-2xl overflow-hidden shadow-sm">
            <div className="px-7 py-6 border-b border-[rgba(30,41,59,0.08)] flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-[#4096ff]/10 border border-[#4096ff]/20 flex items-center justify-center">
                <Code2 size={24} className="text-[#4096ff]" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-[17px] font-bold text-[#1E293B]">Coding Assessment</h2>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-[#4096ff]/10 text-[#4096ff] border border-[#4096ff]/20">
                    Personalized (15 Problems)
                  </span>
                </div>
                <p className="text-[12.5px] text-[#64748B] mt-0.5">15 problems · 60 minutes</p>
              </div>
            </div>

            <div className="px-7 py-6 space-y-4">
              <h3 className="text-[13px] font-semibold text-[#1E293B] uppercase tracking-wide">Instructions</h3>
              <ul className="space-y-2.5">
                {[
                  `This assessment contains exactly ${questions.length} LeetCode-style coding problems.`,
                  "You have 60 minutes to complete all 15 problems.",
                  "Problems adapt to your programming language and domain experience.",
                  "Use the problem switcher at the top to navigate between problems.",
                  "Press 'Run' to test your code against sample test cases — shows real execution results.",
                  "Press 'Submit Problem' to evaluate against hidden test cases (pass count shown, not hidden inputs).",
                  "Press 'Submit All 15' to finalize your assessment with full scoring.",
                  "Your code is saved automatically per problem on each keystroke.",
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
                <p className="text-[12.5px] font-semibold text-[#64748B] uppercase tracking-wide mb-3">Supported Languages</p>
                <div className="flex flex-wrap gap-2">
                  {LANGUAGES.map((l) => (
                    <span key={l} className="px-3 py-1 bg-[#F1F5F9] text-[#475569] text-[12px] font-semibold rounded-lg">{l}</span>
                  ))}
                </div>
              </div>
            </div>

            <div className="px-7 py-5 border-t border-[rgba(30,41,59,0.08)] flex items-center justify-between">
              <button onClick={() => router.back()} className="flex items-center gap-1.5 text-[13px] text-[#64748B] hover:text-[#1E293B] font-medium transition-colors">
                <ArrowLeft size={14} /> Back
              </button>
              <button
                onClick={() => { timerRef.current = false; setStage("IN_PROGRESS"); }}
                className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[14px] font-semibold transition-all shadow-md"
              >
                Start Assessment <ArrowRight size={14} />
              </button>
            </div>
          </div>
        </div>
      </AppShell>
    );
  }

  // ── COMPLETED ──────────────────────────────────────────────────────────────
  if (stage === "COMPLETED" && finalResult) {
    const pct    = Math.round(finalResult.percentage ?? 0);
    const passed = pct >= 40;
    return (
      <AppShell title="Coding Assessment — Results">
        <div className="max-w-2xl mx-auto space-y-5">
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-2xl p-7 flex flex-col sm:flex-row items-center gap-7 shadow-sm">
            <ScoreRing percentage={pct} size={100} />
            <div className="text-center sm:text-left">
              <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-[12px] font-semibold mb-3 ${passed ? "bg-[#F0FDF4] text-[#15803D] border border-[#86EFAC]/50" : "bg-[#FEF2F2] text-[#B91C1C] border border-[#FECACA]/50"}`}>
                <CheckCircle2 size={13} />{passed ? "Passed" : "Failed"}
              </div>
              <h2 className="text-[22px] font-bold text-[#1E293B] mb-1">{pct}% Score</h2>
              <p className="text-[13px] text-[#64748B]">
                Evaluated across 15 coding problems. {Math.round(finalResult.score)}/{Math.round(finalResult.total)} marks awarded.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <ResultCard label="Score"      value={`${Math.round(finalResult.score)}/${Math.round(finalResult.total)}`} />
            <ResultCard label="Percentage" value={`${pct}%`} accent />
            <ResultCard label="Status"     value={passed ? "Passed" : "Failed"} />
          </div>

          {/* Per-problem verdicts */}
          {finalResult.results && finalResult.results.length > 0 && (
            <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 shadow-sm">
              <h3 className="text-[13px] font-semibold text-[#1E293B] mb-3">Problem Verdicts</h3>
              <div className="space-y-2">
                {finalResult.results.map((r, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b border-[rgba(30,41,59,0.06)] last:border-0">
                    <span className="text-[13px] text-[#374151] font-medium">Problem {i + 1}</span>
                    <div className="flex items-center gap-3">
                      <span className="text-[12px] text-[#64748B]">
                        {r.passed_tests}/{r.total_tests} tests
                      </span>
                      <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${verdictColor(r.status)}`}>
                        {r.status}
                      </span>
                      <span className="text-[12px] font-bold text-[#1E293B]">
                        {r.marks_obtained}/{r.max_marks} pts
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => { setRunState("idle"); setRunResult(null); setFinalResult(null); timerRef.current = false; loadQuestions(); }}
              className="flex-1 flex items-center justify-center gap-2 h-11 rounded-xl border border-[rgba(30,41,59,0.14)] text-[13.5px] font-semibold text-[#1E293B] hover:bg-[#F1F5F9] transition-all"
            >
              <RotateCcw size={14} /> Retake Assessment
            </button>
            <button
              onClick={() => router.push("/results")}
              className="flex-1 flex items-center justify-center gap-2 h-11 rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[13.5px] font-semibold transition-all"
            >
              <Trophy size={14} /> View All Results
            </button>
            <button
              onClick={() => router.push("/analytics")}
              className="flex-1 flex items-center justify-center gap-2 h-11 rounded-xl bg-[#1E293B] hover:bg-[#334155] text-white text-[13.5px] font-semibold transition-all"
            >
              View Analytics
            </button>
          </div>
        </div>
      </AppShell>
    );
  }

  // ── IN_PROGRESS ────────────────────────────────────────────────────────────
  const q             = questions[current];
  const problemSubmit = submitMap[current];
  const problemStatus = statusMap[current] ?? "not_attempted";

  const BADGE: Record<ProblemStatus, string> = {
    not_attempted: "bg-[#F1F5F9] text-[#64748B]",
    attempted:     "bg-[#FEF3C7] text-[#B45309]",
    accepted:      "bg-[#F0FDF4] text-[#15803D] border border-[#86EFAC]/50",
  };

  return (
    <AppShell title={`Coding Assessment — Problem ${current + 1} of 15`}>
      <div className="max-w-7xl mx-auto space-y-4">

        {/* Top Problem Switcher Bar */}
        <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-3 flex items-center justify-between gap-4 flex-wrap shadow-sm">
          <div className="flex items-center gap-2 overflow-x-auto py-1 max-w-full">
            <span className="text-[12px] font-bold text-[#64748B] shrink-0 mr-1">Problems:</span>
            {questions.map((_, idx) => {
              const st = statusMap[idx] ?? "not_attempted";
              return (
                <button
                  key={idx}
                  onClick={() => goTo(idx)}
                  title={st}
                  className={`w-8 h-8 rounded-lg text-[12px] font-bold transition-all shrink-0 flex items-center justify-center ${
                    idx === current
                      ? "bg-[#4096ff] text-white shadow-sm scale-105"
                      : st === "accepted"
                      ? "bg-[#F0FDF4] text-[#15803D] border border-[#86EFAC]/50"
                      : st === "attempted"
                      ? "bg-[#FEF3C7] text-[#B45309]"
                      : "bg-[#F1F5F9] text-[#64748B] hover:bg-[#E2E8F0]"
                  }`}
                >
                  {idx + 1}
                </button>
              );
            })}
          </div>

          <AssessmentTimer
            durationSeconds={DURATION_SECONDS}
            onExpire={() => { if (!timerRef.current) { timerRef.current = true; handleSubmitAll(); } }}
          />
        </div>

        {/* Main Split Layout */}
        <div className="grid lg:grid-cols-2 gap-4 h-[calc(100vh-240px)] min-h-[580px]">

          {/* Left: Problem Description */}
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl overflow-y-auto flex flex-col shadow-sm">
            <div className="px-5 py-3 border-b border-[rgba(30,41,59,0.08)] flex items-center justify-between shrink-0">
              <div className="flex items-center gap-2">
                <span className="text-[12px] font-bold text-[#4096ff] bg-[#4096ff]/10 border border-[#4096ff]/20 px-2 py-0.5 rounded-full">
                  Problem {current + 1} of 15
                </span>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-[#F1F5F9] text-[#64748B]">
                  {q.difficulty}
                </span>
                <span className="text-[11px] text-[#94A3B8] font-medium">{q.category}</span>
              </div>
              {/* Problem status badge */}
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${BADGE[problemStatus]}`}>
                {problemStatus === "not_attempted" ? "Not Attempted" : problemStatus === "attempted" ? "Attempted" : "✓ Accepted"}
              </span>
            </div>

            <div className="p-5 space-y-4 text-[13.5px] text-[#374151] leading-relaxed overflow-y-auto flex-1">
              <div>
                <h3 className="text-[16px] font-bold text-[#1E293B] mb-2">{q.title}</h3>
                <p className="leading-relaxed whitespace-pre-wrap">{q.problemStatement}</p>
              </div>

              {q.inputFormat && (
                <div>
                  <p className="text-[12px] font-bold text-[#1E293B] uppercase tracking-wide mb-1">Input Format</p>
                  <p className="text-[13px] text-[#64748B]">{q.inputFormat}</p>
                </div>
              )}

              {q.outputFormat && (
                <div>
                  <p className="text-[12px] font-bold text-[#1E293B] uppercase tracking-wide mb-1">Output Format</p>
                  <p className="text-[13px] text-[#64748B]">{q.outputFormat}</p>
                </div>
              )}

              {q.constraints && (
                <div>
                  <p className="text-[12px] font-bold text-[#1E293B] uppercase tracking-wide mb-1">Constraints</p>
                  <div className="bg-[#F8FAFC] border border-[rgba(30,41,59,0.08)] rounded-lg px-3 py-2 font-mono text-[12px]">
                    {q.constraints}
                  </div>
                </div>
              )}

              {(q.sampleInput || q.sampleOutput) && (
                <div>
                  <p className="text-[12px] font-bold text-[#1E293B] uppercase tracking-wide mb-1.5">Example Test Case</p>
                  <div className="grid sm:grid-cols-2 gap-2">
                    {q.sampleInput && (
                      <div className="bg-[#F8FAFC] border border-[rgba(30,41,59,0.08)] rounded-lg p-3">
                        <p className="text-[10.5px] text-[#64748B] font-bold mb-1">Input (stdin)</p>
                        <pre className="font-mono text-[12px] text-[#1E293B] whitespace-pre-wrap">{q.sampleInput}</pre>
                      </div>
                    )}
                    {q.sampleOutput && (
                      <div className="bg-[#F8FAFC] border border-[rgba(30,41,59,0.08)] rounded-lg p-3">
                        <p className="text-[10.5px] text-[#64748B] font-bold mb-1">Output (stdout)</p>
                        <pre className="font-mono text-[12px] text-[#1E293B] whitespace-pre-wrap">{q.sampleOutput}</pre>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Per-problem submit result */}
              {problemSubmit && (
                <div className={`rounded-xl border p-3 ${verdictColor(problemSubmit.status)}`}>
                  <p className="text-[12px] font-bold mb-1">Submit Result: {problemSubmit.status}</p>
                  <p className="text-[12px]">
                    Sample: {problemSubmit.sample_passed}/{problemSubmit.sample_total} &nbsp;|&nbsp;
                    Hidden: {problemSubmit.hidden_summary.passed}/{problemSubmit.hidden_summary.total} &nbsp;|&nbsp;
                    Score: {problemSubmit.marks_obtained}/{problemSubmit.max_marks} pts
                  </p>
                </div>
              )}
            </div>

            {/* Navigation */}
            <div className="p-4 border-t border-[rgba(30,41,59,0.08)] flex items-center justify-between shrink-0 bg-[#F8FAFC]">
              <button
                onClick={() => goTo(Math.max(0, current - 1))}
                disabled={current === 0}
                className="px-4 py-2 rounded-lg border border-[rgba(30,41,59,0.14)] text-[12.5px] font-bold text-[#1E293B] hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center gap-1.5"
              >
                <ArrowLeft size={13} /> Prev
              </button>

              <span className="text-[12px] font-semibold text-[#64748B]">{current + 1} of 15</span>

              {current < questions.length - 1 ? (
                <button
                  onClick={() => goTo(Math.min(questions.length - 1, current + 1))}
                  className="px-4 py-2 rounded-lg bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[12.5px] font-bold transition-all flex items-center gap-1.5"
                >
                  Next <ArrowRight size={13} />
                </button>
              ) : (
                <button
                  onClick={handleSubmitAll}
                  className="px-5 py-2 rounded-lg bg-[#1E293B] hover:bg-[#334155] text-white text-[12.5px] font-bold transition-all flex items-center gap-1.5"
                >
                  <CheckCircle2 size={13} /> Submit All 15
                </button>
              )}
            </div>
          </div>

          {/* Right: Monaco Editor + Output */}
          <div className="flex flex-col gap-3">
            {/* Editor */}
            <div className="bg-[#1E293B] rounded-xl overflow-hidden flex flex-col flex-1 min-h-0 shadow-md">
              {/* Toolbar */}
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/10 shrink-0">
                <div className="relative">
                  <select
                    value={currentLang}
                    onChange={(e) => handleLanguageChange(e.target.value)}
                    className="appearance-none bg-white/10 border border-white/15 text-white text-[12px] font-bold pl-3 pr-7 py-1.5 rounded-lg cursor-pointer focus:outline-none focus:border-[#4096ff]"
                  >
                    {LANGUAGES.map((l) => (
                      <option key={l} value={l} className="bg-[#1E293B]">{l}</option>
                    ))}
                  </select>
                  <ChevronDown size={11} className="absolute right-2 top-1/2 -translate-y-1/2 text-white/60 pointer-events-none" />
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleRun}
                    disabled={runState === "running"}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 border border-white/10 text-white text-[12px] font-bold transition-all disabled:opacity-50"
                  >
                    {runState === "running" ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
                    Run
                  </button>

                  <button
                    onClick={handleSubmitOne}
                    disabled={submitting}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-[#6366f1] hover:bg-[#818cf8] text-white text-[12px] font-bold transition-all disabled:opacity-50"
                  >
                    {submitting ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />}
                    Submit
                  </button>

                  <button
                    onClick={handleSubmitAll}
                    className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[12px] font-bold transition-all"
                  >
                    <CheckCircle2 size={12} /> Submit All
                  </button>
                </div>
              </div>

              {/* Monaco Editor */}
              <div className="flex-1 min-h-0">
                <Suspense fallback={
                  <div className="w-full h-full flex items-center justify-center text-white/50 text-[13px]">
                    <Loader2 size={16} className="animate-spin mr-2" /> Loading editor...
                  </div>
                }>
                  <Editor
                    height="100%"
                    language={MONACO_LANG[currentLang] ?? "python"}
                    value={currentCode}
                    onChange={updateCode}
                    theme="vs-dark"
                    options={{
                      fontSize: 13,
                      minimap: { enabled: false },
                      scrollBeyondLastLine: false,
                      wordWrap: "on",
                      automaticLayout: true,
                      tabSize: 2,
                      lineNumbers: "on",
                      renderLineHighlight: "line",
                      fontFamily: "JetBrains Mono, Fira Code, Consolas, monospace",
                    }}
                  />
                </Suspense>
              </div>
            </div>

            {/* Output Panel */}
            <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl overflow-hidden shrink-0 shadow-sm" style={{ minHeight: 160 }}>
              <div className="flex items-center gap-2 px-4 py-2 border-b border-[rgba(30,41,59,0.08)]">
                <Terminal size={13} className="text-[#64748B]" />
                <span className="text-[11.5px] font-bold text-[#64748B] uppercase tracking-wide">Test Output</span>
                {runState === "running" && <Loader2 size={12} className="animate-spin text-[#4096ff] ml-auto" />}
                {runState === "done" && runResult?.overall_status === "Accepted" && <CheckCircle2 size={12} className="text-[#15803D] ml-auto" />}
                {runState === "done" && runResult && runResult.overall_status !== "Accepted" && <XCircle size={12} className="text-[#DC2626] ml-auto" />}
                {runError && <AlertCircle size={12} className="text-[#DC2626] ml-auto" />}
              </div>

              <div className="p-3 max-h-[200px] overflow-y-auto space-y-2">
                {runState === "idle" && !runError && (
                  <p className="text-[12px] text-[#94A3B8]">
                    Click &quot;Run&quot; to test your solution against sample test cases. Real execution via Judge0.
                  </p>
                )}

                {runError && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-2">
                    <p className="text-[12px] text-red-700 font-semibold">Error</p>
                    <p className="text-[12px] text-red-600">{runError}</p>
                  </div>
                )}

                {runResult && (
                  <div className="space-y-2">
                    {/* Overall verdict */}
                    <div className={`text-[12px] font-bold px-2.5 py-1.5 rounded-lg border ${verdictColor(runResult.overall_status)}`}>
                      {runResult.overall_status} — {runResult.passed}/{runResult.total} sample tests passed
                    </div>

                    {/* Per-case results */}
                    {runResult.results?.map((tc, i) => (
                      <div key={i} className={`rounded-lg border p-2.5 text-[12px] ${tc.passed ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"}`}>
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="font-bold">Case {i + 1}: {tc.status}</span>
                          <span className="text-[11px] text-[#64748B]">{tc.execution_time_ms.toFixed(1)}ms</span>
                        </div>
                        <div className="grid grid-cols-3 gap-1.5">
                          <div>
                            <p className="text-[10px] text-[#64748B] font-bold mb-0.5">Input</p>
                            <pre className="font-mono text-[11px] bg-white rounded px-1.5 py-1 whitespace-pre-wrap overflow-x-auto max-h-16">{tc.input}</pre>
                          </div>
                          <div>
                            <p className="text-[10px] text-[#64748B] font-bold mb-0.5">Expected</p>
                            <pre className="font-mono text-[11px] bg-white rounded px-1.5 py-1 whitespace-pre-wrap overflow-x-auto max-h-16">{tc.expected_output}</pre>
                          </div>
                          <div>
                            <p className="text-[10px] text-[#64748B] font-bold mb-0.5">Your Output</p>
                            <pre className={`font-mono text-[11px] rounded px-1.5 py-1 whitespace-pre-wrap overflow-x-auto max-h-16 ${tc.passed ? "bg-green-100" : "bg-red-100"}`}>{tc.actual_output || "(empty)"}</pre>
                          </div>
                        </div>
                        {tc.error_message && (
                          <pre className="mt-1.5 font-mono text-[11px] text-red-700 bg-red-100 rounded px-1.5 py-1 whitespace-pre-wrap overflow-x-auto max-h-24">{tc.error_message}</pre>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
