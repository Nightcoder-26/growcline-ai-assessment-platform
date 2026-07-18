import {
  Calendar,
  Clock,
  User,
  Briefcase,
  CheckCircle,
} from "lucide-react";

interface SummaryCardProps {
  candidate: string;
  interview: string;
  duration: string;
  date: string;
  status: "Completed";
}

export default function SummaryCard({
  candidate,
  interview,
  duration,
  date,
  status,
}: SummaryCardProps) {
  return (
    <section className="mt-8 bg-[#111827] border border-white/10 rounded-[28px] p-8">
      <h2 className="text-2xl font-semibold text-white mb-6">
        Interview Summary
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <InfoItem
          icon={<User size={20} />}
          label="Candidate"
          value={candidate}
        />

        <InfoItem
          icon={<Briefcase size={20} />}
          label="Interview"
          value={interview}
        />

        <InfoItem
          icon={<Clock size={20} />}
          label="Duration"
          value={duration}
        />

        <InfoItem
          icon={<Calendar size={20} />}
          label="Date"
          value={date}
        />

        <InfoItem
          icon={<CheckCircle size={20} />}
          label="Status"
          value={status}
          valueColor="text-green-400"
        />
      </div>
    </section>
  );
}

interface InfoItemProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  valueColor?: string;
}

function InfoItem({
  icon,
  label,
  value,
  valueColor = "text-white",
}: InfoItemProps) {
  return (
    <div className="bg-[#0B1120] rounded-2xl p-5 border border-white/10">
      <div className="flex items-center gap-2 text-[#4096FF] mb-3">
        {icon}
        <span className="text-sm text-slate-400">{label}</span>
      </div>

      <p className={`font-semibold text-lg ${valueColor}`}>
        {value}
      </p>
    </div>
  );
}