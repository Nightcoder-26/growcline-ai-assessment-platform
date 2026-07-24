/**
 * useProctoring — live proctoring integration hook.
 *
 * - Accepts interviewId and userId
 * - Queues browser events (tab-switch, face-missing, background-voice, etc.)
 * - Flushes the queue every FLUSH_INTERVAL_MS via POST /api/proctoring/events/batch
 * - Polls GET /api/proctoring/interview/{id}/events every POLL_INTERVAL_MS
 *   to populate the real-time alerts / activity log / warning timeline
 * - Emits a PROCTORING_STARTED event on mount and PROCTORING_STOPPED on unmount
 * - Analyses microphone audio volume via Web Audio API to detect background noise
 */

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import apiClient from "@/lib/apiClient";
import type { AlertEvent, ActivityEvent, TimelineEvent } from "@/components/live-proctoring/types";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const FLUSH_INTERVAL_MS = 5_000;
const POLL_INTERVAL_MS = 5_000;
const MAX_ALERTS = 8;
const MAX_LOGS = 12;
const MAX_TIMELINE = 10;

/** RMS volume (0-1) above which background noise is flagged */
const NOISE_THRESHOLD = 0.08;
/** How long (ms) volume must stay above threshold before we fire an event */
const NOISE_SUSTAIN_MS = 500;
/** Minimum gap (ms) between successive BACKGROUND_VOICE events */
const NOISE_COOLDOWN_MS = 8_000;

// ---------------------------------------------------------------------------
// Severity mapping (server severity → UI AlertSeverity)
// ---------------------------------------------------------------------------

type UISeverity = "success" | "warning" | "danger" | "info";

const SERVER_SEVERITY_MAP: Record<string, UISeverity> = {
  INFO: "info",
  LOW: "info",
  MEDIUM: "warning",
  HIGH: "danger",
  CRITICAL: "danger",
};

// ---------------------------------------------------------------------------
// Status-panel state derived from latest events
// ---------------------------------------------------------------------------

export interface ProctoringStatus {
  faceDetected: boolean;
  microphone: boolean;
  fullscreen: boolean;
  network: "Excellent" | "Good" | "Poor";
}

// ---------------------------------------------------------------------------
// Queued event shape
// ---------------------------------------------------------------------------

interface QueuedEvent {
  event_type: string;
  client_timestamp: string; // ISO string
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useProctoring(interviewId: string | null, userId: string | null) {
  const [status, setStatus] = useState<ProctoringStatus>({
    faceDetected: true,
    microphone: true,
    fullscreen: true,
    network: "Excellent",
  });
  const [alerts, setAlerts] = useState<AlertEvent[]>([]);
  const [logs, setLogs] = useState<ActivityEvent[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  const queue = useRef<QueuedEvent[]>([]);
  const seenEventIds = useRef<Set<string>>(new Set());
  const isActive = useRef(false);

  // ── Audio analysis refs ─────────────────────────────────────────────────
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const micStreamRef = useRef<MediaStream | null>(null);
  const noiseAboveThresholdSince = useRef<number | null>(null);
  const lastNoiseFiredAt = useRef<number>(0);
  const noiseRafId = useRef<number | null>(null);

  // ── Enqueue a new browser-detected proctoring event ─────────────────────

  const logEvent = useCallback((eventType: string) => {
    queue.current.push({
      event_type: eventType,
      client_timestamp: new Date().toISOString(),
    });

    // Immediately reflect the event in local UI state
    const now = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

    const uiSeverity: UISeverity =
      ["NO_FACE", "MULTIPLE_FACES", "BACKGROUND_VOICE", "CAMERA_DISABLED"].includes(eventType)
        ? "danger"
        : ["TAB_SWITCH", "WINDOW_BLUR", "FULLSCREEN_EXIT", "MICROPHONE_DISABLED"].includes(eventType)
        ? "warning"
        : "info";

    const label = eventType
      .toLowerCase()
      .split("_")
      .map((w) => w[0].toUpperCase() + w.slice(1))
      .join(" ");

    const newAlert: AlertEvent = {
      id: Date.now(),
      title: label,
      message: `${label} detected.`,
      severity: uiSeverity,
      time: now,
    };

    const newLog: ActivityEvent = {
      id: Date.now() + 1,
      event: label,
      time: now,
      severity: uiSeverity,
    };

    const newTimeline: TimelineEvent = {
      id: Date.now() + 2,
      title: label,
      subtitle: `${label} event recorded.`,
      severity: uiSeverity,
      time: now,
    };

    setAlerts((prev) => [newAlert, ...prev].slice(0, MAX_ALERTS));
    setLogs((prev) => [newLog, ...prev].slice(0, MAX_LOGS));
    setTimeline((prev) => [newTimeline, ...prev].slice(0, MAX_TIMELINE));
  }, []);

  // ── Flush queued events to backend ────────────────────────────────────────

  const flushQueue = useCallback(async () => {
    if (!interviewId || !isActive.current || queue.current.length === 0) return;

    const events = [...queue.current];
    queue.current = [];

    try {
      await apiClient.post("/api/proctoring/events/batch", {
        interview_id: interviewId,
        events,
      });
    } catch {
      // Silently re-queue on failure (best-effort proctoring)
      queue.current = [...events, ...queue.current];
    }
  }, [interviewId]);

  // ── Poll backend for latest events ────────────────────────────────────────

  const pollEvents = useCallback(async () => {
    if (!interviewId || !isActive.current) return;

    try {
      const res = await apiClient.get(
        `/api/proctoring/interview/${interviewId}/events?limit=20&skip=0`
      );
      const backendEvents: Array<{
        id: string;
        eventType: string;
        severity: string;
        timestamp: string;
      }> = res.data?.data?.events ?? [];

      // Only process events we haven't seen yet
      const newEvents = backendEvents.filter((e) => !seenEventIds.current.has(e.id));
      if (newEvents.length === 0) return;

      newEvents.forEach((e) => seenEventIds.current.add(e.id));

      const now = (ts: string) => {
        try {
          return new Date(ts).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
          });
        } catch {
          return "--:--:--";
        }
      };

      newEvents.forEach((e) => {
        const uiSeverity: UISeverity = SERVER_SEVERITY_MAP[e.severity] ?? "info";
        const label = e.eventType
          .toLowerCase()
          .split("_")
          .map((w) => w[0].toUpperCase() + w.slice(1))
          .join(" ");
        const timeStr = now(e.timestamp);

        const newAlert: AlertEvent = {
          id: Date.now() + Math.random(),
          title: label,
          message: `${label} detected at ${timeStr}.`,
          severity: uiSeverity,
          time: timeStr,
        };

        const newLog: ActivityEvent = {
          id: Date.now() + Math.random(),
          event: label,
          time: timeStr,
          severity: uiSeverity,
        };

        const newTimeline: TimelineEvent = {
          id: Date.now() + Math.random(),
          title: label,
          subtitle: e.eventType,
          severity: uiSeverity,
          time: timeStr,
        };

        setAlerts((prev) => [newAlert, ...prev].slice(0, MAX_ALERTS));
        setLogs((prev) => [newLog, ...prev].slice(0, MAX_LOGS));
        setTimeline((prev) => [newTimeline, ...prev].slice(0, MAX_TIMELINE));
      });
    } catch (err) {
      // Non-fatal: log but don't surface to user
      const msg = err instanceof Error ? err.message : "Polling error";
      console.warn("[useProctoring] poll error:", msg);
    }
  }, [interviewId]);

  // ── Background noise detection via Web Audio API ───────────────────────────

  const startNoiseDetection = useCallback(
    (logEventFn: (type: string) => void) => {
      if (typeof window === "undefined") return;
      if (!navigator.mediaDevices?.getUserMedia) return;

      navigator.mediaDevices
        .getUserMedia({ audio: true, video: false })
        .then((stream) => {
          if (!isActive.current) {
            stream.getTracks().forEach((t) => t.stop());
            return;
          }

          micStreamRef.current = stream;
          const AudioCtx =
            window.AudioContext ||
            (window as unknown as { webkitAudioContext: typeof AudioContext })
              .webkitAudioContext;
          const ctx = new AudioCtx();
          audioCtxRef.current = ctx;

          const source = ctx.createMediaStreamSource(stream);
          const analyser = ctx.createAnalyser();
          analyser.fftSize = 256;
          source.connect(analyser);
          analyserRef.current = analyser;

          const buffer = new Float32Array(analyser.fftSize);

          const tick = () => {
            if (!isActive.current) return;

            analyser.getFloatTimeDomainData(buffer);

            // Compute RMS (root mean square) of audio signal
            let sum = 0;
            for (let i = 0; i < buffer.length; i++) {
              sum += buffer[i] * buffer[i];
            }
            const rms = Math.sqrt(sum / buffer.length);

            const now = Date.now();
            if (rms > NOISE_THRESHOLD) {
              if (noiseAboveThresholdSince.current === null) {
                noiseAboveThresholdSince.current = now;
              } else if (
                now - noiseAboveThresholdSince.current >= NOISE_SUSTAIN_MS &&
                now - lastNoiseFiredAt.current >= NOISE_COOLDOWN_MS
              ) {
                // Sustained loud audio → background voice/noise detected
                lastNoiseFiredAt.current = now;
                noiseAboveThresholdSince.current = null;
                logEventFn("BACKGROUND_VOICE");
              }
            } else {
              noiseAboveThresholdSince.current = null;
            }

            noiseRafId.current = requestAnimationFrame(tick);
          };

          noiseRafId.current = requestAnimationFrame(tick);
        })
        .catch((err) => {
          console.warn("[useProctoring] mic access denied for noise detection:", err);
        });
    },
    []
  );

  const stopNoiseDetection = useCallback(() => {
    if (noiseRafId.current !== null) {
      cancelAnimationFrame(noiseRafId.current);
      noiseRafId.current = null;
    }
    if (analyserRef.current) {
      analyserRef.current.disconnect();
      analyserRef.current = null;
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close().catch(() => {});
      audioCtxRef.current = null;
    }
    if (micStreamRef.current) {
      micStreamRef.current.getTracks().forEach((t) => t.stop());
      micStreamRef.current = null;
    }
  }, []);

  // ── Browser event listeners ────────────────────────────────────────────────

  useEffect(() => {
    if (!interviewId) return;

    isActive.current = true;

    // Log session start
    logEvent("PROCTORING_STARTED");

    const handleVisibility = () => {
      if (document.hidden) logEvent("TAB_SWITCH");
    };
    const handleBlur = () => logEvent("WINDOW_BLUR");
    const handleFullscreenChange = () => {
      if (!document.fullscreenElement) logEvent("FULLSCREEN_EXIT");
    };

    document.addEventListener("visibilitychange", handleVisibility);
    window.addEventListener("blur", handleBlur);
    document.addEventListener("fullscreenchange", handleFullscreenChange);

    // Start background noise monitoring
    startNoiseDetection(logEvent);

    // Periodic flush and poll
    const flushTimer = setInterval(flushQueue, FLUSH_INTERVAL_MS);
    const pollTimer = setInterval(pollEvents, POLL_INTERVAL_MS);

    return () => {
      isActive.current = false;
      logEvent("PROCTORING_STOPPED");
      flushQueue(); // Final flush on unmount

      stopNoiseDetection();

      document.removeEventListener("visibilitychange", handleVisibility);
      window.removeEventListener("blur", handleBlur);
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
      clearInterval(flushTimer);
      clearInterval(pollTimer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [interviewId]);

  return {
    status,
    setStatus,
    alerts,
    logs,
    timeline,
    logEvent,
    error,
  };
}
