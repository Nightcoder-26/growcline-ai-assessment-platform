import { AlertSeverity } from "./types";

export interface SimulationEvent {
  title: string;
  message: string;
  severity: AlertSeverity;

  faceDetected: boolean;
  microphone: boolean;
  fullscreen: boolean;

  network: "Excellent" | "Good" | "Poor";
}

export const simulationEvents: SimulationEvent[] = [
  {
    title: "Interview Started",
    message: "Candidate joined interview.",
    severity: "success",

    faceDetected: true,
    microphone: true,
    fullscreen: true,

    network: "Excellent",
  },

  {
    title: "Looking Away",
    message: "Candidate looked away from screen.",
    severity: "warning",

    faceDetected: true,
    microphone: true,
    fullscreen: true,

    network: "Excellent",
  },

  {
    title: "Face Missing",
    message: "Face not detected.",
    severity: "danger",

    faceDetected: false,
    microphone: true,
    fullscreen: true,

    network: "Excellent",
  },

  {
    title: "Multiple Faces",
    message: "Additional face detected.",
    severity: "warning",

    faceDetected: true,
    microphone: true,
    fullscreen: true,

    network: "Good",
  },

  {
    title: "Network Weak",
    message: "Connection quality dropped.",
    severity: "warning",

    faceDetected: true,
    microphone: true,
    fullscreen: true,

    network: "Poor",
  },

  {
    title: "Face Restored",
    message: "Candidate back in frame.",
    severity: "success",

    faceDetected: true,
    microphone: true,
    fullscreen: true,

    network: "Excellent",
  },
];