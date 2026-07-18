export interface InterviewAnalyticsData {
  candidate: string;
  interview: string;
  duration: string;
  date: string;
  status: "Completed";

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
  };

  recommendations: string[];

  questionScores: {
    question: string;
    score: number;
  }[];
}