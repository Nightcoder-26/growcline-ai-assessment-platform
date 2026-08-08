"use client";

/**
 * /assessments — Assessment Hub
 * Central entry point for all 3 Team A assessment types.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BrainCircuit, BookOpen, Code2, Clock, FileQuestion, ChevronRight } from "lucide-react";
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
  },
  {
    key:           "technical",
    title:         "Technical Assessment",
    description:   "Evaluate your domain knowledge with technology-specific MCQs. Covers programming concepts, software engineering, and computer science fundamentals.",
    icon:          BookOpen,
    href:          "/assessments/technical",
    questionCount: 10,
    duration:      25,
  },
  {
    key:           "coding",
    title:         "Coding Assessment",
    description:   "Solve algorithmic problems in an integrated code editor. Submit solutions and view test case results to demonstrate your problem-solving ability.",
    icon:          Code2,
    href:          "/assessments/coding",
    questionCount: 1,
    duration:      30,
  },
] as const;

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
        <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl px-6 py-5 flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <div className="flex-1">
            <h2 className="text-[15px] font-semibold text-[#1E293B] mb-1">
              Select Your Assessment
            </h2>
            <p className="text-[13px] text-[#64748B] leading-relaxed">
              Each assessment is independently timed and scored. You can attempt them in any order.
              Results are saved automatically after submission.
            </p>
          </div>
          <div className="flex gap-5 text-[12px] text-[#64748B] shrink-0">
            <span className="flex items-center gap-1.5">
              <Clock size={13} className="text-[#4096ff]" />
              Auto-timed
            </span>
            <span className="flex items-center gap-1.5">
              <FileQuestion size={13} className="text-[#4096ff]" />
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
              />
            );
          })}
        </div>

        {/* Info row */}
        <div className="grid sm:grid-cols-3 gap-4">
          {[
            { label: "Instant Results", desc: "Scores calculated and displayed immediately after submission." },
            { label: "Saved Automatically", desc: "Your results are saved to your profile for review anytime." },
            { label: "Review Performance", desc: "Check detailed analytics in the Analytics Dashboard." },
          ].map((info) => (
            <div
              key={info.label}
              className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl px-4 py-4 flex items-start gap-3"
            >
              <div className="w-1.5 h-1.5 rounded-full bg-[#4096ff] mt-1.5 shrink-0" />
              <div>
                <p className="text-[13px] font-semibold text-[#1E293B] mb-0.5">{info.label}</p>
                <p className="text-[12px] text-[#64748B] leading-relaxed">{info.desc}</p>
              </div>
            </div>
          ))}
        </div>

      </div>
    </AppShell>
  );
}
