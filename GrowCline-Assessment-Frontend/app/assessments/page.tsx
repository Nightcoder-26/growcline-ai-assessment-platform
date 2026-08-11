"use client";

/**
 * /assessments — Assessment Hub
 * Central entry point for all 3 Team A assessment types.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BrainCircuit, BookOpen, Code2, Clock, Zap, Sparkles, X, ArrowRight } from "lucide-react";
import AppShell from "@/components/assessment/AppShell";
import { AssessmentCard, StatusBadge } from "@/components/assessment/shared";
import { getStoredToken, getStoredUser } from "@/services/authService";
import { getResumeStatus, generatePersonalizedAssessment, getSkillProfile, type SkillProfile } from "@/services/resumeService";
import { getCandidateResults, type AssessmentResult } from "@/services/assessmentService";

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
    topics:        ["Quantitative Ability", "Logical Reasoning", "Verbal Ability", "Data Interpretation"],
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
    topics:        [], // Filled dynamically from resume
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
    topics:        [], // Filled dynamically from resume
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
  const [profile, setProfile] = useState<SkillProfile | null>(null);
  const [results, setResults] = useState<AssessmentResult[]>([]);

  // Preview Modal state
  const [activePreview, setActivePreview] = useState<typeof ASSESSMENTS[number] | null>(null);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) { router.replace("/login"); return; }

    const user = getStoredUser();
    const userId = user?.id;

    Promise.all([
      getResumeStatus(),
      userId ? getCandidateResults(userId).catch(() => []) : Promise.resolve([]),
      getSkillProfile().catch(() => null),
    ])
      .then(([status, resData, profileData]) => {
        setHasResume(status.hasResume);
        setResults(resData);
        setProfile(profileData);
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
      setActivePreview(null);
    }
  };

  // Helper to determine status for a specific assessment key
  const getAssessmentStatus = (key: string): string => {
    if (results.length > 0) {
      const hasSectionData = results.some((r) => {
        if (key === "aptitude") return r.aptitudeScore > 0 || (r.aptitudeAnswers && r.aptitudeAnswers.length > 0);
        if (key === "technical") return r.technicalScore > 0 || (r.technicalAnswers && r.technicalAnswers.length > 0);
        if (key === "coding") return r.codingScore > 0 || (r.codingSubmissions && r.codingSubmissions.length > 0);
        return false;
      });
      if (hasSectionData) return "Completed";
    }
    return "Not Started";
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

  // Get focused skills based on the preview assessment type
  const getFocusSkills = (key: string): string[] => {
    if (!profile) return [];
    if (key === "technical") {
      return (profile.programming_languages || [])
        .concat(profile.frameworks || [])
        .concat(profile.databases || [])
        .slice(0, 8);
    }
    if (key === "coding") {
      return (profile.programming_languages || []).slice(0, 5);
    }
    return ["Quantitative Logic", "Reasoning", "Verbal Comprehension", "Data Interpretation"];
  };

  return (
    <AppShell
      title="Assessment Suite"
      subtitle="Your personalized talent assessment area"
    >
      <div className="max-w-4xl mx-auto space-y-7 relative">

        {/* Your Resume Stack Strip */}
        {profile && (
          <div className="bg-[#1E293B] border border-slate-700/60 rounded-xl px-5 py-3.5 text-white flex items-center justify-between gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-[#4096ff]/20 text-[#60a5fa] border border-[#4096ff]/30">
                ★
              </span>
              <div>
                <p className="text-[12px] font-bold tracking-tight">Your Resume Profile Stack</p>
                <p className="text-[10px] text-[#94A3B8]">Analyzed stack used for personalization</p>
              </div>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {getFocusSkills("technical").map((s) => (
                <span key={s} className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-[#4096ff] text-[11px] font-medium">
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}

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
            const status = getAssessmentStatus(a.key);

            return (
              <div key={a.key} className="relative flex flex-col bg-white border border-[rgba(30,41,59,0.10)] rounded-xl p-5 shadow-sm hover:shadow-md transition-all">
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-[#4096ff]/10 text-[#4096ff] flex items-center justify-center shrink-0">
                      <Icon size={18} />
                    </div>
                    <div>
                      <h3 className="text-[14px] font-bold text-[#1E293B] leading-tight">{a.title}</h3>
                      <div className="mt-1">
                        <StatusBadge status={status} />
                      </div>
                    </div>
                  </div>
                </div>
                <p className="text-[12.5px] text-[#64748B] leading-relaxed mb-4 flex-1">{a.description}</p>
                <div className="flex items-center gap-4 text-[11.5px] text-[#94A3B8] mb-4">
                  <span>{a.questionCount} Questions</span>
                  <span>{a.duration} Minutes</span>
                </div>
                <button
                  onClick={() => setActivePreview(a)}
                  className="w-full h-[38px] flex items-center justify-center gap-2 rounded-lg text-white text-[13px] font-bold transition-all bg-[#4096ff] hover:bg-[#60a5fa]"
                  style={{ boxShadow: "0 4px 12px rgba(64,150,255,0.3)" }}
                >
                  {status === "Completed" ? "View Details" : "Start Assessment"}
                  <ArrowRight size={13} />
                </button>
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

        {/* Personalized Assessment Preview Modal */}
        {activePreview && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0F172A]/70 backdrop-blur-sm animate-fade-in-up">
            <div className="bg-white rounded-2xl border border-slate-200/80 shadow-2xl max-w-md w-full overflow-hidden">
              {/* Modal header */}
              <div className="bg-[#1E293B] px-6 py-4 flex items-center justify-between text-white border-b border-slate-700">
                <div className="flex items-center gap-2">
                  <Sparkles size={16} className="text-[#60a5fa]" />
                  <span className="text-[12px] font-bold tracking-wider uppercase text-[#60a5fa]">Personalized Preview</span>
                </div>
                <button
                  onClick={() => setActivePreview(null)}
                  className="text-slate-400 hover:text-white transition-colors"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Modal content */}
              <div className="p-6 space-y-5">
                <div>
                  <h3 className="text-[18px] font-bold text-[#1E293B]">{activePreview.title}</h3>
                  <p className="text-[12.5px] text-[#64748B] mt-1">Based on your uploaded resume stack & skill profile.</p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/60">
                    <p className="text-[10px] font-bold text-[#94A3B8] uppercase">Questions</p>
                    <p className="text-[16px] font-extrabold text-[#1E293B] mt-0.5">{activePreview.questionCount} Items</p>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200/60">
                    <p className="text-[10px] font-bold text-[#94A3B8] uppercase">Time Allowed</p>
                    <p className="text-[16px] font-extrabold text-[#1E293B] mt-0.5">{activePreview.duration} Minutes</p>
                  </div>
                </div>

                <div>
                  <p className="text-[11px] font-bold text-[#64748B] uppercase tracking-wider mb-2">Focus Areas & Technologies</p>
                  <div className="flex flex-wrap gap-1.5">
                    {getFocusSkills(activePreview.key).map((skill) => (
                      <span key={skill} className="px-2.5 py-1 rounded bg-[#4096ff]/10 border border-[#4096ff]/20 text-[#4096ff] text-[12px] font-semibold">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="pt-2">
                  <button
                    onClick={() => handleStart(activePreview.href)}
                    disabled={generating}
                    className="w-full h-11 bg-[#4096ff] hover:bg-[#60a5fa] disabled:bg-slate-300 text-white font-bold text-[13.5px] rounded-xl shadow-lg flex items-center justify-center gap-2 transition-all"
                  >
                    {generating ? "Preparing Assessment..." : "Start Assessment"}
                    <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </AppShell>
  );
}

