"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import apiClient from "@/lib/apiClient";

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

  const [data, setData] = useState<FullAnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch full report from GET /api/interview-analytics/{interviewId}
  const fetchAnalytics = useCallback(
    async (isRefresh = false) => {
      if (!interviewId) return;
      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      setError(null);

      try {
        const query = isRefresh ? "?refresh=true" : "";
        const res = await apiClient.get(`/api/interview-analytics/${interviewId}${query}`);
        if (res.data?.data) {
          setData(res.data.data as FullAnalyticsData);
        }
      } catch {
        try {
          await apiClient.post(`/api/analytics/interview/${interviewId}/generate`, {
            force_refresh: true,
          });
          const res = await apiClient.get(`/api/interview-analytics/${interviewId}?refresh=true`);
          if (res.data?.data) {
            setData(res.data.data as FullAnalyticsData);
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
    [interviewId]
  );

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
