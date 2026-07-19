/**
 * useAnalytics — fetches and generates interview analytics reports.
 *
 * Wraps:
 *   GET  /api/analytics/interview/{id}          — fetch existing report
 *   POST /api/analytics/interview/{id}/generate — generate (or refresh) report
 */

"use client";

import { useCallback, useEffect, useState } from "react";
import apiClient from "@/lib/apiClient";

// ---------------------------------------------------------------------------
// Types (matching InterviewAnalytics.response() in backend)
// ---------------------------------------------------------------------------

export interface AnalyticsReport {
  id: string;
  interviewId: string;
  userId: string;
  durationSeconds: number;
  videoUploaded: boolean;
  totalEvents: number;
  riskScore: number;
  riskLevel: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  tabSwitches: number;
  multipleFaces: number;
  backgroundVoice: number;
  cameraDisabled: number;
  microphoneDisabled: number;
  fullscreenExit: number;
  overallStatus: "PASSED" | "REVIEW_REQUIRED" | "MANUAL_REVIEW" | "FLAGGED";
  generatedAt: string | null;
  updatedAt: string | null;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useAnalytics(interviewId: string | null, userRole: string | null) {
  const [report, setReport] = useState<AnalyticsReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  // ── Fetch existing report ─────────────────────────────────────────────────

  const fetchReport = useCallback(async () => {
    if (!interviewId) return;
    setLoading(true);
    setError(null);
    setNotFound(false);

    try {
      const res = await apiClient.get(`/api/analytics/interview/${interviewId}`);
      setReport(res.data.data as AnalyticsReport);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load analytics.";
      if (msg.toLowerCase().includes("not found")) {
        setNotFound(true);
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, [interviewId]);

  // ── Generate / refresh report ─────────────────────────────────────────────

  const generateReport = useCallback(
    async (forceRefresh = false) => {
      if (!interviewId) return;
      setGenerating(true);
      setError(null);
      try {
        const res = await apiClient.post(
          `/api/analytics/interview/${interviewId}/generate`,
          { force_refresh: forceRefresh }
        );
        setReport(res.data.data as AnalyticsReport);
        setNotFound(false);
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Failed to generate analytics.";
        setError(msg);
      } finally {
        setGenerating(false);
      }
    },
    [interviewId]
  );

  // Auto-fetch on mount
  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  return {
    report,
    loading,
    generating,
    error,
    notFound,
    refetch: fetchReport,
    generateReport,
  };
}
