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
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/30",
    },
    "Needs Improvement": {
      icon: TriangleAlert,
      color: "text-amber-400",
      bg: "bg-amber-500/10",
      border: "border-amber-500/30",
    },
    "Not Recommended": {
      icon: CircleX,
      color: "text-rose-400",
      bg: "bg-rose-500/10",
      border: "border-rose-500/30",
    },
  };

  const current = config[status] || config["Needs Improvement"];
  const Icon = current.icon;

  return (
    <section className="bg-[#1E293B] border border-white/10 rounded-[28px] p-8 shadow-2xl">
      <h2 className="text-2xl font-bold text-white mb-8">
        Final Hiring Recommendation
      </h2>

      <div
        className={`rounded-2xl border p-8 ${current.bg} ${current.border}`}
      >
        <div className="flex items-center gap-4 mb-6">
          <Icon size={42} className={current.color} />

          <h3 className={`text-3xl font-extrabold ${current.color}`}>
            {status}
          </h3>
        </div>

        <p className="text-slate-200 leading-relaxed text-base font-medium">
          {summary}
        </p>
      </div>
    </section>
  );
}