"use client";

import {
  Sparkles,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
} from "lucide-react";
import { cn } from "@/lib/utils";

export interface Question {
  questionId: string;
  category: string;
  prompt: string;
  hint: string;
}

interface QuestionPanelProps {
  question: Question;
  index: number;
  total: number;
  answered: boolean[];
  loading?: boolean;
  canGoPrev?: boolean;
  isTimeUp?: boolean;
  onPrev: () => void;
  onNext: () => void;
  onJump: (i: number) => void;
  /** Candidate's typed answer (used for text-based submission) */
  candidateAnswer?: string;
  onAnswerChange?: (val: string) => void;
}

export function QuestionPanel({
  question,
  index,
  total,
  answered,
  loading = false,
  canGoPrev = false,
  isTimeUp = false,
  onPrev,
  onNext,
  onJump,
  candidateAnswer = "",
  onAnswerChange,
}: QuestionPanelProps) {
  return (
    <section className="rounded-[28px] border border-white/10 bg-[#111827]/90 p-6 shadow-[0_20px_60px_rgba(0,0,0,0.35)] backdrop-blur-xl">

      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#4096ff]/20">
            <ClipboardList className="h-5 w-5 text-[#4096ff]" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Interview Question</h2>
            <p className="text-sm text-slate-400">AI Powered Assessment</p>
          </div>
        </div>

        <div className="rounded-full bg-[#4096ff]/15 px-4 py-2">
          <span className="text-sm font-semibold text-[#4096ff]">
            {String(index + 1).padStart(2, "0")} / {String(total).padStart(2, "0")}
          </span>
        </div>
      </div>

      {/* Category badge */}
      <div className="mb-5">
        <span className="inline-flex items-center gap-2 rounded-full bg-[#4096ff]/10 px-4 py-2 text-sm font-semibold text-[#4096ff]">
          <Sparkles className="h-4 w-4" />
          {question.category}
        </span>
      </div>

      {/* Question text */}
      <div className="space-y-4">
        {loading ? (
          <div className="space-y-3">
            <div className="h-6 w-3/4 rounded-lg bg-slate-700 animate-pulse" />
            <div className="h-6 w-1/2 rounded-lg bg-slate-700 animate-pulse" />
          </div>
        ) : (
          <h3 className="text-2xl font-bold leading-relaxed text-white">
            {question.prompt}
          </h3>
        )}

        <div className="rounded-2xl border border-slate-700 bg-[#0F172A] p-4">
          <p className="text-sm leading-7 text-slate-300">💡 {question.hint}</p>
        </div>
      </div>

      {/* Optional text-answer input for when the candidate types their answer */}
      {onAnswerChange && (
        <div className="relative mt-5">
          <textarea
            className={`w-full rounded-2xl border bg-[#0F172A] p-4 text-sm text-white placeholder-slate-500 resize-none focus:outline-none transition-colors ${
              isTimeUp
                ? "border-red-500/50 opacity-60 cursor-not-allowed"
                : "border-slate-700 focus:border-[#4096ff]"
            }`}
            rows={4}
            disabled={isTimeUp}
            placeholder={
              isTimeUp
                ? "⏰ 2-Minute Time's Up! Answer locked. Advancing to next question..."
                : "Type your answer here (optional — spoken answer is captured in continuous video)…"
            }
            value={candidateAnswer}
            onChange={(e) => onAnswerChange(e.target.value)}
          />
          {isTimeUp && (
            <div className="absolute top-3 right-3 rounded-lg bg-red-500/20 px-2.5 py-1 text-xs font-bold text-red-400 border border-red-500/30">
              Locked (2 Min Up)
            </div>
          )}
        </div>
      )}

      {/* Progress dots */}
      <div className="my-8 flex gap-2">
        {Array.from({ length: total }).map((_, i) => (
          <button
            key={i}
            onClick={() => onJump(i)}
            className={cn(
              "h-2 flex-1 rounded-full transition-all duration-300",
              i === index
                ? "bg-[#4096ff]"
                : answered[i]
                ? "bg-green-500"
                : "bg-slate-700 hover:bg-slate-600"
            )}
          />
        ))}
      </div>

      {/* Navigation */}
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={onPrev}
          disabled={!canGoPrev}
          className="flex items-center justify-center gap-2 rounded-2xl border border-slate-700 bg-slate-800 py-3 text-white transition hover:border-[#4096ff] disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="h-5 w-5" />
          Previous
        </button>

        <button
          onClick={onNext}
          disabled={loading}
          className="flex items-center justify-center gap-2 rounded-2xl bg-[#4096ff] py-3 font-semibold text-white transition hover:bg-[#2f86ff] disabled:opacity-40"
        >
          {loading ? (
            <span className="inline-block w-5 h-5 rounded-full border-2 border-white border-t-transparent animate-spin" />
          ) : (
            <>
              Submit &amp; Next
              <ChevronRight className="h-5 w-5" />
            </>
          )}
        </button>
      </div>
    </section>
  );
}