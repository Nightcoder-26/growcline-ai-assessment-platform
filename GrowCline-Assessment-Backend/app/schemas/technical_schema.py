from marshmallow import Schema, fields, validate


class TechnicalQuestionSchema(Schema):
    question = fields.Str(
        required=True,
        validate=validate.Length(
            min=10,
            max=1000
        ),
        error_messages={
            "required": "Question is required."
        }
    )

    category = fields.Str(
        required=True,
        validate=validate.Length(
            min=2,
            max=100
        ),
        error_messages={
            "required": "Category is required."
        }
    )

    difficulty = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "Easy",
                "Medium",
                "Hard"
            ]
        ),
        error_messages={
            "required": "Difficulty is required."
        }
    )

    options = fields.List(
        fields.Str(),
        required=True,
        validate=validate.Length(
            min=2,
            max=6
        ),
        error_messages={
            "required": "Options are required."
        }
    )

    correct_answer = fields.Str(
        required=True,
        error_messages={
            "required": "Correct answer is required."
        }
    )

    explanation = fields.Str(
        load_default=""
    )

    marks = fields.Int(
        required=True,
        validate=validate.Range(
            min=1,
            max=100
        ),
        error_messages={
            "required": "Marks are required."
        }
    )

    technology = fields.Str(load_default=None)
    question_type = fields.Str(load_default="MCQ")
    questionType = fields.Str(load_default="MCQ")
    tags = fields.List(fields.Str(), load_default=[])
    created_by = fields.Str(load_default=None)
    createdBy = fields.Str(load_default=None)


class TechnicalAssessmentSchema(Schema):
    total_questions = fields.Int(
        required=True,
        validate=validate.Range(
            min=1
        ),
        error_messages={
            "required": "Total questions is required."
        }
    )

    difficulty = fields.Str(
        validate=validate.OneOf(
            [
                "Easy",
                "Medium",
                "Hard"
            ]
        ),
        load_default=None
    )

    category = fields.Str(
        load_default=None
    )


class TechnicalSubmissionSchema(Schema):
    assessment_id = fields.Str(
        required=False
    )

    user_id = fields.Str(
        required=False
    )

    answers = fields.List(
        fields.Dict(),
        required=True,
        validate=validate.Length(
            min=1
        ),
        error_messages={
            "required": "Answers are required."
        }
    )