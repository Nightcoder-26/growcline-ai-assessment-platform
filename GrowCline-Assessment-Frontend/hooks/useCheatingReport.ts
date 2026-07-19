/**
 * useCheatingReport — fetches cheating detection report from backend.
 *
 * Wraps:
 *   GET  /api/cheating/interview/{id}/report            (admin)
 *   GET  /api/cheating/interview/{id}/report/candidate  (owner, read-only)
 *   POST /api/cheating/interview/{id}/analyze           (admin only)
 *
 * The hook auto-selects the correct endpoint based on the user's role.
 */

"use client";

import { useCallback, useEffect, useState } from "react";
import apiClient from "@/lib/apiClient";

// ---------------------------------------------------------------------------
// Types (matching CheatingReport.response() in backend)
// ---------------------------------------------------------------------------

export interface EventContribution {
  count: number;
  effectiveCount: number;
  weight: number;
  contribution: number;
}

export interface CheatingReportData {
  id: string;
  interviewId: string;
  userId: string;
  riskScore: number;
  riskLevel: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  totalEvents: number;
  suspiciousEvents: number;
  eventCounts: Record<string, number>;
  eventContributions: Record<string, EventContribution>;
  createdAt: string | null;
  updatedAt: string | null;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useCheatingReport(interviewId: string | null, userRole: string | null) {
  const [report, setReport] = useState<CheatingReportData | null>(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  const isAdmin = userRole === "admin";

  // ── Fetch report ──────────────────────────────────────────────────────────

  const fetchReport = useCallback(async () => {
    if (!interviewId) return;
    setLoading(true);
    setError(null);
    setNotFound(false);

    // Admin → standard endpoint; candidate → candidate-safe endpoint
    const endpoint = isAdmin
      ? `/api/cheating/interview/${interviewId}/report`
      : `/api/cheating/interview/${interviewId}/report/candidate`;

    try {
      const res = await apiClient.get(endpoint);
      setReport(res.data.data as CheatingReportData);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load cheating report.";
      // Treat "not found" as a soft state — report may not exist yet
      if (msg.toLowerCase().includes("not found")) {
        setNotFound(true);
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, [interviewId, isAdmin]);

  // ── Run analysis (admin only) ─────────────────────────────────────────────

  const analyze = useCallback(async () => {
    if (!interviewId || !isAdmin) return;
    setAnalyzing(true);
    setError(null);
    try {
      const res = await apiClient.post(`/api/cheating/interview/${interviewId}/analyze`);
      setReport(res.data.data as CheatingReportData);
      setNotFound(false);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Analysis failed.";
      setError(msg);
    } finally {
      setAnalyzing(false);
    }
  }, [interviewId, isAdmin]);

  // Auto-fetch on mount / interviewId change
  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  return {
    report,
    loading,
    analyzing,
    error,
    notFound,
    isAdmin,
    refetch: fetchReport,
    analyze,
  };
}
