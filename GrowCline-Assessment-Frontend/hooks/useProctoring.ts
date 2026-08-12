/**
 * useProctoring — live proctoring integration hook.
 *
 * LIFECYCLE:
 *   mount(interviewId)  → registers browser listeners, polls events from MongoDB
 *   activateProctoring()→ enables violation event generation (called on session ready)
 *   deactivateProctoring()→ disables violation generation (called before Stop/End)
 *   unmount            → cleanup
 *
 * SINGLE SOURCE OF TRUTH:
 *   All Warning Logs, Activity Logs, and Risk Summary are populated exclusively
 *   from MongoDB via GET /api/proctoring/interview/{id}/events.
 *   No local fake counters are ever used.
 */

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import apiClient from "@/lib/apiClient";
import type {
  AlertEvent,
  ActivityEvent,
  TimelineEvent,
} from "@/components/live-proctoring/types";

// ---------------------------------------------------------------------------
// Config constants
// ---------------------------------------------------------------------------

/** How often to poll backend for fresh events (ms) */
const POLL_INTERVAL_MS = 2_500;

/** Max items shown in each list */
const MAX_ALERTS   = 30;
const MAX_LOGS     = 50;
const MAX_TIMELINE = 30;

/** RMS volume (0–1) above which background voice / mic noise is flagged */
const NOISE_THRESHOLD = 0.035;
/** Minimum gap between successive BACKGROUND_VOICE events (ms) */
const NOISE_COOLDOWN_MS = 6_000;

/** Minimum gap between successive TAB_SWITCH events (ms) */
const TAB_SWITCH_COOLDOWN_MS = 3_000;
/** Minimum gap between successive FULLSCREEN_EXIT events (ms) */
const FULLSCREEN_EXIT_COOLDOWN_MS = 3_000;

// ---------------------------------------------------------------------------
// Cross-browser Fullscreen Detector
// ---------------------------------------------------------------------------

const checkIsFullscreen = (): boolean => {
  if (typeof document === "undefined") return false;
  const doc = document as unknown as {
    fullscreenElement?:       Element;
    webkitFullscreenElement?: Element;
    mozFullScreenElement?:    Element;
    msFullscreenElement?:     Element;
  };
  return !!(
    doc.fullscreenElement ||
    doc.webkitFullscreenElement ||
    doc.mozFullScreenElement ||
    doc.msFullscreenElement
  );
};

// ---------------------------------------------------------------------------
// Server severity → UI severity mapping
// ---------------------------------------------------------------------------

type UISeverity = "success" | "warning" | "danger" | "info";

const SERVER_SEVERITY_MAP: Record<string, UISeverity> = {
  INFO:     "info",
  LOW:      "info",
  MEDIUM:   "warning",
  HIGH:     "danger",
  CRITICAL: "danger",
};

// ---------------------------------------------------------------------------
// Public types
// ---------------------------------------------------------------------------

export interface ProctoringStatus {
  faceDetected: boolean;
  microphone:   boolean;
  fullscreen:   boolean;
  network:      "Excellent" | "Good" | "Poor";
}

interface QueuedEvent {
  event_type:       string;
  client_timestamp: string;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useProctoring(
  interviewId:    string | null,
  userId:         string | null,
  onEventLogged?: () => void,
) {
  // ── State ─────────────────────────────────────────────────────────────────

  const [status, setStatus] = useState<ProctoringStatus>({
    faceDetected: true,
    microphone:   true,
    fullscreen:   checkIsFullscreen(),
    network:      "Excellent",
  });

  const [alerts,   setAlerts]   = useState<AlertEvent[]>([]);
  const [logs,     setLogs]     = useState<ActivityEvent[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [error,    setError]    = useState<string | null>(null);

  // ── Internal refs ─────────────────────────────────────────────────────────

  const mountedRef = useRef(false);

  /**
   * True while proctoring is ACTIVE.
   * logEvent() is a no-op unless this is true.
   */
  const proctoringActive = useRef(false);

  /** Queued events awaiting flush to backend */
  const queue = useRef<QueuedEvent[]>([]);

  // ── Cooldown timestamp refs ───────────────────────────────────────────────

  const lastTabSwitchAt      = useRef<number>(0);
  const lastFullscreenExitAt = useRef<number>(0);
  const isTabVisibleRef      = useRef<boolean>(true);

  // ── Audio analysis refs ───────────────────────────────────────────────────

  const audioCtxRef       = useRef<AudioContext | null>(null);
  const analyserRef       = useRef<AnalyserNode | null>(null);
  const micStreamRef      = useRef<MediaStream | null>(null);
  const noiseFrameCount   = useRef<number>(0);
  const lastNoiseFiredAt  = useRef<number>(0);
  const noiseRafId        = useRef<number | null>(null);

  // ── Helpers ───────────────────────────────────────────────────────────────

  const formatTime = (ts: string) => {
    try {
      return new Date(ts).toLocaleTimeString([], {
        hour:   "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return "--:--:--";
    }
  };

  const toLabel = (eventType: string) =>
    eventType
      .toLowerCase()
      .split("_")
      .map((w) => w[0].toUpperCase() + w.slice(1))
      .join(" ");

  // ── Poll backend for events (authoritative source) ────────────────────────

  const pollEvents = useCallback(async () => {
    if (!interviewId || !mountedRef.current) return;

    try {
      const res = await apiClient.get(
        `/api/proctoring/interview/${interviewId}/events?limit=50&skip=0`,
      );
      const rawEvents: Array<{
        id:        string;
        eventType: string;
        severity:  string;
        timestamp: string;
      }> = res.data?.data?.events ?? [];

      // Filter out lifecycle INFO events from warning logs
      const violations = rawEvents.filter(
        (e) =>
          e.eventType !== "PROCTORING_STARTED" &&
          e.eventType !== "PROCTORING_STOPPED",
      );

      const alertList: AlertEvent[] = violations.map((e) => ({
        id:       e.id,
        title:    toLabel(e.eventType),
        message:  `${toLabel(e.eventType)} detected.`,
        severity: SERVER_SEVERITY_MAP[e.severity] ?? "warning",
        time:     formatTime(e.timestamp),
      }));

      const logList: ActivityEvent[] = rawEvents.map((e) => ({
        id:       e.id,
        event:    toLabel(e.eventType),
        time:     formatTime(e.timestamp),
        severity: SERVER_SEVERITY_MAP[e.severity] ?? "info",
      }));

      const timelineList: TimelineEvent[] = violations.map((e) => ({
        id:       e.id,
        title:    toLabel(e.eventType),
        subtitle: `${toLabel(e.eventType)} event recorded.`,
        severity: SERVER_SEVERITY_MAP[e.severity] ?? "warning",
        time:     formatTime(e.timestamp),
      }));

      setAlerts(alertList.slice(0, MAX_ALERTS));
      setLogs(logList.slice(0, MAX_LOGS));
      setTimeline(timelineList.slice(0, MAX_TIMELINE));
    } catch (err) {
      console.warn("[PROCTOR] poll error:", err instanceof Error ? err.message : err);
    }
  }, [interviewId]);

  // ── Flush queued events to backend ───────────────────────────────────────

  const flushQueue = useCallback(async () => {
    if (!interviewId || !mountedRef.current || queue.current.length === 0) return;

    const batch = [...queue.current];
    queue.current = [];

    try {
      await apiClient.post("/api/proctoring/events/batch", {
        interview_id: interviewId,
        events:       batch,
      });

      // Immediately re-poll so UI reflects persisted events
      await pollEvents();
      onEventLogged?.();
    } catch (err) {
      console.warn("[PROCTOR] flush failed, re-queuing:", err instanceof Error ? err.message : err);
      queue.current = [...batch, ...queue.current];
    }
  }, [interviewId, onEventLogged, pollEvents]);

  // ── Public: log a single proctoring event ────────────────────────────────

  const logEvent = useCallback(
    (eventType: string) => {
      if (!interviewId) {
        console.warn(`[PROCTOR] logEvent(${eventType}) skipped — no interviewId`);
        return;
      }
      if (!proctoringActive.current) {
        console.log(`[PROCTOR] logEvent(${eventType}) skipped — proctoring not active`);
        return;
      }

      console.log(`[PROCTOR] reporting ${eventType}`);
      queue.current.push({
        event_type:       eventType,
        client_timestamp: new Date().toISOString(),
      });

      setTimeout(() => flushQueue(), 100);
    },
    [interviewId, flushQueue],
  );

  // ── Audio noise / background voice detection ──────────────────────────────

  const startNoiseDetection = useCallback(() => {
    if (typeof window === "undefined") return;
    if (!navigator.mediaDevices?.getUserMedia) return;

    navigator.mediaDevices
      .getUserMedia({ audio: true, video: false })
      .then((stream) => {
        if (!mountedRef.current) {
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

        const source   = ctx.createMediaStreamSource(stream);
        const analyser = ctx.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        analyserRef.current = analyser;

        const buffer = new Float32Array(analyser.fftSize);

        const tick = () => {
          if (!mountedRef.current) return;

          analyser.getFloatTimeDomainData(buffer);

          let sum = 0;
          for (let i = 0; i < buffer.length; i++) sum += buffer[i] * buffer[i];
          const rms = Math.sqrt(sum / buffer.length);

          const now = Date.now();
          if (rms > NOISE_THRESHOLD) {
            noiseFrameCount.current += 1;
            // If accumulated speech energy reaches 12 frames (~200ms) and outside cooldown
            if (
              noiseFrameCount.current >= 12 &&
              now - lastNoiseFiredAt.current >= NOISE_COOLDOWN_MS
            ) {
              lastNoiseFiredAt.current = now;
              noiseFrameCount.current = 0;
              logEvent("BACKGROUND_VOICE");
            }
          } else {
            if (noiseFrameCount.current > 0) {
              noiseFrameCount.current -= 0.5;
            }
          }

          noiseRafId.current = requestAnimationFrame(tick);
        };

        noiseRafId.current = requestAnimationFrame(tick);
      })
      .catch((err) => {
        console.warn("[PROCTOR] mic access denied for noise detection:", err);
      });
  }, [logEvent]);

  const stopNoiseDetection = useCallback(() => {
    if (noiseRafId.current !== null) {
      cancelAnimationFrame(noiseRafId.current);
      noiseRafId.current = null;
    }
    analyserRef.current?.disconnect();
    analyserRef.current = null;
    audioCtxRef.current?.close().catch(() => {});
    audioCtxRef.current = null;
    micStreamRef.current?.getTracks().forEach((t) => t.stop());
    micStreamRef.current = null;
  }, []);

  // ── Public: activate proctoring ──────────────────────────────────────────

  const activateProctoring = useCallback(() => {
    if (proctoringActive.current) return;
    proctoringActive.current = true;

    queue.current.push({
      event_type:       "PROCTORING_STARTED",
      client_timestamp: new Date().toISOString(),
    });
    setTimeout(() => flushQueue(), 100);

    startNoiseDetection();
  }, [flushQueue, startNoiseDetection]);

  // ── Public: deactivate proctoring ────────────────────────────────────────

  const deactivateProctoring = useCallback(() => {
    if (!proctoringActive.current) return;
    proctoringActive.current = false;

    stopNoiseDetection();

    queue.current.push({
      event_type:       "PROCTORING_STOPPED",
      client_timestamp: new Date().toISOString(),
    });

    if (interviewId && mountedRef.current) {
      const batch = [...queue.current];
      queue.current = [];
      apiClient
        .post("/api/proctoring/events/batch", {
          interview_id: interviewId,
          events:       batch,
        })
        .catch(() => {/* best-effort */});
    }
  }, [interviewId, stopNoiseDetection]);

  // ── Browser event listeners ───────────────────────────────────────────────

  useEffect(() => {
    if (!interviewId) return;

    mountedRef.current = true;

    setStatus((prev) => ({
      ...prev,
      fullscreen: checkIsFullscreen(),
    }));

    pollEvents();

    const pollTimer = setInterval(pollEvents, POLL_INTERVAL_MS);

    // ── Tab switch & window blur detection ──────────────────────────────────
    const triggerTabSwitch = (source: string) => {
      const now = Date.now();
      if (now - lastTabSwitchAt.current >= TAB_SWITCH_COOLDOWN_MS) {
        lastTabSwitchAt.current = now;
        isTabVisibleRef.current = false;
        logEvent("TAB_SWITCH");
      }
    };

    const handleVisibility = () => {
      if (document.hidden) {
        triggerTabSwitch("visibilitychange (tab hidden)");
      } else {
        isTabVisibleRef.current = true;
      }
    };

    const handleBlur = () => {
      triggerTabSwitch("window blur (focus lost)");
    };

    // ── Fullscreen exit detection ───────────────────────────────────────────
    const handleFullscreenChange = () => {
      const isFS = checkIsFullscreen();
      setStatus((prev) => ({ ...prev, fullscreen: isFS }));

      if (isFS) {
        // Reset exit timestamp when entering fullscreen so next exit is logged immediately
        lastFullscreenExitAt.current = 0;
      } else if (proctoringActive.current) {
        const now = Date.now();
        if (now - lastFullscreenExitAt.current >= FULLSCREEN_EXIT_COOLDOWN_MS) {
          lastFullscreenExitAt.current = now;
          logEvent("FULLSCREEN_EXIT");
        }
      }
    };

    document.addEventListener("visibilitychange",       handleVisibility);
    window.addEventListener("blur",                     handleBlur);
    document.addEventListener("fullscreenchange",        handleFullscreenChange);
    document.addEventListener("webkitfullscreenchange",  handleFullscreenChange);
    document.addEventListener("mozfullscreenchange",     handleFullscreenChange);
    document.addEventListener("MSFullscreenChange",      handleFullscreenChange);
    window.addEventListener("resize",                   handleFullscreenChange);

    return () => {
      mountedRef.current       = false;
      proctoringActive.current = false;

      stopNoiseDetection();

      document.removeEventListener("visibilitychange",       handleVisibility);
      window.removeEventListener("blur",                     handleBlur);
      document.removeEventListener("fullscreenchange",        handleFullscreenChange);
      document.removeEventListener("webkitfullscreenchange",  handleFullscreenChange);
      document.removeEventListener("mozfullscreenchange",     handleFullscreenChange);
      document.removeEventListener("MSFullscreenChange",      handleFullscreenChange);
      window.removeEventListener("resize",                   handleFullscreenChange);
      clearInterval(pollTimer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [interviewId]);

  // ── Public API ────────────────────────────────────────────────────────────

  return {
    status,
    setStatus,
    alerts,
    logs,
    timeline,
    logEvent,
    pollEvents,
    activateProctoring,
    deactivateProctoring,
    error,
  };
}
