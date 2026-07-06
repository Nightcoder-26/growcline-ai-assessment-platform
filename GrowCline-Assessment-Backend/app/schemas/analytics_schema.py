from marshmallow import Schema, fields


class AnalyticsQuerySchema(Schema):
    start_date = fields.Str(required=False)
    end_date = fields.Str(required=False)
    assessment_id = fields.Str(required=False)
    user_id = fields.Str(required=False)


class SkillAnalysisSchema(Schema):
    user_id = fields.Str(required=False)
    category = fields.Str(required=False)
