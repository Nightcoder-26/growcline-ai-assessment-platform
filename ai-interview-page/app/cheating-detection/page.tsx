import DetectionHeader from "@/components/cheating-detection/DetectionHeader";
import QuickStats from "@/components/cheating-detection/QuickStats";
import RiskScoreCard from "@/components/cheating-detection/RiskScoreCard";
import DetectionStatusCards from "@/components/cheating-detection/DetectionStatusCards";
import EventsTimeline from "@/components/cheating-detection/EventsTimeline";
import EventsTable from "@/components/cheating-detection/EventsTable";
import RecommendationCard from "@/components/cheating-detection/RecommendationCard";

import { cheatingData } from "@/data/cheatingData";

export default function CheatingDetectionPage() {
  return (
    <main className="min-h-screen bg-[#0B1120] p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header */}
        <DetectionHeader {...cheatingData.header} />

        {/* Quick Stats */}
        <QuickStats
          events={cheatingData.events.length}
          riskScore={cheatingData.riskScore}
          duration={cheatingData.header.duration}
          status={cheatingData.header.status}
        />

        {/* Risk Score */}
        <RiskScoreCard score={cheatingData.riskScore} />

        {/* Detection Status */}
        <DetectionStatusCards cards={cheatingData.statusCards} />

        {/* Timeline & Events */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <EventsTimeline events={cheatingData.events} />

          <EventsTable events={cheatingData.events} />
        </div>

        {/* Recommendation */}
        <RecommendationCard
          recommendation={cheatingData.recommendation.recommendation}
          reasons={cheatingData.recommendation.reasons}
        />
      </div>
    </main>
  );
}