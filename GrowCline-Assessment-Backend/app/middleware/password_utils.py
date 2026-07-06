from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    if not hashed_password or not password:
        return False
    return check_password_hash(hashed_password, password)
