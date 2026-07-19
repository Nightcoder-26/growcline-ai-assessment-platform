/**
 * Live Proctoring Page
 *
 * Reads interviewId from the URL query string:
 *   /live-proctoring?interviewId=<mongo_id>
 *
 * Falls back to a demo message if no interviewId is provided.
 */
import { Suspense } from "react";
import { ProctorStudio } from "@/components/live-proctoring/proctor-studio";

export default function LiveProctoringPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="w-10 h-10 rounded-full border-4 border-primary border-t-transparent animate-spin" />
      </div>
    }>
      <ProctorStudio />
    </Suspense>
  );
}