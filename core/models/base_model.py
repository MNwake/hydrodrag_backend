# core/models/base_document.py
from mongoengine import Document, DateTimeField

from utils import utcnow


class BaseDocument(Document):
    created_at = DateTimeField(default=utcnow)
    updated_at = DateTimeField(default=utcnow)

    meta = {
        "abstract": True
    }

    def to_dict(self) -> dict:
        """
        Converts MongoEngine document to a clean dict
        suitable for Pydantic serialization.
        """
        data = self.to_mongo().to_dict()

        # Convert ObjectId → str
        data["id"] = str(data.pop("_id"))

        return data

    def save(self, *args, **kwargs):
        self.updated_at = utcnow()
        return super().save(*args, **kwargs)