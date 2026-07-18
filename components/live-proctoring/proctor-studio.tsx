"use client";

import { useEffect, useState } from "react";

import { ProctorHeader } from "./proctor-header";
import { CandidateStage } from "./candidate-stage";
import { StatusPanel } from "./status-panel";
import { AlertsPanel } from "./alerts-panel";
import { WarningTimeline } from "./warning-timeline";
import { ActivityLog } from "./activity-log";

import { initialProctorState } from "./mock-events";

export function ProctorStudio() {
  const [proctorState, setProctorState] = useState(initialProctorState);

  useEffect(() => {
    const interval = setInterval(() => {
      setProctorState((prev) => {
        const faceDetected = !prev.faceDetected;

        const network =
          prev.network === "Excellent"
            ? "Good"
            : prev.network === "Good"
            ? "Poor"
            : "Excellent";

        const currentTime = new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        });

        const newAlert = {
          id: Date.now(),
          title: faceDetected ? "Face Restored" : "Face Missing",
          message: faceDetected
            ? "Candidate face detected again."
            : "Face could not be detected.",
          severity: faceDetected ? "success" : "danger",
          time: currentTime,
        };

        const newLog = {
          id: Date.now() + 1,
          event: faceDetected ? "Face Restored" : "Face Missing",
          time: currentTime,
          severity: faceDetected ? "success" : "danger",
        };

        const newTimeline = {
          id: Date.now() + 2,
          title: newLog.event,
          subtitle: newAlert.message,
          severity: newAlert.severity,
          time: currentTime,
        };

        return {
          ...prev,
          faceDetected,
          network,

          alerts: [newAlert, ...prev.alerts].slice(0, 6),

          logs: [newLog, ...prev.logs].slice(0, 10),

          timeline: [newTimeline, ...prev.timeline].slice(0, 8),
        };
      });
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-background">
      {/* Background Glow */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute -bottom-52 right-0 h-[32rem] w-[32rem] rounded-full bg-primary/5 blur-3xl" />
      </div>

      <div className="relative mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8">

        <ProctorHeader />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.7fr_1fr]">

          <CandidateStage />

          <div className="flex flex-col gap-6">

            <StatusPanel
              faceDetected={proctorState.faceDetected}
              microphone={proctorState.microphone}
              fullscreen={proctorState.fullscreen}
              network={proctorState.network}
            />

            <AlertsPanel
              alerts={proctorState.alerts}
            />

          </div>

        </div>

        <WarningTimeline
          timeline={proctorState.timeline}
        />

        <ActivityLog
          logs={proctorState.logs}
        />

      </div>
    </main>
  );
}