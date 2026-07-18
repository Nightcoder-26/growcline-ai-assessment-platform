import {
  UserCheck,
  Users,
  Monitor,
  Mic,
} from "lucide-react";

import { DetectionStatusCardsProps } from "@/types/cheating";

const iconMap = {
  face: UserCheck,
  users: Users,
  browser: Monitor,
  mic: Mic,
};

const statusStyles = {
  success: {
    badge: "bg-green-500/15 text-green-400",
    icon: "text-green-400",
  },
  warning: {
    badge: "bg-yellow-500/15 text-yellow-400",
    icon: "text-yellow-400",
  },
  danger: {
    badge: "bg-red-500/15 text-red-400",
    icon: "text-red-400",
  },
};

export default function DetectionStatusCards({
  cards,
}: DetectionStatusCardsProps) {
  return (
    <section className="rounded-2xl border border-slate-700 bg-[#111827] p-6 shadow-lg">
      <h2 className="mb-6 text-xl font-semibold text-white">
        Detection Status
      </h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => {
          const Icon = iconMap[card.icon];
          const style = statusStyles[card.status];

          return (
            <div
              key={card.title}
              className="rounded-xl border border-slate-700 bg-[#0F172A] p-5 transition-all duration-300 hover:border-[#4096FF] hover:shadow-lg"
            >
              <div className="mb-5 flex items-center justify-between">
                <div
                  className={`rounded-lg bg-slate-800 p-3 ${style.icon}`}
                >
                  <Icon size={22} />
                </div>

                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${style.badge}`}
                >
                  {card.status.toUpperCase()}
                </span>
              </div>

              <h3 className="text-sm text-slate-400">
                {card.title}
              </h3>

              <p className="mt-2 text-lg font-semibold text-white">
                {card.value}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}