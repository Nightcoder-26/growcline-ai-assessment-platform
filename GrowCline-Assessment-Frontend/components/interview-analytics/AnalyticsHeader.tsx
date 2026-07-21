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
    <header className="bg-[#1E293B] border border-white/10 rounded-[28px] px-8 py-6 flex items-center justify-between shadow-2xl">
      <div>
        <h1 className="text-3xl font-extrabold text-white">
          Interview Analytics &amp; Integrity Report
        </h1>

        <p className="text-slate-400 mt-1 font-medium">
          {interview} • Candidate ID: {candidate}
        </p>
      </div>

      <button
        onClick={() => window.print()}
        className="
          flex items-center
          gap-2
          bg-[#4096ff]
          hover:bg-[#60a5fa]
          transition-colors
          text-white
          px-5
          py-3
          rounded-2xl
          font-bold
          shadow-lg
        "
      >
        <Download size={18} />
        Export PDF Report
      </button>
    </header>
  );
}