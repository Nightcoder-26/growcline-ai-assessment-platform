"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import apiClient from "@/lib/apiClient";
import { useInterviewSession } from "@/contexts/InterviewSessionContext";

import AnalyticsHeader from "@/components/interview-analytics/AnalyticsHeader";
import SummaryCard from "@/components/interview-analytics/SummaryCard";
import OverallScore from "@/components/interview-analytics/OverallScore";
import MetricsGrid from "@/components/interview-analytics/MetricsGrid";
import ProctorSummary from "@/components/interview-analytics/ProctorSummary";
import AIInsights from "@/components/interview-analytics/AIInsights";
import RecommendationCard from "@/components/interview-analytics/RecommendationCard";
import { ArrowLeft, RefreshCw } from "lucide-react";

// ---------------------------------------------------------------------------
// Shape expected by the frontend components
// ---------------------------------------------------------------------------

export interface FullAnalyticsData {
  candidate: string;
  interview: string;
  duration: string;
  date: string;
  overallScore: number;
  metrics: {
    confidence: number;
    communication: number;
    technical: number;
    eyeContact: number;
    riskScore: number;
    grade: string;
  };
  proctor: {
    faceMissing: number;
    multipleFaces: number;
    tabSwitches: number;
    networkIssues: number;
    microphoneIssues: number;
    fullscreenExits: number;
  };
  strengths: string[];
  improvements: string[];
  recommendation: "Recommended" | "Not Recommended" | "Needs Improvement";
  summary: string;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function InterviewAnalyticsClient() {
  const searchParams = useSearchParams();
  const interviewId = searchParams?.get("interviewId") ?? null;

  // ── Context session (written by Video Recording page) ─────────────────────
  const { session, restoreSession } = useInterviewSession();

  const [data, setData] = useState<FullAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Track whether we attempted restoration from sessionStorage
  const restoredRef = useRef(false);

  // ── Restore session from sessionStorage if context is empty ───────────────
  useEffect(() => {
    if (!interviewId || restoredRef.current) return;
    restoredRef.current = true;
    // If context has no live session for this interviewId, try sessionStorage
    if (!session.interviewId || session.interviewId !== interviewId) {
      restoreSession(interviewId);
    }
  }, [interviewId, session.interviewId, restoreSession]);

  // ── Merge context proctoring values into API data ─────────────────────────
  //
  // The context is the canonical source of truth for proctoring metrics.
  // If the context session matches the current interviewId we override
  // those specific fields from context so they are guaranteed identical
  // to what was displayed on the Video Recording page.
  //
  const mergeContextMetrics = useCallback(
    (apiData: FullAnalyticsData): FullAnalyticsData => {
      if (!session.interviewId || session.interviewId !== interviewId) {
        return apiData; // No live session — use API data as-is
      }

      // Proctoring counters: always use context values (live, never cached)
      const proctor = {
        faceMissing:     session.faceMissing,
        multipleFaces:   session.multipleFaces,
        tabSwitches:     session.tabSwitches,
        networkIssues:   apiData.proctor.networkIssues, // not tracked in context
        microphoneIssues: session.microphoneViolations,
        fullscreenExits: session.fullscreenExits,
      };

      // Risk score: prefer context (live), fall back to API
      const riskScore =
        session.riskScore > 0 ? session.riskScore : apiData.metrics.riskScore;

      // Overall score: prefer API (AI-computed), fall back to context
      const overallScore =
        apiData.overallScore > 0 ? apiData.overallScore : session.overallScore;

      // Duration: prefer context (exact elapsed time from Video Recording)
      const duration =
        session.duration && session.duration !== ""
          ? session.duration
          : apiData.duration;

      // Derive AI insights from actual proctoring data in context
      const strengths: string[] = [];
      const improvements: string[] = [];

      if (session.tabSwitches === 0) {
        strengths.push("Maintained full browser focus throughout the session.");
      }
      if (session.multipleFaces === 0) {
        strengths.push(
          "No multiple faces detected — single-candidate integrity confirmed."
        );
      }
      if (riskScore < 20) {
        strengths.push("Overall risk score is low, indicating honest conduct.");
      }
      if (session.tabSwitches > 0) {
        improvements.push(
          `Reduce tab switching — detected ${session.tabSwitches} times.`
        );
      }
      if (session.multipleFaces > 0) {
        improvements.push(
          `Avoid having other people in frame — detected ${session.multipleFaces} times.`
        );
      }
      if (session.fullscreenExits > 0) {
        improvements.push(
          `Stay in fullscreen mode — exited ${session.fullscreenExits} times.`
        );
      }
      if (session.faceMissing > 0) {
        improvements.push(
          `Keep face visible in camera — detected off-screen ${session.faceMissing} times.`
        );
      }
      if (session.microphoneViolations > 0) {
        improvements.push(
          `Avoid muting microphone during interview — detected ${session.microphoneViolations} times.`
        );
      }

      // Use API strengths/improvements as baseline if context has no violations
      const finalStrengths =
        strengths.length > 0 ? strengths : apiData.strengths;
      const finalImprovements =
        improvements.length > 0 ? improvements : apiData.improvements;

      // Final recommendation derived from live risk score
      const finalRecommendation: FullAnalyticsData["recommendation"] =
        riskScore >= 60
          ? "Not Recommended"
          : riskScore >= 25 || overallScore < 60
          ? "Needs Improvement"
          : "Recommended";

      return {
        ...apiData,
        duration,
        overallScore,
        metrics: {
          ...apiData.metrics,
          riskScore,
        },
        proctor,
        strengths: finalStrengths,
        improvements: finalImprovements,
        recommendation: finalRecommendation,
      };
    },
    [session, interviewId]
  );

  // ── Fetch from backend ─────────────────────────────────────────────────────
  const fetchAnalytics = useCallback(
    async (isRefresh = false) => {
      if (!interviewId) return;
      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      setError(null);

      try {
        const query = isRefresh ? "?refresh=true" : "";
        const res = await apiClient.get(
          `/api/interview-analytics/${interviewId}${query}`
        );
        if (res.data?.data) {
          // Merge context metrics on top of API data
          setData(mergeContextMetrics(res.data.data as FullAnalyticsData));
        }
      } catch {
        try {
          await apiClient.post(
            `/api/analytics/interview/${interviewId}/generate`,
            { force_refresh: true }
          );
          const res = await apiClient.get(
            `/api/interview-analytics/${interviewId}?refresh=true`
          );
          if (res.data?.data) {
            setData(mergeContextMetrics(res.data.data as FullAnalyticsData));
          }
        } catch (err) {
          const msg =
            err instanceof Error ? err.message : "Failed to load analytics.";
          setError(msg);
        }
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [interviewId, mergeContextMetrics]
  );

  // ── Re-merge whenever session context updates (live session still running) ─
  useEffect(() => {
    if (!data) return;
    // Re-apply context merge whenever session proctoring values change
    setData((prev) => (prev ? mergeContextMetrics(prev) : prev));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    session.riskScore,
    session.tabSwitches,
    session.faceMissing,
    session.multipleFaces,
    session.microphoneViolations,
    session.fullscreenExits,
  ]);

  // ── Initial fetch + polling ────────────────────────────────────────────────
  useEffect(() => {
    fetchAnalytics(true);
    const interval = setInterval(() => {
      fetchAnalytics(true);
    }, 8000);
    return () => clearInterval(interval);
  }, [fetchAnalytics]);

  // ── Guard: No interview ID ────────────────────────────────────────────────
  if (!interviewId) {
    return (
      <main className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-8">
        <div className="max-w-md w-full rounded-[28px] border border-white/10 bg-[#1E293B] p-8 text-center space-y-4 shadow-2xl text-white">
          <div className="text-5xl">⚠️</div>
          <h2 className="text-xl font-bold text-amber-400">No Interview Session Specified</h2>
          <p className="text-slate-400 text-sm">
            Please provide a valid session parameter in the URL query string.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-2xl bg-[#4096ff] hover:bg-[#60a5fa] px-6 py-3 font-semibold text-white transition"
          >
            <ArrowLeft className="h-4 w-4" /> Start New Session
          </Link>
        </div>
      </main>
    );
  }

  // ── Guard: Loading ────────────────────────────────────────────────────────
  if (loading) {
    return (
      <main className="min-h-screen bg-[#F8FAFC] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-[#4096ff] border-t-transparent animate-spin" />
          <p className="text-slate-700 font-semibold text-sm">Processing session analytics report…</p>
        </div>
      </main>
    );
  }

  // ── Guard: Error ──────────────────────────────────────────────────────────
  if (error || !data) {
    return (
      <main className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-8">
        <div className="max-w-md w-full rounded-[28px] border border-white/10 bg-[#1E293B] p-8 text-center space-y-4 shadow-2xl text-white">
          <div className="text-5xl">❌</div>
          <h2 className="text-xl font-bold text-rose-400">Error Loading Analytics</h2>
          <p className="text-slate-400 text-sm">{error ?? "Unable to load analytics report."}</p>
          <button
            onClick={() => fetchAnalytics(true)}
            className="w-full rounded-2xl bg-[#4096ff] hover:bg-[#60a5fa] py-3 font-semibold text-white transition"
          >
            Retry Analytics Generation
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#F8FAFC] p-6 lg:p-10 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header Bar with Action Controls */}
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-2 rounded-2xl bg-[#1E293B] border border-white/10 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 shadow-md"
          >
            <ArrowLeft className="h-4 w-4 text-[#4096ff]" /> Back to Home
          </Link>

          <button
            onClick={() => fetchAnalytics(true)}
            disabled={refreshing}
            className="flex items-center gap-2 rounded-2xl bg-[#4096ff] px-5 py-2.5 text-sm font-semibold text-white shadow-md transition hover:bg-[#60a5fa] disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
            {refreshing ? "Re-evaluating…" : "Refresh Report"}
          </button>
        </div>

        <AnalyticsHeader
          interview={data.interview}
          candidate={data.candidate}
        />

        <SummaryCard
          candidate={data.candidate}
          interview={data.interview}
          duration={data.duration}
          date={data.date}
          status="Completed"
        />

        <OverallScore score={data.overallScore} />

        <MetricsGrid metrics={data.metrics} />

        <ProctorSummary proctor={data.proctor} />

        <AIInsights strengths={data.strengths} improvements={data.improvements} />

        <RecommendationCard
          status={data.recommendation}
          summary={data.summary}
        />
      </div>
    </main>
  );
}
