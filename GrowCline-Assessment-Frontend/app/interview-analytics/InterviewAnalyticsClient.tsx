"use client";

import { useSearchParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useAnalytics } from "@/hooks/useAnalytics";

import AnalyticsHeader from "@/components/interview-analytics/AnalyticsHeader";
import SummaryCard from "@/components/interview-analytics/SummaryCard";
import OverallScore from "@/components/interview-analytics/OverallScore";
import MetricsGrid from "@/components/interview-analytics/MetricsGrid";
import ProctorSummary from "@/components/interview-analytics/ProctorSummary";
import AIInsights from "@/components/interview-analytics/AIInsights";
import RecommendationCard from "@/components/interview-analytics/RecommendationCard";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Convert riskScore (0-100) to a confidence-style score (inverse) */
function riskToConfidence(riskScore: number): number {
  return Math.max(0, Math.min(100, Math.round(100 - riskScore)));
}

/** Duration in seconds → "X Minutes" label */
function formatDuration(seconds: number): string {
  if (!seconds) return "0 Minutes";
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return s > 0 ? `${m} min ${s} sec` : `${m} Minutes`;
}

/** Format ISO date string to human-readable */
function formatDate(iso: string | null): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString("en-IN", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

/** Map overallStatus → RecommendationCard status */
function mapStatus(overallStatus: string): "Recommended" | "Not Recommended" | "Needs Improvement" {
  if (overallStatus === "PASSED") return "Recommended";
  if (overallStatus === "FLAGGED") return "Not Recommended";
  return "Needs Improvement";
}

/** Map riskLevel → AI-generated strengths/improvements */
function buildInsights(riskLevel: string, tabSwitches: number, multipleFaces: number) {
  const strengths: string[] = [];
  const improvements: string[] = [];

  if (tabSwitches === 0) strengths.push("Maintained full browser focus throughout the session.");
  if (multipleFaces === 0) strengths.push("No multiple faces detected — single-candidate integrity confirmed.");
  if (riskLevel === "LOW") strengths.push("Overall risk score is low, indicating honest conduct.");

  if (tabSwitches > 0) improvements.push(`Reduce tab switching — detected ${tabSwitches} times.`);
  if (multipleFaces > 0) improvements.push(`Avoid having other people in the frame — detected ${multipleFaces} times.`);
  if (riskLevel === "HIGH" || riskLevel === "CRITICAL") improvements.push("High-risk behaviour patterns detected. Manual review is recommended.");

  if (!strengths.length) strengths.push("Session was completed successfully.");
  if (!improvements.length) improvements.push("Continue maintaining interview integrity standards.");

  return { strengths, improvements };
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function InterviewAnalyticsClient() {
  const searchParams = useSearchParams();
  const interviewId = searchParams?.get("interviewId") ?? null;
  const { role } = useAuth();

  const { report, loading, generating, error, notFound, generateReport } =
    useAnalytics(interviewId, role);

  // ── Guard: no interviewId ─────────────────────────────────────────────────

  if (!interviewId) {
    return (
      <main className="min-h-screen bg-[#0B1120] flex items-center justify-center p-8">
        <div className="max-w-md w-full rounded-[28px] border border-yellow-500/30 bg-yellow-900/20 p-8 text-center space-y-4">
          <div className="text-5xl">⚠️</div>
          <h2 className="text-xl font-bold text-yellow-200">No Interview ID</h2>
          <p className="text-yellow-300/80 text-sm">
            Navigate here with{" "}
            <code className="text-yellow-100 bg-yellow-900/40 px-1 rounded">
              ?interviewId=&lt;id&gt;
            </code>
          </p>
        </div>
      </main>
    );
  }

  // ── Guard: loading ────────────────────────────────────────────────────────

  if (loading) {
    return (
      <main className="min-h-screen bg-[#0B1120] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-[#4096ff] border-t-transparent animate-spin" />
          <p className="text-slate-400 text-sm">Loading interview analytics…</p>
        </div>
      </main>
    );
  }

  // ── Guard: error ──────────────────────────────────────────────────────────

  if (error) {
    return (
      <main className="min-h-screen bg-[#0B1120] flex items-center justify-center p-8">
        <div className="max-w-md w-full rounded-[28px] border border-red-500/30 bg-red-900/20 p-8 text-center space-y-4">
          <div className="text-5xl">❌</div>
          <h2 className="text-xl font-bold text-red-200">Error Loading Analytics</h2>
          <p className="text-red-300/80 text-sm">{error}</p>
        </div>
      </main>
    );
  }

  // ── Guard: report not yet generated ──────────────────────────────────────

  if (notFound || !report) {
    return (
      <main className="min-h-screen bg-[#0B1120] flex items-center justify-center p-8">
        <div className="max-w-md w-full rounded-[28px] border border-slate-500/30 bg-[#111827]/80 p-8 text-center space-y-4">
          <div className="text-5xl">📊</div>
          <h2 className="text-xl font-bold text-white">Analytics Not Generated</h2>
          <p className="text-slate-400 text-sm">
            No analytics report found for this interview. Generate one to view results.
          </p>
          <button
            onClick={() => generateReport(false)}
            disabled={generating}
            className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[#4096ff] py-3 font-semibold text-white transition hover:bg-[#2f86ff] disabled:opacity-50"
          >
            {generating ? (
              <>
                <span className="inline-block w-5 h-5 rounded-full border-2 border-white border-t-transparent animate-spin" />
                Generating…
              </>
            ) : (
              "Generate Analytics"
            )}
          </button>
        </div>
      </main>
    );
  }

  // ── Derive display values from report ────────────────────────────────────

  const confidence = riskToConfidence(report.riskScore);
  const overallScore = confidence; // Use confidence as a proxy for overall score
  const { strengths, improvements } = buildInsights(
    report.riskLevel,
    report.tabSwitches,
    report.multipleFaces
  );

  return (
    <main className="min-h-screen bg-[#0B1120] p-8">
      <div className="max-w-7xl mx-auto space-y-8">

        {/* Refresh button */}
        <div className="flex justify-end">
          <button
            onClick={() => generateReport(true)}
            disabled={generating}
            className="flex items-center gap-2 rounded-2xl bg-[#4096ff]/20 border border-[#4096ff]/40 px-5 py-2 text-sm font-semibold text-[#4096ff] transition hover:bg-[#4096ff]/30 disabled:opacity-50"
          >
            {generating ? (
              <>
                <span className="inline-block w-4 h-4 rounded-full border-2 border-[#4096ff] border-t-transparent animate-spin" />
                Refreshing…
              </>
            ) : (
              "↻ Refresh Report"
            )}
          </button>
        </div>

        <AnalyticsHeader
          interview="AI Interview Session"
          candidate={report.userId}
        />

        <SummaryCard
          candidate={report.userId}
          interview="AI Interview"
          duration={formatDuration(report.durationSeconds)}
          date={formatDate(report.generatedAt)}
          status="Completed"
        />

        <OverallScore score={overallScore} />

        <MetricsGrid
          metrics={{
            confidence,
            communication: confidence,
            technical: confidence,
            eyeContact: report.totalEvents === 0 ? 90 : Math.max(40, confidence - 10),
            riskScore: Math.round(report.riskScore),
            grade:
              overallScore >= 90
                ? "A+"
                : overallScore >= 80
                ? "A"
                : overallScore >= 70
                ? "B"
                : overallScore >= 60
                ? "C"
                : "D",
          }}
        />

        <ProctorSummary
          proctor={{
            faceMissing: report.totalEvents - report.multipleFaces - report.tabSwitches - report.backgroundVoice - report.fullscreenExit,
            multipleFaces: report.multipleFaces,
            tabSwitches: report.tabSwitches,
            networkIssues: 0,
            microphoneIssues: report.microphoneDisabled,
            fullscreenExits: report.fullscreenExit,
          }}
        />

        <AIInsights strengths={strengths} improvements={improvements} />

        <RecommendationCard
          status={mapStatus(report.overallStatus)}
          summary={`Overall risk level: ${report.riskLevel}. ${
            report.overallStatus === "PASSED"
              ? "Candidate passed proctoring with no significant issues."
              : report.overallStatus === "FLAGGED"
              ? "Critical proctoring violations detected. Manual review strongly recommended."
              : "Some proctoring events were detected. A review is recommended before final decision."
          } Risk score: ${report.riskScore.toFixed(1)}/100. Total events: ${report.totalEvents}.`}
        />
      </div>
    </main>
  );
}
