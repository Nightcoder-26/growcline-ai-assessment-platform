"use client";

import Link from "next/link";
import {
  Video,
  ShieldCheck,
  UserCircle2,
  Clock3,
} from "lucide-react";

interface StudioHeaderProps {
  clock: string;
}

export function StudioHeader({ clock }: StudioHeaderProps) {
  return (
    <header className="sticky top-0 z-50 rounded-3xl border border-white/10 bg-[#111827]/80 px-6 py-5 shadow-[0_10px_40px_rgba(0,0,0,0.25)] backdrop-blur-xl">

      <div className="flex items-center justify-between">

        {/* Left */}

        <Link href="/" className="flex items-center gap-4 transition hover:opacity-90">

          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#4096ff] shadow-lg shadow-blue-500/30">

            <Video className="h-7 w-7 text-white" />

          </div>

          <div>

            <h1 className="text-2xl font-bold tracking-tight text-white">
              GrowCline
            </h1>

            <p className="text-sm text-slate-400">
              AI Powered Interview Platform
            </p>

          </div>

        </Link>

        {/* Right */}

        <div className="flex items-center gap-5">

          {/* Time */}

          <div className="hidden items-center gap-2 rounded-full border border-slate-700 bg-[#1E293B] px-4 py-2 md:flex">

            <Clock3 className="h-4 w-4 text-[#4096ff]" />

            <span className="font-mono text-sm text-white">
              {clock}
            </span>

          </div>

          {/* Ready */}

          <div className="flex items-center gap-2 rounded-full border border-green-500/20 bg-green-500/10 px-4 py-2">

            <ShieldCheck className="h-5 w-5 text-green-400" />

            <span className="font-semibold text-green-400">
              Ready
            </span>

          </div>

          {/* Candidate */}

          <div className="flex items-center gap-3 rounded-full border border-slate-700 bg-[#1E293B] px-3 py-2">

            <UserCircle2 className="h-9 w-9 text-[#4096ff]" />

            <div>

              <p className="text-sm font-semibold text-white">
                Candidate
              </p>

              <p className="text-xs text-slate-400">
                Interview Session
              </p>

            </div>

          </div>

        </div>

      </div>

    </header>
  );
}