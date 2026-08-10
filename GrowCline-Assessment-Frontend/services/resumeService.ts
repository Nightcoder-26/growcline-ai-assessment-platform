/**
 * Resume Service — Team A API Layer for Resume & Personalized Assessments
 *
 * Interacts with /api/resume backend endpoints.
 */

import apiClient from "@/lib/apiClient";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SkillProfile {
  id?: string;
  name?: string;
  email?: string;
  experience_level?: "Fresher" | "Junior" | "Mid" | "Senior";
  education?: string;
  skills: string[];
  programming_languages: string[];
  frameworks: string[];
  libraries: string[];
  databases: string[];
  cloud_technologies: string[];
  tools: string[];
  domains: string[];
  projects: { name: string; technologies: string[] }[];
  certifications: string[];
  years_of_experience?: number;
}

export interface ProfileSummary {
  experienceLevel: string;
  topSkills: string[];
  totalSkills: number;
}

export interface ResumeStatus {
  hasResume: boolean;
  analyzedAt: string | null;
  resumeFilename: string | null;
  resumeVersion: number;
  profileSummary: ProfileSummary | null;
}

export interface PersonalizedAssessmentResponse {
  assessmentId: string;
  isNew: boolean;
  aptitudeCount: number;
  technicalCount: number;
  codingCount: number;
}

// ---------------------------------------------------------------------------
// API Calls
// ---------------------------------------------------------------------------

export async function uploadResume(file: File): Promise<SkillProfile> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post("/api/resume/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return data.data?.skillProfile ?? data.data ?? {};
}

export async function getResumeStatus(): Promise<ResumeStatus> {
  const { data } = await apiClient.get("/api/resume/status");
  return data.data ?? {
    hasResume: false,
    analyzedAt: null,
    resumeFilename: null,
    resumeVersion: 0,
    profileSummary: null,
  };
}

export async function getSkillProfile(): Promise<SkillProfile> {
  const { data } = await apiClient.get("/api/resume/profile");
  return data.data?.skillProfile ?? data.data ?? {};
}

export async function generatePersonalizedAssessment(
  forceNew = false
): Promise<PersonalizedAssessmentResponse> {
  const { data } = await apiClient.post(
    `/api/resume/generate-assessment${forceNew ? "?force_new=true" : ""}`
  );
  return data.data;
}

export async function deleteResume(): Promise<{ success: boolean; message: string }> {
  const { data } = await apiClient.delete("/api/resume");
  return data;
}
