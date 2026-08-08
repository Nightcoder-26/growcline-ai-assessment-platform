"use client";

/**
 * /analytics — Analytics Dashboard
 * Shows candidate performance analytics from the Team A backend.
 * No fake data — real empty state when no data available.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  BarChart3, TrendingUp, Target, CheckCircle2,
  XCircle, Minus, Brain, BookOpen, Code2,
} from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import { EmptyState, LoadingState, ErrorState } from "@/components/assessment/shared";
import {
  getCandidateAnalytics,
  getSkillAnalysis,
  type CandidateAnalytics,
  type SkillAnalysis,
} from "@/services/assessmentService";
import { getStoredToken, getStoredUser } from "@/services/authService";

// ─── CSS-only bar chart bar ───────────────────────────────────────────────────

function BarChartBar({ label, value, max, icon: Icon }: {
  label: string; value: number; max: number; icon: React.ElementType;
}) {
  const pct = max > 0 ? Math.max(0, Math.min(100, (value / max) * 100)) : 0;
  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 w-36 shrink-0">
        <div className="w-6 h-6 rounded-lg bg-[#4096ff]/08 flex items-center justify-center">
          <Icon size={13} className="text-[#4096ff]" />
        </div>
        <span className="text-[12.5px] font-medium text-[#374151] truncate">{label}</span>
      </div>
      <div className="flex-1 h-2 bg-[#F1F5F9] rounded-full overflow-hidden">
        <div
          className="h-full bg-[#4096ff] rounded-full transition-all duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[12.5px] font-semibold text-[#1E293B] w-10 text-right">
        {Math.round(value)}
      </span>
    </div>
  );
}

// ─── Stat card ────────────────────────────────────────────────────────────────

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4">
      <p className="text-[11.5px] text-[#64748B] font-medium mb-1">{label}</p>
      <p className="text-[26px] font-bold text-[#1E293B] leading-none">{value}</p>
      {sub && <p className="text-[11px] text-[#94A3B8] mt-1">{sub}</p>}
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function AnalyticsPage() {
  const router = useRouter();
  const [analytics, setAnalytics]   = useState<CandidateAnalytics[]>([]);
  const [skills, setSkills]         = useState<SkillAnalysis>({});
  const [loading, setLoading]       = useState(true);
  const [error, setError]           = useState<string | null>(null);

  async function fetchData() {
    const user = getStoredUser();
    if (!user?.id) { setLoading(false); return; }
    try {
      setLoading(true);
      setError(null);
      const [analyticsData, skillData] = await Promise.all([
        getCandidateAnalytics(user.id),
        getSkillAnalysis(user.id),
      ]);
      setAnalytics(analyticsData);
      setSkills(skillData);
    } catch (err: unknown) {
      setError((err as Error)?.message ?? "Failed to load analytics.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const token = getStoredToken();
    if (!token) { router.replace("/login"); return; }
    fetchData();
  }, [router]);

  // ── Derived metrics from analytics array
  const total = analytics.length;
  const avgPct = total > 0
    ? Math.round(analytics.reduce((s, a) => s + (a.percentage ?? 0), 0) / total)
    : 0;
  const avgApt = total > 0
    ? Math.round(analytics.reduce((s, a) => s + (a.aptitudeScore ?? 0), 0) / total)
    : 0;
  const avgTech = total > 0
    ? Math.round(analytics.reduce((s, a) => s + (a.technicalScore ?? 0), 0) / total)
    : 0;
  const avgCode = total > 0
    ? Math.round(analytics.reduce((s, a) => s + (a.codingScore ?? 0), 0) / total)
    : 0;
  const totalCorrect    = analytics.reduce((s, a) => s + (a.correctAnswers ?? 0), 0);
  const totalWrong      = analytics.reduce((s, a) => s + (a.wrongAnswers ?? 0), 0);
  const totalUnanswered = analytics.reduce((s, a) => s + (a.unansweredQuestions ?? 0), 0);

  const strongestSkill = (skills?.strongestSkill as string) ??
    (analytics[0]?.strongestSkill ?? null);
  const weakestSkill   = (skills?.weakestSkill as string) ??
    (analytics[0]?.weakestSkill ?? null);

  // Best score across all attempts
  const bestPct = analytics.length > 0
    ? Math.round(Math.max(...analytics.map((a) => a.percentage ?? 0)))
    : 0;

  const maxScore = Math.max(avgApt, avgTech, avgCode, 1);

  return (
    <AppShell title="Analytics" subtitle="Your performance overview">
      <div className="max-w-5xl mx-auto space-y-6">

        {loading ? (
          <LoadingState message="Loading your analytics…" />
        ) : error ? (
          <ErrorState message={error} onRetry={fetchData} />
        ) : analytics.length === 0 ? (
          <EmptyState
            icon={<BarChart3 size={24} />}
            title="No assessment data available yet"
            description="Complete at least one assessment to see your performance analytics and trends here."
            action={{ label: "Take an Assessment", onClick: () => router.push("/assessments") }}
          />
        ) : (
          <>
            {/* ── Overall Stats ──────────────────────────────────────── */}
            <section>
              <h2 className="text-[13.5px] font-semibold text-[#64748B] uppercase tracking-wide mb-3">Overall Performance</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <StatCard label="Assessments"   value={total}      sub="total attempts"       />
                <StatCard label="Average Score"  value={`${avgPct}%`} sub="across all tests" />
                <StatCard label="Best Score"     value={`${bestPct}%`} sub="personal best"   />
                <StatCard label="Avg Accuracy"   value={
                  totalCorrect + totalWrong + totalUnanswered > 0
                    ? `${Math.round((totalCorrect / (totalCorrect + totalWrong + totalUnanswered)) * 100)}%`
                    : "—"
                } sub="correct answers" />
              </div>
            </section>

            {/* ── Assessment Performance breakdown ───────────────────── */}
            <div className="grid lg:grid-cols-2 gap-5">
              {/* Score by category */}
              <section className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5">
                <h2 className="text-[13.5px] font-semibold text-[#1E293B] mb-4">Average Score by Category</h2>
                <div className="space-y-4">
                  <BarChartBar label="Aptitude"  value={avgApt}  max={maxScore} icon={Brain}    />
                  <BarChartBar label="Technical" value={avgTech} max={maxScore} icon={BookOpen}  />
                  <BarChartBar label="Coding"    value={avgCode} max={maxScore} icon={Code2}     />
                </div>
              </section>

              {/* Answer distribution */}
              <section className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5">
                <h2 className="text-[13.5px] font-semibold text-[#1E293B] mb-4">Answer Distribution</h2>
                <div className="space-y-3">
                  {[
                    { icon: CheckCircle2, color: "text-[#15803D]", bg: "bg-[#F0FDF4]", bar: "bg-[#4096ff]", label: "Correct",    count: totalCorrect,    total: totalCorrect + totalWrong + totalUnanswered },
                    { icon: XCircle,      color: "text-[#B91C1C]", bg: "bg-[#FEF2F2]", bar: "bg-[#1E293B]", label: "Wrong",      count: totalWrong,      total: totalCorrect + totalWrong + totalUnanswered },
                    { icon: Minus,        color: "text-[#64748B]", bg: "bg-[#F1F5F9]", bar: "bg-[#CBD5E1]", label: "Unanswered", count: totalUnanswered, total: totalCorrect + totalWrong + totalUnanswered },
                  ].map((stat) => {
                    const pct = stat.total > 0 ? Math.round((stat.count / stat.total) * 100) : 0;
                    return (
                      <div key={stat.label} className="flex items-center gap-3">
                        <div className={`w-6 h-6 rounded-lg ${stat.bg} flex items-center justify-center shrink-0`}>
                          <stat.icon size={12} className={stat.color} />
                        </div>
                        <span className="text-[12.5px] font-medium text-[#374151] w-24 shrink-0">{stat.label}</span>
                        <div className="flex-1 h-2 bg-[#F1F5F9] rounded-full overflow-hidden">
                          <div className={`h-full ${stat.bar} rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-[12px] font-semibold text-[#1E293B] w-12 text-right">{stat.count} <span className="text-[#94A3B8] font-normal">({pct}%)</span></span>
                      </div>
                    );
                  })}
                </div>

                {/* Quick counts */}
                <div className="mt-4 pt-4 border-t border-[rgba(30,41,59,0.06)] grid grid-cols-3 gap-2 text-center">
                  {[
                    { label: "Correct",    value: totalCorrect },
                    { label: "Wrong",      value: totalWrong },
                    { label: "Unanswered", value: totalUnanswered },
                  ].map((s) => (
                    <div key={s.label}>
                      <p className="text-[18px] font-bold text-[#1E293B]">{s.value}</p>
                      <p className="text-[10.5px] text-[#94A3B8]">{s.label}</p>
                    </div>
                  ))}
                </div>
              </section>
            </div>

            {/* ── Skill Highlights ───────────────────────────────────── */}
            {(strongestSkill || weakestSkill) && (
              <section>
                <h2 className="text-[13.5px] font-semibold text-[#64748B] uppercase tracking-wide mb-3">Skill Analysis</h2>
                <div className="grid sm:grid-cols-2 gap-4">
                  {strongestSkill && (
                    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 flex items-start gap-3">
                      <div className="w-9 h-9 rounded-xl bg-[#F0FDF4] flex items-center justify-center shrink-0">
                        <TrendingUp size={16} className="text-[#15803D]" />
                      </div>
                      <div>
                        <p className="text-[11px] font-semibold text-[#64748B] uppercase tracking-wide mb-1">Strongest Area</p>
                        <p className="text-[14.5px] font-bold text-[#1E293B]">{strongestSkill}</p>
                        <p className="text-[12px] text-[#64748B] mt-0.5">Keep reinforcing this skill.</p>
                      </div>
                    </div>
                  )}
                  {weakestSkill && (
                    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 flex items-start gap-3">
                      <div className="w-9 h-9 rounded-xl bg-[#FEF2F2] flex items-center justify-center shrink-0">
                        <Target size={16} className="text-[#B91C1C]" />
                      </div>
                      <div>
                        <p className="text-[11px] font-semibold text-[#64748B] uppercase tracking-wide mb-1">Area to Improve</p>
                        <p className="text-[14.5px] font-bold text-[#1E293B]">{weakestSkill}</p>
                        <p className="text-[12px] text-[#64748B] mt-0.5">Focus on this to improve your overall score.</p>
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* ── Performance Trend (last 5 attempts) ────────────────── */}
            {analytics.length > 1 && (
              <section className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5">
                <h2 className="text-[13.5px] font-semibold text-[#1E293B] mb-4">
                  Recent Performance Trend
                </h2>
                <div className="flex items-end gap-2 h-32">
                  {analytics.slice(-8).map((a, i) => {
                    const pct = Math.round(a.percentage ?? 0);
                    const height = Math.max(8, pct);
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center gap-1.5">
                        <span className="text-[10px] font-semibold text-[#64748B]">{pct}%</span>
                        <div
                          className="w-full rounded-t-md bg-[#4096ff] transition-all duration-500"
                          style={{ height: `${height}%` }}
                          title={`Attempt ${i + 1}: ${pct}%`}
                        />
                        <span className="text-[10px] text-[#94A3B8]">#{i + 1}</span>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {/* ── Recommendation ─────────────────────────────────────── */}
            {analytics[0]?.recommendation && (
              <section className="bg-[#EFF6FF] border border-[#4096ff]/15 rounded-xl px-5 py-4">
                <p className="text-[11px] font-semibold text-[#4096ff] uppercase tracking-wide mb-2">Recommendation</p>
                <p className="text-[13.5px] text-[#1E293B] leading-relaxed">{analytics[0].recommendation}</p>
              </section>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}
