"use client";

import Link from "next/link";
import { ShieldCheck, ArrowRight } from "lucide-react";

export default function LiveProctoringPage() {
  return (
    <main className="min-h-screen bg-[#0B1120] text-white flex items-center justify-center p-6">
      <div className="max-w-md w-full rounded-[28px] border border-white/10 bg-[#111827]/90 p-8 text-center space-y-6 backdrop-blur-xl shadow-2xl">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
          <ShieldCheck className="h-8 w-8" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Live Proctoring Integrated</h1>
          <p className="mt-2 text-sm text-slate-400 leading-relaxed">
            Live proctoring runs automatically in the backend during an active interview session. Standalone proctoring pages are no longer required.
          </p>
        </div>

        <Link
          href="/video-recording"
          className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#4096ff] py-3.5 font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-[#2f86ff]"
        >
          <span>Go to Interview Session</span>
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </main>
  );
}