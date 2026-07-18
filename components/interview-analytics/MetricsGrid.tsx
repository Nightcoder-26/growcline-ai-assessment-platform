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
      color: "text-green-400",
    },
    {
      title: "Communication",
      value: `${metrics.communication}%`,
      icon: Mic,
      color: "text-blue-400",
    },
    {
      title: "Technical",
      value: `${metrics.technical}%`,
      icon: Brain,
      color: "text-purple-400",
    },
    {
      title: "Eye Contact",
      value: `${metrics.eyeContact}%`,
      icon: Eye,
      color: "text-cyan-400",
    },
    {
      title: "Risk Score",
      value: `${metrics.riskScore}%`,
      icon: ShieldAlert,
      color: "text-red-400",
    },
    {
      title: "Grade",
      value: metrics.grade,
      icon: Award,
      color: "text-yellow-400",
    },
  ];

  return (
    <section className="bg-[#111827] border border-white/10 rounded-[28px] p-8">
      <h2 className="text-2xl font-semibold text-white mb-8">
        Performance Metrics
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
        {cards.map((card) => {
          const Icon = card.icon;

          return (
            <div
              key={card.title}
              className="bg-[#0B1120] rounded-2xl border border-white/10 p-6 hover:border-[#4096FF] transition-all"
            >
              <div className="flex items-center justify-between mb-6">
                <Icon className={`${card.color}`} size={28} />

                <span className="text-xs uppercase tracking-wider text-slate-500">
                  Metric
                </span>
              </div>

              <p className="text-slate-400 text-sm">
                {card.title}
              </p>

              <h3 className={`text-4xl font-bold mt-2 ${card.color}`}>
                {card.value}
              </h3>
            </div>
          );
        })}
      </div>
    </section>
  );
}