/**
 * Interview Analytics Page
 *
 * Reads interviewId from URL: /interview-analytics?interviewId=<id>
 */
import { Suspense } from "react";
import InterviewAnalyticsClient from "./InterviewAnalyticsClient";

export default function Page() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#0B1120] flex items-center justify-center">
          <div className="w-10 h-10 rounded-full border-4 border-[#4096ff] border-t-transparent animate-spin" />
        </div>
      }
    >
      <InterviewAnalyticsClient />
    </Suspense>
  );
}