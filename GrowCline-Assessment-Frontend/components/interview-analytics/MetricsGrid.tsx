import {
  MessageSquare,
  Mic,
  Brain,
  Eye,
  ShieldAlert,
  Award,
} from "lucide-react";

interface MetricsGridProps {
  metrics: {
    confidence: number;
    communication: number;
    technical: number;
    eyeContact: number;
    riskScore: number;
    grade: string;
  };
}

export default function MetricsGrid({
  metrics,
}: MetricsGridProps) {
  const cards = [
    {
      title: "Confidence",
      value: `${metrics.confidence}%`,
      icon: MessageSquare,
      color: "text-emerald-400",
    },
    {
      title: "Communication",
      value: `${metrics.communication}%`,
      icon: Mic,
      color: "text-[#4096ff]",
    },
    {
      title: "Technical Knowledge",
      value: `${metrics.technical}%`,
      icon: Brain,
      color: "text-[#60a5fa]",
    },
    {
      title: "Eye Contact & Gaze",
      value: `${metrics.eyeContact}%`,
      icon: Eye,
      color: "text-cyan-400",
    },
    {
      title: "Cheating Risk Score",
      value: `${metrics.riskScore}%`,
      icon: ShieldAlert,
      color: metrics.riskScore > 30 ? "text-rose-400" : "text-emerald-400",
    },
    {
      title: "Assessment Grade",
      value: metrics.grade,
      icon: Award,
      color: "text-amber-400",
    },
  ];

  return (
    <section className="bg-[#1E293B] border border-white/10 rounded-[28px] p-8 shadow-2xl">
      <h2 className="text-2xl font-bold text-white mb-8">
        Performance Metrics
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
        {cards.map((card) => {
          const Icon = card.icon;

          return (
            <div
              key={card.title}
              className="bg-[#0F172A] rounded-2xl border border-white/10 p-6 hover:border-[#4096ff] transition-all"
            >
              <div className="flex items-center justify-between mb-6">
                <Icon className={`${card.color}`} size={28} />

                <span className="text-xs uppercase tracking-wider text-slate-500 font-semibold">
                  Metric
                </span>
              </div>

              <p className="text-slate-400 text-sm font-medium">
                {card.title}
              </p>

              <h3 className={`text-4xl font-extrabold mt-2 ${card.color}`}>
                {card.value}
              </h3>
            </div>
          );
        })}
      </div>
    </section>
  );
}