/**
 * useInterview — manages the full AI interview session lifecycle.
 *
 * Wraps:
 *   POST /api/interviews/start
 *   POST /api/interviews/{id}/question
 *   POST /api/interviews/{id}/answer
 *   POST /api/interviews/{id}/end
 *
 * Usage:
 *   const { interview, currentQuestion, evaluation, loading, error,
 *           startInterview, getNextQuestion, submitAnswer, endInterview } = useInterview();
 */

"use client";

import { useCallback, useState } from "react";
import apiClient from "@/lib/apiClient";

// ---------------------------------------------------------------------------
// Types (matching backend response shapes)
// ---------------------------------------------------------------------------

export interface InterviewSession {
  id: string;
  userId: string;
  jobRole: string;
  interviewType: string;
  status: string;
  difficulty: string;
  currentQuestion: number;
  totalQuestions: number;
  startedAt: string | null;
  endedAt: string | null;
  durationSeconds: number;
  remainingSeconds: number | null;
}

export interface InterviewQuestion {
  id: string;
  interviewId: string;
  questionNumber: number;
  questionType: string;
  questionText: string;
  generatedBy: string;
  remainingQuestions: number | null;
  totalQuestions: number | null;
  remainingSeconds: number | null;
  createdAt: string | null;
}

export interface InterviewEvaluation {
  id: string;
  interviewId: string;
  questionId: string;
  candidateAnswer: string;
  evaluationScore: number;
  feedback: string;
  keywordsMatched: string[];
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  answeredAt: string | null;
  currentQuestion: number | null;
  totalQuestions: number | null;
  interviewComplete: boolean | null;
}

export interface InterviewSummary {
  interviewId: string;
  status: string;
  jobRole: string;
  interviewType: string;
  difficulty: string;
  totalQuestions: number;
  questionsAnswered: number;
  averageScore: number | null;
  startedAt: string | null;
  endedAt: string | null;
  durationSeconds: number;
  actualDurationSeconds: number | null;
}

// ---------------------------------------------------------------------------
// Start config
// ---------------------------------------------------------------------------

export interface StartInterviewConfig {
  jobRole?: string;
  interviewType?: "TECHNICAL" | "HR" | "BEHAVIORAL" | "RESUME_BASED";
  difficulty?: "EASY" | "MEDIUM" | "HARD";
  totalQuestions?: number;
  durationSeconds?: number;
  resumeId?: string;
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useInterview() {
  const [interview, setInterview] = useState<InterviewSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<InterviewQuestion | null>(null);
  const [evaluation, setEvaluation] = useState<InterviewEvaluation | null>(null);
  const [summary, setSummary] = useState<InterviewSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Start a new interview session ────────────────────────────────────────

  const startInterview = useCallback(
    async (config: StartInterviewConfig = {}) => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.post("/api/interviews/start", {
          jobRole: config.jobRole ?? "Software Engineer",
          interviewType: config.interviewType ?? "TECHNICAL",
          difficulty: config.difficulty ?? "MEDIUM",
          totalQuestions: config.totalQuestions ?? 5,
          durationSeconds: config.durationSeconds ?? 1800,
          ...(config.resumeId ? { resumeId: config.resumeId } : {}),
        });

        const { interview: sess, firstQuestion } = res.data.data as {
          interview: InterviewSession;
          firstQuestion: InterviewQuestion;
        };

        setInterview(sess);
        setCurrentQuestion(firstQuestion);
        setEvaluation(null);
        setSummary(null);
        return { interview: sess, firstQuestion };
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Failed to start interview.";
        setError(msg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // ── Get next question ─────────────────────────────────────────────────────

  const getNextQuestion = useCallback(
    async (interviewId: string, topicHint?: string) => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.post(`/api/interviews/${interviewId}/question`, {
          topicHint: topicHint ?? null,
        });
        const question = res.data.data as InterviewQuestion;
        setCurrentQuestion(question);
        return question;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Failed to get next question.";
        setError(msg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // ── Submit answer ─────────────────────────────────────────────────────────

  const submitAnswer = useCallback(
    async (interviewId: string, questionId: string, candidateAnswer: string) => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiClient.post(`/api/interviews/${interviewId}/answer`, {
          questionId,
          candidateAnswer,
        });
        const eval_ = res.data.data as InterviewEvaluation;
        setEvaluation(eval_);
        return eval_;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Failed to submit answer.";
        setError(msg);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // ── End interview ─────────────────────────────────────────────────────────

  const endInterview = useCallback(async (interviewId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.post(`/api/interviews/${interviewId}/end`);
      const summ = res.data.data as InterviewSummary;
      setSummary(summ);
      return summ;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to end interview.";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    interview,
    currentQuestion,
    evaluation,
    summary,
    loading,
    error,
    startInterview,
    getNextQuestion,
    submitAnswer,
    endInterview,
  };
}
