"use client";

/**
 * /dashboard — Authenticated Candidate Home
 *
 * Shows: welcome, 3 assessment entry points, recent results,
 * performance snapshot, and AI Interview CTA → Team B.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  BrainCircuit, Code2, BookOpen, Video,
  ArrowRight, Trophy, TrendingUp, Target,
  Loader2, Clock, CheckCircle2, AlertCircle,
  Sparkles, Zap, Star,
} from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import DashboardGuideBanner from "@/components/assessment/DashboardGuideBanner";
import { getCandidateResults, type AssessmentResult } from "@/services/assessmentService";
import { getStoredUser, getStoredToken } from "@/services/authService";

// ─── Types ───────────────────────────────────────────────────────────────────

interface AssessmentCategory {
  key: "aptitude" | "technical" | "coding";
  label: string;
  description: string;
  icon: React.ElementType;
  href: string;
  color: string;
  iconBg: string;
  accent: string;
}

const CATEGORIES: AssessmentCategory[] = [
  {
    key:         "aptitude",
    label:       "Aptitude Assessment",
    description: "Quantitative ability, logical reasoning, and verbal aptitude questions.",
    icon:        BrainCircuit,
    href:        "/assessments/aptitude",
    color:       "#4096ff",
    iconBg:      "linear-gradient(135deg, rgba(64,150,255,0.18), rgba(64,150,255,0.06))",
    accent:      "card-accent-blue",
  },
  {
    key:         "technical",
    label:       "Technical Assessment",
    description: "Technology-specific MCQs and scenario-based technical questions.",
    icon:        BookOpen,
    href:        "/assessments/technical",
    color:       "#a855f7",
    iconBg:      "linear-gradient(135deg, rgba(168,85,247,0.18), rgba(168,85,247,0.06))",
    accent:      "card-accent-purple",
  },
  {
    key:         "coding",
    label:       "Coding Assessment",
    description: "Algorithmic problem-solving with a built-in code editor and test cases.",
    icon:        Code2,
    href:        "/assessments/coding",
    color:       "#10b981",
    iconBg:      "linear-gradient(135deg, rgba(16,185,129,0.18), rgba(16,185,129,0.06))",
    accent:      "card-accent-emerald",
  },
];

// ─── Component ────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser]       = useState<{ fullName: string; email: string; role: string } | null>(null);
  const [results, setResults] = useState<AssessmentResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  // Auth guard
  useEffect(() => {
    const token = getStoredToken();
    if (!token) { router.replace("/login"); return; }
    const u = getStoredUser();
    setUser(u);
  }, [router]);

  // Load recent results
  useEffect(() => {
    const u = getStoredUser();
    if (!u?.id) { setLoading(false); return; }
    getCandidateResults(u.id)
      .then((data) => setResults(data.slice(0, 5)))
      .catch((err) => setError(err?.message ?? "Failed to load results"))
      .finally(() => setLoading(false));
  }, []);

  const firstName = user?.fullName?.split(" ")[0] ?? "Candidate";

  // Derived stats from results
  const completed = results.length;
  const avgScore  = completed > 0
    ? Math.round(results.reduce((s, r) => s + (r.percentage ?? 0), 0) / completed)
    : null;

  const recentResult = results[0];

  function formatDate(iso: string | null | undefined) {
    if (!iso) return "—";
    try {
      return new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });
    } catch { return "—"; }
  }

  function statusBadge(status: string) {
    const s = (status ?? "").toLowerCase();
    if (s === "passed") return <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#059669] bg-[#ECFDF5] border border-[#6EE7B7]/50 px-2 py-0.5 rounded-full"><CheckCircle2 size={9} />Passed</span>;
    if (s === "failed") return <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#DC2626] bg-[#FEF2F2] border border-[#FECACA]/50 px-2 py-0.5 rounded-full"><AlertCircle size={9} />Failed</span>;
    return <span className="inline-flex text-[11px] font-semibold text-[#64748B] bg-[#F1F5F9] px-2 py-0.5 rounded-full">{status}</span>;
  }

  // Stat cards config
  const statCards = [
    {
      icon: Trophy,
      label: "Assessments Done",
      value: loading ? "—" : completed.toString(),
      sub: "completed",
      iconClass: "text-[#4096ff]",
      iconBg: "icon-bg-blue",
      accent: "card-accent-blue",
    },
    {
      icon: TrendingUp,
      label: "Average Score",
      value: loading ? "—" : avgScore !== null ? `${avgScore}%` : "—",
      sub: "across all tests",
      iconClass: "text-[#a855f7]",
      iconBg: "icon-bg-purple",
      accent: "card-accent-purple",
    },
    {
      icon: Target,
      label: "Last Result",
      value: loading ? "—" : recentResult ? `${Math.round(recentResult.percentage)}%` : "—",
      sub: recentResult ? formatDate(recentResult.createdAt) : "No attempts yet",
      iconClass: "text-[#10b981]",
      iconBg: "icon-bg-emerald",
      accent: "card-accent-emerald",
    },
  ];

  return (
    <AppShell
      title={`Welcome back, ${firstName}`}
      subtitle="Your assessment dashboard"
    >
      <div className="max-w-5xl mx-auto space-y-7">

        {/* ── Welcome Banner ──────────────────────────────────────── */}
        <div
          className="rounded-2xl px-7 py-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative overflow-hidden"
          style={{
            background: "linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #1a2744 100%)",
          }}
        >
          {/* Background decoration */}
          <div className="absolute inset-0 pointer-events-none">
            <div
              className="absolute inset-0 opacity-[0.03]"
              style={{ backgroundImage: "radial-gradient(circle, #fff 1px, transparent 1px)", backgroundSize: "24px 24px" }}
            />
            <div className="absolute top-0 right-0 w-64 h-64 rounded-full opacity-10 blur-3xl"
              style={{ background: "radial-gradient(circle, #4096ff, transparent)" }} />
            <div className="absolute -bottom-8 -left-8 w-48 h-48 rounded-full opacity-8 blur-2xl"
              style={{ background: "radial-gradient(circle, #818cf8, transparent)" }} />
          </div>

          <div className="relative">
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10.5px] font-bold text-[#93C5FD] tracking-wide"
                style={{ background: "rgba(64,150,255,0.15)", border: "1px solid rgba(64,150,255,0.25)" }}>
                <Zap size={10} className="text-[#60a5fa]" />
                AI ASSESSMENT PLATFORM
              </span>
            </div>
            <h2 className="text-[22px] font-extrabold text-white tracking-tight mb-1 leading-tight">
              Good to see you, {firstName} 👋
            </h2>
            <p className="text-[13px] text-[#64748B] leading-relaxed">
              Track your progress across assessments and sharpen your skills.
            </p>
          </div>
          <Link
            href="/assessments"
            className="relative flex items-center gap-2 px-5 py-2.5 rounded-xl text-white text-[13.5px] font-bold transition-all shrink-0"
            style={{
              background: "linear-gradient(135deg, #4096ff 0%, #60a5fa 100%)",
              boxShadow: "0 4px 16px rgba(64,150,255,0.45)",
            }}
          >
            Start Assessment <ArrowRight size={14} />
          </Link>
        </div>

        {/* ── Performance Snapshot ─────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 animate-stagger">
          {statCards.map((stat) => (
            <div
              key={stat.label}
              className={`bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4 flex items-start gap-3 animate-fade-in-up transition-all duration-200 hover:shadow-md ${stat.accent}`}
            >
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${stat.iconBg}`}>
                <stat.icon size={17} className={stat.iconClass} />
              </div>
              <div>
                <p className="text-[11px] text-[#64748B] font-semibold mb-0.5 uppercase tracking-wide">{stat.label}</p>
                <p className="text-[24px] font-extrabold text-[#1E293B] leading-none">{stat.value}</p>
                <p className="text-[11px] text-[#94A3B8] mt-0.5">{stat.sub}</p>
              </div>
            </div>
          ))}
        </div>

        {/* ── Assessment Categories ─────────────────────────────────── */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-1 h-5 rounded-full bg-[#4096ff]" />
              <h2 className="text-[14px] font-bold text-[#1E293B]">Assessments</h2>
            </div>
            <Link href="/assessments" className="text-[12.5px] text-[#4096ff] hover:text-[#60a5fa] font-semibold transition-colors flex items-center gap-1">
              View all <ArrowRight size={12} />
            </Link>
          </div>
          <div className="grid sm:grid-cols-3 gap-4">
            {CATEGORIES.map((cat) => {
              const Icon = cat.icon;
              return (
                <Link
                  key={cat.key}
                  href={cat.href}
                  className={`bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 flex flex-col gap-3 transition-all duration-200 group hover:shadow-lg ${cat.accent}`}
                  style={{ textDecoration: "none" }}
                >
                  <div
                    className="w-11 h-11 rounded-xl flex items-center justify-center transition-transform duration-200 group-hover:scale-110"
                    style={{ background: cat.iconBg, border: `1px solid ${cat.color}30` }}
                  >
                    <Icon size={19} style={{ color: cat.color }} />
                  </div>
                  <div>
                    <h3 className="text-[13.5px] font-bold text-[#1E293B] leading-tight mb-1.5">
                      {cat.label}
                    </h3>
                    <p className="text-[12px] text-[#64748B] leading-relaxed">{cat.description}</p>
                  </div>
                  <div
                    className="flex items-center gap-1 text-[12.5px] font-bold mt-auto group-hover:gap-2 transition-all"
                    style={{ color: cat.color }}
                  >
                    Start <ArrowRight size={12} />
                  </div>
                </Link>
              );
            })}
          </div>
        </section>

        {/* ── Bottom row: Recent Results + Interview CTA ──────────── */}
        <div className="grid lg:grid-cols-3 gap-5">

          {/* Recent Results — takes 2 columns */}
          <div className="lg:col-span-2 bg-white border border-[rgba(30,41,59,0.10)] rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: "1px solid rgba(30,41,59,0.07)" }}>
              <div className="flex items-center gap-2">
                <div className="w-1 h-4 rounded-full bg-[#4096ff]" />
                <h2 className="text-[14px] font-bold text-[#1E293B]">Recent Results</h2>
              </div>
              <Link href="/results" className="text-[12px] text-[#4096ff] hover:text-[#60a5fa] font-semibold transition-colors">
                View all
              </Link>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-10 gap-2 text-[#64748B]">
                <Loader2 size={16} className="animate-spin text-[#4096ff]" />
                <span className="text-[13px]">Loading results…</span>
              </div>
            ) : error ? (
              <div className="py-8 text-center text-[13px] text-[#64748B]">
                Unable to load results at this time.
              </div>
            ) : results.length === 0 ? (
              <div className="py-10 text-center">
                <div className="w-14 h-14 rounded-2xl bg-[#F1F5F9] flex items-center justify-center mx-auto mb-3 animate-float">
                  <Trophy size={24} className="text-[#CBD5E1]" />
                </div>
                <p className="text-[13px] font-semibold text-[#94A3B8]">No assessments completed yet</p>
                <p className="text-[12px] text-[#CBD5E1] mt-1">Complete an assessment to see results here.</p>
              </div>
            ) : (
              <div className="divide-y divide-[rgba(30,41,59,0.05)]">
                {results.map((r) => {
                  const isPassed = (r.percentage ?? 0) >= 40;
                  return (
                    <div key={r.id} className="flex items-center justify-between px-5 py-3.5 hover:bg-[#F8FAFC] transition-colors group"
                      style={{ borderLeft: `3px solid ${isPassed ? "#10b981" : "#f43f5e"}` }}>
                      <div className="flex-1 min-w-0">
                        <p className="text-[13px] font-semibold text-[#1E293B] truncate">
                          Assessment Result
                        </p>
                        <p className="text-[11px] text-[#94A3B8] mt-0.5 flex items-center gap-1.5">
                          <Clock size={10} />
                          {formatDate(r.createdAt)}
                        </p>
                      </div>
                      <div className="flex items-center gap-3 shrink-0 ml-3">
                        <div className="text-right">
                          <p className="text-[16px] font-extrabold text-[#1E293B]">{Math.round(r.percentage)}%</p>
                          <p className="text-[10.5px] text-[#94A3B8]">{r.correctAnswers}/{r.totalQuestions} correct</p>
                        </div>
                        {statusBadge(r.status)}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* AI Interview CTA */}
          <div
            className="rounded-xl p-5 flex flex-col gap-4 relative overflow-hidden"
            style={{
              background: "linear-gradient(160deg, #0F172A 0%, #1E293B 100%)",
              border: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            {/* Background glow */}
            <div className="absolute top-0 right-0 w-32 h-32 rounded-full opacity-10 blur-2xl pointer-events-none"
              style={{ background: "radial-gradient(circle, #4096ff, transparent)" }} />

            <div className="relative flex items-center gap-3">
              <div
                className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
                style={{ background: "linear-gradient(135deg, rgba(64,150,255,0.25), rgba(64,150,255,0.08))", border: "1px solid rgba(64,150,255,0.3)" }}
              >
                <Video size={20} className="text-[#60a5fa]" />
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse-dot" />
                <span className="text-[11px] font-semibold text-[#10b981]">Live Proctoring</span>
              </div>
            </div>

            <div className="relative">
              <h3 className="text-[16px] font-bold text-white mb-1.5">AI Mock Interview</h3>
              <p className="text-[12.5px] text-[#64748B] leading-relaxed">
                Practice with an AI interviewer. Get live proctoring, recording, and instant feedback.
              </p>
            </div>

            <Link
              href="/video-recording"
              className="relative mt-auto flex items-center justify-center gap-2 h-[42px] rounded-xl text-white text-[13px] font-bold transition-all"
              style={{
                background: "linear-gradient(135deg, #4096ff 0%, #60a5fa 100%)",
                boxShadow: "0 4px 14px rgba(64,150,255,0.4)",
              }}
            >
              Start Interview <ArrowRight size={13} />
            </Link>
            <Link
              href="/interview-analytics"
              className="flex items-center justify-center gap-1.5 text-[12px] text-[#475569] hover:text-white transition-colors"
            >
              View interview analytics <ArrowRight size={11} />
            </Link>
          </div>

        </div>

        {/* ── Platform Guide & How-To Showcase Banner ─────────── */}
        <DashboardGuideBanner />
      </div>
    </AppShell>
  );
}
