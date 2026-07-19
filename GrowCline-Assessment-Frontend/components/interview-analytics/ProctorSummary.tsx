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
      title: "Face Missing",
      value: proctor.faceMissing,
      icon: UserX,
      color: "text-red-400",
    },
    {
      title: "Multiple Faces",
      value: proctor.multipleFaces,
      icon: Users,
      color: "text-orange-400",
    },
    {
      title: "Tab Switches",
      value: proctor.tabSwitches,
      icon: MonitorSmartphone,
      color: "text-yellow-400",
    },
    {
      title: "Network Issues",
      value: proctor.networkIssues,
      icon: Wifi,
      color: "text-blue-400",
    },
    {
      title: "Microphone Issues",
      value: proctor.microphoneIssues,
      icon: MicOff,
      color: "text-pink-400",
    },
    {
      title: "Fullscreen Exits",
      value: proctor.fullscreenExits,
      icon: Minimize,
      color: "text-purple-400",
    },
  ];

  return (
    <section className="bg-[#111827] border border-white/10 rounded-[28px] p-8">
      <h2 className="text-2xl font-semibold text-white mb-8">
        Proctoring Summary
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
        {items.map((item) => {
          const Icon = item.icon;

          return (
            <div
              key={item.title}
              className="bg-[#0B1120] rounded-2xl border border-white/10 p-6 hover:border-[#4096FF] transition-all"
            >
              <div className="flex justify-between items-center mb-6">
                <Icon className={item.color} size={28} />

                <span className="text-4xl font-bold text-white">
                  {item.value}
                </span>
              </div>

              <p className="text-slate-400">
                {item.title}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}