from pydantic import BaseModel


class TodoCreate(BaseModel):
    title: str
    description: str


class TodoUpdate(BaseModel):
    title: str
    description: str
    completed: bool


class TodoResponse(BaseModel):
    id: str
    title: str
    description: str
    completed: bool