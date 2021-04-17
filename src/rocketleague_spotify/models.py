from typing import Optional

from bson import ObjectId
from pydantic import BaseModel


class ObjectIdHelper(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(BaseModel):
    id: str
    goal_music_uri: str


class UpdateUserModel(User):
    id: Optional[str]

class DeleteManyResponse(BaseModel):
    deleted_count: int
