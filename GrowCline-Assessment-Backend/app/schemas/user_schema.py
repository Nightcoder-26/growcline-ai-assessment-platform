from marshmallow import Schema, ValidationError, fields, validate, validates, validates_schema


class UserRegistrationSchema(Schema):
    full_name = fields.Str(
        required=False,
        validate=validate.Length(
            min=3,
            max=100
        ),
        error_messages={
            "required": "Full name is required."
        }
    )

    name = fields.Str(
        required=False,
        validate=validate.Length(
            min=3,
            max=100
        )
    )

    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Enter a valid email address."
        }
    )

    password = fields.Str(
        required=True,
        validate=validate.Length(
            min=8,
            max=128
        ),
        error_messages={
            "required": "Password is required."
        }
    )

    role = fields.Str(
        load_default="candidate",
        validate=validate.OneOf(
            [
                "admin",
                "candidate"
            ]
        )
    )


class UserLoginSchema(Schema):
    email = fields.Email(
        required=True,
        error_messages={
            "required": "Email is required.",
            "invalid": "Enter a valid email address."
        }
    )

    password = fields.Str(
        required=True,
        error_messages={
            "required": "Password is required."
        }
    )


class UserProfileUpdateSchema(Schema):
    full_name = fields.Str(
        validate=validate.Length(
            min=3,
            max=100
        )
    )

    name = fields.Str(
        validate=validate.Length(
            min=3,
            max=100
        )
    )

    email = fields.Email()


class ChangePasswordSchema(Schema):
    current_password = fields.Str(
        required=True
    )

    new_password = fields.Str(
        required=True,
        validate=validate.Length(
            min=8,
            max=128
        )
    )

    confirm_password = fields.Str(
        required=True
    )

    @validates_schema
    def validate_confirm_password(
        self,
        data,
        **kwargs
    ):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if (
            new_password
            and confirm_password
            and confirm_password != new_password
        ):
            raise ValidationError(
                "Passwords do not match.",
                field_name="confirm_password"
            )