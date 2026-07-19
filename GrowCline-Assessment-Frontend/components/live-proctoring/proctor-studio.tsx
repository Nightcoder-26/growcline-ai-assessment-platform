"use client";

import { useSearchParams } from "next/navigation";

import { ProctorHeader } from "./proctor-header";
import { CandidateStage } from "./candidate-stage";
import { StatusPanel } from "./status-panel";
import { AlertsPanel } from "./alerts-panel";
import { WarningTimeline } from "./warning-timeline";
import { ActivityLog } from "./activity-log";

import { useProctoring } from "@/hooks/useProctoring";
import { useAuth } from "@/hooks/useAuth";

export function ProctorStudio() {
  const searchParams = useSearchParams();
  const interviewId = searchParams?.get("interviewId") ?? null;

  const { userId } = useAuth();

  const { status, alerts, logs, timeline, error } = useProctoring(interviewId, userId);

  // ── No interview ID guard ─────────────────────────────────────────────────

  if (!interviewId) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center p-8">
        <div className="max-w-md w-full rounded-[28px] border border-yellow-500/30 bg-yellow-900/20 p-8 text-center space-y-4">
          <div className="text-5xl">⚠️</div>
          <h2 className="text-xl font-bold text-yellow-200">No Interview ID</h2>
          <p className="text-yellow-300/80 text-sm">
            Navigate here with a valid{" "}
            <code className="text-yellow-100 bg-yellow-900/40 px-1 rounded">?interviewId=&lt;id&gt;</code>{" "}
            query parameter.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background">
      {/* Background Glow */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute -bottom-52 right-0 h-[32rem] w-[32rem] rounded-full bg-primary/5 blur-3xl" />
      </div>

      {/* API Error banner */}
      {error && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 max-w-md rounded-2xl bg-red-900/80 border border-red-500/40 px-5 py-3 text-red-200 shadow-xl text-sm">
          ⚠️ {error}
        </div>
      )}

      <div className="relative mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8">

        <ProctorHeader />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.7fr_1fr]">

          <CandidateStage />

          <div className="flex flex-col gap-6">

            <StatusPanel
              faceDetected={status.faceDetected}
              microphone={status.microphone}
              fullscreen={status.fullscreen}
              network={status.network}
            />

            <AlertsPanel alerts={alerts} />

          </div>

        </div>

        <WarningTimeline timeline={timeline} />

        <ActivityLog logs={logs} />

      </div>
    </main>
  );
}