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
}

const CATEGORIES: AssessmentCategory[] = [
  {
    key:         "aptitude",
    label:       "Aptitude Assessment",
    description: "Quantitative ability, logical reasoning, and verbal aptitude questions.",
    icon:        BrainCircuit,
    href:        "/assessments/aptitude",
    color:       "#4096ff",
  },
  {
    key:         "technical",
    label:       "Technical Assessment",
    description: "Technology-specific MCQs and scenario-based technical questions.",
    icon:        BookOpen,
    href:        "/assessments/technical",
    color:       "#4096ff",
  },
  {
    key:         "coding",
    label:       "Coding Assessment",
    description: "Algorithmic problem-solving with a built-in code editor and test cases.",
    icon:        Code2,
    href:        "/assessments/coding",
    color:       "#4096ff",
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
    if (s === "passed") return <span className="inline-flex items-center gap-1 text-[11px] font-medium text-[#15803D] bg-[#F0FDF4] border border-[#86EFAC]/50 px-2 py-0.5 rounded-full"><CheckCircle2 size={10} />Passed</span>;
    if (s === "failed") return <span className="inline-flex items-center gap-1 text-[11px] font-medium text-[#B91C1C] bg-[#FEF2F2] border border-[#FECACA]/50 px-2 py-0.5 rounded-full"><AlertCircle size={10} />Failed</span>;
    return <span className="inline-flex text-[11px] font-medium text-[#64748B] bg-[#F1F5F9] px-2 py-0.5 rounded-full">{status}</span>;
  }

  return (
    <AppShell
      title={`Welcome back, ${firstName}`}
      subtitle="Your assessment dashboard"
    >
      <div className="max-w-5xl mx-auto space-y-7">

        {/* ── Welcome Banner ──────────────────────────────────────── */}
        <div className="bg-[#1E293B] rounded-2xl px-7 py-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-[20px] font-bold text-white tracking-tight mb-1">
              Good to see you, {firstName} 👋
            </h2>
            <p className="text-[13px] text-[#94A3B8]">
              Track your progress across assessments and sharpen your skills.
            </p>
          </div>
          <Link
            href="/assessments"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[13.5px] font-semibold transition-all shrink-0 shadow-[0_4px_14px_rgba(64,150,255,0.35)]"
          >
            Start Assessment <ArrowRight size={14} />
          </Link>
        </div>

        {/* ── Performance Snapshot ─────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
          {[
            {
              icon: Trophy,
              label: "Assessments Done",
              value: loading ? "—" : completed.toString(),
              sub: "completed",
            },
            {
              icon: TrendingUp,
              label: "Average Score",
              value: loading ? "—" : avgScore !== null ? `${avgScore}%` : "—",
              sub: "across all tests",
            },
            {
              icon: Target,
              label: "Last Result",
              value: loading ? "—" : recentResult ? `${Math.round(recentResult.percentage)}%` : "—",
              sub: recentResult ? formatDate(recentResult.createdAt) : "No attempts yet",
            },
          ].map((stat) => (
            <div
              key={stat.label}
              className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4 flex items-start gap-3"
            >
              <div className="w-9 h-9 rounded-xl bg-[#4096ff]/08 border border-[#4096ff]/15 flex items-center justify-center shrink-0">
                <stat.icon size={16} className="text-[#4096ff]" />
              </div>
              <div>
                <p className="text-[11.5px] text-[#64748B] font-medium mb-0.5">{stat.label}</p>
                <p className="text-[22px] font-bold text-[#1E293B] leading-none">{stat.value}</p>
                <p className="text-[11px] text-[#94A3B8] mt-0.5">{stat.sub}</p>
              </div>
            </div>
          ))}
        </div>

        {/* ── Assessment Categories ─────────────────────────────────── */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-[15px] font-semibold text-[#1E293B]">Assessments</h2>
            <Link href="/assessments" className="text-[13px] text-[#4096ff] hover:text-[#60a5fa] font-medium transition-colors flex items-center gap-1">
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
                  className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 flex flex-col gap-3 hover:border-[#4096ff]/30 hover:shadow-[0_4px_20px_rgba(64,150,255,0.08)] transition-all duration-200 group"
                >
                  <div className="w-10 h-10 rounded-xl bg-[#4096ff]/08 border border-[#4096ff]/15 flex items-center justify-center">
                    <Icon size={18} className="text-[#4096ff]" />
                  </div>
                  <div>
                    <h3 className="text-[13.5px] font-semibold text-[#1E293B] leading-tight mb-1.5">
                      {cat.label}
                    </h3>
                    <p className="text-[12px] text-[#64748B] leading-relaxed">{cat.description}</p>
                  </div>
                  <div className="flex items-center gap-1 text-[#4096ff] text-[12.5px] font-semibold mt-auto group-hover:gap-2 transition-all">
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
            <div className="flex items-center justify-between px-5 py-4 border-b border-[rgba(30,41,59,0.08)]">
              <h2 className="text-[14px] font-semibold text-[#1E293B]">Recent Results</h2>
              <Link href="/results" className="text-[12.5px] text-[#4096ff] hover:text-[#60a5fa] font-medium transition-colors">
                View all
              </Link>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-10 gap-2 text-[#64748B]">
                <Loader2 size={16} className="animate-spin" />
                <span className="text-[13px]">Loading results…</span>
              </div>
            ) : error ? (
              <div className="py-8 text-center text-[13px] text-[#64748B]">
                Unable to load results at this time.
              </div>
            ) : results.length === 0 ? (
              <div className="py-10 text-center">
                <Trophy size={28} className="text-[#E2E8F0] mx-auto mb-3" />
                <p className="text-[13px] font-medium text-[#94A3B8]">No assessments completed yet</p>
                <p className="text-[12px] text-[#CBD5E1] mt-1">Complete an assessment to see results here.</p>
              </div>
            ) : (
              <div className="divide-y divide-[rgba(30,41,59,0.06)]">
                {results.map((r) => (
                  <div key={r.id} className="flex items-center justify-between px-5 py-3.5 hover:bg-[#F8FAFC] transition-colors">
                    <div className="flex-1 min-w-0">
                      <p className="text-[13px] font-medium text-[#1E293B] truncate">
                        Assessment Result
                      </p>
                      <p className="text-[11.5px] text-[#94A3B8] mt-0.5 flex items-center gap-1.5">
                        <Clock size={10} />
                        {formatDate(r.createdAt)}
                      </p>
                    </div>
                    <div className="flex items-center gap-3 shrink-0 ml-3">
                      <div className="text-right">
                        <p className="text-[15px] font-bold text-[#1E293B]">{Math.round(r.percentage)}%</p>
                        <p className="text-[10.5px] text-[#94A3B8]">{r.correctAnswers}/{r.totalQuestions} correct</p>
                      </div>
                      {statusBadge(r.status)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* AI Interview CTA */}
          <div className="bg-[#1E293B] rounded-xl p-5 flex flex-col gap-4">
            <div className="w-11 h-11 rounded-xl bg-white/10 flex items-center justify-center">
              <Video size={20} className="text-[#4096ff]" />
            </div>
            <div>
              <h3 className="text-[15px] font-semibold text-white mb-1.5">AI Mock Interview</h3>
              <p className="text-[12.5px] text-[#94A3B8] leading-relaxed">
                Practice with an AI interviewer. Get live proctoring, recording, and instant feedback.
              </p>
            </div>
            <Link
              href="/video-recording"
              className="mt-auto flex items-center justify-center gap-2 h-[40px] rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[13px] font-semibold transition-all shadow-[0_4px_14px_rgba(64,150,255,0.3)]"
            >
              Start Interview <ArrowRight size={13} />
            </Link>
            <Link
              href="/interview-analytics"
              className="flex items-center justify-center gap-1.5 text-[12px] text-[#94A3B8] hover:text-white transition-colors"
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
