"use client";

/**
 * Shared Assessment Components
 * AssessmentCard, QuestionCard, QuestionNavigator, AssessmentTimer,
 * ProgressBar, ResultCard, EmptyState, LoadingState, ErrorState
 */

import { useEffect, useState } from "react";
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
  accentColor?: string;
  iconBg?: string;
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
  accentColor = "#4096ff",
}: AssessmentCardProps) {
  const statusConfig = {
    not_started: { label: "Not Started", color: "text-[#64748B]", bg: "bg-[#F1F5F9]" },
    in_progress:  { label: "In Progress", color: "text-[#4096ff]", bg: "bg-[#4096ff]/10" },
    completed:    { label: "Completed",   color: "text-[#1E293B]", bg: "bg-[#1E293B]/10" },
  }[status];

  const actionLabel = {
    not_started: "Start Assessment",
    in_progress: "Continue",
    completed:   "View Results",
  }[status];

  return (
    <div
      className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 flex flex-col gap-4 transition-all duration-200 hover:shadow-md group card-accent-blue"
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 icon-bg-blue transition-transform duration-200 group-hover:scale-105"
          >
            {icon}
          </div>
          <div>
            <h3 className="text-[14px] font-bold text-[#1E293B] leading-tight">{title}</h3>
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold mt-1 ${statusConfig.bg} ${statusConfig.color}`}>
              {statusConfig.label}
            </span>
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-[12.5px] text-[#64748B] leading-relaxed">{description}</p>

      {/* Meta */}
      {(questionCount !== undefined || duration !== undefined) && (
        <div className="flex items-center gap-4 text-[11.5px] text-[#94A3B8]">
          {questionCount !== undefined && (
            <span className="flex items-center gap-1.5">
              <FileQuestion size={12} />
              {questionCount} questions
            </span>
          )}
          {duration !== undefined && (
            <span className="flex items-center gap-1.5">
              <Clock size={12} />
              {duration} min
            </span>
          )}
        </div>
      )}

      {/* CTA */}
      <button
        onClick={onAction}
        disabled={disabled}
        className="mt-auto w-full h-[38px] flex items-center justify-center gap-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed text-white text-[13px] font-bold transition-all duration-200 bg-[#4096ff] hover:bg-[#60a5fa]"
        style={{ boxShadow: "0 4px 12px rgba(64,150,255,0.3)" }}
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
  marked?: boolean;
  onToggleMark?: () => void;
  autosaveState?: "idle" | "saving" | "saved";
}

export function QuestionCard({
  questionNumber,
  totalQuestions,
  question,
  options,
  selectedAnswer,
  onSelect,
  marked = false,
  onToggleMark,
  autosaveState = "idle",
}: QuestionCardProps) {
  return (
    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-6 shadow-sm">
      {/* Question header */}
      <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
        <span className="text-[11.5px] font-bold text-[#4096ff] uppercase tracking-widest px-2.5 py-1 rounded-md border border-[#4096ff]/20 bg-[#4096ff]/10">
          Question {questionNumber} of {totalQuestions}
        </span>
        <div className="flex items-center gap-3">
          {autosaveState !== "idle" && (
            <span className="text-[11px] text-[#94A3B8] font-medium flex items-center gap-1">
              {autosaveState === "saving" ? (
                <>
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-ping" />
                  Saving...
                </>
              ) : (
                <>
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                  Saved
                </>
              )}
            </span>
          )}
          {onToggleMark && (
            <button
              onClick={onToggleMark}
              aria-label="Mark for review"
              className={`p-1.5 rounded-lg border transition-all ${
                marked
                  ? "bg-amber-500/10 border-amber-500/30 text-amber-500 font-bold"
                  : "bg-white border-slate-200 text-slate-400 hover:text-slate-600 hover:bg-slate-50"
              }`}
            >
              ★ Review
            </button>
          )}
        </div>
      </div>

      {/* Question text */}
      <p className="text-[15px] font-semibold text-[#1E293B] leading-relaxed mb-6">
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
                  ? "bg-[#4096ff]/10 text-[#1E293B] border-[#4096ff]"
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
    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4 shadow-sm">
      <p className="text-[11px] font-bold text-[#64748B] uppercase tracking-widest mb-3">
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
                w-full aspect-square rounded-lg text-[12px] font-bold transition-all duration-150
                ${isCurrent
                  ? "bg-[#4096ff] text-white shadow-sm"
                  : isAnswered
                    ? "bg-[#4096ff]/10 text-[#4096ff] border border-[#4096ff]/25"
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
      <div className="flex items-center gap-4 mt-3 text-[10.5px] text-[#94A3B8]">
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm bg-[#4096ff]" />
          Current
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-sm border border-[#4096ff]/25 bg-[#4096ff]/10" />
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
        flex items-center gap-2 px-3.5 py-2 rounded-xl text-[13.5px] font-mono font-bold
        ${isDanger
          ? "bg-[#1E293B]/10 text-[#1E293B] border border-[#1E293B]/20 animate-pulse"
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
          className="h-full rounded-full transition-all duration-300 bg-[#4096ff]"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[12px] font-bold text-[#64748B] shrink-0 min-w-[52px] text-right">
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
        rounded-xl p-4 border transition-all duration-200
        ${accent
          ? "bg-[#4096ff] border-[#4096ff] text-white"
          : "bg-white border-[rgba(30,41,59,0.10)] text-[#1E293B] hover:shadow-sm"
        }
      `}
    >
      <p className={`text-[11px] font-bold uppercase tracking-widest mb-1 ${accent ? "text-white/70" : "text-[#64748B]"}`}>
        {label}
      </p>
      <p className={`text-[26px] font-extrabold leading-none ${accent ? "text-white" : "text-[#1E293B]"}`}>
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
      <div className="w-16 h-16 rounded-2xl bg-[#F1F5F9] border border-[rgba(30,41,59,0.08)] flex items-center justify-center mb-5 text-[#94A3B8] animate-float">
        {icon ?? <BarChart3 size={28} />}
      </div>
      <h3 className="text-[15px] font-bold text-[#1E293B] mb-2">{title}</h3>
      {description && (
        <p className="text-[13px] text-[#64748B] max-w-xs leading-relaxed">{description}</p>
      )}
      {action && (
        <button
          onClick={action.onClick}
          className="mt-6 px-6 py-2.5 rounded-xl text-white text-[13px] font-bold transition-all bg-[#4096ff] hover:bg-[#60a5fa]"
          style={{ boxShadow: "0 4px 14px rgba(64,150,255,0.35)" }}
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
    <div className="flex flex-col items-center justify-center py-20 gap-5">
      <div className="relative w-10 h-10">
        <div className="absolute inset-0 rounded-full border-[3px] border-[#4096ff]/20" />
        <div className="absolute inset-0 rounded-full border-[3px] border-transparent border-t-[#4096ff] animate-spin" />
      </div>
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
      <div className="w-14 h-14 rounded-2xl flex items-center justify-center bg-[#1E293B]/10 border border-[#1E293B]/20">
        <AlertCircle size={24} className="text-[#1E293B]" />
      </div>
      <div className="text-center">
        <p className="text-[14px] font-bold text-[#1E293B] mb-1">Unable to load</p>
        <p className="text-[13px] text-[#64748B] max-w-xs">{message}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl border border-[rgba(30,41,59,0.14)] text-[13px] font-semibold text-[#1E293B] hover:bg-[#F1F5F9] transition-all"
        >
          <RefreshCw size={13} />
          Try again
        </button>
      )}
    </div>
  );
}

// ─── ScoreRing (brand blue score circle) ────────────────────────────────────────

interface ScoreRingProps {
  percentage: number;
  size?: number;
}

export function ScoreRing({ percentage, size = 80 }: ScoreRingProps) {
  const [animated, setAnimated] = useState(false);
  const r = (size - 8) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (percentage / 100) * circ;

  const color = "#4096ff";

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 100);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#E2E8F0" strokeWidth={4} />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke={color} strokeWidth={4}
          strokeDasharray={circ}
          strokeDashoffset={animated ? offset : circ}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.8s cubic-bezier(0.4,0,0.2,1)" }}
        />
      </svg>
      <span className="absolute text-[12px] font-extrabold text-[#1E293B]">{Math.round(percentage)}%</span>
    </div>
  );
}

export { CheckCircle2, XCircle };

// ─── SkeletonCard ────────────────────────────────────────────────────────────

export function SkeletonCard() {
  return (
    <div className="shimmer-card flex flex-col gap-3">
      <div className="shimmer-element h-6 w-1/3" />
      <div className="shimmer-element h-4 w-full" />
      <div className="shimmer-element h-4 w-5/6" />
      <div className="shimmer-element h-8 w-1/4 mt-2" />
    </div>
  );
}

// ─── StatusBadge ─────────────────────────────────────────────────────────────

interface StatusBadgeProps {
  status: "not_started" | "in_progress" | "completed" | "expired" | string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const norm = (status || "").toLowerCase().replace("_", "-");
  let label = status;
  let bgClass = "badge-status-not-started";

  if (norm === "not-started" || norm === "not_started") {
    label = "Not Started";
    bgClass = "badge-status-not-started";
  } else if (norm === "in-progress" || norm === "in_progress") {
    label = "In Progress";
    bgClass = "badge-status-in-progress";
  } else if (norm === "completed" || norm === "passed" || norm === "failed") {
    label = norm === "completed" ? "Completed" : status;
    bgClass = "badge-status-completed";
  } else if (norm === "expired") {
    label = "Expired";
    bgClass = "badge-status-expired";
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${bgClass}`}>
      {label}
    </span>
  );
}

// ─── ResumeSkillTags ─────────────────────────────────────────────────────────

interface ResumeSkillTagsProps {
  skills: string[];
  maxToShow?: number;
}

export function ResumeSkillTags({ skills, maxToShow = 6 }: ResumeSkillTagsProps) {
  if (!skills || skills.length === 0) {
    return <span className="text-[12px] text-[#94A3B8]">No tech stack detected.</span>;
  }

  const visible = skills.slice(0, maxToShow);
  const extra = skills.length - maxToShow;

  return (
    <div className="flex flex-wrap gap-1.5">
      {visible.map((tag) => (
        <span
          key={tag}
          className="px-2 py-0.5 rounded-md bg-[#4096ff]/10 border border-[#4096ff]/20 text-[#4096ff] text-[11.5px] font-medium"
        >
          {tag}
        </span>
      ))}
      {extra > 0 && (
        <span className="px-2 py-0.5 rounded-md bg-slate-100 border border-slate-200 text-[#64748B] text-[11.5px] font-medium">
          +{extra} more
        </span>
      )}
    </div>
  );
}
