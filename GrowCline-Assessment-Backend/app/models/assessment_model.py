from datetime import datetime
from bson import ObjectId


class Assessment:
    @staticmethod
    def create_assessment(
        title,
        assessment_type,
        user_id,
        aptitude_questions=None,
        technical_questions=None,
        coding_questions=None,
        duration=60,
        total_marks=100,
        created_by=None,
        instructions=None,
        passing_percentage=40,
        scheduled_at=None,
        expires_at=None,
    ):
        aptitude_questions = aptitude_questions or []
        technical_questions = technical_questions or []
        coding_questions = coding_questions or []
        instructions = instructions or []

        total_questions = (
            len(aptitude_questions)
            + len(technical_questions)
            + len(coding_questions)
        )

        return {
            "_id": ObjectId(),

            "title": title,

            "assessmentType": assessment_type,

            "userId": ObjectId(user_id),

            "aptitudeQuestions": [
                ObjectId(question_id)
                for question_id in aptitude_questions
            ],

            "technicalQuestions": [
                ObjectId(question_id)
                for question_id in technical_questions
            ],

            "codingQuestions": [
                ObjectId(question_id)
                for question_id in coding_questions
            ],

            "totalQuestions": total_questions,

            "totalMarks": total_marks,

            "duration": duration,

            "passingPercentage": passing_percentage,

            "instructions": instructions,

            "status": "Pending",

            "scheduledAt": scheduled_at,

            "startedAt": None,

            "submittedAt": None,

            "expiresAt": expires_at,

            "isActive": True,

            "createdBy": (
                ObjectId(created_by)
                if created_by
                else None
            ),

            "createdAt": datetime.utcnow(),

            "updatedAt": datetime.utcnow(),
        }

    @staticmethod
    def response(assessment):
        return {
            "id": str(assessment["_id"]),

            "title": assessment["title"],

            "assessmentType": assessment["assessmentType"],

            "userId": str(assessment["userId"]),

            "aptitudeQuestions": [
                str(question_id)
                for question_id in assessment["aptitudeQuestions"]
            ],

            "technicalQuestions": [
                str(question_id)
                for question_id in assessment["technicalQuestions"]
            ],

            "codingQuestions": [
                str(question_id)
                for question_id in assessment["codingQuestions"]
            ],

            "totalQuestions": assessment["totalQuestions"],

            "totalMarks": assessment["totalMarks"],

            "duration": assessment["duration"],

            "passingPercentage": assessment["passingPercentage"],

            "instructions": assessment["instructions"],

            "status": assessment["status"],

            "scheduledAt": assessment["scheduledAt"],

            "startedAt": assessment["startedAt"],

            "submittedAt": assessment["submittedAt"],

            "expiresAt": assessment["expiresAt"],

            "isActive": assessment["isActive"],

            "createdBy": (
                str(assessment["createdBy"])
                if assessment.get("createdBy")
                else None
            ),

            "createdAt": assessment["createdAt"],

            "updatedAt": assessment["updatedAt"],
        }