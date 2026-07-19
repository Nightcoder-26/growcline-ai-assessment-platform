/**
 * Cheating Detection Page
 *
 * Reads interviewId from URL: /cheating-detection?interviewId=<id>
 *
 * Admin users: can run analysis + view full report
 * Candidate users: can view their own report (read-only)
 */
import { Suspense } from "react";
import CheatingDetectionClient from "./CheatingDetectionClient";

export default function CheatingDetectionPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#0B1120] flex items-center justify-center">
          <div className="w-10 h-10 rounded-full border-4 border-[#4096ff] border-t-transparent animate-spin" />
        </div>
      }
    >
      <CheatingDetectionClient />
    </Suspense>
  );
}