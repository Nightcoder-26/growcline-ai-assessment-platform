from marshmallow import Schema, fields, validate


class AptitudeQuestionSchema(Schema):
    question = fields.Str(required=True, validate=validate.Length(min=5, max=1000))
    category = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    difficulty = fields.Str(required=True, validate=validate.OneOf(["Easy", "Medium", "Hard"]))
    options = fields.List(fields.Str(), required=True, validate=validate.Length(min=2, max=6))
    correct_answer = fields.Str(required=True)
    explanation = fields.Str(load_default="")
    marks = fields.Int(required=False, load_default=1, validate=validate.Range(min=1, max=100))
    question_type = fields.Str(load_default="MCQ")
    questionType = fields.Str(load_default="MCQ")
    tags = fields.List(fields.Str(), load_default=[])


class AptitudeAssessmentSchema(Schema):
    total_questions = fields.Int(required=True, validate=validate.Range(min=1))
    difficulty = fields.Str(validate=validate.OneOf(["Easy", "Medium", "Hard"]), load_default=None)
    category = fields.Str(load_default=None)


class AptitudeSubmissionSchema(Schema):
    assessment_id = fields.Str(required=False)
    user_id = fields.Str(required=False)
    answers = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1))
