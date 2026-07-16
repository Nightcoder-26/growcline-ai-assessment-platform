from bson import ObjectId
from bson.errors import InvalidId
from app.database import todos_collection


def create_todo(todo):
    todo_dict = todo.dict()

    # Every new todo starts as incomplete
    todo_dict["completed"] = False

    result = todos_collection.insert_one(todo_dict)

    created_todo = todos_collection.find_one({"_id": result.inserted_id})

    created_todo["id"] = str(created_todo["_id"])
    del created_todo["_id"]

    return created_todo


def get_all_todos():
    todos = []

    for todo in todos_collection.find():
        todo["id"] = str(todo["_id"])
        del todo["_id"]
        todos.append(todo)

    return todos


def get_todo_by_id(todo_id):
    try:
        object_id = ObjectId(todo_id)
    except InvalidId:
        return "invalid"

    todo = todos_collection.find_one({"_id": object_id})

    if not todo:
        return None

    todo["id"] = str(todo["_id"])
    del todo["_id"]

    return todo


def update_todo(todo_id, todo):
    try:
        object_id = ObjectId(todo_id)
    except InvalidId:
        return "invalid"

    result = todos_collection.update_one(
        {"_id": object_id},
        {"$set": todo.dict()}
    )

    if result.matched_count == 0:
        return None

    updated_todo = todos_collection.find_one({"_id": object_id})

    updated_todo["id"] = str(updated_todo["_id"])
    del updated_todo["_id"]

    return updated_todo


def delete_todo(todo_id):
    try:
        object_id = ObjectId(todo_id)
    except InvalidId:
        return "invalid"

    result = todos_collection.delete_one({"_id": object_id})

    if result.deleted_count == 0:
        return False

    return True