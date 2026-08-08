"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  ShieldCheck,
  BrainCircuit,
  Video,
  BarChart3,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  CheckCircle2,
  ListOrdered,
} from "lucide-react";

interface GuideSlide {
  id: string;
  badge: string;
  title: string;
  subtitle: string;
  steps: string[];
  imageSrc: string;
  ctaText: string;
  ctaHref: string;
  icon: React.ElementType;
}

const GUIDE_SLIDES: GuideSlide[] = [
  {
    id: "proctoring-guide",
    badge: "GUIDE 01 — TEST RULES & PROCTORING",
    title: "How to Take Assessments & Live Rules",
    subtitle: "Ensure a smooth proctored assessment experience with these steps:",
    steps: [
      "Select Aptitude, Technical, or Coding assessment from the Hub.",
      "Allow browser permissions for camera, microphone, and fullscreen mode.",
      "Stay focused in full screen — tab switching or multiple faces log warnings.",
      "Submit your answers before the timer expires to automatically save results.",
    ],
    imageSrc: "/images/assessment_guide.png",
    ctaText: "Explore Assessments",
    ctaHref: "/assessments",
    icon: ShieldCheck,
  },
  {
    id: "interview-guide",
    badge: "GUIDE 02 — AI MOCK INTERVIEW",
    title: "AI Interview Studio & Proctoring Logs",
    subtitle: "Practice video interviews with real-time AI feedback and monitoring:",
    steps: [
      "Launch the AI Interview Studio directly from your dashboard.",
      "Respond to role-specific technical questions on video.",
      "Live proctoring monitors microphone activity, presence, and focus.",
      "Review your recorded session and cheating risk score report.",
    ],
    imageSrc: "/images/ai_interview.png",
    ctaText: "Start AI Interview",
    ctaHref: "/video-recording",
    icon: Video,
  },
  {
    id: "analytics-guide",
    badge: "GUIDE 03 — RESULTS & ANALYTICS",
    title: "Performance Tracking & Skill Insights",
    subtitle: "Gain actionable feedback from your assessment performance data:",
    steps: [
      "Every completed test calculates instant scores and percentages.",
      "Review category breakdowns across Quantitative, Technical & Coding.",
      "Identify your strongest skills and target specific weak areas.",
      "Monitor historical attempt trends over time on your Analytics dashboard.",
    ],
    imageSrc: "/images/analytics_guide.png",
    ctaText: "View Analytics",
    ctaHref: "/analytics",
    icon: BarChart3,
  },
];

export default function DashboardGuideBanner() {
  const [currentIdx, setCurrentIdx] = useState(0);

  // Auto slide every 6 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIdx((prev) => (prev + 1) % GUIDE_SLIDES.length);
    }, 6000);
    return () => clearInterval(timer);
  }, []);

  const activeSlide = GUIDE_SLIDES[currentIdx];
  const Icon = activeSlide.icon;

  return (
    <div className="bg-white border border-[rgba(30,41,59,0.10)] rounded-2xl overflow-hidden shadow-[0_4px_25px_rgba(15,23,42,0.03)] transition-all duration-300">
      {/* Top Header bar with navigation controls */}
      <div className="px-6 py-4 border-b border-[rgba(30,41,59,0.08)] flex items-center justify-between bg-[#F8FAFC]">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#4096ff]/10 border border-[#4096ff]/20 flex items-center justify-center text-[#4096ff]">
            <Sparkles size={16} />
          </div>
          <div>
            <h3 className="text-[14px] font-bold text-[#1E293B]">
              Platform Guide & Candidate Handbook
            </h3>
            <p className="text-[11.5px] text-[#64748B]">
              Learn how to take tests, proctoring rules, and platform features
            </p>
          </div>
        </div>

        {/* Slide selectors & Controls */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1.5 mr-2">
            {GUIDE_SLIDES.map((s, idx) => (
              <button
                key={s.id}
                onClick={() => setCurrentIdx(idx)}
                className={`px-3 py-1 rounded-lg text-[11.5px] font-semibold transition-all ${
                  idx === currentIdx
                    ? "bg-[#4096ff] text-white shadow-sm"
                    : "bg-[#E2E8F0]/60 text-[#64748B] hover:bg-[#E2E8F0] hover:text-[#1E293B]"
                }`}
              >
                Guide 0{idx + 1}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() =>
                setCurrentIdx((prev) => (prev - 1 + GUIDE_SLIDES.length) % GUIDE_SLIDES.length)
              }
              className="w-8 h-8 rounded-lg border border-[rgba(30,41,59,0.12)] flex items-center justify-center text-[#64748B] hover:text-[#1E293B] hover:bg-white transition-colors"
              title="Previous guide"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setCurrentIdx((prev) => (prev + 1) % GUIDE_SLIDES.length)}
              className="w-8 h-8 rounded-lg border border-[rgba(30,41,59,0.12)] flex items-center justify-center text-[#64748B] hover:text-[#1E293B] hover:bg-white transition-colors"
              title="Next guide"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Main Slide Content */}
      <div className="p-6 lg:p-7 grid md:grid-cols-12 gap-6 lg:gap-8 items-center">
        {/* Left Col: Steps & Instructions */}
        <div className="md:col-span-7 space-y-4">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#4096ff]/10 text-[#4096ff] text-[11px] font-extrabold tracking-wider uppercase border border-[#4096ff]/20">
            <Icon size={12} />
            {activeSlide.badge}
          </span>

          <h2 className="text-[20px] lg:text-[22px] font-extrabold text-[#1E293B] tracking-tight leading-snug">
            {activeSlide.title}
          </h2>

          <p className="text-[13px] text-[#64748B] font-medium">
            {activeSlide.subtitle}
          </p>

          {/* Steps List */}
          <div className="space-y-2.5 pt-1">
            {activeSlide.steps.map((step, idx) => (
              <div key={idx} className="flex items-start gap-3">
                <span className="w-5 h-5 rounded-full bg-[#4096ff]/10 border border-[#4096ff]/25 text-[#4096ff] text-[10.5px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                  {idx + 1}
                </span>
                <p className="text-[13px] text-[#334155] font-medium leading-relaxed">
                  {step}
                </p>
              </div>
            ))}
          </div>

          {/* Action Button */}
          <div className="pt-3 flex items-center gap-4">
            <Link
              href={activeSlide.ctaHref}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#4096ff] hover:bg-[#60a5fa] text-white text-[13.5px] font-semibold transition-all shadow-[0_4px_14px_rgba(64,150,255,0.35)]"
            >
              {activeSlide.ctaText} <ArrowRight size={14} />
            </Link>
            <span className="text-[12px] text-[#94A3B8] flex items-center gap-1">
              <CheckCircle2 size={13} className="text-[#15803D]" /> Verified Guide
            </span>
          </div>
        </div>

        {/* Right Col: AI Generated Image Showcase */}
        <div className="md:col-span-5 relative group">
          <div className="relative w-full aspect-[4/3] rounded-xl overflow-hidden border border-[rgba(30,41,59,0.12)] bg-[#F8FAFC] shadow-sm">
            <Image
              src={activeSlide.imageSrc}
              alt={activeSlide.title}
              fill
              className="object-cover transition-transform duration-500 group-hover:scale-105"
              priority
            />
          </div>
          <div className="absolute bottom-2 right-2 px-2.5 py-1 rounded-md bg-[#1E293B]/80 backdrop-blur-md text-white text-[10px] font-medium flex items-center gap-1 border border-white/10">
            <Sparkles size={10} className="text-[#4096ff]" />
            AI Generated Illustration
          </div>
        </div>
      </div>
    </div>
  );
}
