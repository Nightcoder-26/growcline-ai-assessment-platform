/**
 * Video Recording Page
 *
 * Supports optional URL params:
 *   /video-recording?jobRole=Backend+Developer&interviewType=TECHNICAL&difficulty=MEDIUM
 *
 * Defaults to: Software Engineer / TECHNICAL / MEDIUM
 *
 * InterviewStudio uses react-media-recorder which requires browser APIs
 * (Web Worker, MediaRecorder) — it must be loaded client-side only.
 */
"use client";

import dynamic from "next/dynamic";

// Disable SSR for InterviewStudio — react-media-recorder uses Web Worker
// which is not available in Node.js
const InterviewStudio = dynamic(
  () =>
    import("@/components/interview/interview-studio").then((m) => ({
      default: m.InterviewStudio,
    })),
  {
    ssr: false,
    loading: () => (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-10 h-10 rounded-full border-4 border-primary border-t-transparent animate-spin" />
      </div>
    ),
  }
);

export default function Page() {
  return <InterviewStudio />;
}