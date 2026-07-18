export const cheatingData = {
  header: {
    interview: "Frontend Developer",
    candidate: "John Doe",
    duration: "00:15:42",
    sessionId: "INT-2026-001",
    status: "Monitoring" as const,
  },

  riskScore: 72,

  statusCards: [
    {
      title: "Face Detection",
      value: "Detected",
      status: "success",
      icon: "face",
    },
    {
      title: "Multiple Faces",
      value: "Not Detected",
      status: "success",
      icon: "users",
    },
    {
      title: "Browser Focus",
      value: "Focused",
      status: "success",
      icon: "browser",
    },
    {
      title: "Audio",
      value: "Voice Detected",
      status: "warning",
      icon: "mic",
    },
  ],

  events: [
    {
      id: 1,
      time: "10:15",
      event: "Tab Switched",
      severity: "High",
    },
    {
      id: 2,
      time: "10:18",
      event: "Face Lost",
      severity: "Medium",
    },
    {
      id: 3,
      time: "10:20",
      event: "Voice Detected",
      severity: "High",
    },
  ],

  recommendation: {
    recommendation: "Manual Review Required",
    reasons: [
      "Multiple tab switches detected.",
      "Voice activity detected.",
      "Face was temporarily unavailable.",
    ],
  },
};