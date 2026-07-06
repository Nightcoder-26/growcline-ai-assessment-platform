from marshmallow import Schema, fields, validate


class CodingQuestionSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str(required=True, validate=validate.Length(min=10, max=5000))
    difficulty = fields.Str(required=True, validate=validate.OneOf(["Easy", "Medium", "Hard"]))
    category = fields.Str(required=False, load_default="General")
    marks = fields.Int(required=False, load_default=10, validate=validate.Range(min=1, max=100))
    test_cases = fields.List(fields.Dict(), required=False, load_default=[])
    testCases = fields.List(fields.Dict(), required=False, load_default=[])
    sample_code = fields.Dict(required=False, load_default={})
    sampleCode = fields.Dict(required=False, load_default={})
    constraints = fields.List(fields.Str(), required=False, load_default=[])
    tags = fields.List(fields.Str(), required=False, load_default=[])


class CodingAssessmentSchema(Schema):
    total_questions = fields.Int(required=True, validate=validate.Range(min=1))
    difficulty = fields.Str(validate=validate.OneOf(["Easy", "Medium", "Hard"]), load_default=None)
    category = fields.Str(load_default=None)


class CodeRunSchema(Schema):
    question_id = fields.Str(required=False)
    questionId = fields.Str(required=False)
    code = fields.Str(required=True)
    language = fields.Str(required=True)
    test_cases = fields.List(fields.Dict(), required=False, load_default=[])
    testCases = fields.List(fields.Dict(), required=False, load_default=[])


class CodingSubmissionSchema(Schema):
    assessment_id = fields.Str(required=False)
    user_id = fields.Str(required=False)
    submissions = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1))
