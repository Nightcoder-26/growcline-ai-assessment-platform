import os
import datetime
import jwt

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", os.environ.get("JWT_SECRET", "growcline-super-secret-key"))


def generate_token(payload: dict, expires_in_hours: int = 24) -> str:
    data = payload.copy()
    data["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in_hours)
    return jwt.encode(data, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception:
        return {}
