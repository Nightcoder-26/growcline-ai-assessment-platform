/**
 * useProctoring — live proctoring integration hook.
 *
 * LIFECYCLE:
 *   mount(interviewId)  → registers browser listeners, polls events from MongoDB
 *   activateProctoring()→ enables violation event generation (call on Start Recording)
 *   deactivateProctoring()→ disables violation generation (call before Stop/End)
 *   unmount            → cleanup
 *
 * SINGLE SOURCE OF TRUTH:
 *   All Warning Logs, Activity Logs, and Risk Summary are populated exclusively
 *   from MongoDB via GET /api/proctoring/interview/{id}/events.
 *   No local fake counters are ever used.
 *
 * VIOLATION GUARD:
 *   logEvent() is a no-op unless proctoringActive.current === true.
 *   This prevents false violations during page load, permission requests,
 *   question loading, etc.
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
const POLL_INTERVAL_MS = 3_000;

/** Max items shown in each list */
const MAX_ALERTS   = 30;
const MAX_LOGS     = 50;
const MAX_TIMELINE = 30;

/** RMS volume (0–1) above which background noise is flagged */
const NOISE_THRESHOLD = 0.08;
/** How long noise must sustain before firing an event (ms) */
const NOISE_SUSTAIN_MS = 1_500;
/** Minimum gap between successive BACKGROUND_VOICE events (ms) */
const NOISE_COOLDOWN_MS = 15_000;

/** Minimum gap between successive TAB_SWITCH events (ms) */
const TAB_SWITCH_COOLDOWN_MS = 5_000;

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
    // Read actual fullscreen state — don't lie with a hardcoded true
    fullscreen:   typeof document !== "undefined" ? !!document.fullscreenElement : false,
    network:      "Excellent",
  });

  const [alerts,   setAlerts]   = useState<AlertEvent[]>([]);
  const [logs,     setLogs]     = useState<ActivityEvent[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [error,    setError]    = useState<string | null>(null);

  // ── Internal refs ─────────────────────────────────────────────────────────

  /** True from mount(interviewId) to unmount — guards polling/cleanup */
  const mountedRef = useRef(false);

  /**
   * True only while recording is ACTIVE.
   * logEvent() is a no-op unless this is true.
   * Set via activateProctoring() / deactivateProctoring().
   */
  const proctoringActive = useRef(false);

  /** Queued events awaiting flush to backend */
  const queue = useRef<QueuedEvent[]>([]);

  // ── Browser event state/cooldown refs ─────────────────────────────────────

  const lastTabSwitchAt     = useRef<number>(0);
  const isTabVisibleRef     = useRef<boolean>(true);
  /** True once fullscreen has been ENTERED at least once during this session */
  const fullscreenWasActive = useRef<boolean>(false);

  // ── Audio analysis refs ───────────────────────────────────────────────────

  const audioCtxRef          = useRef<AudioContext | null>(null);
  const analyserRef          = useRef<AnalyserNode | null>(null);
  const micStreamRef         = useRef<MediaStream | null>(null);
  const noiseAboveSince      = useRef<number | null>(null);
  const lastNoiseFiredAt     = useRef<number>(0);
  const noiseRafId           = useRef<number | null>(null);

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

      // Separate violation events from lifecycle events for display purposes
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
      // Non-fatal: display stale data
      console.warn("[PROCTOR] poll error:", err instanceof Error ? err.message : err);
    }
  }, [interviewId]);

  // ── Flush queued events to backend ───────────────────────────────────────

  const flushQueue = useCallback(async () => {
    if (!interviewId || !mountedRef.current || queue.current.length === 0) return;

    const batch = [...queue.current];
    queue.current = [];

    console.log(`[PROCTOR] flushing ${batch.length} event(s) to backend:`, batch.map(e => e.event_type));

    try {
      await apiClient.post("/api/proctoring/events/batch", {
        interview_id: interviewId,
        events:       batch,
      });
      console.log("[PROCTOR] backend accepted events");

      // Immediately re-poll so UI reflects persisted events
      await pollEvents();
      onEventLogged?.();
    } catch (err) {
      console.warn("[PROCTOR] flush failed, re-queuing:", err instanceof Error ? err.message : err);
      // Re-queue so events are retried on next flush
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
        console.log(`[PROCTOR] logEvent(${eventType}) skipped — proctoring not active (recording not started)`);
        return;
      }

      console.log(`[PROCTOR] reporting ${eventType}`);
      queue.current.push({
        event_type:       eventType,
        client_timestamp: new Date().toISOString(),
      });

      // Flush immediately with a tiny debounce so multiple synchronous pushes batch together
      setTimeout(() => flushQueue(), 100);
    },
    [interviewId, flushQueue],
  );

  // ── Audio noise detection ─────────────────────────────────────────────────

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
            if (noiseAboveSince.current === null) {
              noiseAboveSince.current = now;
            } else if (
              now - noiseAboveSince.current >= NOISE_SUSTAIN_MS &&
              now - lastNoiseFiredAt.current >= NOISE_COOLDOWN_MS
            ) {
              lastNoiseFiredAt.current  = now;
              noiseAboveSince.current   = null;
              logEvent("BACKGROUND_VOICE");
            }
          } else {
            noiseAboveSince.current = null;
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

  // ── Public: activate proctoring (call on Start Recording) ────────────────

  /**
   * Enable violation event generation.
   * Must be called from the Start Recording user gesture after fullscreen entry.
   */
  const activateProctoring = useCallback(() => {
    if (proctoringActive.current) return; // already active
    console.log("[PROCTOR] session activated");
    proctoringActive.current = true;

    // Log session start to backend
    queue.current.push({
      event_type:       "PROCTORING_STARTED",
      client_timestamp: new Date().toISOString(),
    });
    setTimeout(() => flushQueue(), 100);

    // Start microphone noise monitoring now that recording is active
    startNoiseDetection();
  }, [flushQueue, startNoiseDetection]);

  // ── Public: deactivate proctoring (call before Stop Recording / End) ──────

  /**
   * Disable violation event generation.
   * Must be called BEFORE stopping/ending the interview, so the resulting
   * fullscreen exit does NOT generate a FULLSCREEN_EXIT violation.
   */
  const deactivateProctoring = useCallback(() => {
    if (!proctoringActive.current) return;
    console.log("[PROCTOR] session deactivated");
    proctoringActive.current = false;
    fullscreenWasActive.current = false;

    // Stop mic monitoring
    stopNoiseDetection();

    // Log session stop
    queue.current.push({
      event_type:       "PROCTORING_STOPPED",
      client_timestamp: new Date().toISOString(),
    });
    // Use a direct flush (proctoringActive is now false so logEvent would skip)
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

  // ── Browser event listeners (registered on mount, not on activation) ──────

  useEffect(() => {
    if (!interviewId) return;

    mountedRef.current = true;

    // Sync fullscreen state with actual browser state
    setStatus((prev) => ({
      ...prev,
      fullscreen: !!document.fullscreenElement,
    }));

    // Load existing events from MongoDB (for page refresh recovery)
    pollEvents();

    // Periodic poll
    const pollTimer = setInterval(pollEvents, POLL_INTERVAL_MS);

    // ── visibilitychange — tab switching ────────────────────────────────────
    const handleVisibility = () => {
      const now = Date.now();
      if (document.hidden) {
        if (
          isTabVisibleRef.current &&
          now - lastTabSwitchAt.current >= TAB_SWITCH_COOLDOWN_MS
        ) {
          isTabVisibleRef.current  = false;
          lastTabSwitchAt.current  = now;
          console.log("[PROCTOR] tab hidden → TAB_SWITCH");
          logEvent("TAB_SWITCH");
        }
      } else {
        isTabVisibleRef.current = true;
      }
    };

    // ── fullscreenchange ────────────────────────────────────────────────────
    const handleFullscreenChange = () => {
      if (document.fullscreenElement) {
        // Entered fullscreen
        fullscreenWasActive.current = true;
        setStatus((prev) => ({ ...prev, fullscreen: true }));
        console.log("[PROCTOR] fullscreen entered");
      } else {
        // Exited fullscreen — only count as violation if:
        // 1. fullscreen was actually active this session
        // 2. proctoring is currently active (recording in progress)
        setStatus((prev) => ({ ...prev, fullscreen: false }));
        if (fullscreenWasActive.current && proctoringActive.current) {
          console.log("[PROCTOR] fullscreen exited → FULLSCREEN_EXIT");
          logEvent("FULLSCREEN_EXIT");
        } else {
          console.log("[PROCTOR] fullscreen exited — not logging violation (proctoring not active or fullscreen was never entered)");
        }
        fullscreenWasActive.current = false;
      }
    };

    document.addEventListener("visibilitychange",  handleVisibility);
    document.addEventListener("fullscreenchange",   handleFullscreenChange);

    return () => {
      mountedRef.current       = false;
      proctoringActive.current = false;

      stopNoiseDetection();

      document.removeEventListener("visibilitychange",  handleVisibility);
      document.removeEventListener("fullscreenchange",   handleFullscreenChange);
      clearInterval(pollTimer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [interviewId]);

  // ── Public API ────────────────────────────────────────────────────────────

  return {
    /** Live status booleans for the Candidate Monitoring panel */
    status,
    setStatus,

    /** Warning alerts from confirmed backend events */
    alerts,
    /** Activity log entries from backend events */
    logs,
    /** Timeline entries for warning timeline component */
    timeline,

    /** Report a violation event (no-op unless proctoring is active) */
    logEvent,

    /** Force a backend poll to refresh warning logs */
    pollEvents,

    /** Enable violation logging — call from Start Recording user gesture */
    activateProctoring,

    /** Disable violation logging — call BEFORE stopping recording / ending session */
    deactivateProctoring,

    /** Any display-level error string */
    error,
  };
}
