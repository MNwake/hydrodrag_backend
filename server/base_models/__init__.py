# server/schemas/base.py
from typing import TypeVar

T = TypeVar("T", bound="MongoReadModel")

from bson import ObjectId
from pydantic import BaseModel


class MongoReadModel(BaseModel):
    @classmethod
    def from_mongo(cls, document):
        raw = document.to_mongo().to_dict()
        data = {}

        for key, value in raw.items():
            if key == "_id":
                data["id"] = str(value)
            elif isinstance(value, ObjectId):
                data[key] = str(value)
            else:
                data[key] = value

        return cls(**data)