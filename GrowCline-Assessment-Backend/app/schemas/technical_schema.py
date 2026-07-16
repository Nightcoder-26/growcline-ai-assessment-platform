"""
Technical Schema Module
Marshmallow schemas for Technical Question validation.
"""

from marshmallow import Schema, fields, validate, pre_load


class TechnicalQuestionSchema(Schema):
    question = fields.Str(required=True, validate=validate.Length(min=3, max=2000))
    technology = fields.Str(required=False, load_default="Python")
    category = fields.Str(required=False, load_default="Python")
    difficulty = fields.Str(required=False, validate=validate.OneOf(["Easy", "Medium", "Hard"]), load_default="Easy")
    options = fields.List(fields.Str(), required=True, validate=validate.Length(min=2, max=10))
    correctAnswer = fields.Str(required=False)
    correct_answer = fields.Str(required=False)
    explanation = fields.Str(load_default="")
    marks = fields.Int(required=False, load_default=1, validate=validate.Range(min=1, max=100))
    questionType = fields.Str(load_default="MCQ")
    question_type = fields.Str(load_default="MCQ")
    tags = fields.List(fields.Str(), load_default=[])

    @pre_load
    def normalize_fields(self, data, **kwargs):
        if isinstance(data, dict):
            if "correctAnswer" in data and "correct_answer" not in data:
                data = dict(data)
                data["correct_answer"] = data["correctAnswer"]
            elif "correct_answer" in data and "correctAnswer" not in data:
                data = dict(data)
                data["correctAnswer"] = data["correct_answer"]
        return data


class TechnicalAssessmentSchema(Schema):
    technology = fields.Str(required=False)
    numberOfQuestions = fields.Int(required=False, load_default=10, validate=validate.Range(min=1, max=100))
    total_questions = fields.Int(required=False, load_default=10, validate=validate.Range(min=1, max=100))
    difficulty = fields.Str(validate=validate.OneOf(["Easy", "Medium", "Hard"]), load_default=None)
    category = fields.Str(load_default=None)


class TechnicalSubmissionSchema(Schema):
    assessmentId = fields.Str(required=False)
    answers = fields.List(fields.Dict(), required=True)