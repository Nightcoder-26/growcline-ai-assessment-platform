def serialize_user(user):
    if user:
        user["id"] = str(user["_id"])
        del user["_id"]
    return user