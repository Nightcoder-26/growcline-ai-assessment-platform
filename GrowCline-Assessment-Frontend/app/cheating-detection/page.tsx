"use client";

import Link from "next/link";
import { BrainCircuit, ArrowRight } from "lucide-react";

export default function CheatingDetectionPage() {
  return (
    <main className="min-h-screen bg-[#0B1120] text-white flex items-center justify-center p-6">
      <div className="max-w-md w-full rounded-[28px] border border-white/10 bg-[#111827]/90 p-8 text-center space-y-6 backdrop-blur-xl shadow-2xl">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
          <BrainCircuit className="h-8 w-8" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Cheating Detection Integrated</h1>
          <p className="mt-2 text-sm text-slate-400 leading-relaxed">
            Cheating detection engine operates seamlessly in the backend during your interview and generates automated risk scores on completion.
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