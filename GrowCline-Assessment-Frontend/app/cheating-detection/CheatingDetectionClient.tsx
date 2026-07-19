"use client";

import { useSearchParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useCheatingReport } from "@/hooks/useCheatingReport";

import DetectionHeader from "@/components/cheating-detection/DetectionHeader";
import QuickStats from "@/components/cheating-detection/QuickStats";
import RiskScoreCard from "@/components/cheating-detection/RiskScoreCard";
import DetectionStatusCards from "@/components/cheating-detection/DetectionStatusCards";
import EventsTimeline from "@/components/cheating-detection/EventsTimeline";
import EventsTable from "@/components/cheating-detection/EventsTable";
import RecommendationCard from "@/components/cheating-detection/RecommendationCard";

// ---------------------------------------------------------------------------
// Helpers — transform backend report → frontend prop shapes
// ---------------------------------------------------------------------------

function riskLevelToStatus(riskLevel: string): "success" | "warning" | "danger" {
  if (riskLevel === "LOW") return "success";
  if (riskLevel === "MEDIUM") return "warning";
  return "danger";
}

function buildStatusCards(eventCounts: Record<string, number>) {
  return [
    {
      title: "Face Detection",
      value: (eventCounts["NO_FACE"] ?? 0) === 0 ? "Detected" : "Missing",
      status: (eventCounts["NO_FACE"] ?? 0) === 0 ? "success" : "danger",
      icon: "face" as const,
    },
    {
      title: "Multiple Faces",
      value: (eventCounts["MULTIPLE_FACES"] ?? 0) === 0 ? "Not Detected" : `Detected (${eventCounts["MULTIPLE_FACES"]})`,
      status: (eventCounts["MULTIPLE_FACES"] ?? 0) === 0 ? "success" : "danger",
      icon: "users" as const,
    },
    {
      title: "Browser Focus",
      value: (eventCounts["TAB_SWITCH"] ?? 0) === 0 ? "Focused" : `${eventCounts["TAB_SWITCH"]} switches`,
      status: (eventCounts["TAB_SWITCH"] ?? 0) === 0 ? "success" : "warning",
      icon: "browser" as const,
    },
    {
      title: "Audio",
      value: (eventCounts["BACKGROUND_VOICE"] ?? 0) === 0 ? "Clear" : "Voice Detected",
      status: (eventCounts["BACKGROUND_VOICE"] ?? 0) === 0 ? "success" : "warning",
      icon: "mic" as const,
    },
  ] as const;
}

function buildEvents(eventCounts: Record<string, number>) {
  let id = 1;
  const events: { id: number; time: string; event: string; severity: "Low" | "Medium" | "High" }[] = [];

  const add = (key: string, label: string, sev: "Low" | "Medium" | "High") => {
    const count = eventCounts[key] ?? 0;
    for (let i = 0; i < count; i++) {
      events.push({ id: id++, time: "--:--", event: label, severity: sev });
    }
  };

  add("TAB_SWITCH", "Tab Switched", "High");
  add("NO_FACE", "Face Lost", "Medium");
  add("MULTIPLE_FACES", "Multiple Faces", "High");
  add("BACKGROUND_VOICE", "Voice Detected", "High");
  add("WINDOW_BLUR", "Window Blurred", "Low");
  add("FULLSCREEN_EXIT", "Fullscreen Exit", "Medium");
  add("CAMERA_DISABLED", "Camera Disabled", "High");
  add("MICROPHONE_DISABLED", "Microphone Disabled", "High");

  return events.slice(0, 20);
}

function buildRecommendation(riskLevel: string, eventCounts: Record<string, number>) {
  const reasons: string[] = [];

  if ((eventCounts["TAB_SWITCH"] ?? 0) > 0) reasons.push("Multiple tab switches detected.");
  if ((eventCounts["NO_FACE"] ?? 0) > 0) reasons.push("Face was temporarily unavailable.");
  if ((eventCounts["MULTIPLE_FACES"] ?? 0) > 0) reasons.push("Multiple faces detected in frame.");
  if ((eventCounts["BACKGROUND_VOICE"] ?? 0) > 0) reasons.push("Background voice activity detected.");
  if ((eventCounts["FULLSCREEN_EXIT"] ?? 0) > 0) reasons.push("Candidate exited fullscreen mode.");

  const recommendation =
    riskLevel === "LOW"
      ? "No action required."
      : riskLevel === "MEDIUM"
      ? "Review Recommended"
      : "Manual Review Required";

  return { recommendation, reasons: reasons.length ? reasons : ["No significant events detected."] };
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CheatingDetectionClient() {
  const searchParams = useSearchParams();
  const interviewId = searchParams?.get("interviewId") ?? null;
  const { role, isAuthenticated } = useAuth();

  const { report, loading, analyzing, error, notFound, isAdmin, analyze } =
    useCheatingReport(interviewId, role);

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
          <p className="text-slate-400 text-sm">Loading cheating report…</p>
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
          <h2 className="text-xl font-bold text-red-200">Error Loading Report</h2>
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
          <h2 className="text-xl font-bold text-white">Report Not Generated Yet</h2>
          <p className="text-slate-400 text-sm">
            The cheating detection analysis has not been run for this interview.
          </p>
          {isAdmin && (
            <button
              onClick={analyze}
              disabled={analyzing}
              className="mt-2 flex w-full items-center justify-center gap-2 rounded-2xl bg-[#4096ff] py-3 font-semibold text-white transition hover:bg-[#2f86ff] disabled:opacity-50"
            >
              {analyzing ? (
                <>
                  <span className="inline-block w-5 h-5 rounded-full border-2 border-white border-t-transparent animate-spin" />
                  Analyzing…
                </>
              ) : (
                "Run Analysis"
              )}
            </button>
          )}
          {!isAdmin && (
            <p className="text-xs text-slate-500">
              Contact an administrator to generate the report.
            </p>
          )}
        </div>
      </main>
    );
  }

  // ── Build derived data from report ────────────────────────────────────────

  const statusCards = buildStatusCards(report.eventCounts);
  const events = buildEvents(report.eventCounts);
  const { recommendation, reasons } = buildRecommendation(report.riskLevel, report.eventCounts);

  const headerStatus: "Monitoring" | "Completed" =
    report.updatedAt ? "Completed" : "Monitoring";

  return (
    <main className="min-h-screen bg-[#0B1120] p-6">
      <div className="mx-auto max-w-7xl space-y-6">

        {/* Admin action bar */}
        {isAdmin && (
          <div className="flex justify-end">
            <button
              onClick={analyze}
              disabled={analyzing}
              className="flex items-center gap-2 rounded-2xl bg-[#4096ff]/20 border border-[#4096ff]/40 px-5 py-2 text-sm font-semibold text-[#4096ff] transition hover:bg-[#4096ff]/30 disabled:opacity-50"
            >
              {analyzing ? (
                <>
                  <span className="inline-block w-4 h-4 rounded-full border-2 border-[#4096ff] border-t-transparent animate-spin" />
                  Re-analyzing…
                </>
              ) : (
                "↻ Re-run Analysis"
              )}
            </button>
          </div>
        )}

        {/* Header */}
        <DetectionHeader
          interview="AI Interview Session"
          candidate={report.userId}
          duration={report.updatedAt ? new Date(report.updatedAt).toLocaleTimeString() : "--:--"}
          sessionId={report.interviewId}
          status={headerStatus}
        />

        {/* Quick Stats */}
        <QuickStats
          events={report.totalEvents}
          riskScore={Math.round(report.riskScore)}
          duration={"--:--"}
          status={headerStatus}
        />

        {/* Risk Score */}
        <RiskScoreCard score={Math.round(report.riskScore)} />

        {/* Detection Status */}
        <DetectionStatusCards cards={[...statusCards]} />

        {/* Timeline & Events */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <EventsTimeline events={events} />
          <EventsTable events={events} />
        </div>

        {/* Recommendation */}
        <RecommendationCard
          recommendation={recommendation}
          reasons={reasons}
        />
      </div>
    </main>
  );
}
