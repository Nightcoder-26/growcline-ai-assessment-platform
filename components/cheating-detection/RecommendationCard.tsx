import {
  Bot,
  ShieldAlert,
  CheckCircle2,
} from "lucide-react";

import { RecommendationProps } from "@/types/cheating";

export default function RecommendationCard({
  recommendation,
  reasons,
}: RecommendationProps) {
  return (
    <section className="rounded-2xl border border-slate-700 bg-[#111827] p-8 shadow-lg">
      <div className="mb-6 flex items-center gap-3">
        <Bot
          className="text-[#4096FF]"
          size={28}
        />

        <div>
          <h2 className="text-2xl font-bold text-white">
            AI Recommendation
          </h2>

          <p className="text-slate-400">
            Final interview integrity assessment
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-5">
        <div className="flex items-center gap-3">
          <ShieldAlert
            className="text-red-400"
            size={22}
          />

          <span className="text-lg font-semibold text-red-400">
            {recommendation}
          </span>
        </div>
      </div>

      <div className="mt-8">
        <h3 className="mb-3 text-lg font-semibold text-white">
          AI Summary
        </h3>

        <p className="text-slate-400">
          Multiple suspicious activities were detected during
          the interview. Based on browser activity, voice
          monitoring, and face tracking, this interview should
          be reviewed manually before final evaluation.
        </p>
      </div>

      <div className="mt-8">
        <h3 className="mb-4 text-lg font-semibold text-white">
          Findings
        </h3>

        <div className="space-y-3">
          {reasons.map((reason, index) => (
            <div
              key={index}
              className="flex items-center gap-3"
            >
              <CheckCircle2
                size={18}
                className="text-[#4096FF]"
              />

              <span className="text-slate-300">
                {reason}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-8 rounded-xl bg-[#0F172A] p-5">
        <div className="mb-2 flex justify-between">
          <span className="text-slate-400">
            Overall Integrity
          </span>

          <span className="font-semibold text-white">
            72%
          </span>
        </div>

        <div className="h-3 overflow-hidden rounded-full bg-slate-700">
          <div className="h-full w-[72%] rounded-full bg-red-500" />
        </div>
      </div>
    </section>
  );
}