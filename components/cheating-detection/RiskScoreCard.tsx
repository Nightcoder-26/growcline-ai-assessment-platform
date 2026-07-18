"use client";

import {
  CircularProgressbar,
  buildStyles,
} from "react-circular-progressbar";

import "react-circular-progressbar/dist/styles.css";

import {
  ShieldAlert,
  CheckCircle2,
} from "lucide-react";

import { RiskScoreCardProps } from "@/types/cheating";

export default function RiskScoreCard({
  score,
}: RiskScoreCardProps) {
  const getRiskDetails = (score: number) => {
    if (score <= 30) {
      return {
        label: "Low Risk",
        color: "#22C55E",
        description: "No suspicious activity detected.",
      };
    }

    if (score <= 60) {
      return {
        label: "Medium Risk",
        color: "#F59E0B",
        description: "Some suspicious activity detected.",
      };
    }

    return {
      label: "High Risk",
      color: "#EF4444",
      description: "Multiple suspicious activities detected.",
    };
  };

  const risk = getRiskDetails(score);

  return (
    <section
      className="rounded-2xl border-l-4 border-slate-700 bg-[#111827]
      shadow-lg"
      style={{
        borderLeftColor: risk.color,
      }}
    >
      <div className="p-8">
        <div className="mb-8 flex items-center gap-3">
          <ShieldAlert
            className="text-[#4096FF]"
            size={28}
          />

          <div>
            <h2 className="text-2xl font-bold text-white">
              Overall Risk Score
            </h2>

            <p className="text-slate-400">
              AI generated interview integrity score
            </p>
          </div>
        </div>

        <div className="flex flex-col items-center gap-10 lg:flex-row">
          <div className="h-48 w-48">
            <CircularProgressbar
              value={score}
              text={`${score}%`}
              styles={buildStyles({
                pathColor: risk.color,
                textColor: "#FFFFFF",
                trailColor: "#1E293B",
                strokeLinecap: "round",
                textSize: "18px",
              })}
            />
          </div>

          <div className="flex-1">
            <span
              className="rounded-full px-4 py-2 text-sm font-semibold"
              style={{
                backgroundColor: `${risk.color}20`,
                color: risk.color,
              }}
            >
              {risk.label.toUpperCase()}
            </span>

            <h3 className="mt-5 text-3xl font-bold text-white">
              Overall Integrity Score
            </h3>

            <p className="mt-3 max-w-xl text-slate-400">
              {risk.description}
            </p>

            <div className="mt-8">
              <h4 className="mb-4 text-lg font-semibold text-white">
                Risk Factors
              </h4>

              <div className="space-y-3">
                {[
                  "Face Detection",
                  "Browser Activity",
                  "Audio Monitoring",
                ].map((item) => (
                  <div
                    key={item}
                    className="flex items-center gap-3"
                  >
                    <CheckCircle2
                      size={18}
                      className="text-[#4096FF]"
                    />

                    <span className="text-slate-300">
                      {item}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}