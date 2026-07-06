from marshmallow import Schema, fields, validate


class AssessmentCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str(required=False, load_default="")
    job_role = fields.Str(required=False, load_default="")
    jobRole = fields.Str(required=False, load_default="")
    duration = fields.Int(required=False, load_default=60, validate=validate.Range(min=1))
    total_questions = fields.Int(required=False, load_default=10, validate=validate.Range(min=1))
    totalQuestions = fields.Int(required=False, load_default=10, validate=validate.Range(min=1))
    status = fields.Str(validate=validate.OneOf(["Draft", "Published", "Archived", "Completed"]), load_default="Draft")


class AssessmentUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=3, max=200))
    description = fields.Str()
    job_role = fields.Str()
    jobRole = fields.Str()
    duration = fields.Int(validate=validate.Range(min=1))
    total_questions = fields.Int(validate=validate.Range(min=1))
    totalQuestions = fields.Int(validate=validate.Range(min=1))
    status = fields.Str(validate=validate.OneOf(["Draft", "Published", "Archived", "Completed"]))


class AssessmentStartSchema(Schema):
    user_id = fields.Str(required=False)
    userId = fields.Str(required=False)


class AssessmentSubmitSchema(Schema):
    user_id = fields.Str(required=False)
    userId = fields.Str(required=False)
    answers = fields.Dict(required=False, load_default={})
