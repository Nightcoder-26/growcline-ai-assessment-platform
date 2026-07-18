interface OverallScoreProps {
  score: number;
}

export default function OverallScore({
  score,
}: OverallScoreProps) {
  const circumference = 2 * Math.PI * 70;
  const progress = circumference - (score / 100) * circumference;

  return (
    <section className="bg-[#111827] border border-white/10 rounded-[28px] p-8">
      <h2 className="text-2xl font-semibold text-white mb-8">
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
              stroke="#1E293B"
              strokeWidth="12"
              fill="none"
            />

            <circle
              cx="90"
              cy="90"
              r="70"
              stroke="#4096FF"
              strokeWidth="12"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={progress}
            />
          </svg>

          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-5xl font-bold text-white">
              {score}%
            </span>

            <span className="text-slate-400 text-sm mt-2">
              Interview Score
            </span>
          </div>
        </div>

        <h3 className="text-2xl font-bold text-white mt-8">
          Excellent Performance
        </h3>

        <p className="text-slate-400 mt-3 max-w-lg text-center leading-7">
          Candidate demonstrated excellent technical knowledge,
          effective communication, and maintained a consistent
          interview performance throughout the session.
        </p>
      </div>
    </section>
  );
}