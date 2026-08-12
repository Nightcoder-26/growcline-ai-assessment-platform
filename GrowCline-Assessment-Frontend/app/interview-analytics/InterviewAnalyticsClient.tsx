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

  // Sanitise: treat null, undefined, and empty string as "no ID"
  const rawId = searchParams?.get("interviewId");
  const interviewId: string | null = rawId?.trim() || null;

  // ── Context session (written by Video Recording page) ─────────────────────
  const { session, restoreSession } = useInterviewSession();

  // Start with loading=false when there is no interviewId
  const [data, setData] = useState<FullAnalyticsData | null>(null);
  const [loading, setLoading] = useState(!!interviewId);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Track whether we attempted restoration from sessionStorage
  const restoredRef = useRef(false);

  // ── Restore session from sessionStorage if context is empty ───────────────
  useEffect(() => {
    if (!interviewId || restoredRef.current) return;
    restoredRef.current = true;
    if (!session.interviewId || session.interviewId !== interviewId) {
      restoreSession(interviewId);
    }
  }, [interviewId, session.interviewId, restoreSession]);

  // ── Merge context proctoring values into API data ─────────────────────────
  const mergeContextMetrics = useCallback(
    (apiData: FullAnalyticsData): FullAnalyticsData => {
      if (!session.interviewId || session.interviewId !== interviewId) {
        return apiData; // No live session — use API data as-is
      }

      const proctor = {
        faceMissing:      session.faceMissing,
        multipleFaces:    session.multipleFaces,
        tabSwitches:      session.tabSwitches,
        networkIssues:    apiData.proctor.networkIssues,
        microphoneIssues: session.microphoneViolations,
        fullscreenExits:  session.fullscreenExits,
      };

      const riskScore =
        session.riskScore > 0 ? session.riskScore : apiData.metrics.riskScore;

      const overallScore =
        apiData.overallScore > 0 ? apiData.overallScore : session.overallScore;

      const duration =
        session.duration && session.duration !== ""
          ? session.duration
          : apiData.duration;

      // Derive insights from actual session data
      const strengths: string[] = [];
      const improvements: string[] = [];

      if (session.tabSwitches === 0)
        strengths.push("Maintained full browser focus throughout the session.");
      if (session.multipleFaces === 0)
        strengths.push("No multiple faces detected — single-candidate integrity confirmed.");
      if (riskScore < 20)
        strengths.push("Overall risk score is low, indicating honest conduct.");
      if (session.tabSwitches > 0)
        improvements.push(`Reduce tab switching — detected ${session.tabSwitches} times.`);
      if (session.multipleFaces > 0)
        improvements.push(`Avoid having other people in frame — detected ${session.multipleFaces} times.`);
      if (session.fullscreenExits > 0)
        improvements.push(`Stay in fullscreen mode — exited ${session.fullscreenExits} times.`);
      if (session.faceMissing > 0)
        improvements.push(`Keep face visible in camera — off-screen ${session.faceMissing} times.`);
      if (session.microphoneViolations > 0)
        improvements.push(`Avoid muting microphone — detected ${session.microphoneViolations} times.`);

      const finalStrengths = strengths.length > 0 ? strengths : apiData.strengths;
      const finalImprovements = improvements.length > 0 ? improvements : apiData.improvements;

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
        metrics: { ...apiData.metrics, riskScore },
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
      // Guard: never call API with empty/null interviewId
      if (!interviewId) {
        setLoading(false);
        return;
      }

      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      setError(null);

      try {
        const query = isRefresh ? "?refresh=true" : "";
        const res = await apiClient.get(
          `/api/interview-analytics/${interviewId}${query}`
        );
        if (res.data?.data) {
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
          const msg = err instanceof Error ? err.message : "Failed to load analytics.";
          setError(msg);
        }
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [interviewId, mergeContextMetrics]
  );

  // Re-merge whenever live session proctoring values change
  useEffect(() => {
    if (!data) return;
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

  // Initial fetch + conditional polling (stops once data is successfully loaded)
  useEffect(() => {
    if (!interviewId) return;
    fetchAnalytics(true);
    if (data) return;
    const interval = setInterval(() => fetchAnalytics(true), 15000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [interviewId, !!data]);

  // ── Guard: No interview ID ────────────────────────────────────────────────
  if (!interviewId) {
    return (
      <main className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-8">
        <div className="max-w-md w-full rounded-[28px] border border-white/10 bg-[#1E293B] p-8 text-center space-y-4 shadow-2xl text-white">
          <div className="text-5xl">⚠️</div>
          <h2 className="text-xl font-bold text-amber-400">No Interview Session Specified</h2>
          <p className="text-slate-400 text-sm">
            Please complete an interview on the Video Recording page first. You'll be
            automatically redirected here when your session ends.
          </p>
          <Link
            href="/video-recording"
            className="inline-flex items-center gap-2 rounded-2xl bg-[#4096ff] hover:bg-[#60a5fa] px-6 py-3 font-semibold text-white transition"
          >
            <ArrowLeft className="h-4 w-4" /> Start Interview
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
          <Link
            href="/video-recording"
            className="block mt-2 text-sm text-slate-400 hover:text-white transition"
          >
            ← Back to Interview
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#F8FAFC] p-6 lg:p-10 font-sans">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header Bar */}
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

        <AnalyticsHeader interview={data.interview} candidate={data.candidate} />

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

        <RecommendationCard status={data.recommendation} summary={data.summary} />
      </div>
    </main>
  );
}
