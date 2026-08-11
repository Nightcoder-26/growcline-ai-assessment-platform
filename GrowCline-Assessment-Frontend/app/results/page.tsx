"use client";

/**
 * /results — Assessment Results
 * Lists all candidate results from backend. Click to expand detail.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Trophy, ChevronDown, ChevronUp, Clock, CheckCircle2,
  XCircle, Minus, BarChart3,
} from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import { EmptyState, LoadingState, ErrorState, ScoreRing, ResultCard } from "@/components/assessment/shared";
import { getCandidateResults, type AssessmentResult } from "@/services/assessmentService";
import { getStoredToken, getStoredUser } from "@/services/authService";

export default function ResultsPage() {
  const router = useRouter();
  const [results, setResults]       = useState<AssessmentResult[]>([]);
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState<string | null>(null);
  const [expanded, setExpanded]     = useState<string | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) { router.replace("/login"); return; }
    const user = getStoredUser();
    if (!user?.id) { setLoading(false); return; }

    getCandidateResults(user.id)
      .then(setResults)
      .catch((err) => setError(err?.message ?? "Failed to load results"))
      .finally(() => setLoading(false));
  }, [router]);

  function formatDate(iso: string | null | undefined) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleString("en-IN", {
        day: "numeric", month: "short", year: "numeric",
        hour: "2-digit", minute: "2-digit",
      });
    } catch { return "—"; }
  }

  function formatDuration(seconds: number) {
    if (!seconds) return "—";
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return m > 0 ? `${m}m ${s}s` : `${s}s`;
  }

  /** Derive meaningful assessment type label from which section scores are populated */
  function getAssessmentTypeLabel(r: AssessmentResult): string {
    const hasApt  = (r.aptitudeScore  ?? 0) > 0;
    const hasTech = (r.technicalScore ?? 0) > 0;
    const hasCode = (r.codingScore    ?? 0) > 0;
    const count   = [hasApt, hasTech, hasCode].filter(Boolean).length;
    if (count >= 2) return "Full Assessment";
    if (hasApt)    return "Aptitude Assessment";
    if (hasTech)   return "Technical Assessment";
    if (hasCode)   return "Coding Assessment";
    return "Assessment";
  }

  function toggleExpand(id: string) {
    setExpanded((prev) => (prev === id ? null : id));
  }

  // Aggregate stats
  const completed = results.length;
  const avgPct    = completed > 0 ? Math.round(results.reduce((s, r) => s + (r.percentage ?? 0), 0) / completed) : 0;
  const passed    = results.filter((r) => (r.percentage ?? 0) >= 40).length;

  const summaryCards = [
    { label: "Completed",     value: completed,     icon: Trophy },
    { label: "Average Score", value: `${avgPct}%`,  icon: BarChart3 },
    { label: "Passed",        value: passed,        icon: CheckCircle2 },
  ];

  return (
    <AppShell title="Results" subtitle="Your assessment history">
      <div className="max-w-4xl mx-auto space-y-6">

        {/* Summary strip */}
        {!loading && !error && results.length > 0 && (
          <div className="grid grid-cols-3 gap-4">
            {summaryCards.map((card) => (
              <div
                key={card.label}
                className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl px-4 py-4 flex items-center gap-3 hover:shadow-sm transition-all duration-200 card-accent-blue"
              >
                <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 icon-bg-blue">
                  <card.icon size={17} className="text-[#4096ff]" />
                </div>
                <div>
                  <p className="text-[11px] text-[#64748B] font-semibold uppercase tracking-wide mb-0.5">{card.label}</p>
                  <p className="text-[24px] font-extrabold text-[#1E293B] leading-none">{card.value}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Content */}
        {loading ? (
          <LoadingState message="Loading your results…" />
        ) : error ? (
          <ErrorState message={error} onRetry={() => { setLoading(true); setError(null); }} />
        ) : results.length === 0 ? (
          <EmptyState
            icon={<Trophy size={26} />}
            title="No results yet"
            description="Complete an assessment to see your results here."
            action={{ label: "Go to Assessments", onClick: () => router.push("/assessments") }}
          />
        ) : (
          <div className="space-y-3">
            {results.map((r, idx) => {
              const pct     = Math.round(r.percentage ?? 0);
              const isOpen  = expanded === r.id;
              const isPassed = pct >= 40;

              return (
                <div
                  key={r.id ?? idx}
                  className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl overflow-hidden transition-all duration-200 hover:shadow-sm card-accent-blue"
                >
                  {/* Row header */}
                  <button
                    onClick={() => toggleExpand(r.id)}
                    className="w-full flex items-center justify-between px-5 py-4 hover:bg-[#F8FAFC] transition-colors text-left gap-4"
                  >
                    {/* Left: index + score ring */}
                    <div className="flex items-center gap-4">
                      <div className="text-[11px] font-bold text-white w-7 h-7 rounded-full flex items-center justify-center shrink-0 bg-[#1E293B]">
                        {idx + 1}
                      </div>
                      <ScoreRing percentage={pct} size={52} />
                      <div>
                        <p className="text-[13.5px] font-bold text-[#1E293B]">
                          {getAssessmentTypeLabel(r)}
                        </p>
                        <p className="text-[11px] text-[#94A3B8] flex items-center gap-1.5 mt-0.5">
                          <Clock size={10} />
                          {formatDate(r.createdAt)}
                        </p>
                      </div>
                    </div>

                    {/* Right: stats + badge */}
                    <div className="flex items-center gap-4 shrink-0">
                      <div className="hidden sm:flex items-center gap-6 text-center">
                        <div>
                          <p className="text-[10px] text-[#94A3B8] font-medium">Correct</p>
                          <p className="text-[14px] font-extrabold text-[#1E293B]">{r.correctAnswers}/{r.totalQuestions}</p>
                        </div>
                        <div>
                          <p className="text-[10px] text-[#94A3B8] font-medium">Time</p>
                          <p className="text-[14px] font-extrabold text-[#1E293B]">{formatDuration(r.totalTime)}</p>
                        </div>
                      </div>
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold bg-[#4096ff]/10 text-[#4096ff] border border-[#4096ff]/20">
                        {isPassed ? <CheckCircle2 size={11} /> : <XCircle size={11} />}
                        {r.status}
                      </span>
                      {isOpen ? <ChevronUp size={16} className="text-[#94A3B8]" /> : <ChevronDown size={16} className="text-[#94A3B8]" />}
                    </div>
                  </button>

                  {/* Expanded detail */}
                  {isOpen && (
                    <div className="animate-fade-in-up" style={{ borderTop: "1px solid rgba(30,41,59,0.07)" }}>
                      <div className="px-5 py-5 space-y-5">
                        {/* Score breakdown */}
                        <div>
                          <p className="text-[10.5px] font-bold text-[#64748B] uppercase tracking-widest mb-3">Score Breakdown</p>
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                            <ResultCard label="Aptitude Score"  value={`${r.aptitudeScore ?? 0}`}  />
                            <ResultCard label="Technical Score" value={`${r.technicalScore ?? 0}`} />
                            <ResultCard label="Coding Score"    value={`${r.codingScore ?? 0}`}    />
                            <ResultCard label="Total Score"     value={`${Math.round(r.percentage ?? 0)}%`} accent />
                          </div>
                        </div>

                        {/* Question summary */}
                        <div>
                          <p className="text-[10.5px] font-bold text-[#64748B] uppercase tracking-widest mb-3">Question Summary</p>
                          <div className="grid grid-cols-3 gap-3">
                            {[
                              { icon: CheckCircle2, label: "Correct",    value: r.correctAnswers },
                              { icon: XCircle,      label: "Wrong",      value: r.wrongAnswers },
                              { icon: Minus,        label: "Unanswered", value: r.unansweredQuestions },
                            ].map((stat) => (
                              <div key={stat.label} className="rounded-xl p-3.5 flex items-center gap-3 bg-[#F1F5F9] border border-[rgba(30,41,59,0.08)]">
                                <stat.icon size={16} className="text-[#4096ff]" />
                                <div>
                                  <p className="text-[10px] text-[#64748B] font-semibold">{stat.label}</p>
                                  <p className="text-[18px] font-extrabold text-[#1E293B]">{stat.value ?? 0}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Skill highlights */}
                        {(r.strongestSkill || r.weakestSkill || r.recommendation) && (
                          <div className="grid sm:grid-cols-2 gap-3">
                            {r.strongestSkill && (
                              <div className="rounded-xl px-4 py-3 bg-[#4096ff]/10 border border-[#4096ff]/20">
                                <p className="text-[10.5px] font-bold text-[#4096ff] uppercase tracking-widest mb-1">Strongest Skill</p>
                                <p className="text-[13.5px] font-bold text-[#1E293B]">{r.strongestSkill}</p>
                              </div>
                            )}
                            {r.weakestSkill && (
                              <div className="rounded-xl px-4 py-3 bg-[#1E293B]/10 border border-[#1E293B]/20">
                                <p className="text-[10.5px] font-bold text-[#1E293B] uppercase tracking-widest mb-1">Weakest Skill</p>
                                <p className="text-[13.5px] font-bold text-[#1E293B]">{r.weakestSkill}</p>
                              </div>
                            )}
                            {r.recommendation && (
                              <div className="sm:col-span-2 rounded-xl px-4 py-3 bg-[#4096ff]/10 border border-[#4096ff]/20">
                                <p className="text-[10.5px] font-bold text-[#4096ff] uppercase tracking-widest mb-1">Recommendation</p>
                                <p className="text-[13px] text-[#1E293B]">{r.recommendation}</p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AppShell>
  );
}
