"use client";

/**
 * Shared Assessment Components
 * AssessmentCard, QuestionCard, QuestionNavigator, AssessmentTimer,
 * ProgressBar, ResultCard, EmptyState, LoadingState, ErrorState
 */

import { useEffect, useState, useCallback } from "react";
import {
  Clock, CheckCircle2, XCircle, AlertCircle,
  RefreshCw, FileQuestion, BarChart3, ArrowRight,
} from "lucide-react";

// ─── AssessmentCard ──────────────────────────────────────────────────────────

interface AssessmentCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  status?: "not_started" | "in_progress" | "completed";
  questionCount?: number;
  duration?: number;
  onAction: () => void;
  disabled?: boolean;
}

export function AssessmentCard({
  title,
  description,
  icon,
  status = "not_started",
  questionCount,
  duration,
  onAction,
  disabled,
}: AssessmentCardProps) {
  const statusConfig = {
    not_started: { label: "Not Started", color: "text-[#64748B]", bg: "bg-[#F1F5F9]" },
    in_progress:  { label: "In Progress", color: "text-[#4096ff]", bg: "bg-[#EFF6FF]" },
    completed:    { label: "Completed",   color: "text-[#0F172A]", bg: "bg-[#F0FDF4]" },
  }[status];

  const actionLabel = {
    not_started: "Start Assessment",
    in_progress: "Continue",
    completed:   "View Results",
  }[status];

  return (
    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 flex flex-col gap-4 hover:border-[#4096ff]/30 hover:shadow-[0_4px_20px_rgba(64,150,255,0.08)] transition-all duration-200">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#4096ff]/08 border border-[#4096ff]/15 flex items-center justify-center text-[#4096ff] shrink-0">
            {icon}
          </div>
          <div>
            <h3 className="text-[14.5px] font-semibold text-[#1E293B] leading-tight">{title}</h3>
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium mt-1 ${statusConfig.bg} ${statusConfig.color}`}>
              {statusConfig.label}
            </span>
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-[13px] text-[#64748B] leading-relaxed">{description}</p>

      {/* Meta */}
      {(questionCount !== undefined || duration !== undefined) && (
        <div className="flex items-center gap-4 text-[12px] text-[#94A3B8]">
          {questionCount !== undefined && (
            <span className="flex items-center gap-1.5">
              <FileQuestion size={13} />
              {questionCount} questions
            </span>
          )}
          {duration !== undefined && (
            <span className="flex items-center gap-1.5">
              <Clock size={13} />
              {duration} min
            </span>
          )}
        </div>
      )}

      {/* CTA */}
      <button
        onClick={onAction}
        disabled={disabled}
        className="mt-auto w-full h-[38px] flex items-center justify-center gap-2 rounded-lg bg-[#4096ff] hover:bg-[#60a5fa] disabled:opacity-50 disabled:cursor-not-allowed text-white text-[13px] font-semibold transition-all"
      >
        {actionLabel}
        <ArrowRight size={13} />
      </button>
    </div>
  );
}

// ─── QuestionCard ────────────────────────────────────────────────────────────

interface QuestionCardProps {
  questionNumber: number;
  totalQuestions: number;
  question: string;
  options: string[];
  selectedAnswer: string | null;
  onSelect: (answer: string) => void;
}

export function QuestionCard({
  questionNumber,
  totalQuestions,
  question,
  options,
  selectedAnswer,
  onSelect,
}: QuestionCardProps) {
  return (
    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-6">
      {/* Question header */}
      <div className="flex items-center justify-between mb-4">
        <span className="text-[12px] font-medium text-[#64748B] uppercase tracking-wide">
          Question {questionNumber} of {totalQuestions}
        </span>
      </div>

      {/* Question text */}
      <p className="text-[15px] font-medium text-[#1E293B] leading-relaxed mb-6">
        {question}
      </p>

      {/* Options */}
      <div className="space-y-2.5">
        {options.map((opt, i) => {
          const letter = String.fromCharCode(65 + i);
          const selected = selectedAnswer === opt;
          return (
            <button
              key={i}
              onClick={() => onSelect(opt)}
              className={`
                w-full flex items-center gap-3.5 px-4 py-3.5 rounded-xl border text-left
                text-[13.5px] font-medium transition-all duration-150
                ${selected
                  ? "border-[#4096ff] bg-[#EFF6FF] text-[#1E293B] shadow-[0_0_0_3px_rgba(64,150,255,0.12)]"
                  : "border-[rgba(30,41,59,0.10)] bg-white text-[#374151] hover:border-[#4096ff]/40 hover:bg-[#F8FAFC]"
                }
              `}
            >
              <span
                className={`
                  w-7 h-7 rounded-lg flex items-center justify-center text-[12px] font-bold shrink-0
                  ${selected ? "bg-[#4096ff] text-white" : "bg-[#F1F5F9] text-[#64748B]"}
                `}
              >
                {letter}
              </span>
              <span className="flex-1">{opt}</span>
              {selected && <CheckCircle2 size={16} className="text-[#4096ff] shrink-0" />}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ─── QuestionNavigator ───────────────────────────────────────────────────────

interface QuestionNavigatorProps {
  total: number;
  current: number;
  answered: Set<number>;
  onJump: (index: number) => void;
}

export function QuestionNavigator({ total, current, answered, onJump }: QuestionNavigatorProps) {
  return (
    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4">
      <p className="text-[12px] font-semibold text-[#64748B] uppercase tracking-wide mb-3">
        Questions
      </p>
      <div className="grid grid-cols-5 gap-1.5">
        {Array.from({ length: total }, (_, i) => {
          const isCurrent  = i === current;
          const isAnswered = answered.has(i);
          return (
            <button
              key={i}
              onClick={() => onJump(i)}
              className={`
                w-full aspect-square rounded-lg text-[12px] font-semibold transition-all
                ${isCurrent
                  ? "bg-[#4096ff] text-white shadow-[0_2px_6px_rgba(64,150,255,0.4)]"
                  : isAnswered
                    ? "bg-[#DBEAFE] text-[#4096ff] border border-[#4096ff]/20"
                    : "bg-[#F1F5F9] text-[#64748B] hover:bg-[#E2E8F0]"
                }
              `}
            >
              {i + 1}
            </button>
          );
        })}
      </div>
      {/* Legend */}
      <div className="flex items-center gap-4 mt-3 text-[11px] text-[#94A3B8]">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-[#4096ff]" />
          Current
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-[#DBEAFE] border border-[#4096ff]/20" />
          Answered
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-[#F1F5F9]" />
          Unanswered
        </span>
      </div>
    </div>
  );
}

// ─── AssessmentTimer ─────────────────────────────────────────────────────────

interface AssessmentTimerProps {
  durationSeconds: number;
  onExpire?: () => void;
}

export function AssessmentTimer({ durationSeconds, onExpire }: AssessmentTimerProps) {
  const [remaining, setRemaining] = useState(durationSeconds);
  const isWarning = remaining <= 300; // 5 min warning
  const isDanger  = remaining <= 60;  // 1 min danger

  useEffect(() => {
    const id = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(id);
          onExpire?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [onExpire]);

  const mins = Math.floor(remaining / 60).toString().padStart(2, "0");
  const secs = (remaining % 60).toString().padStart(2, "0");

  return (
    <div
      className={`
        flex items-center gap-2 px-3.5 py-2 rounded-xl text-[13.5px] font-mono font-semibold
        ${isDanger
          ? "bg-[#FEF2F2] text-[#DC2626] border border-[#FECACA]"
          : isWarning
            ? "bg-[#FFF7ED] text-[#C2410C] border border-[#FDBA74]/50"
            : "bg-[#F1F5F9] text-[#1E293B] border border-[rgba(30,41,59,0.10)]"
        }
      `}
    >
      <Clock size={14} className={isDanger ? "animate-pulse" : ""} />
      {mins}:{secs}
    </div>
  );
}

// ─── ProgressBar ─────────────────────────────────────────────────────────────

interface ProgressBarProps {
  current: number;
  total: number;
  answered: number;
}

export function ProgressBar({ current, total, answered }: ProgressBarProps) {
  const pct = total > 0 ? Math.round((answered / total) * 100) : 0;
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-1.5 bg-[#E2E8F0] rounded-full overflow-hidden">
        <div
          className="h-full bg-[#4096ff] rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[12px] font-medium text-[#64748B] shrink-0 min-w-[52px] text-right">
        {answered}/{total}
      </span>
    </div>
  );
}

// ─── ResultCard ──────────────────────────────────────────────────────────────

interface ResultCardProps {
  label: string;
  value: string | number;
  sub?: string;
  accent?: boolean;
}

export function ResultCard({ label, value, sub, accent }: ResultCardProps) {
  return (
    <div
      className={`
        rounded-xl p-4 border
        ${accent
          ? "bg-[#4096ff] border-[#4096ff] text-white"
          : "bg-white border-[rgba(30,41,59,0.10)] text-[#1E293B]"
        }
      `}
    >
      <p className={`text-[11.5px] font-medium uppercase tracking-wide mb-1 ${accent ? "text-white/70" : "text-[#64748B]"}`}>
        {label}
      </p>
      <p className={`text-[26px] font-bold leading-none ${accent ? "text-white" : "text-[#1E293B]"}`}>
        {value}
      </p>
      {sub && (
        <p className={`text-[11px] mt-1 ${accent ? "text-white/60" : "text-[#94A3B8]"}`}>{sub}</p>
      )}
    </div>
  );
}

// ─── EmptyState ──────────────────────────────────────────────────────────────

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="w-14 h-14 rounded-2xl bg-[#F1F5F9] border border-[rgba(30,41,59,0.08)] flex items-center justify-center mb-4 text-[#94A3B8]">
        {icon ?? <BarChart3 size={24} />}
      </div>
      <h3 className="text-[15px] font-semibold text-[#1E293B] mb-1.5">{title}</h3>
      {description && (
        <p className="text-[13px] text-[#64748B] max-w-xs leading-relaxed">{description}</p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="mt-5 px-5 py-2 rounded-lg bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[13px] font-semibold transition-all"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}

// ─── LoadingState ─────────────────────────────────────────────────────────────

export function LoadingState({ message = "Loading…" }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <div className="w-9 h-9 rounded-full border-[3px] border-[#4096ff] border-t-transparent animate-spin" />
      <p className="text-[13px] text-[#64748B] font-medium">{message}</p>
    </div>
  );
}

// ─── ErrorState ───────────────────────────────────────────────────────────────

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message = "Something went wrong.", onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <div className="w-12 h-12 rounded-2xl bg-[#FEF2F2] border border-[#FECACA] flex items-center justify-center">
        <AlertCircle size={22} className="text-[#DC2626]" />
      </div>
      <div className="text-center">
        <p className="text-[14px] font-semibold text-[#1E293B] mb-1">Unable to load</p>
        <p className="text-[13px] text-[#64748B] max-w-xs">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[rgba(30,41,59,0.14)] text-[13px] font-medium text-[#1E293B] hover:bg-[#F1F5F9] transition-all"
        >
          <RefreshCw size={13} />
          Try again
        </button>
      )}
    </div>
  );
}

// ─── ScoreRing (compact score circle) ────────────────────────────────────────

interface ScoreRingProps {
  percentage: number;
  size?: number;
}

export function ScoreRing({ percentage, size = 80 }: ScoreRingProps) {
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (percentage / 100) * circ;

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#E2E8F0" strokeWidth={4} />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke="#4096ff" strokeWidth={4}
          strokeDasharray={circ} strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-700"
        />
      </svg>
      <span className="absolute text-[13px] font-bold text-[#1E293B]">{Math.round(percentage)}%</span>
    </div>
  );
}

// Re-export CheckCircle2, XCircle for use in pages
export { CheckCircle2, XCircle };
