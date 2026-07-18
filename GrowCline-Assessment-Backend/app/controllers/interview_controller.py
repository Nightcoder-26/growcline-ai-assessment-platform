"""
Interview Controller
Handles HTTP request/response lifecycle for all AI Interview endpoints.

Design principles (matching Team B's existing controllers):
- Receive FastAPI request parameters
- Delegate ALL business logic to interview_service
- Format JSONResponse with the standard {success, message, data} envelope
- Handle ValueError (400/404), PermissionError (403), RuntimeError (500)
- Never contain business logic
"""

import logging

from fastapi.responses import JSONResponse

try:
    import services.interview_service as interview_service
except ImportError:
    import app.services.interview_service as interview_service

logger = logging.getLogger(__name__)


class InterviewController:
    """AI Interview Controller — thin delegation and response formatting layer."""

    # ── POST /api/interviews/start ──────────────────────────────────────────

    @staticmethod
    async def start_interview(body: dict, current_user: dict) -> JSONResponse:
        """
        Create a new interview session and generate the first AI question.

        Returns 201 on success.
        """
        try:
            user_id = str(current_user["id"])

            result = interview_service.create_interview(
                user_id=user_id,
                job_role=body["jobRole"],
                interview_type=body["interviewType"],
                difficulty=body.get("difficulty", "MEDIUM"),
                total_questions=body.get("totalQuestions", 10),
                duration_seconds=body.get("durationSeconds", 1800),
                resume_id=body.get("resumeId"),
            )

            return JSONResponse(
                status_code=201,
                content={
                    "success": True,
                    "message": "Interview started successfully. First question generated.",
                    "data": result,
                },
            )

        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": str(error)},
            )

        except RuntimeError as error:
            logger.error("Start interview error: %s", error)
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": str(error)},
            )

        except Exception as error:
            logger.error("Unexpected error starting interview: %s", error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )

    # ── POST /api/interviews/{interview_id}/question ────────────────────────

    @staticmethod
    async def get_next_question(
        interview_id: str,
        body: dict,
        current_user: dict,
    ) -> JSONResponse:
        """
        Generate and return the next AI question for an active interview session.

        Returns 200 on success.
        """
        try:
            user_id    = str(current_user["id"])
            topic_hint = body.get("topicHint") if body else None

            question = interview_service.get_next_question(
                interview_id=interview_id,
                user_id=user_id,
                topic_hint=topic_hint,
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Question generated successfully.",
                    "data": question,
                },
            )

        except ValueError as error:
            status = 409 if "completed" in str(error).lower() else 400
            return JSONResponse(
                status_code=status,
                content={"success": False, "message": str(error)},
            )

        except PermissionError as error:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": str(error)},
            )

        except RuntimeError as error:
            logger.error("Next question error for %s: %s", interview_id, error)
            # Distinguish AI rate limit errors
            if "rate" in str(error).lower() or "429" in str(error):
                return JSONResponse(
                    status_code=429,
                    content={"success": False, "message": "AI service rate limit reached. Please try again shortly."},
                )
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": str(error)},
            )

        except Exception as error:
            logger.error("Unexpected error generating question for %s: %s", interview_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )

    # ── POST /api/interviews/{interview_id}/answer ──────────────────────────

    @staticmethod
    async def submit_answer(
        interview_id: str,
        body: dict,
        current_user: dict,
    ) -> JSONResponse:
        """
        Accept a candidate answer, evaluate it with AI, and persist the result.

        Returns 200 on success.
        """
        try:
            user_id = str(current_user["id"])

            if not body.get("questionId"):
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": "questionId is required."},
                )
            if not body.get("candidateAnswer", "").strip():
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": "candidateAnswer must not be blank."},
                )

            evaluation = interview_service.submit_answer(
                interview_id=interview_id,
                user_id=user_id,
                question_id=body["questionId"],
                candidate_answer=body["candidateAnswer"].strip(),
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Answer submitted and evaluated successfully.",
                    "data": evaluation,
                },
            )

        except ValueError as error:
            status = 409 if "already been answered" in str(error).lower() else 400
            return JSONResponse(
                status_code=status,
                content={"success": False, "message": str(error)},
            )

        except PermissionError as error:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": str(error)},
            )

        except RuntimeError as error:
            logger.error("Answer submission error for %s: %s", interview_id, error)
            if "rate" in str(error).lower() or "429" in str(error):
                return JSONResponse(
                    status_code=429,
                    content={"success": False, "message": "AI service rate limit reached. Please try again shortly."},
                )
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": str(error)},
            )

        except Exception as error:
            logger.error("Unexpected error submitting answer for %s: %s", interview_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )

    # ── GET /api/interviews/{interview_id} ──────────────────────────────────

    @staticmethod
    async def get_interview(interview_id: str, current_user: dict) -> JSONResponse:
        """
        Return metadata for a single interview session.

        Returns 200 on success.
        """
        try:
            user_id = str(current_user["id"])

            interview = interview_service.get_interview(
                interview_id=interview_id,
                user_id=user_id,
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Interview retrieved successfully.",
                    "data": interview,
                },
            )

        except ValueError as error:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": str(error)},
            )

        except PermissionError as error:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": str(error)},
            )

        except Exception as error:
            logger.error("Unexpected error fetching interview %s: %s", interview_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )

    # ── GET /api/interviews/{interview_id}/history ──────────────────────────

    @staticmethod
    async def get_interview_history(
        interview_id: str,
        current_user: dict,
    ) -> JSONResponse:
        """
        Return the complete question-answer-evaluation history for an interview.

        Returns 200 on success.
        """
        try:
            user_id = str(current_user["id"])

            history = interview_service.get_interview_history(
                interview_id=interview_id,
                user_id=user_id,
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Interview history retrieved successfully.",
                    "data": history,
                },
            )

        except ValueError as error:
            return JSONResponse(
                status_code=404,
                content={"success": False, "message": str(error)},
            )

        except PermissionError as error:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": str(error)},
            )

        except Exception as error:
            logger.error("Unexpected error fetching history for %s: %s", interview_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )

    # ── POST /api/interviews/{interview_id}/end ─────────────────────────────

    @staticmethod
    async def end_interview(interview_id: str, current_user: dict) -> JSONResponse:
        """
        Complete an interview session and return the summary.

        Returns 200 on success.
        """
        try:
            user_id = str(current_user["id"])

            summary = interview_service.end_interview(
                interview_id=interview_id,
                user_id=user_id,
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Interview completed successfully.",
                    "data": summary,
                },
            )

        except ValueError as error:
            status = 409 if "already been completed" in str(error).lower() else 400
            return JSONResponse(
                status_code=status,
                content={"success": False, "message": str(error)},
            )

        except PermissionError as error:
            return JSONResponse(
                status_code=403,
                content={"success": False, "message": str(error)},
            )

        except Exception as error:
            logger.error("Unexpected error ending interview %s: %s", interview_id, error)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )

    # ── GET /api/interviews/user/{user_id} ──────────────────────────────────

    @staticmethod
    async def get_user_interviews(
        requested_user_id: str,
        current_user: dict,
    ) -> JSONResponse:
        """
        Return all interview sessions for a user.

        Enforces that the authenticated user can only retrieve their own interviews
        (unless future admin roles are introduced).

        Returns 200 on success.
        """
        try:
            auth_user_id = str(current_user["id"])

            # Candidates may only access their own interview list
            if requested_user_id != auth_user_id:
                return JSONResponse(
                    status_code=403,
                    content={
                        "success": False,
                        "message": "You are not authorised to view another user's interviews.",
                    },
                )

            interviews = interview_service.get_user_interviews(user_id=auth_user_id)

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": f"Retrieved {len(interviews)} interview(s) for user.",
                    "data": interviews,
                },
            )

        except ValueError as error:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": str(error)},
            )

        except Exception as error:
            logger.error(
                "Unexpected error listing interviews for user %s: %s",
                requested_user_id,
                error,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "An unexpected error occurred. Please try again.",
                },
            )
