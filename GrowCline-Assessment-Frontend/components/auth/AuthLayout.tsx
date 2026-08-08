"use client";

/**
 * AuthLayout — Split-screen wrapper for Login & Signup pages.
 * Left panel: brand illustration + testimonial
 * Right panel: form slot
 */

import { useEffect, useState } from "react";
import Link from "next/link";
import { Brain, Shield, Zap, Users, TrendingUp } from "lucide-react";

// ─── Animated floating stats card ─────────────────────────────────────────────
function StatCard({
  icon: Icon,
  value,
  label,
  delay = 0,
}: {
  icon: React.ElementType;
  value: string;
  label: string;
  delay?: number;
}) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(t);
  }, [delay]);

  return (
    <div
      className="flex items-center gap-3 bg-white/10 backdrop-blur-md border border-white/15 rounded-2xl px-4 py-3 shadow-lg transition-all duration-700"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0px)" : "translateY(12px)",
      }}
    >
      <div className="w-9 h-9 rounded-xl bg-[#4096FF]/20 flex items-center justify-center shrink-0">
        <Icon size={16} className="text-[#60A5FA]" />
      </div>
      <div>
        <p className="text-white font-extrabold text-[15px] leading-none tracking-tight">
          {value}
        </p>
        <p className="text-[#94A3B8] text-[11px] mt-0.5">{label}</p>
      </div>
    </div>
  );
}

// ─── Brand panel (left) ───────────────────────────────────────────────────────
function BrandPanel() {
  return (
    <div className="hidden lg:flex flex-col justify-between h-full px-12 py-12 bg-[#1E293B] relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 pointer-events-none">
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: "radial-gradient(circle, #fff 1px, transparent 1px)",
            backgroundSize: "28px 28px",
          }}
        />
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-[#4096FF] opacity-[0.07] blur-[80px]" />
        <div className="absolute -top-24 -right-24 w-72 h-72 rounded-full border border-[#4096FF]/10" />
        <div className="absolute -bottom-16 -left-16 w-56 h-56 rounded-full border border-[#4096FF]/8" />
      </div>

      {/* Logo */}
      <div className="relative flex items-center gap-3">
        <div className="w-10 h-10 rounded-[11px] bg-[#4096FF] flex items-center justify-center shadow-[0_4px_16px_rgba(64,150,255,0.5)]">
          <Brain size={20} className="text-white" />
        </div>
        <span className="text-white font-extrabold text-[22px] tracking-[-0.03em]">
          Assess<span className="text-[#4096FF]">AI</span>
        </span>
      </div>

      {/* Hero copy */}
      <div className="relative space-y-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#4096FF]/15 border border-[#4096FF]/25">
          <Zap size={11} className="text-[#60A5FA]" />
          <span className="text-[11px] font-bold text-[#93C5FD] tracking-wide">
            AI-Powered Assessment Platform
          </span>
        </div>

        <h2 className="text-[clamp(28px,3.5vw,44px)] font-extrabold text-white leading-[1.1] tracking-[-0.03em]">
          Hire smarter.
          <br />
          <span className="text-[#4096FF]">Assess faster.</span>
        </h2>

        <p className="text-[15px] text-[#64748B] leading-[1.75] max-w-[340px]">
          Join 1,200+ companies that transformed their hiring with adaptive AI
          interviews, live proctoring, and deep analytics.
        </p>

        {/* Stat cards */}
        <div className="space-y-3 pt-2">
          <StatCard icon={Users} value="3,200+" label="Candidates assessed" delay={150} />
          <StatCard icon={TrendingUp} value="58% faster" label="Time-to-hire reduction" delay={300} />
          <StatCard icon={Shield} value="SOC 2 Type II" label="Enterprise security" delay={450} />
        </div>
      </div>

      {/* Bottom testimonial */}
      <div className="relative bg-white/5 border border-white/10 rounded-2xl p-5">
        <p className="text-[13.5px] text-[#94A3B8] leading-[1.7] italic mb-4">
          &ldquo;AssessAI cut our screening time by 70%. The AI insights are
          remarkably accurate and our recruiters love it.&rdquo;
        </p>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-[#4096FF] flex items-center justify-center font-bold text-white text-[13px]">
            SP
          </div>
          <div>
            <p className="text-white font-semibold text-[13px]">Sarah Park</p>
            <p className="text-[#64748B] text-[11px]">Head of Talent · Nexgen Corp</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Top mobile logo bar ───────────────────────────────────────────────────────
function MobileLogoBar() {
  return (
    <div className="lg:hidden flex items-center justify-center gap-2.5 py-6 border-b border-[rgba(30,41,59,0.07)]">
      <div className="w-8 h-8 rounded-[9px] bg-[#4096FF] flex items-center justify-center shadow-[0_2px_8px_rgba(64,150,255,0.4)]">
        <Brain size={15} className="text-white" />
      </div>
      <Link
        href="/"
        className="text-[#1E293B] font-extrabold text-[18px] tracking-[-0.025em] hover:opacity-80 transition-opacity"
      >
        Assess<span className="text-[#4096FF]">AI</span>
      </Link>
    </div>
  );
}

// ─── Auth Layout ───────────────────────────────────────────────────────────────
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-[#F8FAFC]">
      {/* Left: brand panel */}
      <div className="lg:w-[480px] xl:w-[520px] shrink-0">
        <BrandPanel />
      </div>

      {/* Right: form area */}
      <div className="flex-1 flex flex-col">
        <MobileLogoBar />
        <div className="flex-1 flex items-center justify-center px-6 py-10 lg:py-16">
          <div className="w-full max-w-[440px]">{children}</div>
        </div>
      </div>
    </div>
  );
}
