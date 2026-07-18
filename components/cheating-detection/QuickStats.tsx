import {
  AlertTriangle,
  ShieldAlert,
  Clock3,
  Activity,
} from "lucide-react";

import { QuickStatsProps } from "@/types/cheating";

export default function QuickStats({
  events,
  riskScore,
  duration,
  status,
}: QuickStatsProps) {
  const stats = [
    {
      title: "Events",
      value: events,
      icon: AlertTriangle,
      color: "text-red-400",
      bg: "bg-red-500/10",
    },
    {
      title: "Risk Score",
      value: `${riskScore}%`,
      icon: ShieldAlert,
      color: "text-yellow-400",
      bg: "bg-yellow-500/10",
    },
    {
      title: "Duration",
      value: duration,
      icon: Clock3,
      color: "text-blue-400",
      bg: "bg-blue-500/10",
    },
    {
      title: "Status",
      value: status,
      icon: Activity,
      color: "text-green-400",
      bg: "bg-green-500/10",
    },
  ];

  return (
    <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => {
        const Icon = stat.icon;

        return (
          <div
            key={stat.title}
            className="rounded-2xl border border-slate-700 bg-[#111827] p-5 shadow-lg transition-all duration-300 hover:-translate-y-1 hover:border-[#4096FF]"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">
                  {stat.title}
                </p>

                <h3 className="mt-2 text-2xl font-bold text-white">
                  {stat.value}
                </h3>
              </div>

              <div className={`rounded-xl p-3 ${stat.bg}`}>
                <Icon
                  size={24}
                  className={stat.color}
                />
              </div>
            </div>
          </div>
        );
      })}
    </section>
  );
}