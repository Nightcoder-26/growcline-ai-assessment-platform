import AnalyticsHeader from "./AnalyticsHeader";
import SummaryCard from "./SummaryCard";
import OverallScore from "./OverallScore";
import MetricsGrid from "./MetricsGrid";
import ProctorSummary from "./ProctorSummary";
import AIInsights from "./AIInsights";
import RecommendationCard from "./RecommendationCard";

export default function InterviewAnalytics() {
  return (
    <main className="min-h-screen bg-[#0B1120] p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <AnalyticsHeader
          interview="Frontend Developer Interview"
          candidate="John Doe"
        />

        <SummaryCard
          candidate="John Doe"
          interview="Frontend Developer"
          duration="32 Minutes"
          date="18 July 2026"
          status="Completed"
        />

        <OverallScore score={84} />

        <MetricsGrid
          metrics={{
            confidence: 89,
            communication: 84,
            technical: 91,
            eyeContact: 76,
            riskScore: 18,
            grade: "A",
          }}
        />

        <ProctorSummary
          proctor={{
            faceMissing: 2,
            multipleFaces: 1,
            tabSwitches: 3,
            networkIssues: 1,
            microphoneIssues: 0,
            fullscreenExits: 2,
          }}
        />
        <AIInsights
            strengths={[
                "Excellent communication skills",
                "Strong technical knowledge",
                "Maintained good eye contact",
            ]}
            improvements={[
                "Improve confidence during system design discussions",
                "Reduce unnecessary pauses while answering",
            ]}
        />
        <RecommendationCard
            status="Recommended"
            summary="The candidate demonstrated strong technical knowledge, clear communication skills, maintained good eye contact, and showed minimal proctoring violations throughout the interview. Overall performance indicates a strong fit for the role."
        />
      </div>
    </main>
  );
}