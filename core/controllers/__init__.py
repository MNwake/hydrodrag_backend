from typing import Type, List
from mongoengine import EmbeddedDocument


def convert_embedded(
    model: Type[EmbeddedDocument],
    value: dict | list | None,
):
    if value is None:
        return None

    if isinstance(value, list):
        return [model.from_payload(v) for v in value]

    return model.from_payload(value)