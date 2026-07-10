"""
Coding Schema Module
Marshmallow schemas for Coding Question validation.
"""

from marshmallow import Schema, fields, validate


class CodingQuestionSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    programmingLanguage = fields.Str(required=False, load_default="Python")
    difficulty = fields.Str(required=False, validate=validate.OneOf(["Easy", "Medium", "Hard"]), load_default="Easy")
    problemStatement = fields.Str(required=True, validate=validate.Length(min=5, max=10000))
    inputFormat = fields.Str(required=False, load_default="")
    outputFormat = fields.Str(required=False, load_default="")
    constraints = fields.Str(required=False, load_default="")
    sampleInput = fields.Str(required=False, load_default="")
    sampleOutput = fields.Str(required=False, load_default="")
    testCases = fields.List(fields.Dict(), required=False, load_default=[])
    hiddenTestCases = fields.List(fields.Dict(), required=False, load_default=[])
    marks = fields.Int(required=False, load_default=10, validate=validate.Range(min=1, max=1000))
    category = fields.Str(required=False, load_default="Algorithms")
    tags = fields.List(fields.Str(), required=False, load_default=[])


class CodingAssessmentSchema(Schema):
    programmingLanguage = fields.Str(required=False)
    numberOfQuestions = fields.Int(required=False, load_default=5, validate=validate.Range(min=1, max=100))
    total_questions = fields.Int(required=False, load_default=5, validate=validate.Range(min=1, max=100))
    difficulty = fields.Str(validate=validate.OneOf(["Easy", "Medium", "Hard"]), load_default=None)


class CodingSubmissionSchema(Schema):
    assessmentId = fields.Str(required=False)
    answers = fields.List(fields.Dict(), required=True)
