export interface DetectionHeaderProps {
  interview: string;
  candidate: string;
  duration: string;
  sessionId: string;
  status: "Monitoring" | "Completed";
}

export interface RiskScoreCardProps {
  score: number;
}

export interface StatusCard {
  title: string;
  value: string;
  status: "success" | "warning" | "danger";
  icon: "face" | "users" | "browser" | "mic";
}

export interface DetectionStatusCardsProps {
  cards: StatusCard[];
}

export interface DetectionEvent {
  id: number;
  time: string;
  event: string;
  severity: "Low" | "Medium" | "High";
}

export interface EventsTimelineProps {
  events: DetectionEvent[];
}

export interface EventsTableProps {
  events: DetectionEvent[];
}

export interface RecommendationProps {
  recommendation: string;
  reasons: string[];
}

export interface QuickStatsProps {
  events: number;
  riskScore: number;
  duration: string;
  status: string;
}