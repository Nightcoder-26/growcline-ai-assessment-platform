"use client";

/**
 * /assessments — Assessment Hub
 * Central entry point for all 3 Team A assessment types.
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { BrainCircuit, BookOpen, Code2, Clock, Zap } from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import { AssessmentCard } from "@/components/assessment/shared";
import { getStoredToken } from "@/services/authService";

import { useState } from "react";
import { Sparkles, FileCheck, AlertCircle } from "lucide-react";
import { getResumeStatus, generatePersonalizedAssessment } from "@/services/resumeService";

const ASSESSMENTS = [
  {
    key:           "aptitude",
    title:         "Aptitude Assessment",
    description:   "25 Questions covering quantitative ability, logical reasoning, analytical thinking, and verbal comprehension.",
    icon:          BrainCircuit,
    href:          "/assessments/aptitude",
    questionCount: 25,
    duration:      35,
    tag:           "General Reasoning",
  },
  {
    key:           "technical",
    title:         "Technical Assessment",
    description:   "25 Questions personalized strictly to your resume stack, testing architecture, tradeoffs, and scenario-based knowledge.",
    icon:          BookOpen,
    href:          "/assessments/technical",
    questionCount: 25,
    duration:      40,
    tag:           "Personalized to Resume",
  },
  {
    key:           "coding",
    title:         "Coding Assessment",
    description:   "15 LeetCode-style coding problems matched to your programming background and experience level.",
    icon:          Code2,
    href:          "/assessments/coding",
    questionCount: 15,
    duration:      60,
    tag:           "Matched to Skills",
  },
] as const;

const INFO_CARDS = [
  {
    label:  "Resume Personalization",
    desc:   "Questions adapt dynamically based on your uploaded resume.",
  },
  {
    label:  "Persistent Attempts",
    desc:   "Questions remain stable across page refreshes.",
  },
  {
    label:  "Instant Feedback",
    desc:   "Scores and analytics calculated immediately after submission.",
  },
];

export default function AssessmentsPage() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);
  const [hasResume, setHasResume] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) { router.replace("/login"); return; }

    getResumeStatus()
      .then((status) => {
        setHasResume(status.hasResume);
        if (!status.hasResume) {
          router.replace("/resume-onboarding");
        }
      })
      .catch(() => {})
      .finally(() => setChecking(false));
  }, [router]);

  const handleStart = async (href: string) => {
    setGenerating(true);
    try {
      await generatePersonalizedAssessment();
      router.push(href);
    } catch (err) {
      router.push(href);
    } finally {
      setGenerating(false);
    }
  };

  if (checking) {
    return (
      <AppShell title="Assessment Hub" subtitle="Verifying your resume profile...">
        <div className="max-w-4xl mx-auto py-20 text-center">
          <div className="w-8 h-8 border-3 border-[#4096ff] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-[13px] text-[#64748B]">Preparing your personalized assessment hub...</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell
      title="Assessment Hub"
      subtitle="Choose a personalized assessment to begin"
    >
      <div className="max-w-4xl mx-auto space-y-7">

        {/* Page intro */}
        <div className="rounded-xl px-6 py-5 flex flex-col sm:flex-row items-start sm:items-center gap-4 bg-white border border-[rgba(30,41,59,0.10)] shadow-sm">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1.5">
              <Sparkles size={16} className="text-[#4096ff]" />
              <h2 className="text-[15px] font-bold text-[#1E293B]">
                Personalized Assessment Suite
              </h2>
            </div>
            <p className="text-[13px] text-[#64748B] leading-relaxed">
              Your assessment contains <strong className="text-[#1E293B]">25 Aptitude</strong>, <strong className="text-[#1E293B]">25 Technical</strong>, and <strong className="text-[#1E293B]">15 Coding</strong> problems generated specifically for your skill profile. Questions remain stable during your attempt.
            </p>
          </div>
          <div className="flex gap-3 text-[12px] shrink-0">
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold bg-[#4096ff]/10 text-[#4096ff] border border-[#4096ff]/20">
              <Clock size={12} />
              Timed Attempts
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-semibold bg-[#1E293B]/10 text-[#1E293B] border border-[#1E293B]/20">
              <Zap size={12} />
              Instant Evaluation
            </span>
          </div>
        </div>

        {/* Assessment Cards */}
        <div className="grid md:grid-cols-3 gap-5">
          {ASSESSMENTS.map((a) => {
            const Icon = a.icon;
            return (
              <div key={a.key} className="relative flex">
                <AssessmentCard
                  title={a.title}
                  description={a.description}
                  icon={<Icon size={18} />}
                  status="not_started"
                  questionCount={a.questionCount}
                  duration={a.duration}
                  onAction={() => handleStart(a.href)}
                />
              </div>
            );
          })}
        </div>

        {/* Info row */}
        <div className="grid sm:grid-cols-3 gap-4">
          {INFO_CARDS.map((info) => (
            <div
              key={info.label}
              className="bg-white border border-[rgba(30,41,59,0.10)] rounded-xl px-4 py-4 flex items-start gap-3 hover:shadow-sm transition-all duration-200 card-accent-blue"
            >
              <div
                className="w-2 h-2 rounded-full mt-1.5 shrink-0 bg-[#4096ff]"
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

