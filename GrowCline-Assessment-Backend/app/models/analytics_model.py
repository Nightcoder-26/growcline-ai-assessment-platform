from datetime import datetime
from bson import ObjectId


class Analytics:
    @staticmethod
    def create_analytics(
        user_id,
        assessment_id,
        aptitude_score=0,
        technical_score=0,
        coding_score=0,
        total_score=0,
        percentage=0.0,
        rank=None,
        strongest_skill="",
        weakest_skill="",
        recommendation="",
        total_questions=0,
        correct_answers=0,
        wrong_answers=0,
        unanswered_questions=0,
        total_time=0
    ):
        return {
            "_id": ObjectId(),

            "userId": ObjectId(user_id),
            "assessmentId": ObjectId(assessment_id),

            "aptitudeScore": aptitude_score,
            "technicalScore": technical_score,
            "codingScore": coding_score,

            "totalScore": total_score,
            "percentage": percentage,
            "rank": rank,

            "strongestSkill": strongest_skill,
            "weakestSkill": weakest_skill,

            "recommendation": recommendation,

            "totalQuestions": total_questions,
            "correctAnswers": correct_answers,
            "wrongAnswers": wrong_answers,
            "unansweredQuestions": unanswered_questions,

            "totalTime": total_time,

            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }

    @staticmethod
    def analytics_response(analytics):
        return {
            "id": str(analytics["_id"]),
            "userId": str(analytics["userId"]),
            "assessmentId": str(analytics["assessmentId"]),

            "aptitudeScore": analytics["aptitudeScore"],
            "technicalScore": analytics["technicalScore"],
            "codingScore": analytics["codingScore"],

            "totalScore": analytics["totalScore"],
            "percentage": analytics["percentage"],
            "rank": analytics["rank"],

            "strongestSkill": analytics["strongestSkill"],
            "weakestSkill": analytics["weakestSkill"],

            "recommendation": analytics["recommendation"],

            "totalQuestions": analytics["totalQuestions"],
            "correctAnswers": analytics["correctAnswers"],
            "wrongAnswers": analytics["wrongAnswers"],
            "unansweredQuestions": analytics["unansweredQuestions"],

            "totalTime": analytics["totalTime"],

            "createdAt": analytics["createdAt"],
            "updatedAt": analytics["updatedAt"]
        }