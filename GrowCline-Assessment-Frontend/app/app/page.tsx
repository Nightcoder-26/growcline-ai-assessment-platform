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

export default function AppHome() {
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
              <p className="text-xs text-[#94A3B8]">AI Interview Studio</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2">
              <ShieldCheck className="h-4 w-4 text-[#4096ff]" />
              <span className="text-sm font-medium text-[#94A3B8]">
                Secure & Private
              </span>
            </div>
            <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2">
              <Sparkles className="h-4 w-4 text-[#4096ff]" />
              <span className="text-sm font-medium text-[#94A3B8]">
                AI Powered
              </span>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <div className="mt-16 flex flex-col items-center text-center">
          <div className="mb-6 flex items-center gap-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-4 py-2">
            <BrainCircuit className="h-4 w-4 text-[#4096ff]" />
            <span className="text-sm font-medium text-[#4096ff]">
              Powered by Advanced AI
            </span>
          </div>

          <h1 className="max-w-4xl text-5xl font-extrabold leading-tight tracking-tight text-[#0F172A] md:text-6xl lg:text-7xl">
            Your AI Interview
            <span className="block bg-gradient-to-r from-[#4096ff] to-blue-600 bg-clip-text text-transparent">
              Studio
            </span>
          </h1>

          <p className="mt-6 max-w-2xl text-lg text-[#64748B] leading-relaxed">
            Practice with intelligent AI interviewers, get real-time feedback,
            and build confidence for your dream role. Professional-grade
            experience from anywhere.
          </p>

          {/* Interview Setup Card */}
          <div className="mt-12 w-full max-w-2xl rounded-3xl border border-white/10 bg-[#1E293B] p-8 shadow-2xl">
            <h2 className="mb-6 text-xl font-bold text-white text-left">
              Configure Your Interview
            </h2>

            <div className="space-y-6">
              {/* Job Role */}
              <div>
                <label className="mb-2 block text-sm font-medium text-[#94A3B8]">
                  Job Role
                </label>
                <input
                  type="text"
                  value={jobRole}
                  onChange={(e) => setJobRole(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-white placeholder-[#64748B] focus:border-[#4096ff]/50 focus:outline-none focus:ring-2 focus:ring-[#4096ff]/20 transition-all"
                  placeholder="e.g. Frontend Developer, Product Manager..."
                />
              </div>

              {/* Interview Type */}
              <div>
                <label className="mb-2 block text-sm font-medium text-[#94A3B8]">
                  Interview Type
                </label>
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  {(
                    [
                      "TECHNICAL",
                      "HR",
                      "BEHAVIORAL",
                      "RESUME_BASED",
                    ] as const
                  ).map((type) => (
                    <button
                      key={type}
                      onClick={() => setInterviewType(type)}
                      className={`rounded-xl border px-3 py-2.5 text-xs font-semibold transition-all ${
                        interviewType === type
                          ? "border-[#4096ff] bg-[#4096ff]/20 text-[#4096ff]"
                          : "border-white/10 bg-white/5 text-[#94A3B8] hover:border-white/20 hover:text-white"
                      }`}
                    >
                      {type.replace("_", " ")}
                    </button>
                  ))}
                </div>
              </div>

              {/* Difficulty */}
              <div>
                <label className="mb-2 block text-sm font-medium text-[#94A3B8]">
                  Difficulty Level
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {(["EASY", "MEDIUM", "HARD"] as const).map((level) => (
                    <button
                      key={level}
                      onClick={() => setDifficulty(level)}
                      className={`rounded-xl border px-3 py-2.5 text-sm font-semibold transition-all ${
                        difficulty === level
                          ? "border-[#4096ff] bg-[#4096ff]/20 text-[#4096ff]"
                          : "border-white/10 bg-white/5 text-[#94A3B8] hover:border-white/20 hover:text-white"
                      }`}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              {/* Start Button */}
              <button
                onClick={handleStartInterview}
                disabled={isStarting || !jobRole.trim()}
                className="group mt-2 flex w-full items-center justify-center gap-3 rounded-2xl bg-[#4096ff] px-6 py-4 text-base font-bold text-white shadow-lg shadow-blue-500/30 transition-all hover:bg-blue-500 hover:shadow-xl hover:shadow-blue-500/40 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isStarting ? (
                  <>
                    <div className="h-5 w-5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Setting up your interview...
                  </>
                ) : (
                  <>
                    <Video className="h-5 w-5" />
                    Start Interview Session
                    <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Feature Pills */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            {[
              { icon: Lock, text: "End-to-end encrypted" },
              { icon: Cpu, text: "Real-time AI analysis" },
              { icon: BarChart3, text: "Detailed analytics" },
              { icon: ShieldAlert, text: "Fraud detection" },
            ].map(({ icon: Icon, text }) => (
              <div
                key={text}
                className="flex items-center gap-2 rounded-full border border-[#1E293B] bg-white px-4 py-2 text-sm text-[#64748B] shadow-sm"
              >
                <Icon className="h-4 w-4 text-[#4096ff]" />
                {text}
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
