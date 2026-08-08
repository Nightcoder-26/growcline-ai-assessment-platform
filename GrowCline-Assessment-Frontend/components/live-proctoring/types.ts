export type AlertSeverity =
  | "success"
  | "warning"
  | "danger"
  | "info";

export interface AlertEvent {
  /** MongoDB document ObjectId string */
  id: string;
  title: string;
  message: string;
  severity: AlertSeverity;
  time: string;
}

export interface ActivityEvent {
  /** MongoDB document ObjectId string */
  id: string;
  event: string;
  time: string;
  severity: AlertSeverity;
}

export interface TimelineEvent {
  /** MongoDB document ObjectId string */
  id: string;
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