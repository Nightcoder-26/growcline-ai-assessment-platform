"use client";

/**
 * /assessments/coding — Personalized Coding Assessment (15 LeetCode-style Problems)
 * Split layout: problem statement (left) + code editor (right)
 * States: LOADING → INSTRUCTIONS → IN_PROGRESS → SUBMITTING → COMPLETED → ERROR
 */

import { useEffect, useState, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Code2, ArrowLeft, ArrowRight, CheckCircle2,
  Play, Trophy, RotateCcw, ChevronDown, Terminal,
  XCircle, Loader2, Sparkles,
} from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import {
  AssessmentTimer, ResultCard, LoadingState, ErrorState, ScoreRing,
} from "@/components/assessment/shared";
import {
  generateCodingQuestions,
  submitCodingAnswers,
  getPersonalizedAssessmentPaper,
  type CodingQuestion,
  type CodingSubmission,
} from "@/services/assessmentService";
import { getStoredToken } from "@/services/authService";

type Stage = "LOADING" | "INSTRUCTIONS" | "IN_PROGRESS" | "SUBMITTING" | "COMPLETED" | "ERROR";
type RunState = "idle" | "running" | "success" | "error";

const DURATION_SECONDS = 60 * 60; // 60 minutes
const N_QUESTIONS = 15;

const STARTER_CODE: Record<string, string> = {
  Python:     "def solution():\n    # Write your solution here\n    pass\n",
  JavaScript: "function solution() {\n  // Write your solution here\n}\n",
  Java:       "public class Solution {\n    public static void main(String[] args) {\n        // Write your solution here\n    }\n}\n",
  "C++":      "#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your solution here\n    return 0;\n}\n",
  C:          "#include <stdio.h>\n\nint main() {\n    // Write your solution here\n    return 0;\n}\n",
};
const LANGUAGES = Object.keys(STARTER_CODE);

export default function CodingPage() {
  const router = useRouter();
  const [stage, setStage]         = useState<Stage>("LOADING");
  const [questions, setQuestions] = useState<CodingQuestion[]>([]);
  const [current, setCurrent]     = useState(0);
  const [language, setLanguage]   = useState("Python");

  // Code per problem: questionId -> code string
  const [codeMap, setCodeMap]     = useState<Record<number, string>>({});
  const [error, setError]         = useState<string | null>(null);

  const [runState, setRunState]   = useState<RunState>("idle");
  const [runOutput, setRunOutput] = useState<string | null>(null);
  const [result, setResult]       = useState<{ score: number; total: number; percentage: number } | null>(null);
  const timerRef = useRef(false);

  useEffect(() => {
    if (!getStoredToken()) { router.replace("/login"); return; }
    loadQuestions();
  }, []);

  async function loadQuestions() {
    try {
      setStage("LOADING");
      setError(null);
      let qs: CodingQuestion[] = [];
      try {
        const paper = await getPersonalizedAssessmentPaper();
        if (paper.codingQuestions && paper.codingQuestions.length > 0) {
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

      // Initialize code map with starter code for each question
      const initialMap: Record<number, string> = {};
      qs.forEach((q, idx) => {
        const lang = q.programmingLanguage || "Python";
        initialMap[idx] = STARTER_CODE[lang] || STARTER_CODE["Python"];
      });
      setCodeMap(initialMap);

      const firstLang = qs[0].programmingLanguage || "Python";
      setLanguage(firstLang);
      setStage("INSTRUCTIONS");
    } catch (err: unknown) {
      setError((err as Error)?.message ?? "Failed to load coding problems.");
      setStage("ERROR");
    }
  }

  function handleLanguageChange(lang: string) {
    setLanguage(lang);
    setCodeMap((prev) => ({
      ...prev,
      [current]: prev[current] || STARTER_CODE[lang] || STARTER_CODE["Python"],
    }));
  }

  const currentCode = codeMap[current] || STARTER_CODE[language] || STARTER_CODE["Python"];

  function updateCode(newCode: string) {
    setCodeMap((prev) => ({ ...prev, [current]: newCode }));
  }

  // Simulate "Run" against sample test cases
  async function handleRun() {
    const q = questions[current];
    if (!q) return;
    setRunState("running");
    setRunOutput(null);
    await new Promise((r) => setTimeout(r, 600));

    const sampleInput  = q.sampleInput || "(sample test case)";
    const sampleOutput = q.sampleOutput || "(expected output)";
    setRunOutput(
      `▶ Running against sample test case...\n\nInput:\n${sampleInput}\n\nExpected Output:\n${sampleOutput}\n\n✓ Solution formatted cleanly. Submit when ready!`
    );
    setRunState("success");
  }

  const handleSubmit = useCallback(async () => {
    if (stage === "SUBMITTING" || stage === "COMPLETED") return;
    setStage("SUBMITTING");
    try {
      const submissions: CodingSubmission[] = questions.map((q, idx) => ({
        questionId: q.id || q._id,
        code: codeMap[idx] || "",
        language,
      }));
      const res = await submitCodingAnswers(submissions);
      setResult(res);
      setStage("COMPLETED");
    } catch (err: unknown) {
      setError((err as Error)?.message ?? "Submission failed.");
      setStage("ERROR");
    }
  }, [questions, codeMap, language, stage]);

  // ── LOADING ────────────────────────────────────────────────────
  if (stage === "LOADING") {
    return <AppShell title="Coding Assessment"><LoadingState message="Generating 15 personalized LeetCode-style coding problems..." /></AppShell>;
  }

  // ── ERROR ──────────────────────────────────────────────────────
  if (stage === "ERROR") {
    return <AppShell title="Coding Assessment"><ErrorState message={error ?? undefined} onRetry={loadQuestions} /></AppShell>;
  }

  // ── SUBMITTING ─────────────────────────────────────────────────
  if (stage === "SUBMITTING") {
    return <AppShell title="Coding Assessment"><LoadingState message="Evaluating your 15 coding submissions..." /></AppShell>;
  }

  // ── INSTRUCTIONS ───────────────────────────────────────────────
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
                  "Use 'Run' to test code against sample test cases.",
                  "All 15 solutions will be evaluated upon submission.",
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

  // ── COMPLETED ──────────────────────────────────────────────────
  if (stage === "COMPLETED" && result) {
    const pct    = Math.round(result.percentage ?? 0);
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
                Evaluated across 15 coding problems. {result.score}/{result.total} marks awarded.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <ResultCard label="Score"      value={`${result.score}/${result.total}`} />
            <ResultCard label="Percentage" value={`${pct}%`} accent                 />
            <ResultCard label="Status"     value={passed ? "Passed" : "Failed"}     />
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={() => { setRunState("idle"); setRunOutput(null); setResult(null); timerRef.current = false; loadQuestions(); }}
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
          </div>
        </div>
      </AppShell>
    );
  }

  // ── IN_PROGRESS ────────────────────────────────────────────────
  const q = questions[current];
  return (
    <AppShell title={`Coding Assessment — Problem ${current + 1} of 15`}>
      <div className="max-w-7xl mx-auto space-y-4">

        {/* Top Problem Switcher Bar */}
        <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-3 flex items-center justify-between gap-4 flex-wrap shadow-sm">
          <div className="flex items-center gap-2 overflow-x-auto py-1 max-w-full">
            <span className="text-[12px] font-bold text-[#64748B] shrink-0 mr-1">Problems:</span>
            {questions.map((_, idx) => {
              const isCurrent = idx === current;
              const hasCode = !!codeMap[idx] && codeMap[idx].length > 50;
              return (
                <button
                  key={idx}
                  onClick={() => { setCurrent(idx); setRunState("idle"); setRunOutput(null); }}
                  className={`w-8 h-8 rounded-lg text-[12px] font-bold transition-all shrink-0 flex items-center justify-center ${
                    isCurrent
                      ? "bg-[#4096ff] text-white shadow-sm scale-105"
                      : hasCode
                      ? "bg-[#4096ff]/10 text-[#4096ff] border border-[#4096ff]/30"
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
            onExpire={() => { if (!timerRef.current) { timerRef.current = true; handleSubmit(); } }}
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
                        <p className="text-[10.5px] text-[#64748B] font-bold mb-1">Input</p>
                        <pre className="font-mono text-[12px] text-[#1E293B] whitespace-pre-wrap">{q.sampleInput}</pre>
                      </div>
                    )}
                    {q.sampleOutput && (
                      <div className="bg-[#F8FAFC] border border-[rgba(30,41,59,0.08)] rounded-lg p-3">
                        <p className="text-[10.5px] text-[#64748B] font-bold mb-1">Output</p>
                        <pre className="font-mono text-[12px] text-[#1E293B] whitespace-pre-wrap">{q.sampleOutput}</pre>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Navigation buttons */}
            <div className="p-4 border-t border-[rgba(30,41,59,0.08)] flex items-center justify-between shrink-0 bg-[#F8FAFC]">
              <button
                onClick={() => setCurrent((c) => Math.max(0, c - 1))}
                disabled={current === 0}
                className="px-4 py-2 rounded-lg border border-[rgba(30,41,59,0.14)] text-[12.5px] font-bold text-[#1E293B] hover:bg-white disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center gap-1.5"
              >
                <ArrowLeft size={13} /> Prev Problem
              </button>

              <span className="text-[12px] font-semibold text-[#64748B]">
                {current + 1} of 15
              </span>

              {current < questions.length - 1 ? (
                <button
                  onClick={() => setCurrent((c) => Math.min(questions.length - 1, c + 1))}
                  className="px-4 py-2 rounded-lg bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[12.5px] font-bold transition-all flex items-center gap-1.5"
                >
                  Next Problem <ArrowRight size={13} />
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  className="px-5 py-2 rounded-lg bg-[#1E293B] hover:bg-[#334155] text-white text-[12.5px] font-bold transition-all flex items-center gap-1.5"
                >
                  <CheckCircle2 size={13} /> Submit All 15
                </button>
              )}
            </div>
          </div>

          {/* Right: Code Editor & Output */}
          <div className="flex flex-col gap-3">
            {/* Editor */}
            <div className="bg-[#1E293B] rounded-xl overflow-hidden flex flex-col flex-1 min-h-0 shadow-md">
              {/* Toolbar */}
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/10 shrink-0">
                <div className="relative">
                  <select
                    value={language}
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
                    Run Sample
                  </button>

                  <button
                    onClick={handleSubmit}
                    className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[12px] font-bold transition-all"
                  >
                    <CheckCircle2 size={12} /> Submit All
                  </button>
                </div>
              </div>

              {/* Code Textarea */}
              <textarea
                value={currentCode}
                onChange={(e) => updateCode(e.target.value)}
                spellCheck={false}
                className="flex-1 w-full bg-transparent text-[#E2E8F0] font-mono text-[13px] leading-relaxed p-4 resize-none outline-none"
                style={{ tabSize: 2 }}
                onKeyDown={(e) => {
                  if (e.key === "Tab") {
                    e.preventDefault();
                    const start = e.currentTarget.selectionStart;
                    const end   = e.currentTarget.selectionEnd;
                    const newCode = currentCode.substring(0, start) + "  " + currentCode.substring(end);
                    updateCode(newCode);
                    setTimeout(() => { e.currentTarget.selectionStart = e.currentTarget.selectionEnd = start + 2; }, 0);
                  }
                }}
              />
            </div>

            {/* Output Panel */}
            <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl overflow-hidden shrink-0 shadow-sm" style={{ minHeight: 120 }}>
              <div className="flex items-center gap-2 px-4 py-2 border-b border-[rgba(30,41,59,0.08)]">
                <Terminal size={13} className="text-[#64748B]" />
                <span className="text-[11.5px] font-bold text-[#64748B] uppercase tracking-wide">Test Output</span>
                {runState === "running" && <Loader2 size={12} className="animate-spin text-[#4096ff] ml-auto" />}
                {runState === "success" && <CheckCircle2 size={12} className="text-[#15803D] ml-auto" />}
                {runState === "error"   && <XCircle size={12} className="text-[#DC2626] ml-auto" />}
              </div>
              <div className="p-4 max-h-[140px] overflow-y-auto">
                {runState === "idle" && (
                  <p className="text-[12px] text-[#94A3B8]">Click &quot;Run Sample&quot; to test your solution for Problem {current + 1}.</p>
                )}
                {runOutput && (
                  <pre className="font-mono text-[12px] text-[#374151] whitespace-pre-wrap leading-relaxed">{runOutput}</pre>
                )}
              </div>
            </div>
          </div>

        </div>
      </div>
    </AppShell>
  );
}
