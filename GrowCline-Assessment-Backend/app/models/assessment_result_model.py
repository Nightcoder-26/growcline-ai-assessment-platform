from datetime import datetime
from bson import ObjectId


class AssessmentResult:
    @staticmethod
    def create_result(
        assessment_id,
        user_id,
        aptitude_answers=None,
        technical_answers=None,
        coding_submissions=None,
        aptitude_score=0,
        technical_score=0,
        coding_score=0,
        total_score=0,
        percentage=0.0,
        rank=None,
        total_questions=0,
        correct_answers=0,
        wrong_answers=0,
        unanswered_questions=0,
        total_time=0,
        strongest_skill="",
        weakest_skill="",
        recommendation="",
        status="Completed",
    ):
        aptitude_answers = aptitude_answers or []
        technical_answers = technical_answers or []
        coding_submissions = coding_submissions or []

        return {
            "_id": ObjectId(),

            "assessmentId": ObjectId(assessment_id),

            "userId": ObjectId(user_id),

            "aptitudeAnswers": aptitude_answers,

            "technicalAnswers": technical_answers,

            "codingSubmissions": coding_submissions,

            "aptitudeScore": aptitude_score,

            "technicalScore": technical_score,

            "codingScore": coding_score,

            "totalScore": total_score,

            "percentage": percentage,

            "rank": rank,

            "totalQuestions": total_questions,

            "correctAnswers": correct_answers,

            "wrongAnswers": wrong_answers,

            "unansweredQuestions": unanswered_questions,

            "totalTime": total_time,

            "strongestSkill": strongest_skill,

            "weakestSkill": weakest_skill,

            "recommendation": recommendation,

            "status": status,

            "createdAt": datetime.utcnow(),

            "updatedAt": datetime.utcnow(),
        }

    @staticmethod
    def response(result):
        return {
            "id": str(result["_id"]),

            "assessmentId": str(result["assessmentId"]),

            "userId": str(result["userId"]),

            "aptitudeAnswers": result["aptitudeAnswers"],

            "technicalAnswers": result["technicalAnswers"],

            "codingSubmissions": result["codingSubmissions"],

            "aptitudeScore": result["aptitudeScore"],

            "technicalScore": result["technicalScore"],

            "codingScore": result["codingScore"],

            "totalScore": result["totalScore"],

            "percentage": result["percentage"],

            "rank": result["rank"],

            "totalQuestions": result["totalQuestions"],

            "correctAnswers": result["correctAnswers"],

            "wrongAnswers": result["wrongAnswers"],

            "unansweredQuestions": result["unansweredQuestions"],

            "totalTime": result["totalTime"],

            "strongestSkill": result["strongestSkill"],

            "weakestSkill": result["weakestSkill"],

            "recommendation": result["recommendation"],

            "status": result["status"],

            "createdAt": result["createdAt"],

            "updatedAt": result["updatedAt"],
        }