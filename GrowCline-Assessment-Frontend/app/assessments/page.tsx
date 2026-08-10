"use client";

/**
 * /assessments — Assessment Hub
 * Central entry point for all 3 Team A assessment types.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { BrainCircuit, BookOpen, Code2, Clock, FileQuestion, CheckCircle2, Zap } from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import { AssessmentCard } from "@/components/assessment/shared";
import { getStoredToken } from "@/services/authService";

const ASSESSMENTS = [
  {
    key:           "aptitude",
    title:         "Aptitude Assessment",
    description:   "Test your quantitative ability, logical reasoning, and verbal aptitude. Questions span mathematics, pattern recognition, and language comprehension.",
    icon:          BrainCircuit,
    href:          "/assessments/aptitude",
    questionCount: 10,
    duration:      20,
    accentColor:   "#4096ff",
    iconBg:        "linear-gradient(135deg, rgba(64,150,255,0.18), rgba(64,150,255,0.06))",
  },
  {
    key:           "technical",
    title:         "Technical Assessment",
    description:   "Evaluate your domain knowledge with technology-specific MCQs. Covers programming concepts, software engineering, and computer science fundamentals.",
    icon:          BookOpen,
    href:          "/assessments/technical",
    questionCount: 10,
    duration:      25,
    accentColor:   "#a855f7",
    iconBg:        "linear-gradient(135deg, rgba(168,85,247,0.18), rgba(168,85,247,0.06))",
  },
  {
    key:           "coding",
    title:         "Coding Assessment",
    description:   "Solve algorithmic problems in an integrated code editor. Submit solutions and view test case results to demonstrate your problem-solving ability.",
    icon:          Code2,
    href:          "/assessments/coding",
    questionCount: 1,
    duration:      30,
    accentColor:   "#10b981",
    iconBg:        "linear-gradient(135deg, rgba(16,185,129,0.18), rgba(16,185,129,0.06))",
  },
] as const;

const INFO_CARDS = [
  {
    label:  "Instant Results",
    desc:   "Scores calculated and displayed immediately after submission.",
    color:  "#4096ff",
    accent: "card-accent-blue",
  },
  {
    label:  "Saved Automatically",
    desc:   "Your results are saved to your profile for review anytime.",
    color:  "#a855f7",
    accent: "card-accent-purple",
  },
  {
    label:  "Review Performance",
    desc:   "Check detailed analytics in the Analytics Dashboard.",
    color:  "#10b981",
    accent: "card-accent-emerald",
  },
];

export default function AssessmentsPage() {
  const router = useRouter();

  useEffect(() => {
    const token = getStoredToken();
    if (!token) router.replace("/login");
  }, [router]);

  return (
    <AppShell
      title="Assessment Hub"
      subtitle="Choose an assessment to begin"
    >
      <div className="max-w-4xl mx-auto space-y-7">

        {/* Page intro */}
        <div
          className="rounded-xl px-6 py-5 flex flex-col sm:flex-row items-start sm:items-center gap-4"
          style={{
            background: "linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)",
            border: "1px solid rgba(30,41,59,0.08)",
            boxShadow: "0 2px 12px rgba(30,41,59,0.04)",
          }}
        >
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-1 h-4 rounded-full bg-[#4096ff]" />
              <h2 className="text-[15px] font-bold text-[#1E293B]">
                Select Your Assessment
              </h2>
            </div>
            <p className="text-[13px] text-[#64748B] leading-relaxed">
              Each assessment is independently timed and scored. You can attempt them in any order.
              Results are saved automatically after submission.
            </p>
          </div>
          <div className="flex gap-4 text-[12px] text-[#64748B] shrink-0">
            <span
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold"
              style={{ background: "rgba(64,150,255,0.08)", border: "1px solid rgba(64,150,255,0.15)", color: "#4096ff" }}
            >
              <Clock size={12} />
              Auto-timed
            </span>
            <span
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold"
              style={{ background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.15)", color: "#059669" }}
            >
              <Zap size={12} />
              Instant scoring
            </span>
          </div>
        </div>

        {/* Assessment Cards */}
        <div className="grid md:grid-cols-3 gap-5">
          {ASSESSMENTS.map((a) => {
            const Icon = a.icon;
            return (
              <AssessmentCard
                key={a.key}
                title={a.title}
                description={a.description}
                icon={<Icon size={18} />}
                status="not_started"
                questionCount={a.questionCount}
                duration={a.duration}
                onAction={() => router.push(a.href)}
                accentColor={a.accentColor}
                iconBg={a.iconBg}
              />
            );
          })}
        </div>

        {/* Info row */}
        <div className="grid sm:grid-cols-3 gap-4">
          {INFO_CARDS.map((info) => (
            <div
              key={info.label}
              className={`bg-white border border-[rgba(30,41,59,0.10)] rounded-xl px-4 py-4 flex items-start gap-3 hover:shadow-sm transition-all duration-200 ${info.accent}`}
            >
              <div
                className="w-2 h-2 rounded-full mt-1.5 shrink-0"
                style={{ background: info.color, boxShadow: `0 0 6px ${info.color}60` }}
              />
              <div>
                <p className="text-[13px] font-bold text-[#1E293B] mb-0.5">{info.label}</p>
                <p className="text-[12px] text-[#64748B] leading-relaxed">{info.desc}</p>
              </div>
            </div>
          ))}
        </div>

      </div>
    </AppShell>
  );
}
