export type AlertSeverity =
  | "success"
  | "warning"
  | "danger"
  | "info";

export interface AlertEvent {
  id: number;
  title: string;
  message: string;
  severity: AlertSeverity;
  time: string;
}

export interface ActivityEvent {
  id: number;
  event: string;
  time: string;
  severity: AlertSeverity;
}

export interface TimelineEvent {
  id: number;
  title: string;
  subtitle: string;
  severity: AlertSeverity;
  time: string;
}

export interface ProctorState {
  faceDetected: boolean;
  microphone: boolean;
  fullscreen: boolean;
  network: "Excellent" | "Good" | "Poor";

  alerts: AlertEvent[];
  logs: ActivityEvent[];
  timeline: TimelineEvent[];
}