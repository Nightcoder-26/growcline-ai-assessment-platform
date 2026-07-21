interface OverallScoreProps {
  score: number;
}

export default function OverallScore({
  score,
}: OverallScoreProps) {
  const circumference = 2 * Math.PI * 70;
  const progress = circumference - (Math.max(0, Math.min(100, score)) / 100) * circumference;

  const getVerdict = (s: number) => {
    if (s >= 85) return { title: "Excellent Performance", text: "Candidate demonstrated strong domain knowledge, effective communication, and maintained solid integrity throughout the interview." };
    if (s >= 70) return { title: "Good Performance", text: "Candidate performed well across questions with moderate performance and satisfactory session integrity." };
    if (s >= 50) return { title: "Average Performance", text: "Candidate showed mixed technical capabilities with some proctoring flags noted during the session." };
    return { title: "Needs Improvement", text: "Multiple proctoring violations or low evaluation scores recorded. Manual review is recommended." };
  };

  const verdict = getVerdict(score);

  return (
    <section className="bg-[#1E293B] border border-white/10 rounded-[28px] p-8 shadow-2xl">
      <h2 className="text-2xl font-bold text-white mb-8">
        Overall Performance
      </h2>

      <div className="flex flex-col items-center">
        <div className="relative w-48 h-48">
          <svg
            className="w-48 h-48 -rotate-90"
            viewBox="0 0 180 180"
          >
            <circle
              cx="90"
              cy="90"
              r="70"
              stroke="#0F172A"
              strokeWidth="12"
              fill="none"
            />

            <circle
              cx="90"
              cy="90"
              r="70"
              stroke="#4096ff"
              strokeWidth="12"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={progress}
            />
          </svg>

          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-5xl font-extrabold text-white">
              {score}%
            </span>

            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider mt-1">
              Final Score
            </span>
          </div>
        </div>

        <h3 className="text-2xl font-bold text-white mt-8">
          {verdict.title}
        </h3>

        <p className="text-slate-300 mt-3 max-w-lg text-center leading-relaxed text-sm font-medium">
          {verdict.text}
        </p>
      </div>
    </section>
  );
}