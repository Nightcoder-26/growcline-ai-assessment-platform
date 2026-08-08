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
} from "lucide-react";

interface GuideSlide {
  id: number;
  tag: string;
  title: string;
  description: string;
  icon: React.ElementType;
  color: string;
}

const GUIDE_SLIDES: GuideSlide[] = [
  {
    id: 1,
    tag: "PROCTORING RULES",
    title: "Stay in Fullscreen & Frame",
    description: "Tab switches, exiting fullscreen, or leaving camera view will log proctoring warnings.",
    icon: ShieldAlert,
    color: "#4096ff",
  },
  {
    id: 2,
    tag: "TEST INSTRUCTIONS",
    title: "3 Assessment Modules",
    description: "Aptitude, Technical MCQs & Coding. Complete at your pace; scores save automatically.",
    icon: HelpCircle,
    color: "#4096ff",
  },
  {
    id: 3,
    tag: "AI INTERVIEW",
    title: "Practice Mock Sessions",
    description: "Experience adaptive AI questioning with real-time audio analysis and live proctoring.",
    icon: Video,
    color: "#4096ff",
  },
  {
    id: 4,
    tag: "ANALYTICS",
    title: "Detailed Performance Reports",
    description: "View skill breakdowns, time efficiency metrics, and targeted improvement suggestions.",
    icon: Award,
    color: "#4096ff",
  },
  {
    id: 5,
    tag: "PRO TIPS",
    title: "Camera & Mic Setup",
    description: "Ensure good lighting and test microphone levels before initiating interview recordings.",
    icon: Sparkles,
    color: "#4096ff",
  },
];

export default function SidebarGuideCarousel() {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Auto slide every 4.5 seconds
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % GUIDE_SLIDES.length);
    }, 4500);
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
    <div className="mx-3 my-3 p-3.5 rounded-xl bg-[#0F172A]/60 border border-white/10 flex flex-col justify-between transition-all duration-300 relative group">
      {/* Header Badge */}
      <div className="flex items-center justify-between mb-2">
        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-[#4096ff]/15 text-[#4096ff] text-[10px] font-bold tracking-wider uppercase border border-[#4096ff]/20">
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

      {/* Content */}
      <div className="flex items-start gap-2.5 my-1">
        <div className="w-7 h-7 rounded-lg bg-[#4096ff]/10 border border-[#4096ff]/20 flex items-center justify-center shrink-0 mt-0.5">
          <Icon size={14} className="text-[#4096ff]" />
        </div>
        <div>
          <h4 className="text-white text-[12.5px] font-semibold leading-snug">
            {slide.title}
          </h4>
          <p className="text-[#94A3B8] text-[11px] leading-relaxed mt-1">
            {slide.description}
          </p>
        </div>
      </div>

      {/* Slide dots */}
      <div className="flex items-center justify-center gap-1 mt-2.5">
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
  );
}
