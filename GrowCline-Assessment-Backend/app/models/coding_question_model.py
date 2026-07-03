from datetime import datetime
from bson import ObjectId


class CodingQuestion:
    @staticmethod
    def create_question(
        title,
        programming_language,
        category,
        problem_statement,
        difficulty,
        input_format,
        output_format,
        constraints,
        sample_test_cases,
        hidden_test_cases,
        marks=10,
        time_limit=2,
        memory_limit=256,
        explanation="",
        tags=None,
        created_by=None,
    ):
        return {
            "_id": ObjectId(),

            "title": title,

            "programmingLanguage": programming_language,

            "category": category,

            "problemStatement": problem_statement,

            "difficulty": difficulty,

            "inputFormat": input_format,

            "outputFormat": output_format,

            "constraints": constraints,

            "sampleTestCases": sample_test_cases,

            "hiddenTestCases": hidden_test_cases,

            "marks": marks,

            "timeLimit": time_limit,

            "memoryLimit": memory_limit,

            "explanation": explanation,

            "tags": tags if tags else [],

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
    def response(question):
        return {
            "id": str(question["_id"]),

            "title": question["title"],

            "programmingLanguage": question["programmingLanguage"],

            "category": question["category"],

            "problemStatement": question["problemStatement"],

            "difficulty": question["difficulty"],

            "inputFormat": question["inputFormat"],

            "outputFormat": question["outputFormat"],

            "constraints": question["constraints"],

            "sampleTestCases": question["sampleTestCases"],

            "marks": question["marks"],

            "timeLimit": question["timeLimit"],

            "memoryLimit": question["memoryLimit"],

            "explanation": question["explanation"],

            "tags": question.get("tags", []),

            "isActive": question["isActive"],

            "createdBy": (
                str(question["createdBy"])
                if question.get("createdBy")
                else None
            ),

            "createdAt": question["createdAt"],

            "updatedAt": question["updatedAt"],
        }