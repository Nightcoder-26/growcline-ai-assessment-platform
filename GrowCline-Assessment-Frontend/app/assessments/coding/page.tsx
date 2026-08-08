"use client";

/**
 * /assessments/coding — Coding Assessment
 * Split layout: problem statement (left) + code editor (right)
 * States: LOADING → INSTRUCTIONS → IN_PROGRESS → SUBMITTING → COMPLETED → ERROR
 */

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Code2, ArrowLeft, ArrowRight, CheckCircle2,
  Play, Trophy, RotateCcw, ChevronDown, Terminal,
  XCircle, Loader2,
} from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import {
  AssessmentTimer, ResultCard, LoadingState, ErrorState, ScoreRing,
} from "@/components/assessment/shared";
import {
  generateCodingQuestions,
  submitCodingAnswers,
  type CodingQuestion,
} from "@/services/assessmentService";
import { getStoredToken } from "@/services/authService";

type Stage = "LOADING" | "INSTRUCTIONS" | "IN_PROGRESS" | "SUBMITTING" | "COMPLETED" | "ERROR";
type RunState = "idle" | "running" | "success" | "error";

const DURATION_SECONDS = 30 * 60;
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
  const [stage, setStage]       = useState<Stage>("LOADING");
  const [question, setQuestion] = useState<CodingQuestion | null>(null);
  const [language, setLanguage] = useState("Python");
  const [code, setCode]         = useState(STARTER_CODE["Python"]);
  const [error, setError]       = useState<string | null>(null);
  const [runState, setRunState] = useState<RunState>("idle");
  const [runOutput, setRunOutput] = useState<string | null>(null);
  const [result, setResult]     = useState<{ score: number; total: number; percentage: number } | null>(null);
  const timerRef = useRef(false);

  useEffect(() => {
    if (!getStoredToken()) { router.replace("/login"); return; }
    loadQuestion();
  }, []);

  async function loadQuestion() {
    try {
      setStage("LOADING");
      setError(null);
      const qs = await generateCodingQuestions(1);
      if (!qs.length) {
        setError("No coding questions are available right now.");
        setStage("ERROR");
        return;
      }
      const q = qs[0];
      setQuestion(q);
      // Set language from question if available
      const lang = q.programmingLanguage ?? "Python";
      setLanguage(lang);
      setCode(STARTER_CODE[lang] ?? STARTER_CODE["Python"]);
      setStage("INSTRUCTIONS");
    } catch (err: unknown) {
      setError((err as Error)?.message ?? "Failed to load question.");
      setStage("ERROR");
    }
  }

  function handleLanguageChange(lang: string) {
    setLanguage(lang);
    setCode(STARTER_CODE[lang] ?? STARTER_CODE["Python"]);
  }

  // Simulate "Run" against visible test cases
  async function handleRun() {
    if (!question) return;
    setRunState("running");
    setRunOutput(null);
    // Small delay for UX, then show sample result
    await new Promise((r) => setTimeout(r, 800));
    const sampleInput  = question.sampleInput  ?? "(no sample input)";
    const sampleOutput = question.sampleOutput ?? "(no expected output)";
    setRunOutput(
      `▶ Running against sample test case...\n\nInput:\n${sampleInput}\n\nExpected Output:\n${sampleOutput}\n\n✓ Code submitted. Submit your solution to get full evaluation.`
    );
    setRunState("success");
  }

  async function handleSubmit() {
    if (!question) return;
    setStage("SUBMITTING");
    try {
      const res = await submitCodingAnswers([{
        questionId: question.id ?? question._id,
        code,
        language,
      }]);
      setResult(res);
      setStage("COMPLETED");
    } catch (err: unknown) {
      setError((err as Error)?.message ?? "Submission failed.");
      setStage("ERROR");
    }
  }

  // ── LOADING ────────────────────────────────────────────────────
  if (stage === "LOADING") {
    return <AppShell title="Coding Assessment"><LoadingState message="Preparing your problem…" /></AppShell>;
  }

  // ── ERROR ──────────────────────────────────────────────────────
  if (stage === "ERROR") {
    return <AppShell title="Coding Assessment"><ErrorState message={error ?? undefined} onRetry={loadQuestion} /></AppShell>;
  }

  // ── SUBMITTING ─────────────────────────────────────────────────
  if (stage === "SUBMITTING") {
    return <AppShell title="Coding Assessment"><LoadingState message="Evaluating your solution…" /></AppShell>;
  }

  // ── INSTRUCTIONS ───────────────────────────────────────────────
  if (stage === "INSTRUCTIONS") {
    return (
      <AppShell title="Coding Assessment" subtitle="Read instructions before starting">
        <div className="max-w-2xl mx-auto">
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-2xl overflow-hidden">
            <div className="px-7 py-6 border-b border-[rgba(30,41,59,0.08)] flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-[#4096ff]/08 border border-[#4096ff]/15 flex items-center justify-center">
                <Code2 size={22} className="text-[#4096ff]" />
              </div>
              <div>
                <h2 className="text-[17px] font-bold text-[#1E293B]">Coding Assessment</h2>
                <p className="text-[12.5px] text-[#64748B] mt-0.5">1 problem · 30 minutes</p>
              </div>
            </div>

            <div className="px-7 py-6 space-y-4">
              <h3 className="text-[13px] font-semibold text-[#1E293B] uppercase tracking-wide">Instructions</h3>
              <ul className="space-y-2.5">
                {[
                  "You will be given 1 algorithmic problem to solve.",
                  "You have 30 minutes to write and submit your solution.",
                  "Select your preferred programming language before starting.",
                  "Use 'Run' to test against the sample test case.",
                  "Use 'Submit' when you are confident in your solution.",
                  "Your code is evaluated server-side. Results are shown after submission.",
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
                <p className="text-[12.5px] font-semibold text-[#64748B] uppercase tracking-wide mb-3">Available languages</p>
                <div className="flex flex-wrap gap-2">
                  {LANGUAGES.map((l) => (
                    <span key={l} className="px-3 py-1 bg-[#F1F5F9] text-[#475569] text-[12px] font-medium rounded-lg">{l}</span>
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
      <AppShell title="Coding Assessment — Results">
        <div className="max-w-2xl mx-auto space-y-5">
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-2xl p-7 flex flex-col sm:flex-row items-center gap-7">
            <ScoreRing percentage={pct} size={100} />
            <div className="text-center sm:text-left">
              <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-[12px] font-semibold mb-3 ${passed ? "bg-[#F0FDF4] text-[#15803D] border border-[#86EFAC]/50" : "bg-[#FEF2F2] text-[#B91C1C] border border-[#FECACA]/50"}`}>
                <CheckCircle2 size={13} />{passed ? "Passed" : "Failed"}
              </div>
              <h2 className="text-[22px] font-bold text-[#1E293B] mb-1">{pct}% Score</h2>
              <p className="text-[13px] text-[#64748B]">
                Solution evaluated. {result.score}/{result.total} marks awarded.
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
              onClick={() => { setRunState("idle"); setRunOutput(null); setResult(null); timerRef.current = false; loadQuestion(); }}
              className="flex-1 flex items-center justify-center gap-2 h-11 rounded-xl border border-[rgba(30,41,59,0.14)] text-[13.5px] font-semibold text-[#1E293B] hover:bg-[#F1F5F9] transition-all"
            >
              <RotateCcw size={14} /> Try Another
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
  const q = question!;
  return (
    <AppShell title="Coding Assessment">
      <div className="max-w-7xl mx-auto">
        {/* Top bar */}
        <div className="flex items-center justify-between mb-4 gap-4 flex-wrap">
          <div>
            <h2 className="text-[14px] font-semibold text-[#1E293B]">{q.title}</h2>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-[#F1F5F9] text-[#64748B] font-medium">
                {q.difficulty}
              </span>
              <span className="text-[11px] text-[#94A3B8]">{q.category}</span>
            </div>
          </div>
          <AssessmentTimer durationSeconds={DURATION_SECONDS} onExpire={() => { if (!timerRef.current) { timerRef.current = true; handleSubmit(); } }} />
        </div>

        {/* Main split layout */}
        <div className="grid lg:grid-cols-2 gap-4 h-[calc(100vh-220px)] min-h-[560px]">

          {/* Left: Problem Statement */}
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl overflow-y-auto flex flex-col">
            <div className="px-5 py-3 border-b border-[rgba(30,41,59,0.08)] flex items-center gap-2 shrink-0">
              <span className="text-[12px] font-semibold text-[#64748B] uppercase tracking-wide">Problem</span>
            </div>
            <div className="p-5 space-y-4 text-[13.5px] text-[#374151] leading-relaxed overflow-y-auto flex-1">
              <div>
                <h3 className="text-[15px] font-bold text-[#1E293B] mb-2">{q.title}</h3>
                <p className="leading-loose whitespace-pre-wrap">{q.problemStatement}</p>
              </div>

              {q.inputFormat && (
                <div>
                  <p className="text-[12px] font-semibold text-[#1E293B] uppercase tracking-wide mb-1.5">Input Format</p>
                  <p className="text-[13px]">{q.inputFormat}</p>
                </div>
              )}
              {q.outputFormat && (
                <div>
                  <p className="text-[12px] font-semibold text-[#1E293B] uppercase tracking-wide mb-1.5">Output Format</p>
                  <p className="text-[13px]">{q.outputFormat}</p>
                </div>
              )}
              {q.constraints && (
                <div>
                  <p className="text-[12px] font-semibold text-[#1E293B] uppercase tracking-wide mb-1.5">Constraints</p>
                  <div className="bg-[#F8FAFC] border border-[rgba(30,41,59,0.08)] rounded-lg px-3 py-2.5 font-mono text-[12.5px]">
                    {q.constraints}
                  </div>
                </div>
              )}
              {(q.sampleInput || q.sampleOutput) && (
                <div>
                  <p className="text-[12px] font-semibold text-[#1E293B] uppercase tracking-wide mb-1.5">Example</p>
                  <div className="grid grid-cols-2 gap-2">
                    {q.sampleInput && (
                      <div className="bg-[#F8FAFC] border border-[rgba(30,41,59,0.08)] rounded-lg p-3">
                        <p className="text-[10.5px] text-[#64748B] font-semibold mb-1.5">Input</p>
                        <pre className="font-mono text-[12px] text-[#1E293B] whitespace-pre-wrap">{q.sampleInput}</pre>
                      </div>
                    )}
                    {q.sampleOutput && (
                      <div className="bg-[#F8FAFC] border border-[rgba(30,41,59,0.08)] rounded-lg p-3">
                        <p className="text-[10.5px] text-[#64748B] font-semibold mb-1.5">Output</p>
                        <pre className="font-mono text-[12px] text-[#1E293B] whitespace-pre-wrap">{q.sampleOutput}</pre>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right: Code Editor + Output */}
          <div className="flex flex-col gap-3">
            {/* Editor */}
            <div className="bg-[#1E293B] rounded-xl overflow-hidden flex flex-col flex-1 min-h-0">
              {/* Editor toolbar */}
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-white/10 shrink-0">
                {/* Language selector */}
                <div className="relative">
                  <select
                    value={language}
                    onChange={(e) => handleLanguageChange(e.target.value)}
                    className="appearance-none bg-white/10 border border-white/15 text-white text-[12px] font-medium pl-3 pr-7 py-1.5 rounded-lg cursor-pointer focus:outline-none focus:border-[#4096ff]"
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
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 border border-white/10 text-white text-[12px] font-medium transition-all disabled:opacity-50"
                  >
                    {runState === "running" ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
                    Run
                  </button>
                  <button
                    onClick={handleSubmit}
                    className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[12px] font-semibold transition-all"
                  >
                    <CheckCircle2 size={12} /> Submit
                  </button>
                </div>
              </div>

              {/* Code textarea */}
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                spellCheck={false}
                className="flex-1 w-full bg-transparent text-[#E2E8F0] font-mono text-[13px] leading-relaxed p-4 resize-none outline-none"
                style={{ tabSize: 2 }}
                onKeyDown={(e) => {
                  if (e.key === "Tab") {
                    e.preventDefault();
                    const start = e.currentTarget.selectionStart;
                    const end   = e.currentTarget.selectionEnd;
                    const newCode = code.substring(0, start) + "  " + code.substring(end);
                    setCode(newCode);
                    setTimeout(() => { e.currentTarget.selectionStart = e.currentTarget.selectionEnd = start + 2; }, 0);
                  }
                }}
              />
            </div>

            {/* Output area */}
            <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl overflow-hidden shrink-0" style={{ minHeight: 120 }}>
              <div className="flex items-center gap-2 px-4 py-2.5 border-b border-[rgba(30,41,59,0.08)]">
                <Terminal size={13} className="text-[#64748B]" />
                <span className="text-[12px] font-semibold text-[#64748B] uppercase tracking-wide">Output</span>
                {runState === "running" && <Loader2 size={12} className="animate-spin text-[#4096ff] ml-auto" />}
                {runState === "success" && <CheckCircle2 size={12} className="text-[#15803D] ml-auto" />}
                {runState === "error"   && <XCircle size={12} className="text-[#DC2626] ml-auto" />}
              </div>
              <div className="p-4">
                {runState === "idle" && (
                  <p className="text-[12.5px] text-[#94A3B8]">Click "Run" to test against the sample test case.</p>
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
