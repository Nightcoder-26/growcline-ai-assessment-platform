import { CheckCircle2, AlertTriangle } from "lucide-react";

interface AIInsightsProps {
  strengths: string[];
  improvements: string[];
}

export default function AIInsights({
  strengths,
  improvements,
}: AIInsightsProps) {
  return (
    <section className="bg-[#111827] border border-white/10 rounded-[28px] p-8">
      <h2 className="text-2xl font-semibold text-white mb-8">
        AI Insights
      </h2>

      <div className="space-y-4">
        {strengths.map((item, index) => (
          <div
            key={`strength-${index}`}
            className="flex items-center gap-4 bg-[#0B1120] border border-white/10 rounded-2xl p-5"
          >
            <CheckCircle2
              size={24}
              className="text-green-400 flex-shrink-0"
            />

            <p className="text-white">{item}</p>
          </div>
        ))}

        {improvements.map((item, index) => (
          <div
            key={`improvement-${index}`}
            className="flex items-center gap-4 bg-[#0B1120] border border-white/10 rounded-2xl p-5"
          >
            <AlertTriangle
              size={24}
              className="text-yellow-400 flex-shrink-0"
            />

            <p className="text-white">{item}</p>
          </div>
        ))}
      </div>
    </section>
  );
}