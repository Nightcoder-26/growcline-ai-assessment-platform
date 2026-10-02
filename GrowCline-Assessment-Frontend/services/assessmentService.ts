/**
 * Assessment Service — Team A API Layer
 *
 * Centralises all Team A API calls using the shared Axios instance.
 * Controllers: /api/aptitude, /api/technical, /api/coding,
 *              /api/assessment, /api/results, /api/analytics, /api/users
 */

import apiClient from "@/lib/apiClient";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AptitudeQuestion {
  id: string;
  _id: string;
  question: string;
  category: string;
  difficulty: string;
  options: string[];
  correctAnswer: string;
  explanation: string;
  marks: number;
  questionType: string;
  tags: string[];
}

export interface TechnicalQuestion {
  id: string;
  _id: string;
  question: string;
  technology: string;
  category: string;
  difficulty: string;
  options: string[];
  correctAnswer: string;
  explanation: string;
  marks: number;
  questionType: string;
  tags: string[];
}

export interface CodingQuestion {
  id: string;
  _id: string;
  title: string;
  programmingLanguage: string;
  difficulty: string;
  problemStatement: string;
  inputFormat: string;
  outputFormat: string;
  constraints: string;
  sampleInput: string;
  sampleOutput: string;
  testCases: { input: string; output: string; explanation?: string }[];
  marks: number;
  category: string;
  timeLimit: number;
  memoryLimit: number;
  explanation: string;
  tags: string[];
}

export interface AssessmentResult {
  id: string;
  assessmentId: string;
  userId: string;
  aptitudeScore: number;
  technicalScore: number;
  codingScore: number;
  totalScore: number;
  percentage: number;
  rank: number | null;
  totalQuestions: number;
  correctAnswers: number;
  wrongAnswers: number;
  unansweredQuestions: number;
  totalTime: number;
  strongestSkill: string;
  weakestSkill: string;
  recommendation: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  aptitudeAnswers: AnswerRecord[];
  technicalAnswers: AnswerRecord[];
  codingSubmissions: CodingSubmission[];
}

export interface AnswerRecord {
  questionId: string;
  selectedAnswer: string;
  isCorrect?: boolean;
}

export interface CodingSubmission {
  questionId: string;
  code: string;
  language: string;
  score?: number;
  testsPassed?: number;
  testsTotal?: number;
}

// ── Judge / Run types ────────────────────────────────────────────────────────

export interface RunCaseResult {
  test_case_id: string;
  is_hidden: boolean;
  passed: boolean;
  status: string;
  execution_time_ms: number;
  memory_kb: number;
  error_message: string;
  input: string;
  expected_output: string;
  actual_output: string;
}

export interface RunResult {
  success: boolean;
  overall_status: string;
  passed: number;
  total: number;
  results: RunCaseResult[];
  message?: string;
}

export interface SubmitOneResult {
  success: boolean;
  question_id: string;
  status: string;
  marks_obtained: number;
  max_marks: number;
  passed_tests: number;
  total_tests: number;
  percentage: number;
  sample_results: RunCaseResult[];
  sample_passed: number;
  sample_total: number;
  hidden_summary: { passed: number; total: number };
}

export interface SubmitAllResult {
  success: boolean;
  score: number;
  total: number;
  percentage: number;
  results: SubmitOneResult[];
}

export interface CandidateAnalytics {
  id: string;
  userId: string;
  assessmentId: string;
  aptitudeScore: number;
  technicalScore: number;
  codingScore: number;
  totalScore: number;
  percentage: number;
  rank: number | null;
  strongestSkill: string;
  weakestSkill: string;
  recommendation: string;
  totalQuestions: number;
  correctAnswers: number;
  wrongAnswers: number;
  unansweredQuestions: number;
  totalTime: number;
  createdAt: string;
  updatedAt: string;
}

export interface SkillAnalysis {
  averageAptitude?: number;
  averageTechnical?: number;
  averageCoding?: number;
  averageTotal?: number;
  strongestSkill?: string;
  weakestSkill?: string;
  totalAssessments?: number;
  [key: string]: unknown;
}

export interface UserProfile {
  id?: string;
  _id?: string;
  fullName: string;
  email: string;
  role: string;
}

// ---------------------------------------------------------------------------
// Aptitude
// ---------------------------------------------------------------------------

export async function generateAptitudeQuestions(
  numberOfQuestions = 10,
  difficulty?: string
): Promise<AptitudeQuestion[]> {
  const body: Record<string, unknown> = { numberOfQuestions };
  if (difficulty) body.difficulty = difficulty;
  const { data } = await apiClient.post("/api/aptitude/generate", body);
  // backend returns { questions: [...] } or array directly
  return Array.isArray(data) ? data : (data.questions ?? data.data ?? []);
}

export async function submitAptitudeAnswers(
  answers: AnswerRecord[]
): Promise<{ score: number; total: number; percentage: number; results?: unknown[] }> {
  const { data } = await apiClient.post("/api/aptitude/submit", { answers });
  return data;
}

// ---------------------------------------------------------------------------
// Technical
// ---------------------------------------------------------------------------

export async function generateTechnicalQuestions(
  numberOfQuestions = 10,
  difficulty?: string,
  technology?: string
): Promise<TechnicalQuestion[]> {
  const body: Record<string, unknown> = { numberOfQuestions };
  if (difficulty) body.difficulty = difficulty;
  if (technology) body.technology = technology;
  const { data } = await apiClient.post("/api/technical/generate", body);
  return Array.isArray(data) ? data : (data.questions ?? data.data ?? []);
}

export async function submitTechnicalAnswers(
  answers: AnswerRecord[]
): Promise<{ score: number; total: number; percentage: number; results?: unknown[] }> {
  const { data } = await apiClient.post("/api/technical/submit", { answers });
  return data;
}

// ---------------------------------------------------------------------------
// Coding
// ---------------------------------------------------------------------------

export async function generateCodingQuestions(
  numberOfQuestions = 1,
  difficulty?: string
): Promise<CodingQuestion[]> {
  const body: Record<string, unknown> = { numberOfQuestions };
  if (difficulty) body.difficulty = difficulty;
  const { data } = await apiClient.post("/api/coding/generate", body);
  return Array.isArray(data) ? data : (data.questions ?? data.data ?? []);
}

export async function runCode(
  questionId: string,
  code: string,
  language: string
): Promise<RunResult> {
  const { data } = await apiClient.post("/api/coding/run", {
    questionId,
    code,
    language,
  });
  return data;
}

export async function submitOneProblem(
  questionId: string,
  code: string,
  language: string
): Promise<SubmitOneResult> {
  const { data } = await apiClient.post("/api/coding/submit-one", {
    questionId,
    code,
    language,
  });
  return data;
}

export async function submitCodingAnswers(
  answers: CodingSubmission[],
  assessmentId?: string
): Promise<SubmitAllResult> {
  const { data } = await apiClient.post("/api/coding/submit", {
    answers,
    assessmentId,
  });
  return data;
}

// ---------------------------------------------------------------------------
// Results
// ---------------------------------------------------------------------------

export async function getCandidateResults(userId: string): Promise<AssessmentResult[]> {
  const { data } = await apiClient.get(`/api/results/candidate/${userId}`);
  return Array.isArray(data) ? data : (data.results ?? data.data ?? []);
}

export async function saveResult(payload: Partial<AssessmentResult> & {
  assessmentId: string;
  userId: string;
}): Promise<AssessmentResult> {
  const { data } = await apiClient.post("/api/results", payload);
  return data.result ?? data;
}

// ---------------------------------------------------------------------------
// Analytics
// ---------------------------------------------------------------------------

export async function getCandidateAnalytics(userId: string): Promise<CandidateAnalytics[]> {
  const { data } = await apiClient.get(`/api/analytics/candidate/${userId}`);
  return Array.isArray(data) ? data : (data.analytics ?? data.data ?? []);
}

export async function getSkillAnalysis(userId: string): Promise<SkillAnalysis> {
  const { data } = await apiClient.get(`/api/analytics/skill-analysis/${userId}`);
  return data.skillAnalysis ?? data.data ?? data ?? {};
}

export async function getDashboardAnalytics(userId: string): Promise<Record<string, unknown>> {
  const { data } = await apiClient.get(`/api/analytics/dashboard/${userId}`);
  return data.analytics ?? data.data ?? data ?? {};
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------

export async function getUserProfile(userId: string): Promise<UserProfile | null> {
  try {
    const { data } = await apiClient.get(`/api/users/${userId}`);
    return data.user ?? data.data ?? data ?? null;
  } catch {
    return null;
  }
}

// ---------------------------------------------------------------------------
// Personalized Assessment Paper Fetching (Stable, Non-repeating)
// ---------------------------------------------------------------------------

export async function getPersonalizedAssessmentPaper(): Promise<{
  assessmentId: string;
  aptitudeQuestions: AptitudeQuestion[];
  technicalQuestions: TechnicalQuestion[];
  codingQuestions: CodingQuestion[];
}> {
  const { data: res } = await apiClient.post("/api/resume/generate-assessment");
  const dataObj = res.data ?? res;
  const assessmentId = dataObj.assessmentId;

  if (!assessmentId) {
    throw new Error("Unable to locate personalized assessment.");
  }

  const { data: paperRes } = await apiClient.post(`/api/assessment/${assessmentId}/start`);
  const paper = paperRes.data ?? paperRes;

  return {
    assessmentId,
    aptitudeQuestions: paper.aptitudeQuestionsList ?? [],
    technicalQuestions: paper.technicalQuestionsList ?? [],
    codingQuestions: paper.codingQuestionsList ?? [],
  };
}

