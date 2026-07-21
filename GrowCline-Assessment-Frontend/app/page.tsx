"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Video,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  BrainCircuit,
  Lock,
  Cpu,
  BarChart3,
  ShieldAlert,
} from "lucide-react";

export default function Home() {
  const router = useRouter();

  const [jobRole, setJobRole] = useState("Frontend Developer");
  const [interviewType, setInterviewType] = useState<
    "TECHNICAL" | "HR" | "BEHAVIORAL" | "RESUME_BASED"
  >("TECHNICAL");
  const [difficulty, setDifficulty] = useState<"EASY" | "MEDIUM" | "HARD">(
    "MEDIUM"
  );
  const [isStarting, setIsStarting] = useState(false);

  const handleStartInterview = () => {
    setIsStarting(true);
    const params = new URLSearchParams({
      jobRole,
      interviewType,
      difficulty,
    });
    router.push(`/video-recording?${params.toString()}`);
  };

  return (
    <main className="min-h-screen bg-[#F8FAFC] text-[#0F172A] relative overflow-hidden font-sans">
      <div className="relative mx-auto flex max-w-7xl flex-col px-6 py-10">
        {/* Navigation Header */}
        <header className="flex items-center justify-between py-4 rounded-3xl border border-white/10 bg-[#1E293B] px-8 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#4096ff] shadow-lg shadow-blue-500/30">
              <Video className="h-6 w-6 text-white" />
            </div>
            <div>
              <span className="text-2xl font-bold tracking-tight text-white">
                GrowCline
              </span>
              <span className="ml-2 rounded-full bg-[#4096ff]/20 px-2.5 py-0.5 text-xs font-semibold text-[#4096ff]">
                Interview Platform
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 rounded-full bg-[#0F172A] border border-white/10 px-4 py-2 text-xs text-slate-300">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span>Automated Backend Proctoring</span>
            </div>
          </div>
        </header>

        {/* Hero & Setup Section */}
        <div className="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-12 items-center">
          {/* Left Column: Vision & Features */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full bg-[#4096ff]/10 border border-[#4096ff]/30 px-4 py-2 text-sm font-semibold text-[#4096ff]">
              <Sparkles className="h-4 w-4" />
              <span>Unified AI Assessment &amp; Proctoring Engine</span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-black leading-tight tracking-tight text-[#1E293B]">
              Integrated AI Interview &amp; Proctoring Studio
            </h1>

            <p className="text-base text-slate-600 max-w-2xl leading-relaxed font-medium">
              Start your interview session in a single unified studio. Real-time video recording, live camera gaze tracking, proctoring alerts, and cheating risk analysis run seamlessly in the backend.
            </p>

            {/* Feature Cards Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
              <div className="rounded-2xl border border-white/10 bg-[#1E293B] p-5 shadow-xl text-white">
                <Video className="h-7 w-7 text-[#4096ff] mb-3" />
                <h3 className="font-bold text-white text-base">Video Studio</h3>
                <p className="mt-1 text-xs text-slate-400">
                  Interactive AI question delivery &amp; media recording.
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-[#1E293B] p-5 shadow-xl text-white">
                <ShieldAlert className="h-7 w-7 text-emerald-400 mb-3" />
                <h3 className="font-bold text-white text-base">Live Proctoring</h3>
                <p className="mt-1 text-xs text-slate-400">
                  Real-time face detection, tab-switch &amp; presence logs.
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-[#1E293B] p-5 shadow-xl text-white">
                <BrainCircuit className="h-7 w-7 text-[#60a5fa] mb-3" />
                <h3 className="font-bold text-white text-base">Cheating Detection</h3>
                <p className="mt-1 text-xs text-slate-400">
                  Automated risk scoring engine &amp; comprehensive report.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Session Configuration */}
          <div className="lg:col-span-5">
            <div className="rounded-[28px] border border-white/10 bg-[#1E293B] p-8 shadow-2xl space-y-6 text-white">
              <div>
                <h2 className="text-2xl font-bold text-white">Start Interview Session</h2>
                <p className="mt-1 text-sm text-slate-400">
                  Select job role and difficulty to generate tailored questions.
                </p>
              </div>

              <div className="space-y-4">
                {/* Job Role Input */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                    Target Job Role
                  </label>
                  <select
                    value={jobRole}
                    onChange={(e) => setJobRole(e.target.value)}
                    className="w-full rounded-2xl border border-white/10 bg-[#0F172A] px-4 py-3.5 text-sm text-white focus:border-[#4096ff] focus:outline-none"
                  >
                    <option value="Frontend Developer">Frontend Developer</option>
                    <option value="Backend Engineer">Backend Engineer</option>
                    <option value="Fullstack Developer">Fullstack Developer</option>
                    <option value="DevOps Engineer">DevOps Engineer</option>
                    <option value="Data Scientist">Data Scientist</option>
                    <option value="Product Manager">Product Manager</option>
                  </select>
                </div>

                {/* Interview Type Selector */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                    Interview Type
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {(
                      [
                        { id: "TECHNICAL", label: "Technical" },
                        { id: "HR", label: "HR Round" },
                        { id: "BEHAVIORAL", label: "Behavioral" },
                        { id: "RESUME_BASED", label: "Resume Based" },
                      ] as const
                    ).map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => setInterviewType(item.id)}
                        className={`rounded-xl border px-3 py-2.5 text-xs font-semibold transition-all ${
                          interviewType === item.id
                            ? "border-[#4096ff] bg-[#4096ff] text-white shadow-md"
                            : "border-white/10 bg-[#0F172A] text-slate-400 hover:border-[#4096ff]"
                        }`}
                      >
                        {item.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Difficulty Selector */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                    Difficulty Level
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {(["EASY", "MEDIUM", "HARD"] as const).map((level) => (
                      <button
                        key={level}
                        type="button"
                        onClick={() => setDifficulty(level)}
                        className={`rounded-xl border py-2.5 text-xs font-bold tracking-wider transition-all ${
                          difficulty === level
                            ? level === "EASY"
                              ? "border-emerald-500 bg-emerald-500/20 text-emerald-400"
                              : level === "MEDIUM"
                              ? "border-amber-500 bg-amber-500/20 text-amber-400"
                              : "border-rose-500 bg-rose-500/20 text-rose-400"
                            : "border-white/10 bg-[#0F172A] text-slate-400 hover:border-white/20"
                        }`}
                      >
                        {level}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Start Session CTA Button */}
              <button
                onClick={handleStartInterview}
                disabled={isStarting}
                className="w-full flex items-center justify-center gap-3 rounded-2xl bg-[#4096ff] hover:bg-[#60a5fa] py-4 font-bold text-white shadow-xl shadow-blue-500/25 transition-all disabled:opacity-50"
              >
                {isStarting ? (
                  <>
                    <span className="h-5 w-5 rounded-full border-2 border-white border-t-transparent animate-spin" />
                    <span>Launching Interview...</span>
                  </>
                ) : (
                  <>
                    <span>Enter Interview Studio</span>
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </button>

              <div className="flex items-center justify-center gap-2 text-center text-xs text-slate-400 pt-1 font-medium">
                <Lock className="h-3.5 w-3.5 text-[#4096ff]" />
                <span>Backend proctoring &amp; risk detection start automatically</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Info Banner */}
        <footer className="mt-14 border-t border-slate-200 pt-6 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4 font-medium">
          <div className="flex items-center gap-6">
            <span className="flex items-center gap-1.5 text-[#1E293B]">
              <Cpu className="h-4 w-4 text-[#4096ff]" /> AI Question Engine
            </span>
            <span className="flex items-center gap-1.5 text-[#1E293B]">
              <ShieldCheck className="h-4 w-4 text-emerald-600" /> Automated Proctoring
            </span>
            <span className="flex items-center gap-1.5 text-[#1E293B]">
              <BarChart3 className="h-4 w-4 text-indigo-600" /> Instant Analytics
            </span>
          </div>
          <p>© 2026 GrowCline AI Assessment Platform</p>
        </footer>
      </div>
    </main>
  );
}