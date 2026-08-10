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
  XCircle, Minus, Brain, BookOpen, Code2, Trophy, Zap,
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

// ─── Category bar ─────────────────────────────────────────────────────────────

function CategoryBar({ label, value, max, icon: Icon }: {
  label: string; value: number; max: number; icon: React.ElementType;
}) {
  const [animated, setAnimated] = useState(false);
  const pct = max > 0 ? Math.max(0, Math.min(100, (value / max) * 100)) : 0;

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 200);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 w-36 shrink-0">
        <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 icon-bg-blue">
          <Icon size={13} className="text-[#4096ff]" />
        </div>
        <span className="text-[12.5px] font-semibold text-[#374151] truncate">{label}</span>
      </div>
      <div className="flex-1 h-2.5 bg-[#F1F5F9] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700 bg-[#4096ff]"
          style={{ width: animated ? `${pct}%` : "0%" }}
        />
      </div>
      <span className="text-[13px] font-extrabold text-[#1E293B] w-10 text-right">
        {Math.round(value)}
      </span>
    </div>
  );
}

// ─── Stat card ────────────────────────────────────────────────────────────────

function StatCard({ label, value, sub, icon: Icon }: {
  label: string; value: string | number; sub?: string; icon: React.ElementType;
}) {
  return (
    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4 flex items-start gap-3 hover:shadow-md transition-all duration-200 card-accent-blue">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 icon-bg-blue">
        <Icon size={17} className="text-[#4096ff]" />
      </div>
      <div>
        <p className="text-[11px] text-[#64748B] font-semibold uppercase tracking-wide mb-0.5">{label}</p>
        <p className="text-[24px] font-extrabold text-[#1E293B] leading-none">{value}</p>
        {sub && <p className="text-[11px] text-[#94A3B8] mt-0.5">{sub}</p>}
      </div>
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

  const bestPct = analytics.length > 0
    ? Math.round(Math.max(...analytics.map((a) => a.percentage ?? 0)))
    : 0;

  const totalQs = totalCorrect + totalWrong + totalUnanswered;
  const accuracy = totalQs > 0 ? Math.round((totalCorrect / totalQs) * 100) : 0;

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
            icon={<BarChart3 size={26} />}
            title="No assessment data available yet"
            description="Complete at least one assessment to see your performance analytics and trends here."
            action={{ label: "Take an Assessment", onClick: () => router.push("/assessments") }}
          />
        ) : (
          <>
            {/* ── Overall Stats ──────────────────────────────────────── */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-1 h-5 rounded-full bg-[#4096ff]" />
                <h2 className="text-[14px] font-bold text-[#1E293B]">Overall Performance</h2>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <StatCard label="Assessments"   value={total}          sub="total attempts"    icon={Trophy}    />
                <StatCard label="Average Score"  value={`${avgPct}%`}   sub="across all tests"  icon={BarChart3} />
                <StatCard label="Best Score"     value={`${bestPct}%`}  sub="personal best"     icon={Zap}       />
                <StatCard label="Avg Accuracy"   value={`${accuracy}%`} sub="correct answers"   icon={Target}    />
              </div>
            </section>

            {/* ── Assessment Performance breakdown ───────────────────── */}
            <div className="grid lg:grid-cols-2 gap-5">
              {/* Score by category */}
              <section className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 shadow-sm card-accent-blue">
                <div className="flex items-center gap-2 mb-5">
                  <div className="w-1 h-4 rounded-full bg-[#4096ff]" />
                  <h2 className="text-[13.5px] font-bold text-[#1E293B]">Average Score by Category</h2>
                </div>
                <div className="space-y-4">
                  <CategoryBar label="Aptitude"  value={avgApt}  max={maxScore} icon={Brain}    />
                  <CategoryBar label="Technical" value={avgTech} max={maxScore} icon={BookOpen}  />
                  <CategoryBar label="Coding"    value={avgCode} max={maxScore} icon={Code2}     />
                </div>
              </section>

              {/* Answer distribution */}
              <section className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 shadow-sm card-accent-blue">
                <div className="flex items-center gap-2 mb-5">
                  <div className="w-1 h-4 rounded-full bg-[#4096ff]" />
                  <h2 className="text-[13.5px] font-bold text-[#1E293B]">Answer Distribution</h2>
                </div>
                <div className="space-y-3">
                  {[
                    { icon: CheckCircle2, label: "Correct",    count: totalCorrect,    total: totalQs },
                    { icon: XCircle,      label: "Wrong",      count: totalWrong,      total: totalQs },
                    { icon: Minus,        label: "Unanswered", count: totalUnanswered, total: totalQs },
                  ].map((stat) => {
                    const pct = stat.total > 0 ? Math.round((stat.count / stat.total) * 100) : 0;
                    return (
                      <div key={stat.label} className="flex items-center gap-3">
                        <div className="w-6 h-6 rounded-lg flex items-center justify-center shrink-0 icon-bg-blue">
                          <stat.icon size={12} className="text-[#4096ff]" />
                        </div>
                        <span className="text-[12.5px] font-semibold text-[#374151] w-24 shrink-0">{stat.label}</span>
                        <div className="flex-1 h-2.5 bg-[#F1F5F9] rounded-full overflow-hidden">
                          <div className="h-full bg-[#4096ff] rounded-full transition-all duration-700"
                            style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-[12px] font-bold text-[#1E293B] w-16 text-right">
                          {stat.count} <span className="text-[#94A3B8] font-normal">({pct}%)</span>
                        </span>
                      </div>
                    );
                  })}
                </div>

                {/* Quick counts */}
                <div className="mt-5 pt-4 grid grid-cols-3 gap-2 text-center" style={{ borderTop: "1px solid rgba(30,41,59,0.06)" }}>
                  {[
                    { label: "Correct",    value: totalCorrect },
                    { label: "Wrong",      value: totalWrong },
                    { label: "Unanswered", value: totalUnanswered },
                  ].map((s) => (
                    <div key={s.label}>
                      <p className="text-[20px] font-extrabold text-[#1E293B]">{s.value}</p>
                      <p className="text-[10.5px] text-[#94A3B8] font-medium">{s.label}</p>
                    </div>
                  ))}
                </div>
              </section>
            </div>

            {/* ── Skill Highlights ───────────────────────────────────── */}
            {(strongestSkill || weakestSkill) && (
              <section>
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-1 h-5 rounded-full bg-[#4096ff]" />
                  <h2 className="text-[14px] font-bold text-[#1E293B]">Skill Analysis</h2>
                </div>
                <div className="grid sm:grid-cols-2 gap-4">
                  {strongestSkill && (
                    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 flex items-start gap-3 hover:shadow-sm transition-all card-accent-blue">
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 icon-bg-blue">
                        <TrendingUp size={17} className="text-[#4096ff]" />
                      </div>
                      <div>
                        <p className="text-[10.5px] font-bold text-[#4096ff] uppercase tracking-widest mb-1">Strongest Area</p>
                        <p className="text-[14.5px] font-extrabold text-[#1E293B]">{strongestSkill}</p>
                        <p className="text-[12px] text-[#64748B] mt-0.5">Keep reinforcing this skill.</p>
                      </div>
                    </div>
                  )}
                  {weakestSkill && (
                    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 flex items-start gap-3 hover:shadow-sm transition-all card-accent-blue">
                      <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 icon-bg-blue">
                        <Target size={17} className="text-[#4096ff]" />
                      </div>
                      <div>
                        <p className="text-[10.5px] font-bold text-[#4096ff] uppercase tracking-widest mb-1">Area to Improve</p>
                        <p className="text-[14.5px] font-extrabold text-[#1E293B]">{weakestSkill}</p>
                        <p className="text-[12px] text-[#64748B] mt-0.5">Focus on this to improve your overall score.</p>
                      </div>
                    </div>
                  )}
                </div>
              </section>
            )}

            {/* ── Performance Trend (last 8 attempts) ────────────────── */}
            {analytics.length > 1 && (
              <section className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 shadow-sm">
                <div className="flex items-center gap-2 mb-5">
                  <div className="w-1 h-4 rounded-full bg-[#4096ff]" />
                  <h2 className="text-[13.5px] font-bold text-[#1E293B]">
                    Recent Performance Trend
                  </h2>
                </div>
                <div className="flex items-end gap-2 h-36">
                  {analytics.slice(-8).map((a, i) => {
                    const pct = Math.round(a.percentage ?? 0);
                    const height = Math.max(8, pct);
                    return (
                      <div key={i} className="flex-1 flex flex-col items-center gap-1.5">
                        <span className="text-[10px] font-bold text-[#4096ff]">{pct}%</span>
                        <div
                          className="w-full rounded-t-lg transition-all duration-700 bg-[#4096ff]"
                          style={{
                            height: `${height}%`,
                            boxShadow: "0 2px 6px rgba(64,150,255,0.3)",
                          }}
                          title={`Attempt ${i + 1}: ${pct}%`}
                        />
                        <span className="text-[10px] text-[#94A3B8] font-medium">#{i + 1}</span>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {/* ── Recommendation ─────────────────────────────────────── */}
            {analytics[0]?.recommendation && (
              <section className="rounded-xl px-5 py-4 bg-[#4096ff]/10 border border-[#4096ff]/20">
                <p className="text-[10.5px] font-bold text-[#4096ff] uppercase tracking-widest mb-2">Recommendation</p>
                <p className="text-[13.5px] text-[#1E293B] leading-relaxed">{analytics[0].recommendation}</p>
              </section>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}
