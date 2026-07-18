import {
  CircleCheckBig,
  TriangleAlert,
  CircleX,
} from "lucide-react";

interface RecommendationCardProps {
  status: "Recommended" | "Needs Improvement" | "Not Recommended";
  summary: string;
}

export default function RecommendationCard({
  status,
  summary,
}: RecommendationCardProps) {
  const config = {
    Recommended: {
      icon: CircleCheckBig,
      color: "text-green-400",
      bg: "bg-green-500/10",
      border: "border-green-500/30",
    },
    "Needs Improvement": {
      icon: TriangleAlert,
      color: "text-yellow-400",
      bg: "bg-yellow-500/10",
      border: "border-yellow-500/30",
    },
    "Not Recommended": {
      icon: CircleX,
      color: "text-red-400",
      bg: "bg-red-500/10",
      border: "border-red-500/30",
    },
  };

  const current = config[status];
  const Icon = current.icon;

  return (
    <section className="bg-[#111827] border border-white/10 rounded-[28px] p-8">
      <h2 className="text-2xl font-semibold text-white mb-8">
        Final Recommendation
      </h2>

      <div
        className={`rounded-2xl border p-8 ${current.bg} ${current.border}`}
      >
        <div className="flex items-center gap-4 mb-6">
          <Icon size={42} className={current.color} />

          <h3 className={`text-3xl font-bold ${current.color}`}>
            {status}
          </h3>
        </div>

        <p className="text-slate-300 leading-8 text-lg">
          {summary}
        </p>
      </div>
    </section>
  );
}