import LandingPage from "@/components/landing/LandingPage";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AssessAI — AI-Powered Assessment & Interview Intelligence",
  description:
    "Automate screening with adaptive AI interviews, live proctoring, and deep analytics. Go from applicant to offer in days, not weeks.",
};

export default function Home() {
  return <LandingPage />;
}