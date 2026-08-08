"use client";

import { useState, useEffect } from "react";
import {
  ShieldAlert,
  HelpCircle,
  Sparkles,
  Award,
  Video,
  ChevronLeft,
  ChevronRight,
  Info,
  Activity,
  CheckCircle2,
} from "lucide-react";

interface GuideSlide {
  id: number;
  tag: string;
  title: string;
  description: string;
  steps: string[];
  icon: React.ElementType;
}

const GUIDE_SLIDES: GuideSlide[] = [
  {
    id: 1,
    tag: "PROCTORING RULES",
    title: "Stay in Fullscreen & Frame",
    description: "Anti-cheat rules enforced during proctored assessments:",
    steps: [
      "Keep browser in full screen",
      "Remain visible in camera frame",
      "Do not switch tabs or windows",
      "Avoid secondary voice/persons",
    ],
    icon: ShieldAlert,
  },
  {
    id: 2,
    tag: "TEST INSTRUCTIONS",
    title: "3 Assessment Modules",
    description: "Complete tests at your own pace:",
    steps: [
      "Aptitude: Math & Logic MCQs",
      "Technical: Tech Domain Questions",
      "Coding: Algorithmic Problem",
      "Automated evaluation & scores",
    ],
    icon: HelpCircle,
  },
  {
    id: 3,
    tag: "AI MOCK INTERVIEW",
    title: "Practice Mock Sessions",
    description: "Adaptive AI interview features:",
    steps: [
      "Real-time video & audio stream",
      "Live voice frequency detection",
      "Instant cheating risk score",
      "Automated summary report",
    ],
    icon: Video,
  },
  {
    id: 4,
    tag: "ANALYTICS & RESULTS",
    title: "Performance Reports",
    description: "Actionable growth insights:",
    steps: [
      "Category score breakdown",
      "Speed & accuracy tracking",
      "Targeted improvement tips",
      "Historical attempt trends",
    ],
    icon: Award,
  },
  {
    id: 5,
    tag: "PRO TIPS",
    title: "Camera & Mic Setup",
    description: "Prepare before starting tests:",
    steps: [
      "Position in a well-lit room",
      "Check microphone volume",
      "Use stable internet connection",
      "Read all instructions carefully",
    ],
    icon: Sparkles,
  },
];

export default function SidebarGuideCarousel() {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Auto slide every 5 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % GUIDE_SLIDES.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  const slide = GUIDE_SLIDES[currentIndex];
  const Icon = slide.icon;

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % GUIDE_SLIDES.length);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + GUIDE_SLIDES.length) % GUIDE_SLIDES.length);
  };

  return (
    <div className="flex-1 mx-3 my-2 flex flex-col min-h-0 justify-between">
      {/* Platform Status Badge */}
      <div className="px-3 py-2 rounded-xl bg-[#0F172A]/70 border border-white/10 flex items-center justify-between mb-2 shrink-0">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#4096ff] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#4096ff]"></span>
          </span>
          <span className="text-white text-[11.5px] font-semibold tracking-tight">
            AI Proctor Engine
          </span>
        </div>
        <span className="text-[10px] font-bold text-[#4096ff] bg-[#4096ff]/15 px-2 py-0.5 rounded border border-[#4096ff]/20">
          ONLINE
        </span>
      </div>

      {/* Main Guide Widget Box (Flex-1 to stretch down) */}
      <div className="flex-1 p-3.5 rounded-xl bg-[#0F172A]/60 border border-white/10 flex flex-col justify-between transition-all duration-300 relative group overflow-y-auto">
        {/* Header Badge & Navigation */}
        <div className="flex items-center justify-between mb-2.5 shrink-0">
          <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-[#4096ff]/15 text-[#4096ff] text-[9.5px] font-extrabold tracking-wider uppercase border border-[#4096ff]/20">
            <Info size={10} />
            {slide.tag}
          </span>
          <div className="flex items-center gap-1">
            <button
              onClick={prevSlide}
              className="w-5 h-5 rounded flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-colors"
              title="Previous tip"
            >
              <ChevronLeft size={12} />
            </button>
            <button
              onClick={nextSlide}
              className="w-5 h-5 rounded flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-colors"
              title="Next tip"
            >
              <ChevronRight size={12} />
            </button>
          </div>
        </div>

        {/* Title & Description */}
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-[#4096ff]/10 border border-[#4096ff]/20 flex items-center justify-center shrink-0">
              <Icon size={13} className="text-[#4096ff]" />
            </div>
            <h4 className="text-white text-[12.5px] font-semibold leading-tight truncate">
              {slide.title}
            </h4>
          </div>

          <p className="text-[#94A3B8] text-[11px] leading-relaxed">
            {slide.description}
          </p>

          {/* Quick Steps Bullets */}
          <div className="space-y-1 pt-1.5">
            {slide.steps.map((st, i) => (
              <div key={i} className="flex items-start gap-1.5 text-[10.5px] text-white/80 font-medium">
                <CheckCircle2 size={11} className="text-[#4096ff] shrink-0 mt-0.5" />
                <span className="leading-tight">{st}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Slide indicator dots */}
        <div className="flex items-center justify-center gap-1.5 mt-3 pt-2 border-t border-white/5 shrink-0">
          {GUIDE_SLIDES.map((_, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentIndex(idx)}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                idx === currentIndex ? "w-4 bg-[#4096ff]" : "w-1.5 bg-white/20 hover:bg-white/40"
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
