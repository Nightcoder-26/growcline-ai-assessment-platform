import { Download } from "lucide-react";

interface AnalyticsHeaderProps {
  interview: string;
  candidate: string;
}

export default function AnalyticsHeader({
  interview,
  candidate,
}: AnalyticsHeaderProps) {
  return (
    <header className="bg-[#111827] border border-white/10 rounded-[28px] px-8 py-6 flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold text-white">
          Interview Analytics
        </h1>

        <p className="text-slate-400 mt-2">
          {interview} • {candidate}
        </p>
      </div>

      <button
        className="
          flex items-center
          gap-2
          bg-[#4096FF]
          hover:bg-blue-500
          transition-colors
          text-white
          px-5
          py-3
          rounded-xl
          font-medium
        "
      >
        <Download size={18} />
        Export Report
      </button>
    </header>
  );
}