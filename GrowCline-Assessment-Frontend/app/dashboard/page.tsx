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
  Zap, Sparkles, FileCheck, Upload
} from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import DashboardGuideBanner from "@/components/assessment/DashboardGuideBanner";
import { getCandidateResults, type AssessmentResult } from "@/services/assessmentService";
import { getStoredUser, getStoredToken } from "@/services/authService";
import { getResumeStatus, type ResumeStatus, getSkillProfile, type SkillProfile } from "@/services/resumeService";
import { StatusBadge, ResumeSkillTags } from "@/components/assessment/shared";

// ─── Types ───────────────────────────────────────────────────────────────────

interface AssessmentCategory {
  key: "aptitude" | "technical" | "coding";
  label: string;
  description: string;
  icon: React.ElementType;
  href: string;
  badge?: string;
}

const CATEGORIES: AssessmentCategory[] = [
  {
    key:         "aptitude",
    label:       "Aptitude Assessment",
    description: "25 Questions — Quantitative, logical, and analytical reasoning.",
    icon:        BrainCircuit,
    href:        "/assessments/aptitude",
    badge:       "25 Questions",
  },
  {
    key:         "technical",
    label:       "Technical Assessment",
    description: "25 Questions — Personalized to your uploaded resume stack.",
    icon:        BookOpen,
    href:        "/assessments/technical",
    badge:       "Based on resume",
  },
  {
    key:         "coding",
    label:       "Coding Assessment",
    description: "15 Problems — LeetCode-style algorithmic challenges.",
    icon:        Code2,
    href:        "/assessments/coding",
    badge:       "Matched to skills",
  },
];

// ─── Component ────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser]       = useState<{ fullName: string; email: string; role: string } | null>(null);
  const [results, setResults] = useState<AssessmentResult[]>([]);
  const [resumeStatus, setResumeStatus] = useState<ResumeStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  // Auth guard
  useEffect(() => {
    const token = getStoredToken();
    if (!token) { router.replace("/login"); return; }
    const u = getStoredUser();
    setUser(u);
  }, [router]);

  // Load recent results & resume status (with auto-refetch on window focus)
  useEffect(() => {
    const u = getStoredUser();
    if (!u?.id) { setLoading(false); return; }

    function fetchDashboardData() {
      Promise.all([
        getCandidateResults(u!.id).catch(() => []),
        getResumeStatus().catch(() => null),
      ]).then(([resData, statusData]) => {
        setResults(resData);
        setResumeStatus(statusData);
      }).finally(() => setLoading(false));
    }

    fetchDashboardData();

    const handleFocus = () => fetchDashboardData();
    window.addEventListener("focus", handleFocus);
    window.addEventListener("visibilitychange", handleFocus);

    return () => {
      window.removeEventListener("focus", handleFocus);
      window.removeEventListener("visibilitychange", handleFocus);
    };
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

  /** Derive a meaningful assessment type label from which section scores are populated */
  function getAssessmentTypeLabel(r: typeof results[number]): string {
    const hasApt  = (r.aptitudeScore  ?? 0) > 0 || (r as any).aptitudeAnswers?.length  > 0;
    const hasTech = (r.technicalScore ?? 0) > 0 || (r as any).technicalAnswers?.length > 0;
    const hasCode = (r.codingScore    ?? 0) > 0 || (r as any).codingSubmissions?.length > 0;
    const count   = [hasApt, hasTech, hasCode].filter(Boolean).length;
    if (count >= 2) return "Full Assessment";
    if (hasApt)    return "Aptitude Assessment";
    if (hasTech)   return "Technical Assessment";
    if (hasCode)   return "Coding Assessment";
    return "Assessment";
  }

  function statusBadge(status: string) {
    const s = (status ?? "").toLowerCase();
    if (s === "passed") return <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#4096ff] bg-[#4096ff]/10 border border-[#4096ff]/20 px-2.5 py-0.5 rounded-full"><CheckCircle2 size={10} />Passed</span>;
    if (s === "failed") return <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#1E293B] bg-[#1E293B]/10 border border-[#1E293B]/20 px-2.5 py-0.5 rounded-full"><AlertCircle size={10} />Failed</span>;
    return <span className="inline-flex text-[11px] font-semibold text-[#64748B] bg-[#F1F5F9] px-2.5 py-0.5 rounded-full">{status}</span>;
  }

  // Stat cards config strictly using brand colors
  const statCards = [
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
  ];

  return (
    <AppShell
      title={`Welcome back, ${firstName}`}
      subtitle="Your assessment dashboard"
    >
      <div className="max-w-5xl mx-auto space-y-7">

        {/* ── Welcome Banner ──────────────────────────────────────── */}
        <div
          className="rounded-2xl px-7 py-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative overflow-hidden shadow-sm"
          style={{
            background: "#1E293B",
            border: "1px solid rgba(255, 255, 255, 0.1)",
          }}
        >
          {/* Subtle background highlight */}
          <div className="absolute top-0 right-0 w-80 h-80 rounded-full opacity-10 blur-3xl pointer-events-none"
            style={{ background: "#4096ff" }} />

          <div className="relative">
            <div className="flex items-center gap-2 mb-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[10.5px] font-bold text-[#4096ff] tracking-wide"
                style={{ background: "rgba(64, 150, 255, 0.12)", border: "1px solid rgba(64, 150, 255, 0.25)" }}>
                <Zap size={11} className="text-[#60a5fa]" />
                AI ASSESSMENT PLATFORM
              </span>
            </div>
            <h2 className="text-[22px] font-extrabold text-white tracking-tight mb-1 leading-tight">
              Good to see you, {firstName} 👋
            </h2>
            <p className="text-[13px] text-[#94A3B8] leading-relaxed">
              Track your progress across assessments and sharpen your skills.
            </p>
          </div>
          <Link
            href="/assessments"
            className="relative flex items-center gap-2 px-5 py-2.5 rounded-xl text-white text-[13.5px] font-bold transition-all shrink-0 hover:bg-[#60a5fa]"
            style={{
              background: "#4096ff",
              boxShadow: "0 4px 14px rgba(64,150,255,0.35)",
            }}
          >
            Start Assessment <ArrowRight size={14} />
          </Link>
        </div>

        {/* ── Resume Personalization Status Banner ──────────────────── */}
        {resumeStatus?.hasResume ? (
          <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm card-accent-blue">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-[#4096ff]/10 text-[#4096ff] flex items-center justify-center shrink-0">
                <FileCheck size={20} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-[13px] font-bold text-[#1E293B]">
                    Resume Analyzed & Active
                  </span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-extrabold bg-[#4096ff]/10 text-[#4096ff] border border-[#4096ff]/20">
                    ✓ Profile Personalization Enabled
                  </span>
                </div>
                <p className="text-[12px] text-[#64748B] mt-0.5">
                  {resumeStatus.resumeFilename ? `File: ${resumeStatus.resumeFilename} • ` : ""}
                  {resumeStatus.profileSummary?.topSkills && resumeStatus.profileSummary.topSkills.length > 0
                    ? `Top Stack: ${resumeStatus.profileSummary.topSkills.join(", ")}`
                    : "Personalized question generation active"}
                </p>
              </div>
            </div>

            <Link
              href="/resume-onboarding"
              className="text-[12px] text-[#4096ff] hover:text-[#60a5fa] font-bold transition-colors shrink-0 flex items-center gap-1"
            >
              Update Resume <ArrowRight size={12} />
            </Link>
          </div>
        ) : (
          <div className="bg-white border border-amber-200 rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
                <Upload size={20} />
              </div>
              <div>
                <p className="text-[13px] font-bold text-[#1E293B]">
                  Upload Your Resume for Personalized Assessments
                </p>
                <p className="text-[12px] text-[#64748B] mt-0.5">
                  Upload your PDF/DOCX resume to generate custom 25 Aptitude, 25 Technical, and 15 Coding questions.
                </p>
              </div>
            </div>

            <Link
              href="/resume-onboarding"
              className="px-4 py-2 rounded-lg bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[12px] font-bold transition-colors shrink-0 flex items-center gap-1"
            >
              Upload Resume <ArrowRight size={12} />
            </Link>
          </div>
        )}

        {/* ── Performance Snapshot ─────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 animate-stagger">
          {statCards.map((stat) => (
            <div
              key={stat.label}
              className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-4 flex items-start gap-3 animate-fade-in-up transition-all duration-200 hover:shadow-sm card-accent-blue"
            >
              <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 icon-bg-blue">
                <stat.icon size={18} className="text-[#4096ff]" />
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
                  className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 flex flex-col gap-3 transition-all duration-200 group hover:shadow-md card-accent-blue"
                  style={{ textDecoration: "none" }}
                >
                  <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0 icon-bg-blue transition-transform duration-200 group-hover:scale-105">
                    <Icon size={20} className="text-[#4096ff]" />
                  </div>
                  <div>
                    <h3 className="text-[14px] font-bold text-[#1E293B] leading-tight mb-1.5">
                      {cat.label}
                    </h3>
                    <p className="text-[12px] text-[#64748B] leading-relaxed">{cat.description}</p>
                  </div>
                  <div className="flex items-center gap-1 text-[12.5px] font-bold text-[#4096ff] mt-auto group-hover:gap-2 transition-all">
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
                  const typeLabel = getAssessmentTypeLabel(r);
                  return (
                    <div key={r.id} className="flex items-center justify-between px-5 py-3.5 hover:bg-[#F8FAFC] transition-colors group card-accent-blue">
                      <div className="flex-1 min-w-0">
                        <p className="text-[13px] font-semibold text-[#1E293B] truncate">
                          {typeLabel}
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
            className="rounded-xl p-5 flex flex-col gap-4 relative overflow-hidden bg-[#1E293B] border border-white/10"
          >
            <div className="relative flex items-center gap-3">
              <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0 icon-bg-blue">
                <Video size={20} className="text-[#4096ff]" />
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#4096ff] animate-pulse-dot" />
                <span className="text-[11px] font-semibold text-[#4096ff]">Live Proctoring</span>
              </div>
            </div>

            <div className="relative">
              <h3 className="text-[16px] font-bold text-white mb-1.5">AI Mock Interview</h3>
              <p className="text-[12.5px] text-[#94A3B8] leading-relaxed">
                Practice with an AI interviewer. Get live proctoring, recording, and instant feedback.
              </p>
            </div>

            <Link
              href="/video-recording"
              className="relative mt-auto flex items-center justify-center gap-2 h-[42px] rounded-xl text-white text-[13px] font-bold transition-all bg-[#4096ff] hover:bg-[#60a5fa]"
              style={{
                boxShadow: "0 4px 14px rgba(64,150,255,0.35)",
              }}
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
