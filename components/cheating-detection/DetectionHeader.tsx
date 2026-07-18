import {
  ShieldCheck,
  User,
  Clock3,
  BadgeInfo,
  FileDown,
  SquareX,
} from "lucide-react";

import { DetectionHeaderProps } from "@/types/cheating";

export default function DetectionHeader({
  interview,
  candidate,
  duration,
  sessionId,
  status,
}: DetectionHeaderProps) {
  return (
    <section className="rounded-2xl border border-slate-700 bg-[#111827] p-6 shadow-lg">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        {/* Left Side */}
        <div className="flex-1">
          <div className="mb-6 flex items-center gap-3">
            <div className="rounded-xl bg-[#4096FF]/20 p-3">
              <ShieldCheck
                size={28}
                className="text-[#4096FF]"
              />
            </div>

            <div>
              <h1 className="text-2xl font-bold text-white">
                Cheating Detection Engine
              </h1>

              <p className="text-sm text-slate-400">
                AI-powered interview monitoring dashboard
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 text-sm sm:grid-cols-2">
            <div className="flex items-center gap-3">
              <User
                size={18}
                className="text-[#4096FF]"
              />

              <div>
                <p className="text-slate-400">
                  Candidate
                </p>

                <p className="font-medium text-white">
                  {candidate}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <BadgeInfo
                size={18}
                className="text-[#4096FF]"
              />

              <div>
                <p className="text-slate-400">
                  Interview
                </p>

                <p className="font-medium text-white">
                  {interview}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Clock3
                size={18}
                className="text-[#4096FF]"
              />

              <div>
                <p className="text-slate-400">
                  Duration
                </p>

                <p className="font-medium text-white">
                  {duration}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <BadgeInfo
                size={18}
                className="text-[#4096FF]"
              />

              <div>
                <p className="text-slate-400">
                  Session ID
                </p>

                <p className="font-medium text-white">
                  {sessionId}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side */}
        <div className="flex flex-col items-start gap-4 lg:items-end">
          <span className="rounded-full bg-green-500/15 px-4 py-2 text-sm font-semibold text-green-400">
            ● {status}
          </span>

          <div className="flex flex-wrap gap-3">
            <button className="flex items-center gap-2 rounded-lg bg-[#4096FF] px-4 py-2 text-white transition hover:opacity-90">
              <FileDown size={18} />
              Export Report
            </button>

            <button className="flex items-center gap-2 rounded-lg bg-red-500 px-4 py-2 text-white transition hover:bg-red-600">
              <SquareX size={18} />
              End Session
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}