import { ProctorState } from "./types";

export const initialProctorState: ProctorState = {
  faceDetected: true,
  microphone: true,
  fullscreen: true,
  network: "Excellent",

  // Live alerts will be generated dynamically
  alerts: [],

  // Activity log will be generated dynamically
  logs: [],

  // Timeline will also be generated dynamically
  timeline: [],
};