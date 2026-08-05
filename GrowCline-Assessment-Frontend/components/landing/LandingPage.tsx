/**
 * Landing Page — GrowCline AssessAI
 * Migrated from SaaS Landing Page Design/src/app/App.tsx
 * Route: /  (Next.js App Router)
 */

"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, LineChart, Line,
} from "recharts";
import {
  Brain, Code2, BarChart3, Shield, FileText,
  Play, Check, Star, ArrowRight, Menu, X,
  TrendingUp, Users, Clock, Eye, Cpu,
  BookOpen, Target, ChevronRight, Bell,
  Search, CircleCheck, ArrowUpRight, Zap,
  Lock, GitBranch, Link2,
} from "lucide-react";

// ─── Chart Data ───────────────────────────────────────────────────────────────
const scoreHistory = [
  { m: "Jan", you: 61, avg: 54 }, { m: "Feb", you: 67, avg: 56 },
  { m: "Mar", you: 72, avg: 57 }, { m: "Apr", you: 76, avg: 59 },
  { m: "May", you: 81, avg: 61 }, { m: "Jun", you: 85, avg: 62 },
  { m: "Jul", you: 89, avg: 64 }, { m: "Aug", you: 93, avg: 65 },
];
const pipelineWeeks = [
  { w: "Wk 1", screened: 48, advanced: 21, hired: 8 },
  { w: "Wk 2", screened: 62, advanced: 28, hired: 11 },
  { w: "Wk 3", screened: 55, advanced: 24, hired: 9 },
  { w: "Wk 4", screened: 74, advanced: 37, hired: 15 },
  { w: "Wk 5", screened: 69, advanced: 32, hired: 13 },
  { w: "Wk 6", screened: 83, advanced: 45, hired: 19 },
];
const topCandidates = [
  { name: "Aisha Patel",    role: "Senior SWE",      score: 94, status: "Recommended", init: "AP" },
  { name: "James Okafor",   role: "ML Engineer",     score: 91, status: "Recommended", init: "JO" },
  { name: "Mei Lin",        role: "Product Manager", score: 88, status: "In Review",    init: "ML" },
  { name: "Carlos Rivera",  role: "DevOps Lead",     score: 85, status: "In Review",    init: "CR" },
  { name: "Yuki Tanaka",    role: "Data Scientist",  score: 82, status: "Pending",      init: "YT" },
];

// ─── Tooltip styles ───────────────────────────────────────────────────────────
const TT_LIGHT = {
  borderRadius: 10, border: "1px solid rgba(30,41,59,0.08)",
  fontSize: 11, boxShadow: "0 8px 32px rgba(0,0,0,0.07)", padding: "8px 12px",
};
const TT_DARK = {
  background: "#1E293B", border: "1px solid rgba(255,255,255,0.06)",
  borderRadius: 10, fontSize: 11, padding: "8px 12px",
};

// ─── Primitives ───────────────────────────────────────────────────────────────
function Tag({ children, dark = false }: { children: React.ReactNode; dark?: boolean }) {
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold tracking-wide border ${
      dark
        ? "bg-white/8 text-[#93C5FD] border-white/10"
        : "bg-[#EFF6FF] text-[#4096FF] border-[#DBEAFE]"
    }`}>
      {children}
    </span>
  );
}

function SectionEyebrow({ label, dark = false }: { label: string; dark?: boolean }) {
  return (
    <div className="flex items-center gap-2 mb-5">
      <div className="w-[3px] h-5 rounded-full bg-[#4096FF]" />
      <span className={`text-[11px] font-bold tracking-[0.14em] uppercase ${dark ? "text-[#60A5FA]" : "text-[#4096FF]"}`}>
        {label}
      </span>
    </div>
  );
}

// ─── Twitter/X Icon (text-based replacement) ─────────────────────────────────
function XIcon({ size = 14, className = "" }: { size?: number; className?: string }) {
  return (
    <span
      style={{ fontSize: size, fontWeight: 900, lineHeight: 1, fontFamily: "system-ui" }}
      className={className}
      aria-label="X (Twitter)"
    >
      𝕏
    </span>
  );
}

// ─── Navbar ───────────────────────────────────────────────────────────────────
function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", fn);
    return () => window.removeEventListener("scroll", fn);
  }, []);
  const links = ["Features", "Assessments", "AI Interview", "Analytics", "Pricing", "Contact"];
  return (
    <header className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
      scrolled
        ? "bg-white/96 backdrop-blur-xl border-b border-[rgba(30,41,59,0.07)] shadow-[0_1px_24px_rgba(30,41,59,0.07)]"
        : "bg-transparent"
    }`}>
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8 h-[64px] flex items-center justify-between gap-8">
        <a href="#" className="flex items-center gap-2.5 shrink-0">
          <div className="w-[32px] h-[32px] rounded-[9px] bg-[#4096FF] flex items-center justify-center shadow-[0_2px_8px_rgba(64,150,255,0.4)]">
            <Brain size={16} className="text-white" />
          </div>
          <span className="text-[#1E293B] font-extrabold text-[18px] tracking-[-0.025em]">
            Assess<span className="text-[#4096FF]">AI</span>
          </span>
        </a>
        <nav className="hidden md:flex items-center gap-0">
          {links.map((l) => (
            <a key={l} href="#" className="px-4 py-2 text-[13.5px] font-medium text-[#64748B] hover:text-[#1E293B] rounded-xl transition-colors hover:bg-[rgba(30,41,59,0.04)]">
              {l}
            </a>
          ))}
        </nav>
        <div className="hidden md:flex items-center gap-3">
          <Link href="/login" className="text-[13.5px] font-medium text-[#64748B] hover:text-[#1E293B] transition-colors px-2">
            Log in
          </Link>
          <Link href="/signup" className="flex items-center gap-1.5 px-4 py-2 text-[13.5px] font-semibold text-white rounded-[10px] bg-[#4096FF] hover:bg-[#3580eb] transition-all shadow-[0_2px_10px_rgba(64,150,255,0.35)] hover:shadow-[0_4px_18px_rgba(64,150,255,0.45)]">
            Get Started <ChevronRight size={14} className="-mr-0.5" />
          </Link>
        </div>
        <button onClick={() => setOpen(!open)} className="md:hidden p-2 text-[#64748B] rounded-lg hover:bg-[#F1F5F9]">
          {open ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>
      {open && (
        <div className="md:hidden bg-white/98 backdrop-blur-xl border-t border-[rgba(30,41,59,0.06)] px-6 py-5 space-y-1 shadow-lg">
          {links.map((l) => (
            <a key={l} href="#" className="block px-4 py-3 text-[14px] font-medium text-[#475569] hover:text-[#1E293B] rounded-xl hover:bg-[#F8FAFC]">{l}</a>
          ))}
          <div className="pt-4 space-y-2 border-t border-[rgba(30,41,59,0.06)] mt-4">
            <Link href="/login" className="block text-center py-3 text-[14px] font-medium text-[#64748B]">Log in</Link>
            <Link href="/signup" className="block text-center py-3 text-[14px] font-semibold text-white rounded-[10px] bg-[#4096FF]">Get Started</Link>
          </div>
        </div>
      )}
    </header>
  );
}

// ─── HeroCard ─────────────────────────────────────────────────────────────────
function HeroCard() {
  return (
    <div className="relative hidden lg:block">
      <div className="absolute -inset-4 rounded-3xl bg-[#4096FF] opacity-[0.06] blur-2xl" />
      <div className="relative rounded-2xl overflow-hidden border border-[rgba(30,41,59,0.1)] bg-white shadow-[0_20px_70px_rgba(30,41,59,0.13)] ring-1 ring-inset ring-white/80">
        {/* Browser chrome */}
        <div className="flex items-center gap-3 px-4 py-3 bg-[#F8FAFC] border-b border-[rgba(30,41,59,0.07)]">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-[#FC6055]" />
            <div className="w-3 h-3 rounded-full bg-[#FEBC2E]" />
            <div className="w-3 h-3 rounded-full bg-[#28C840]" />
          </div>
          <div className="flex-1 flex justify-center">
            <div className="h-[22px] w-56 bg-white border border-[rgba(30,41,59,0.1)] rounded-md flex items-center justify-center gap-1.5 px-3">
              <Lock size={8} className="text-[#94A3B8]" />
              <span className="text-[9.5px] text-[#94A3B8] font-mono">app.assessai.com</span>
            </div>
          </div>
          <div className="w-6 h-6 rounded-md bg-white border border-[rgba(30,41,59,0.08)] flex items-center justify-center">
            <Bell size={10} className="text-[#94A3B8]" />
          </div>
        </div>

        {/* App shell */}
        <div className="flex" style={{ height: 460 }}>
          {/* Sidebar */}
          <aside className="w-[160px] shrink-0 bg-[#1E293B] flex flex-col py-4 px-2.5">
            <div className="flex items-center gap-2 px-2 mb-5">
              <div className="w-5 h-5 rounded-[5px] bg-[#4096FF] flex items-center justify-center"><Brain size={10} className="text-white" /></div>
              <span className="text-white text-[11px] font-bold tracking-tight">AssessAI</span>
            </div>
            <p className="px-2 text-[8.5px] font-bold tracking-widest text-[#475569] uppercase mb-2">Menu</p>
            {[
              { I: BarChart3, l: "Dashboard", a: true },
              { I: Users,     l: "Candidates" },
              { I: Brain,     l: "AI Interviews" },
              { I: FileText,  l: "Assessments" },
              { I: Code2,     l: "Coding Tests" },
              { I: Eye,       l: "Proctoring" },
              { I: TrendingUp,l: "Analytics" },
              { I: Shield,    l: "Compliance" },
            ].map(({ I, l, a }) => (
              <div key={l} className={`flex items-center gap-2 px-3 py-2 rounded-lg mb-0.5 ${a ? "bg-[#4096FF] text-white" : "text-[#64748B] hover:text-[#94A3B8]"}`}>
                <I size={11} />
                <span className="text-[10px] font-medium">{l}</span>
              </div>
            ))}
            <div className="mt-auto mx-1 p-2.5 rounded-xl bg-[#4096FF]/10 border border-[#4096FF]/20">
              <p className="text-[8.5px] font-semibold text-[#60A5FA] mb-1">Pro Plan Active</p>
              <div className="h-1 w-full bg-white/10 rounded-full"><div className="h-1 w-3/4 bg-[#4096FF] rounded-full" /></div>
              <p className="text-[7.5px] text-[#475569] mt-1">74% of monthly quota</p>
            </div>
          </aside>

          {/* Content */}
          <div className="flex-1 bg-[#F8FAFC] p-4 overflow-hidden">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-[12px] font-bold text-[#1E293B]">Good morning, Sarah 👋</p>
                <p className="text-[9.5px] text-[#94A3B8]">Mon, Oct 28 · Hiring dashboard</p>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-6 w-6 bg-white border border-[rgba(30,41,59,0.08)] rounded-md flex items-center justify-center"><Search size={9} className="text-[#94A3B8]" /></div>
                <div className="h-[26px] px-2.5 bg-[#4096FF] text-white text-[9px] font-bold rounded-lg flex items-center gap-1">+ New Assessment</div>
              </div>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-4 gap-2 mb-3">
              {[
                { l: "Candidates",   v: "3,284", d: "↑ 124", g: true  },
                { l: "Active Tests", v: "156",   d: "↑ 18",  g: true  },
                { l: "Avg Score",    v: "84.2%", d: "↑ 2.1%",g: true  },
                { l: "Fraud Alerts", v: "3",     d: "↓ 2",   g: false },
              ].map(({ l, v, d, g }) => (
                <div key={l} className="bg-white rounded-xl border border-[rgba(30,41,59,0.07)] p-3 shadow-[0_1px_3px_rgba(30,41,59,0.04)]">
                  <p className="text-[8px] text-[#94A3B8] font-semibold uppercase tracking-wide mb-1.5">{l}</p>
                  <p className="text-[16px] font-extrabold text-[#1E293B] leading-none tracking-tight">{v}</p>
                  <p className={`text-[8.5px] font-bold mt-1 ${g ? "text-[#10B981]" : "text-[#EF4444]"}`}>{d}</p>
                </div>
              ))}
            </div>

            {/* Chart */}
            <div className="bg-white rounded-xl border border-[rgba(30,41,59,0.07)] p-3 mb-3 shadow-[0_1px_3px_rgba(30,41,59,0.04)]">
              <div className="flex items-center justify-between mb-2">
                <p className="text-[10px] font-bold text-[#1E293B]">Score vs Industry</p>
                <div className="flex gap-3 text-[8px]">
                  <span className="flex items-center gap-1"><span className="inline-block w-3 h-0.5 bg-[#4096FF] rounded" />Yours</span>
                  <span className="flex items-center gap-1"><span className="inline-block w-3 h-0.5 bg-[#CBD5E1] rounded" />Avg</span>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={72}>
                <AreaChart data={scoreHistory} margin={{ top: 2, right: 2, left: -22, bottom: 0 }}>
                  <defs>
                    <linearGradient id="hero-card-score-fill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#4096FF" stopOpacity={0.18} />
                      <stop offset="100%" stopColor="#4096FF" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="m" tick={{ fontSize: 7.5, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 7.5, fill: "#94A3B8" }} axisLine={false} tickLine={false} domain={[50, 100]} />
                  <Tooltip contentStyle={{ ...TT_LIGHT, fontSize: 10 }} />
                  <Area type="monotone" dataKey="you" stroke="#4096FF" strokeWidth={1.8} fill="url(#hero-card-score-fill)" dot={false} name="Yours" />
                  <Area type="monotone" dataKey="avg" stroke="#CBD5E1" strokeWidth={1.2} fill="none" strokeDasharray="3 3" dot={false} name="Avg" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Candidates mini table */}
            <div className="bg-white rounded-xl border border-[rgba(30,41,59,0.07)] overflow-hidden shadow-[0_1px_3px_rgba(30,41,59,0.04)]">
              <div className="flex items-center justify-between px-3 py-2 border-b border-[rgba(30,41,59,0.05)]">
                <p className="text-[10px] font-bold text-[#1E293B]">Top Candidates</p>
                <button className="text-[8.5px] text-[#4096FF] font-semibold">View all →</button>
              </div>
              {topCandidates.slice(0, 4).map(({ name, role, score, status, init }) => (
                <div key={name} className="flex items-center gap-2 px-3 py-2 border-b border-[rgba(30,41,59,0.03)] last:border-0">
                  <div className="w-[22px] h-[22px] rounded-full bg-gradient-to-br from-[#4096FF] to-[#1E40AF] flex items-center justify-center text-white text-[7px] font-bold shrink-0">{init}</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[9.5px] font-semibold text-[#1E293B] truncate">{name}</p>
                    <p className="text-[8px] text-[#94A3B8]">{role}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-1.5 bg-[#F1F5F9] rounded-full"><div className="h-1.5 rounded-full bg-[#4096FF]" style={{ width: `${score}%` }} /></div>
                    <span className="text-[9px] font-bold text-[#1E293B] w-6 text-right">{score}</span>
                  </div>
                  <span className={`text-[7.5px] font-bold px-1.5 py-0.5 rounded ${
                    status === "Recommended" ? "bg-[#DCFCE7] text-[#16A34A]" :
                    status === "In Review"   ? "bg-[#FEF9C3] text-[#CA8A04]" :
                                              "bg-[#F1F5F9] text-[#64748B]"
                  }`}>{status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Hero ─────────────────────────────────────────────────────────────────────
function Hero() {
  return (
    <section className="relative overflow-hidden bg-[#F8FAFC] pt-20 pb-0 min-h-[100svh] flex flex-col justify-center">
      {/* Geometric background */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 opacity-[0.5]" style={{
          backgroundImage: "radial-gradient(circle, #CBD5E1 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }} />
        <div className="absolute -top-20 right-[-10%] w-[700px] h-[700px] rounded-full blur-[130px] opacity-[0.12]"
          style={{ background: "radial-gradient(circle, #4096FF, transparent 65%)" }} />
        <div className="absolute bottom-0 left-[-5%] w-[500px] h-[400px] rounded-full blur-[100px] opacity-[0.07]"
          style={{ background: "radial-gradient(circle, #1E293B, transparent 70%)" }} />
        <div className="absolute top-32 right-[42%] w-[500px] h-[500px] rounded-full border border-[#4096FF]/10" />
        <div className="absolute top-20 right-[38%] w-[700px] h-[700px] rounded-full border border-[#4096FF]/5" />
      </div>

      <div className="relative max-w-[1200px] mx-auto px-6 lg:px-8 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.05fr] gap-10 lg:gap-16 items-center py-12 lg:py-20">

          {/* Left — copy */}
          <div>
            <Tag>
              <span className="w-1.5 h-1.5 rounded-full bg-[#4096FF] animate-pulse" />
              Trusted by 1,200+ enterprises
            </Tag>

            <h1 className="mt-7 text-[clamp(36px,5.5vw,62px)] font-extrabold text-[#1E293B] leading-[1.07] tracking-[-0.033em]">
              AI-Powered
              <br />
              <span style={{
                backgroundImage: "linear-gradient(110deg, #4096FF 10%, #1E40AF 90%)",
                WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
              }}>
                Assessment &<br />Interview
              </span>
              <br />
              Intelligence
            </h1>

            <p className="mt-6 text-[17px] text-[#64748B] leading-[1.72] max-w-[480px]">
              Automate screening with adaptive AI interviews, live proctoring, and
              deep analytics. Go from applicant to offer in days, not weeks.
            </p>

            <div className="mt-9 flex flex-col sm:flex-row gap-3.5">
              <Link href="/signup" className="group inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-[11px] bg-[#4096FF] hover:bg-[#3580eb] text-white text-[14.5px] font-semibold transition-all shadow-[0_4px_18px_rgba(64,150,255,0.42)] hover:shadow-[0_6px_28px_rgba(64,150,255,0.54)] hover:-translate-y-px">
                Start for free
                <ArrowRight size={15} className="group-hover:translate-x-0.5 transition-transform" />
              </Link>
              <a href="#" className="group inline-flex items-center justify-center gap-2.5 px-6 py-3.5 rounded-[11px] bg-white border border-[rgba(30,41,59,0.14)] text-[#1E293B] text-[14.5px] font-semibold hover:border-[#4096FF]/40 hover:bg-white transition-all shadow-sm hover:shadow-md hover:-translate-y-px">
                <div className="w-[26px] h-[26px] rounded-full bg-[#EFF6FF] flex items-center justify-center shrink-0">
                  <Play size={9} className="text-[#4096FF] fill-[#4096FF] translate-x-[1px]" />
                </div>
                Watch 2-min demo
              </a>
            </div>

            <div className="mt-8 flex flex-wrap gap-x-5 gap-y-2.5">
              {["No credit card required", "14-day free trial", "SOC 2 Type II"].map((t) => (
                <div key={t} className="flex items-center gap-1.5 text-[13px] text-[#94A3B8]">
                  <Check size={13} className="text-[#4096FF]" strokeWidth={2.5} />
                  {t}
                </div>
              ))}
            </div>

            {/* Social proof avatars */}
            <div className="mt-10 flex items-center gap-4 pt-8 border-t border-[rgba(30,41,59,0.07)]">
              <div className="flex -space-x-2">
                {["#4096FF","#1E40AF","#3B82F6","#60A5FA","#93C5FD"].map((c, i) => (
                  <div key={i} className="w-8 h-8 rounded-full border-2 border-white flex items-center justify-center text-white text-[9px] font-bold"
                    style={{ background: c, zIndex: 5 - i }}>
                    {["SC","MW","PK","RN","AL"][i]}
                  </div>
                ))}
              </div>
              <div>
                <div className="flex gap-0.5 mb-0.5">
                  {[1,2,3,4,5].map(i => <Star key={i} size={11} className="text-[#FBBF24] fill-[#FBBF24]" />)}
                </div>
                <p className="text-[12px] text-[#94A3B8]"><span className="font-semibold text-[#1E293B]">4.9/5</span> from 2,400+ reviews</p>
              </div>
            </div>
          </div>

          {/* Right — Dashboard card */}
          <HeroCard />
        </div>
      </div>
    </section>
  );
}

// ─── LogoBar ──────────────────────────────────────────────────────────────────
function LogoBar() {
  const logos = ["Google","Microsoft","Amazon","Stripe","Airbnb","Notion","Vercel","Linear","Figma","Shopify"];
  return (
    <section className="py-14 bg-white border-y border-[rgba(30,41,59,0.06)]">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
        <p className="text-center text-[10.5px] font-bold text-[#CBD5E1] tracking-[0.2em] uppercase mb-9">
          Trusted by engineering and talent teams at
        </p>
        <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-5">
          {logos.map((n) => (
            <span key={n} className="text-[16px] font-black text-[#D1D5DB] hover:text-[#94A3B8] tracking-[-0.02em] transition-colors cursor-default select-none">{n}</span>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── Stats ────────────────────────────────────────────────────────────────────
function Stats() {
  const items = [
    { v: "2.4M+",  l: "Assessments completed", icon: FileText },
    { v: "58%",    l: "Faster time-to-hire",    icon: Clock },
    { v: "1,200+", l: "Enterprise customers",   icon: Users },
    { v: "96%",    l: "Candidate satisfaction", icon: Star },
  ];
  return (
    <section className="bg-[#F8FAFC] border-b border-[rgba(30,41,59,0.06)]">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 divide-x divide-y lg:divide-y-0 divide-[rgba(30,41,59,0.06)]">
          {items.map(({ v, l, icon: I }) => (
            <div key={l} className="flex flex-col items-center py-12 px-8">
              <div className="w-11 h-11 rounded-xl bg-[#EFF6FF] flex items-center justify-center mb-4">
                <I size={20} className="text-[#4096FF]" />
              </div>
              <span className="text-[38px] font-extrabold text-[#1E293B] tracking-[-0.04em] leading-none mb-2">{v}</span>
              <span className="text-[13px] text-[#94A3B8] font-medium text-center">{l}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── Features ─────────────────────────────────────────────────────────────────
const FEATURES = [
  { icon: Brain,    title: "AI Mock Interviews",      desc: "Adaptive AI interviewers that probe depth and reasoning across 60+ formats. Instant rubric-based feedback after every session.", tag: "Most Popular", metric: "4.9★ · 38k sessions",        dark: true  },
  { icon: BookOpen, title: "Aptitude Assessments",    desc: "Psychometrically validated tests for numerical reasoning, verbal ability, and abstract thinking — normed to your industry.",          tag: null,          metric: "200+ validated questions",   dark: false },
  { icon: Code2,    title: "Technical Assessments",   desc: "Role-specific evaluations covering system design, SQL, cloud architecture, and 40+ engineering domains. Auto-graded instantly.",     tag: null,          metric: "40+ engineering domains",    dark: false },
  { icon: Target,   title: "Coding Challenges",       desc: "Browser-native IDE with real-time execution. 300+ curated problems in Python, TypeScript, Go, Rust, Java, and more.",              tag: "New",          metric: "300+ curated problems",      dark: false },
  { icon: Eye,      title: "Live Proctoring",         desc: "AI face detection, gaze tracking, tab-switch alerts, and anomaly flagging — fully GDPR-compliant with a full audit trail.",         tag: null,          metric: "99.2% anomaly accuracy",     dark: false },
  { icon: BarChart3,title: "Analytics & AI Recs",     desc: "Cohort benchmarking, skill gap mapping, and predictive performance scores. AI ranks and recommends top candidates automatically.",   tag: null,          metric: "Real-time · Export ready",   dark: false },
];

function Features() {
  return (
    <section className="py-28 bg-white">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-8 mb-14">
          <div className="max-w-xl">
            <SectionEyebrow label="Platform Features" />
            <h2 className="text-[clamp(28px,3.8vw,44px)] font-extrabold text-[#1E293B] leading-[1.1] tracking-[-0.028em]">
              Every tool your hiring team needs, unified
            </h2>
          </div>
          <p className="text-[15.5px] text-[#64748B] leading-[1.7] max-w-md lg:text-right">
            Replace five disconnected tools with one coherent workflow — from first screen to signed offer.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURES.map(({ icon: I, title, desc, tag, metric, dark }) => (
            <div key={title} className={`group relative rounded-[20px] p-7 border flex flex-col transition-all duration-300 cursor-default ${
              dark
                ? "bg-[#1E293B] border-transparent shadow-xl"
                : "bg-white border-[rgba(30,41,59,0.09)] hover:border-[#4096FF]/30 hover:shadow-[0_10px_48px_rgba(64,150,255,0.09)] shadow-[0_2px_8px_rgba(30,41,59,0.05)]"
            }`}>
              {tag && (
                <span className={`absolute top-5 right-5 text-[10px] font-bold px-2.5 py-[3px] rounded-full ${
                  dark ? "bg-white/10 text-[#93C5FD]" : "bg-[#EFF6FF] text-[#4096FF]"
                }`}>{tag}</span>
              )}

              <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-6 transition-all duration-300 ${
                dark
                  ? "bg-[#4096FF] shadow-[0_4px_12px_rgba(64,150,255,0.4)]"
                  : "bg-[#EFF6FF] group-hover:bg-[#4096FF] group-hover:shadow-[0_4px_12px_rgba(64,150,255,0.35)]"
              }`}>
                <I size={20} className={dark ? "text-white" : "text-[#4096FF] group-hover:text-white transition-colors"} />
              </div>

              <h3 className={`text-[15.5px] font-bold mb-2.5 ${dark ? "text-white" : "text-[#1E293B]"}`}>{title}</h3>
              <p className="text-[13.5px] text-[#64748B] leading-[1.66] flex-1">{desc}</p>

              <div className={`flex items-center justify-between mt-6 pt-5 border-t ${dark ? "border-white/8" : "border-[rgba(30,41,59,0.07)]"}`}>
                <span className={`text-[11px] font-medium ${dark ? "text-[#475569]" : "text-[#94A3B8]"}`}>{metric}</span>
                <div className={`flex items-center gap-1 text-[11px] font-semibold opacity-0 group-hover:opacity-100 transition-opacity ${dark ? "text-[#60A5FA]" : "text-[#4096FF]"}`}>
                  Learn more <ArrowRight size={11} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── How It Works ─────────────────────────────────────────────────────────────
function HowItWorks() {
  const steps = [
    { n: "01", I: FileText,  title: "Build your assessment", body: "Pick from 500+ templates or create from scratch in minutes. Drag-and-drop builder, no engineers required." },
    { n: "02", I: Users,     title: "Invite candidates",     body: "Branded email invitations or direct ATS integration. One-click bulk invites with flexible scheduling." },
    { n: "03", I: Cpu,       title: "AI evaluates instantly",body: "Responses scored, proctored, and summarised the moment a candidate submits. Zero manual review." },
    { n: "04", I: BarChart3, title: "Hire with confidence",  body: "AI-ranked shortlists, evidence-based recommendations, and side-by-side comparisons. Decide in hours." },
  ];
  return (
    <section className="py-28 bg-[#F8FAFC]">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
        <div className="text-center max-w-[560px] mx-auto mb-18">
          <SectionEyebrow label="How It Works" />
          <h2 className="text-[clamp(28px,3.8vw,44px)] font-extrabold text-[#1E293B] leading-[1.1] tracking-[-0.028em] mb-5">
            From job post to hire in four steps
          </h2>
          <p className="text-[15.5px] text-[#64748B] leading-[1.7]">
            Teams go live the same day — no IT project, no migrations, no setup overhead.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 relative">
          {/* Connector line */}
          <div className="hidden lg:block absolute top-[52px] left-[calc(12.5%+28px)] right-[calc(12.5%+28px)] h-px"
            style={{ background: "linear-gradient(90deg, transparent, rgba(64,150,255,0.3) 20%, rgba(64,150,255,0.3) 80%, transparent)" }} />

          {steps.map(({ n, I, title, body }, i) => (
            <div key={n} className="relative bg-white rounded-[20px] border border-[rgba(30,41,59,0.08)] p-7 shadow-[0_2px_10px_rgba(30,41,59,0.05)] hover:shadow-[0_10px_40px_rgba(64,150,255,0.09)] hover:border-[#4096FF]/25 transition-all duration-300">
              <div className="flex items-center justify-between mb-6">
                <div className="w-14 h-14 rounded-2xl bg-[#EFF6FF] flex items-center justify-center">
                  <I size={22} className="text-[#4096FF]" />
                </div>
                <span className="text-[32px] font-black text-[rgba(30,41,59,0.06)] tracking-tighter leading-none">{n}</span>
              </div>
              <h3 className="text-[15px] font-bold text-[#1E293B] mb-2.5">{title}</h3>
              <p className="text-[13.5px] text-[#64748B] leading-[1.66]">{body}</p>
              {i < 3 && (
                <div className="hidden lg:flex absolute -right-3 top-[52px] -translate-y-1/2 z-10 w-6 h-6 rounded-full bg-white border border-[#DBEAFE] items-center justify-center shadow-sm">
                  <ChevronRight size={11} className="text-[#4096FF]" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ─── Dashboard Preview ────────────────────────────────────────────────────────
function DashboardPreview() {
  const [tab, setTab] = useState<"pipeline" | "trends">("pipeline");
  return (
    <section className="py-28 bg-[#1E293B] overflow-hidden relative">
      <div className="absolute inset-0 opacity-[0.025]" style={{
        backgroundImage: "radial-gradient(circle, #fff 1px, transparent 1px)",
        backgroundSize: "28px 28px",
      }} />
      <div className="absolute top-0 right-0 w-[700px] h-[600px] rounded-full bg-[#4096FF] opacity-[0.05] blur-[140px] pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[500px] h-[400px] rounded-full bg-[#4096FF] opacity-[0.03] blur-[100px] pointer-events-none" />

      <div className="relative max-w-[1200px] mx-auto px-6 lg:px-8">
        <div className="flex flex-col lg:flex-row items-start lg:items-end justify-between gap-8 mb-14">
          <div className="max-w-lg">
            <SectionEyebrow label="Product Preview" dark />
            <h2 className="text-[clamp(28px,3.8vw,44px)] font-extrabold text-white leading-[1.1] tracking-[-0.028em] mb-4">
              A command center for every hiring decision
            </h2>
            <p className="text-[15.5px] text-[#64748B] leading-[1.7]">
              Surface every candidate signal in real time. Filter by role, cohort,
              score band, or test type — no SQL, no spreadsheets.
            </p>
          </div>
          <div className="flex items-center gap-1.5 bg-[#0F172A] rounded-xl p-1 border border-white/5">
            {(["pipeline","trends"] as const).map((t) => (
              <button key={t} onClick={() => setTab(t)}
                className={`px-5 py-2 rounded-[9px] text-[13px] font-semibold capitalize transition-all ${
                  tab === t ? "bg-[#4096FF] text-white shadow-[0_2px_10px_rgba(64,150,255,0.4)]" : "text-[#475569] hover:text-[#64748B]"
                }`}>
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Dashboard window */}
        <div className="rounded-2xl border border-white/8 bg-[#0F172A] overflow-hidden shadow-[0_40px_100px_rgba(0,0,0,0.5)]">
          {/* Window chrome */}
          <div className="flex items-center gap-2 px-5 py-3.5 border-b border-white/5">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-white/10" />
              <div className="w-3 h-3 rounded-full bg-white/10" />
              <div className="w-3 h-3 rounded-full bg-white/10" />
            </div>
            <div className="flex-1 flex justify-center">
              <div className="w-[260px] h-6 bg-white/5 rounded-md flex items-center gap-1.5 px-3">
                <Lock size={8} className="text-[#475569]" />
                <span className="text-[9.5px] text-[#475569] font-mono">app.assessai.com/analytics</span>
              </div>
            </div>
            <div className="flex items-center gap-2 text-[9.5px] text-[#475569]">
              <span className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />Live
              </span>
            </div>
          </div>

          <div className="grid grid-cols-[175px_1fr]" style={{ minHeight: 440 }}>
            {/* Sidebar */}
            <div className="bg-[#1E293B] border-r border-white/5 p-3">
              {[
                { I: BarChart3,  l: "Overview",     a: true },
                { I: Users,      l: "Candidates" },
                { I: Brain,      l: "AI Interviews" },
                { I: Code2,      l: "Coding Tests" },
                { I: FileText,   l: "Assessments" },
                { I: Eye,        l: "Proctoring" },
                { I: TrendingUp, l: "Analytics",   a: tab === "trends" },
                { I: Shield,     l: "Compliance" },
              ].map(({ I, l, a }) => (
                <div key={l} className={`flex items-center gap-2.5 px-3 py-[9px] rounded-lg mb-0.5 transition-colors ${
                  a ? "bg-[#4096FF]/15 text-[#60A5FA]" : "text-[#475569] hover:text-[#64748B] hover:bg-white/4"
                }`}>
                  <I size={13} />
                  <span className="text-[11.5px] font-medium">{l}</span>
                  {a && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-[#4096FF]" />}
                </div>
              ))}
            </div>

            {/* Main panel */}
            <div className="p-6">
              <div className="grid grid-cols-4 gap-3 mb-5">
                {[
                  { l: "Total Candidates", v: "3,284", d: "+124 this wk", pos: true  },
                  { l: "Tests Active",     v: "156",   d: "+18 today",    pos: true  },
                  { l: "Avg Completion",   v: "84.2%", d: "+2.1%",        pos: true  },
                  { l: "Fraud Detected",   v: "3",     d: "−2 vs last wk",pos: false },
                ].map(({ l, v, d, pos }) => (
                  <div key={l} className="rounded-xl bg-[#1E293B] border border-white/5 p-4">
                    <p className="text-[9.5px] text-[#475569] font-semibold mb-2">{l}</p>
                    <p className="text-[22px] font-extrabold text-white leading-none tracking-tight mb-1.5">{v}</p>
                    <p className={`text-[9px] font-bold ${pos ? "text-[#10B981]" : "text-[#EF4444]"}`}>{d}</p>
                  </div>
                ))}
              </div>

              {tab === "pipeline" ? (
                <div className="grid grid-cols-[1fr_215px] gap-4">
                  <div className="bg-[#1E293B] rounded-xl border border-white/5 p-5">
                    <div className="flex items-center justify-between mb-4">
                      <p className="text-[12.5px] font-bold text-white">Hiring Pipeline</p>
                      <div className="flex gap-3">
                        {[{ l: "Screened", c: "#1E3A5F" }, { l: "Advanced", c: "#2563EB" }, { l: "Hired", c: "#4096FF" }].map(({ l, c }) => (
                          <div key={l} className="flex items-center gap-1.5"><div className="w-2.5 h-2.5 rounded-sm" style={{ background: c }} /><span className="text-[10px] text-[#475569]">{l}</span></div>
                        ))}
                      </div>
                    </div>
                    <ResponsiveContainer width="100%" height={168}>
                      <BarChart data={pipelineWeeks} barGap={3} barCategoryGap="32%">
                        <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.04)" />
                        <XAxis dataKey="w" tick={{ fontSize: 10, fill: "#475569" }} axisLine={false} tickLine={false} />
                        <YAxis tick={{ fontSize: 10, fill: "#475569" }} axisLine={false} tickLine={false} />
                        <Tooltip contentStyle={TT_DARK} labelStyle={{ color: "#94A3B8" }} cursor={{ fill: "rgba(255,255,255,0.025)" }} />
                        <Bar dataKey="screened" name="Screened" fill="#1E3A5F" radius={[3,3,0,0]} />
                        <Bar dataKey="advanced" name="Advanced" fill="#2563EB" radius={[3,3,0,0]} />
                        <Bar dataKey="hired"    name="Hired"    fill="#4096FF" radius={[3,3,0,0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="space-y-3">
                    <div className="bg-[#1E293B] rounded-xl border border-white/5 p-4">
                      <p className="text-[11.5px] font-bold text-white mb-3.5">Score Distribution</p>
                      {[
                        { r: "90–100", p: 18, c: "#4096FF" },
                        { r: "75–89",  p: 34, c: "#60A5FA" },
                        { r: "60–74",  p: 28, c: "#93C5FD" },
                        { r: "< 60",   p: 20, c: "#1E3A5F" },
                      ].map(({ r, p, c }) => (
                        <div key={r} className="mb-3">
                          <div className="flex justify-between mb-1"><span className="text-[9.5px] text-[#475569]">{r}</span><span className="text-[9.5px] font-bold text-[#94A3B8]">{p}%</span></div>
                          <div className="h-1.5 w-full bg-white/5 rounded-full"><div className="h-1.5 rounded-full" style={{ width: `${p * 2.5}%`, background: c }} /></div>
                        </div>
                      ))}
                    </div>
                    <div className="bg-[#1E293B] rounded-xl border border-white/5 p-4">
                      <p className="text-[11.5px] font-bold text-white mb-3">AI Recommendations</p>
                      {topCandidates.slice(0, 3).map(({ name, status }) => (
                        <div key={name} className="flex items-center justify-between py-1.5">
                          <span className="text-[10px] text-[#64748B]">{name}</span>
                          <span className={`text-[8.5px] font-bold px-2 py-0.5 rounded-full ${
                            status === "Recommended" ? "bg-[#4096FF]/15 text-[#60A5FA]" : "bg-white/5 text-[#475569]"
                          }`}>{status}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-[#1E293B] rounded-xl border border-white/5 p-5" style={{ height: 248 }}>
                  <div className="flex items-center justify-between mb-4">
                    <p className="text-[12.5px] font-bold text-white">8-Month Performance Trend</p>
                    <span className="text-[10px] font-semibold text-[#10B981] bg-[#10B981]/10 px-2.5 py-1 rounded-full">↑ +32 pts YoY</span>
                  </div>
                  <ResponsiveContainer width="100%" height={172}>
                    <LineChart data={scoreHistory} margin={{ left: -15, right: 8 }}>
                      <defs>
                        <linearGradient id="preview-trend-line-gradient" x1="0" y1="0" x2="1" y2="0">
                          <stop offset="0%" stopColor="#1E40AF" />
                          <stop offset="100%" stopColor="#4096FF" />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.04)" />
                      <XAxis dataKey="m" tick={{ fontSize: 10, fill: "#475569" }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 10, fill: "#475569" }} axisLine={false} tickLine={false} domain={[50, 100]} />
                      <Tooltip contentStyle={TT_DARK} labelStyle={{ color: "#94A3B8" }} />
                      <Line type="monotone" dataKey="you" stroke="url(#preview-trend-line-gradient)" strokeWidth={2.5} dot={{ fill: "#4096FF", strokeWidth: 0, r: 3 }} name="Your Score" />
                      <Line type="monotone" dataKey="avg" stroke="#2D3748" strokeWidth={1.5} strokeDasharray="5 4" dot={false} name="Industry Avg" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ─── Analytics Section ────────────────────────────────────────────────────────
function AnalyticsSection() {
  return (
    <section className="py-28 bg-white">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_1.15fr] gap-16 items-start">
          <div>
            <SectionEyebrow label="Analytics & Intelligence" />
            <h2 className="text-[clamp(28px,3.8vw,44px)] font-extrabold text-[#1E293B] leading-[1.1] tracking-[-0.028em] mb-5">
              Data-driven decisions on every hire
            </h2>
            <p className="text-[15.5px] text-[#64748B] leading-[1.7] mb-10">
              Surface hidden talent, map skill gaps, and benchmark candidates against
              industry standards. AI generates hiring recommendations grounded in
              evidence — not gut feel.
            </p>

            <div className="space-y-5 mb-10">
              {[
                { t: "Predictive Performance Scores", d: "ML models trained on 2.4M+ assessments predict on-the-job performance with 89% accuracy." },
                { t: "Cohort Benchmarking",           d: "Compare any candidate against your top performers, role norms, or industry percentile bands." },
                { t: "Full Historical Records",       d: "Persistent profiles with every assessment, score, and progression — searchable forever." },
              ].map(({ t, d }) => (
                <div key={t} className="flex gap-4">
                  <div className="mt-0.5 w-5 h-5 rounded-full bg-[#EFF6FF] border border-[#DBEAFE] flex items-center justify-center shrink-0">
                    <Check size={11} className="text-[#4096FF]" strokeWidth={2.5} />
                  </div>
                  <div>
                    <p className="text-[14.5px] font-bold text-[#1E293B] mb-0.5">{t}</p>
                    <p className="text-[13.5px] text-[#64748B] leading-[1.65]">{d}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-3 gap-3">
              {[
                { v: "89%",  l: "Prediction accuracy", s: "ML model" },
                { v: "4.2h", l: "Time-to-screen",       s: "vs 3-day avg" },
                { v: "−67%", l: "Bias reduction",        s: "vs manual" },
              ].map(({ v, l, s }) => (
                <div key={l} className="rounded-[16px] border border-[rgba(30,41,59,0.08)] p-4 bg-[#F8FAFC] hover:border-[#4096FF]/25 transition-colors text-center">
                  <p className="text-[26px] font-extrabold text-[#1E293B] tracking-tight leading-none mb-1">{v}</p>
                  <p className="text-[12px] font-semibold text-[#1E293B]">{l}</p>
                  <p className="text-[11px] text-[#94A3B8] mt-0.5">{s}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Right — chart panel */}
          <div className="space-y-4">
            <div className="rounded-[20px] border border-[rgba(30,41,59,0.08)] bg-white p-7 shadow-[0_4px_28px_rgba(30,41,59,0.07)]">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <p className="text-[15px] font-bold text-[#1E293B]">Score vs Industry Benchmark</p>
                  <p className="text-[12.5px] text-[#94A3B8] mt-0.5">8-month trend · All assessments</p>
                </div>
                <span className="text-[11px] font-bold text-[#10B981] bg-[#DCFCE7] px-3 py-1 rounded-full">+14.2% YoY</span>
              </div>
              <ResponsiveContainer width="100%" height={210}>
                <AreaChart data={scoreHistory} margin={{ left: -10, right: 4 }}>
                  <defs>
                    <linearGradient id="analytics-score-area-fill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#4096FF" stopOpacity={0.14} />
                      <stop offset="100%" stopColor="#4096FF" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 4" stroke="rgba(30,41,59,0.05)" />
                  <XAxis dataKey="m" tick={{ fontSize: 11, fill: "#94A3B8" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 11, fill: "#94A3B8" }} axisLine={false} tickLine={false} domain={[50, 100]} />
                  <Tooltip contentStyle={TT_LIGHT} />
                  <Area type="monotone" dataKey="you" stroke="#4096FF" strokeWidth={2.5} fill="url(#analytics-score-area-fill)" dot={false} name="Your Score" />
                  <Area type="monotone" dataKey="avg" stroke="#CBD5E1" strokeWidth={1.5} fill="none" strokeDasharray="5 4" dot={false} name="Industry Avg" />
                </AreaChart>
              </ResponsiveContainer>
              <div className="flex gap-5 mt-4 pt-4 border-t border-[rgba(30,41,59,0.06)]">
                <span className="flex items-center gap-2 text-[11.5px] text-[#94A3B8]">
                  <span className="inline-block w-5 h-[2px] bg-[#4096FF] rounded" />Your score
                </span>
                <span className="flex items-center gap-2 text-[11.5px] text-[#94A3B8]">
                  <span className="inline-block w-5 h-[2px] bg-[#CBD5E1] rounded" />Industry avg
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {[
                { v: "2.4M+", l: "Assessments run",       icon: FileText },
                { v: "96%",   l: "Candidate satisfaction", icon: Star },
              ].map(({ v, l, icon: I }) => (
                <div key={l} className="rounded-[16px] border border-[rgba(30,41,59,0.08)] p-6 bg-[#F8FAFC] hover:border-[#4096FF]/25 transition-colors">
                  <I size={20} className="text-[#4096FF] mb-3.5" />
                  <p className="text-[30px] font-extrabold text-[#1E293B] tracking-tight leading-none mb-1.5">{v}</p>
                  <p className="text-[13px] text-[#94A3B8] font-medium">{l}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ─── Testimonials ─────────────────────────────────────────────────────────────
function Testimonials() {
  const tms = [
    { name: "Sarah Chen",     role: "Head of Talent Acquisition", co: "Stripe",  init: "SC",
      quote: "AssessAI cut our time-to-hire by 58% while measurably improving quality. The AI interview module delivers the most signal-rich data I've seen from any screening tool.", feat: true },
    { name: "Marcus Williams",role: "VP Engineering",             co: "Airbnb",  init: "MW",
      quote: "The coding environment is production-grade. Candidates feel at ease and we get genuine engineering signal — not just puzzle performance.", feat: false },
    { name: "Priya Kapoor",   role: "Director of People Ops",     co: "Notion",  init: "PK",
      quote: "Live proctoring gave our compliance team full confidence. The analytics dashboard is the clearest I've seen in any HR tool.", feat: false },
  ];
  return (
    <section className="py-28 bg-[#F8FAFC]">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
        <div className="text-center mb-16">
          <SectionEyebrow label="Testimonials" />
          <h2 className="text-[clamp(28px,3.8vw,44px)] font-extrabold text-[#1E293B] leading-[1.1] tracking-[-0.028em]">
            Loved by hiring leaders worldwide
          </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-[1.55fr_1fr] gap-5">
          {tms.filter((t) => t.feat).map(({ name, role, co, init, quote }) => (
            <div key={name} className="rounded-[22px] bg-[#1E293B] p-10 flex flex-col justify-between shadow-xl">
              <div>
                <div className="flex gap-1 mb-7">
                  {[1,2,3,4,5].map(i => <Star key={i} size={14} className="text-[#FBBF24] fill-[#FBBF24]" />)}
                </div>
                <blockquote className="text-[19px] text-[#CBD5E1] leading-[1.65] font-medium">&ldquo;{quote}&rdquo;</blockquote>
              </div>
              <div className="flex items-center gap-4 pt-8 mt-8 border-t border-white/8">
                <div className="w-11 h-11 rounded-full bg-gradient-to-br from-[#4096FF] to-[#1E40AF] flex items-center justify-center text-white text-[12px] font-bold shrink-0">{init}</div>
                <div>
                  <p className="text-[14.5px] font-bold text-white">{name}</p>
                  <p className="text-[12.5px] text-[#475569]">{role} · {co}</p>
                </div>
                <span className="ml-auto text-[11px] font-bold text-[#4096FF] bg-[#4096FF]/12 border border-[#4096FF]/20 px-3 py-1 rounded-full">{co}</span>
              </div>
            </div>
          ))}

          <div className="flex flex-col gap-5">
            {tms.filter((t) => !t.feat).map(({ name, role, co, init, quote }) => (
              <div key={name} className="rounded-[22px] bg-white border border-[rgba(30,41,59,0.09)] p-8 flex flex-col gap-5 shadow-[0_2px_12px_rgba(30,41,59,0.05)] hover:border-[#4096FF]/25 hover:shadow-[0_8px_32px_rgba(64,150,255,0.08)] transition-all flex-1">
                <div className="flex gap-1">
                  {[1,2,3,4,5].map(i => <Star key={i} size={12} className="text-[#FBBF24] fill-[#FBBF24]" />)}
                </div>
                <blockquote className="text-[14.5px] text-[#475569] leading-[1.68] flex-1">&ldquo;{quote}&rdquo;</blockquote>
                <div className="flex items-center gap-3 pt-5 border-t border-[rgba(30,41,59,0.06)]">
                  <div className="w-9 h-9 rounded-full bg-[#EFF6FF] flex items-center justify-center text-[#4096FF] text-[10px] font-bold shrink-0">{init}</div>
                  <div>
                    <p className="text-[13.5px] font-bold text-[#1E293B]">{name}</p>
                    <p className="text-[12px] text-[#94A3B8]">{role} · {co}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

// ─── CTA ──────────────────────────────────────────────────────────────────────
function CTA() {
  return (
    <section className="py-20 bg-white border-t border-[rgba(30,41,59,0.06)]">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
        <div className="relative rounded-[26px] bg-[#1E293B] overflow-hidden px-8 sm:px-14 py-16 lg:py-20">
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute inset-0 opacity-[0.025]" style={{
              backgroundImage: "radial-gradient(circle, #fff 1px, transparent 1px)",
              backgroundSize: "24px 24px",
            }} />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] rounded-full bg-[#4096FF] opacity-[0.09] blur-[80px]" />
            <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full border border-[#4096FF]/10" />
            <div className="absolute -bottom-16 -left-16 w-48 h-48 rounded-full border border-[#4096FF]/8" />
          </div>

          <div className="relative text-center">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#4096FF]/15 border border-[#4096FF]/25 mb-8">
              <Zap size={11} className="text-[#60A5FA]" />
              <span className="text-[11px] font-bold text-[#93C5FD] tracking-wide">Set up in under 5 minutes</span>
            </div>

            <h2 className="text-[clamp(28px,5vw,54px)] font-extrabold text-white leading-[1.07] tracking-[-0.033em] mb-5 max-w-2xl mx-auto">
              Ready to Transform<br />Candidate Assessments?
            </h2>
            <p className="text-[16px] text-[#64748B] max-w-lg mx-auto mb-10 leading-[1.72]">
              Join 1,200+ companies that cut time-to-hire by 58% and hire with
              measurably higher confidence. No card required, cancel anytime.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/signup" className="flex items-center gap-2 px-8 py-4 bg-[#4096FF] hover:bg-[#3580eb] text-white text-[15px] font-bold rounded-[12px] transition-all shadow-[0_4px_22px_rgba(64,150,255,0.55)] hover:shadow-[0_6px_32px_rgba(64,150,255,0.65)] hover:-translate-y-px">
                Start Free Trial <ArrowRight size={16} />
              </Link>
              <a href="#" className="flex items-center gap-2 px-8 py-4 border border-white/15 text-white text-[15px] font-semibold rounded-[12px] hover:bg-white/6 hover:border-white/25 transition-all">
                Talk to Sales <ArrowUpRight size={15} />
              </a>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-6 mt-10">
              {["14-day free trial","No credit card","Cancel anytime","SOC 2 certified"].map((t) => (
                <div key={t} className="flex items-center gap-1.5 text-[12.5px] text-[#475569]">
                  <CircleCheck size={13} className="text-[#4096FF]" />
                  {t}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ─── Footer ───────────────────────────────────────────────────────────────────
function Footer() {
  const cols = [
    { h: "Product",    links: ["AI Interviews","Aptitude Tests","Technical Assessments","Coding Challenges","Live Proctoring","Analytics"] },
    { h: "Company",    links: ["About us","Blog","Careers","Press kit","Partners","Contact"] },
    { h: "Developers", links: ["Documentation","API Reference","SDKs & Libraries","Status","Changelog","GitHub"] },
    { h: "Legal",      links: ["Privacy Policy","Terms of Service","GDPR","SOC 2 Report","Cookie Policy","CCPA"] },
  ];
  return (
    <footer className="bg-[#1E293B]">
      <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-[220px_1fr] gap-12 py-16 border-b border-white/7">
          <div>
            <div className="flex items-center gap-2.5 mb-5">
              <div className="w-[32px] h-[32px] rounded-[9px] bg-[#4096FF] flex items-center justify-center shadow-[0_2px_8px_rgba(64,150,255,0.4)]">
                <Brain size={16} className="text-white" />
              </div>
              <span className="text-white font-extrabold text-[18px] tracking-[-0.025em]">
                Assess<span className="text-[#4096FF]">AI</span>
              </span>
            </div>
            <p className="text-[13.5px] text-[#475569] leading-[1.7] mb-6 max-w-[200px]">
              The intelligence layer for modern talent acquisition teams.
            </p>
            <div className="flex gap-2">
              <a href="#" className="w-9 h-9 rounded-[9px] bg-white/5 hover:bg-white/10 border border-white/7 flex items-center justify-center transition-colors">
                <XIcon size={14} className="text-[#475569]" />
              </a>
              <a href="#" className="w-9 h-9 rounded-[9px] bg-white/5 hover:bg-white/10 border border-white/7 flex items-center justify-center transition-colors">
                <Link2 size={14} className="text-[#475569]" />
              </a>
              <a href="#" className="w-9 h-9 rounded-[9px] bg-white/5 hover:bg-white/10 border border-white/7 flex items-center justify-center transition-colors">
                <GitBranch size={14} className="text-[#475569]" />
              </a>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-8">
            {cols.map(({ h, links }) => (
              <div key={h}>
                <p className="text-[11px] font-bold tracking-[0.14em] uppercase text-[#64748B] mb-5">{h}</p>
                <ul className="space-y-3">
                  {links.map((l) => (
                    <li key={l}><a href="#" className="text-[13.5px] text-[#475569] hover:text-[#94A3B8] transition-colors">{l}</a></li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between py-7 gap-4">
          <p className="text-[12.5px] text-[#334155]">© 2025 AssessAI, Inc. All rights reserved.</p>
          <div className="flex items-center gap-2 text-[12px] text-[#334155]">
            <Shield size={12} className="text-[#475569]" />
            <span>SOC 2 Type II</span>
            <span className="mx-1.5 opacity-30">·</span>
            <span>GDPR Compliant</span>
            <span className="mx-1.5 opacity-30">·</span>
            <span>ISO 27001</span>
            <span className="mx-1.5 opacity-30">·</span>
            <span>CCPA Ready</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

// ─── Landing Page ─────────────────────────────────────────────────────────────
export default function LandingPage() {
  return (
    <div
      className="min-h-screen antialiased bg-[#F8FAFC] text-[#1E293B]"
      style={{ fontFamily: "'Inter', system-ui, -apple-system, sans-serif" }}
    >
      <style>{`
        * { scrollbar-width: none; }
        *::-webkit-scrollbar { display: none; }
      `}</style>
      <Navbar />
      <main>
        <Hero />
        <LogoBar />
        <Stats />
        <Features />
        <HowItWorks />
        <DashboardPreview />
        <AnalyticsSection />
        <Testimonials />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}
