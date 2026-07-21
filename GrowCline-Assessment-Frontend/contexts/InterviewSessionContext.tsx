/**
 * InterviewSessionContext
 * =======================
 * Single source of truth for all interview session state.
 *
 * WRITE side: InterviewStudio updates this context as proctoring/cheating
 *             metrics arrive from the backend.
 *
 * READ side:  InterviewAnalyticsClient reads from this context to guarantee
 *             its proctor summary values are identical to what was shown
 *             during the live Video Recording session.
 *
 * Persistence: On every update the state is serialised to
 *              sessionStorage["growcline_session_<interviewId>"] so that
 *              data survives the router.push() from /video-recording →
 *              /interview-analytics within the same browser tab.
 */

"use client";

import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
  type ReactNode,
} from "react";

// ---------------------------------------------------------------------------
// State Shape
// ---------------------------------------------------------------------------

export interface InterviewSessionState {
  // Identity
  interviewId: string | null;
  sessionId: string | null;

  // Candidate & session info
  candidate: string;
  jobRole: string;
  startTime: string | null;      // ISO string
  date: string;
  duration: string;              // e.g. "12 Minutes"

  // Recording status
  recordingStatus: "idle" | "recording" | "paused" | "ended";

  // Live hardware status
  cameraStatus: boolean;
  microphoneStatus: boolean;
  fullscreen: boolean;
  networkQuality: "Excellent" | "Good" | "Poor";
  faceDetected: boolean;

  // Proctoring event counters — exact match to Video Recording widget
  riskScore: number;
  multipleFaces: number;
  tabSwitches: number;
  faceMissing: number;
  microphoneViolations: number;
  fullscreenExits: number;
  recommendation: string;

  // AI performance metrics (from answer evaluations)
  confidence: number;
  communication: number;
  technicalKnowledge: number;
  eyeContact: number;
  overallScore: number;
  grade: string;

  // Report fields
  strengths: string[];
  improvements: string[];
  finalRecommendation: "Recommended" | "Needs Improvement" | "Not Recommended";
  summary: string;

  // Lifecycle
  status: "idle" | "active" | "frozen";   // "frozen" = session ended, values locked
}

// ---------------------------------------------------------------------------
// Context Interface
// ---------------------------------------------------------------------------

interface InterviewSessionContextValue {
  session: InterviewSessionState;
  /** Merge partial updates into the session state (writer side) */
  updateSession: (patch: Partial<InterviewSessionState>) => void;
  /** Freeze the session — no further updates will be accepted */
  freezeSession: () => void;
  /** Restore a session from sessionStorage given an interviewId */
  restoreSession: (interviewId: string) => boolean;
}

// ---------------------------------------------------------------------------
// Defaults
// ---------------------------------------------------------------------------

const DEFAULT_SESSION: InterviewSessionState = {
  interviewId: null,
  sessionId: null,
  candidate: "Candidate",
  jobRole: "Interview",
  startTime: null,
  date: "",
  duration: "",
  recordingStatus: "idle",
  cameraStatus: true,
  microphoneStatus: true,
  fullscreen: true,
  networkQuality: "Excellent",
  faceDetected: true,
  riskScore: 0,
  multipleFaces: 0,
  tabSwitches: 0,
  faceMissing: 0,
  microphoneViolations: 0,
  fullscreenExits: 0,
  recommendation: "Low Risk",
  confidence: 0,
  communication: 0,
  technicalKnowledge: 0,
  eyeContact: 0,
  overallScore: 0,
  grade: "—",
  strengths: [],
  improvements: [],
  finalRecommendation: "Needs Improvement",
  summary: "",
  status: "idle",
};

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

const InterviewSessionContext = createContext<InterviewSessionContextValue>({
  session: DEFAULT_SESSION,
  updateSession: () => {},
  freezeSession: () => {},
  restoreSession: () => false,
});

// ---------------------------------------------------------------------------
// Storage helpers
// ---------------------------------------------------------------------------

function storageKey(interviewId: string) {
  return `growcline_session_${interviewId}`;
}

function saveToStorage(state: InterviewSessionState) {
  if (typeof window === "undefined" || !state.interviewId) return;
  try {
    sessionStorage.setItem(storageKey(state.interviewId), JSON.stringify(state));
  } catch {
    // sessionStorage may be unavailable (private mode / quota exceeded)
  }
}

function loadFromStorage(interviewId: string): InterviewSessionState | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(storageKey(interviewId));
    if (!raw) return null;
    return JSON.parse(raw) as InterviewSessionState;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

export function InterviewSessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<InterviewSessionState>(DEFAULT_SESSION);
  // Track frozen state separately to prevent writes after session ends
  const isFrozen = useRef(false);

  const updateSession = useCallback((patch: Partial<InterviewSessionState>) => {
    // Reject writes if the session is frozen (ended)
    if (isFrozen.current) return;

    setSession((prev) => {
      const next = { ...prev, ...patch };
      saveToStorage(next);
      return next;
    });
  }, []);

  const freezeSession = useCallback(() => {
    isFrozen.current = true;
    setSession((prev) => {
      const frozen = { ...prev, status: "frozen" as const };
      saveToStorage(frozen);
      return frozen;
    });
  }, []);

  const restoreSession = useCallback((interviewId: string): boolean => {
    const stored = loadFromStorage(interviewId);
    if (!stored) return false;
    isFrozen.current = stored.status === "frozen";
    setSession(stored);
    return true;
  }, []);

  return (
    <InterviewSessionContext.Provider
      value={{ session, updateSession, freezeSession, restoreSession }}
    >
      {children}
    </InterviewSessionContext.Provider>
  );
}

// ---------------------------------------------------------------------------
// Consumer hook
// ---------------------------------------------------------------------------

export function useInterviewSession() {
  return useContext(InterviewSessionContext);
}
