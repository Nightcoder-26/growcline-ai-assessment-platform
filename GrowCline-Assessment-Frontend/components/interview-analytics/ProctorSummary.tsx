import {
  UserX,
  Users,
  MonitorSmartphone,
  Wifi,
  MicOff,
  Minimize,
} from "lucide-react";

interface ProctorSummaryProps {
  proctor: {
    faceMissing: number;
    multipleFaces: number;
    tabSwitches: number;
    networkIssues: number;
    microphoneIssues: number;
    fullscreenExits: number;
  };
}

export default function ProctorSummary({
  proctor,
}: ProctorSummaryProps) {
  const items = [
    {
      title: "Face Missing Events",
      value: proctor.faceMissing,
      icon: UserX,
      color: proctor.faceMissing > 0 ? "text-rose-400" : "text-emerald-400",
    },
    {
      title: "Multiple Faces Detected",
      value: proctor.multipleFaces,
      icon: Users,
      color: proctor.multipleFaces > 0 ? "text-amber-400" : "text-emerald-400",
    },
    {
      title: "Tab Switches",
      value: proctor.tabSwitches,
      icon: MonitorSmartphone,
      color: proctor.tabSwitches > 0 ? "text-amber-400" : "text-emerald-400",
    },
    {
      title: "Network Interruptions",
      value: proctor.networkIssues,
      icon: Wifi,
      color: "text-[#4096ff]",
    },
    {
      title: "Microphone Violations",
      value: proctor.microphoneIssues,
      icon: MicOff,
      color: proctor.microphoneIssues > 0 ? "text-rose-400" : "text-emerald-400",
    },
    {
      title: "Fullscreen Exits",
      value: proctor.fullscreenExits,
      icon: Minimize,
      color: proctor.fullscreenExits > 0 ? "text-rose-400" : "text-emerald-400",
    },
  ];

  return (
    <section className="bg-[#1E293B] border border-white/10 rounded-[28px] p-8 shadow-2xl">
      <h2 className="text-2xl font-bold text-white mb-8">
        Proctoring &amp; Behavioral Log Summary
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
        {items.map((item) => {
          const Icon = item.icon;

          return (
            <div
              key={item.title}
              className="bg-[#0F172A] rounded-2xl border border-white/10 p-6 hover:border-[#4096ff] transition-all"
            >
              <div className="flex justify-between items-center mb-6">
                <Icon className={item.color} size={28} />

                <span className={`text-4xl font-extrabold ${item.value > 0 ? "text-amber-400" : "text-white"}`}>
                  {item.value}
                </span>
              </div>

              <p className="text-slate-300 font-medium text-sm">
                {item.title}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}