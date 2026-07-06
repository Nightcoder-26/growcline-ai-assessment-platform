from marshmallow import Schema, fields, validate


class ResultCalculationSchema(Schema):
    assessment_id = fields.Str(
        required=True,
        error_messages={
            "required": "Assessment ID is required."
        }
    )

    user_id = fields.Str(
        required=True,
        error_messages={
            "required": "User ID is required."
        }
    )

    aptitude_score = fields.Float(
        required=False,
        load_default=0.0,
        validate=validate.Range(min=0)
    )

    technical_score = fields.Float(
        required=False,
        load_default=0.0,
        validate=validate.Range(min=0)
    )

    coding_score = fields.Float(
        required=False,
        load_default=0.0,
        validate=validate.Range(min=0)
    )

    total_score = fields.Float(required=False, load_default=0.0)
    percentage = fields.Float(required=False, load_default=0.0)
    rank = fields.Int(required=False, load_default=None)
    total_questions = fields.Int(required=False, load_default=0)
    correct_answers = fields.Int(required=False, load_default=0)
    wrong_answers = fields.Int(required=False, load_default=0)
    unanswered_questions = fields.Int(required=False, load_default=0)
    total_time = fields.Int(required=False, load_default=0)
    strongest_skill = fields.Str(required=False, load_default="")
    weakest_skill = fields.Str(required=False, load_default="")
    recommendation = fields.Str(required=False, load_default="")
    status = fields.Str(required=False, load_default="Completed")
    aptitude_answers = fields.List(fields.Dict(), required=False, load_default=[])
    technical_answers = fields.List(fields.Dict(), required=False, load_default=[])
    coding_submissions = fields.List(fields.Dict(), required=False, load_default=[])


class ResultQuerySchema(Schema):
    result_id = fields.Str(
        required=True,
        error_messages={
            "required": "Result ID is required."
        }
    )


class CandidateResultSchema(Schema):
    user_id = fields.Str(
        required=True,
        error_messages={
            "required": "User ID is required."
        }
    )


class AssessmentResultSchema(Schema):
    assessment_id = fields.Str(
        required=True,
        error_messages={
            "required": "Assessment ID is required."
        }
    )


class DeleteResultSchema(Schema):
    result_id = fields.Str(
        required=True,
        error_messages={
            "required": "Result ID is required."
        }
    )